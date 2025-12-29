"""Job orchestration service."""

import asyncio
import uuid
from typing import Any

import structlog

from app.agents.graph import get_research_graph
from app.agents.state import AgentState
from app.core.config import get_settings
from app.core.errors import classify_error
from app.core.logging import get_logger
from app.db.models import JobStatus
from app.db.repo import ResearchJobRepository
from app.db.session import get_session

logger = get_logger(__name__)


class JobService:
    """Service for managing research jobs."""

    async def create_job(self, query: str) -> str:
        """Create a new research job.
        
        Args:
            query: Research query
            
        Returns:
            Job ID
        """
        settings = get_settings()
        job_id = str(uuid.uuid4())
        trace_id = str(uuid.uuid4())
        
        # Bind context for logging
        structlog.contextvars.bind_contextvars(job_id=job_id, trace_id=trace_id)
        
        logger.info("job_created", query=query)
        
        # Save to database
        async with get_session() as session:
            repo = ResearchJobRepository(session)
            await repo.create_job(
                job_id=job_id,
                query=query,
                max_steps=settings.max_agent_steps,
            )
        
        # Start job execution in background
        asyncio.create_task(self._execute_job(job_id, query, trace_id))
        
        return job_id

    async def _execute_job(self, job_id: str, query: str, trace_id: str) -> None:
        """Execute research job (runs in background).
        
        Args:
            job_id: Job identifier
            query: Research query
            trace_id: Trace identifier
        """
        structlog.contextvars.bind_contextvars(job_id=job_id, trace_id=trace_id)
        logger.info("job_execution_started")
        
        try:
            # Update status to running
            async with get_session() as session:
                repo = ResearchJobRepository(session)
                await repo.update_job_status(
                    job_id=job_id,
                    status=JobStatus.RUNNING,
                    progress="Starting research workflow",
                )
            
            # Initialize state
            settings = get_settings()
            initial_state: AgentState = {
                "job_id": job_id,
                "query": query,
                "trace_id": trace_id,
                "step_count": 0,
                "max_steps": settings.max_agent_steps,
                "max_urls": settings.max_urls,
                "errors": [],
                "progress": "Initializing",
            }
            
            # Execute workflow with streaming to update progress in real-time
            graph = get_research_graph()
            final_state = initial_state
            
            async for chunk in graph.astream(initial_state):
                # Each chunk contains the output from one node
                for node_name, node_output in chunk.items():
                    # Merge node output into final state
                    final_state = {**final_state, **node_output}
                    
                    # Update database with current progress
                    step_count = final_state.get("step_count", 0)
                    progress = final_state.get("progress", "Processing...")
                    
                    async with get_session() as session:
                        repo = ResearchJobRepository(session)
                        await repo.update_job_status(
                            job_id=job_id,
                            status=JobStatus.RUNNING,
                            progress=progress,
                            step_count=step_count,
                        )
                    
                    logger.info(
                        "node_completed",
                        node=node_name,
                        step_count=step_count,
                        progress=progress,
                    )
            
            # Save results
            async with get_session() as session:
                repo = ResearchJobRepository(session)
                
                # Save report if generated
                if final_state.get("report_md"):
                    await repo.save_report(
                        job_id=job_id,
                        report_md=final_state["report_md"],
                        report_json=final_state.get("report_json", {}),
                    )
                
                # Update final status
                errors = final_state.get("errors", [])
                if errors:
                    await repo.update_job_status(
                        job_id=job_id,
                        status=JobStatus.COMPLETED,  # Completed with errors
                        progress=f"Completed with {len(errors)} errors",
                        step_count=final_state.get("step_count", 0),
                    )
                else:
                    await repo.update_job_status(
                        job_id=job_id,
                        status=JobStatus.COMPLETED,
                        progress="Completed successfully",
                        step_count=final_state.get("step_count", 0),
                    )
            
            logger.info(
                "job_execution_completed",
                step_count=final_state.get("step_count", 0),
                error_count=len(final_state.get("errors", [])),
            )
            
        except Exception as e:
            logger.error("job_execution_failed", error=str(e), error_type=type(e).__name__)
            
            # Update status to failed
            async with get_session() as session:
                repo = ResearchJobRepository(session)
                await repo.update_job_status(
                    job_id=job_id,
                    status=JobStatus.FAILED,
                    progress="Job failed",
                    error_message=str(e),
                )
                
                # Add error to job
                await repo.add_error(
                    job_id=job_id,
                    error={
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "error_category": classify_error(e),
                    },
                )

    async def get_job_status(self, job_id: str) -> dict[str, Any]:
        """Get job status and progress.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status information
        """
        async with get_session() as session:
            repo = ResearchJobRepository(session)
            job = await repo.get_job(job_id)
            
            return {
                "job_id": job.job_id,
                "query": job.query,
                "status": job.status.value,
                "progress": job.progress,
                "step_count": job.step_count,
                "max_steps": job.max_steps,
                "errors": job.errors or [],
                "error_message": job.error_message,
                "created_at": job.created_at.isoformat(),
                "updated_at": job.updated_at.isoformat(),
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            }

    async def get_job_report(self, job_id: str) -> dict[str, Any]:
        """Get job report.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job report data
        """
        async with get_session() as session:
            repo = ResearchJobRepository(session)
            job = await repo.get_job(job_id)
            
            return {
                "job_id": job.job_id,
                "query": job.query,
                "status": job.status.value,
                "report_md": job.report_md,
                "report_json": job.report_json,
            }


# Global job service instance
_job_service: JobService | None = None


def get_job_service() -> JobService:
    """Get the global job service instance.
    
    Returns:
        JobService: Global job service
    """
    global _job_service
    if _job_service is None:
        _job_service = JobService()
    return _job_service
