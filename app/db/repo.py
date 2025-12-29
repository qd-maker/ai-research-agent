"""Repository pattern for database operations."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import DatabaseError, JobNotFoundError
from app.core.logging import get_logger
from app.db.models import ExtractedEntity, JobStatus, ResearchJob, SourceURL

logger = get_logger(__name__)


class ResearchJobRepository:
    """Repository for research job operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.
        
        Args:
            session: Database session
        """
        self.session = session

    async def create_job(
        self,
        job_id: str,
        query: str,
        max_steps: int,
    ) -> ResearchJob:
        """Create a new research job.
        
        Args:
            job_id: Unique job identifier
            query: Research query
            max_steps: Maximum execution steps
            
        Returns:
            Created research job
            
        Raises:
            DatabaseError: If job creation fails
        """
        try:
            job = ResearchJob(
                job_id=job_id,
                query=query,
                status=JobStatus.PENDING,
                max_steps=max_steps,
                errors=[],
            )
            self.session.add(job)
            await self.session.flush()
            logger.info("job_created", job_id=job_id, query=query)
            return job
        except Exception as e:
            logger.error("job_creation_failed", job_id=job_id, error=str(e))
            raise DatabaseError(f"Failed to create job: {e}") from e

    async def get_job(self, job_id: str) -> ResearchJob:
        """Get a research job by ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Research job
            
        Raises:
            JobNotFoundError: If job doesn't exist
        """
        result = await self.session.execute(
            select(ResearchJob).where(ResearchJob.job_id == job_id)
        )
        job = result.scalar_one_or_none()
        if job is None:
            raise JobNotFoundError(f"Job not found: {job_id}")
        return job

    async def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: str | None = None,
        step_count: int | None = None,
        error_message: str | None = None,
    ) -> ResearchJob:
        """Update job status and progress.
        
        Args:
            job_id: Job identifier
            status: New status
            progress: Progress description
            step_count: Current step count
            error_message: Error message if failed
            
        Returns:
            Updated job
        """
        job = await self.get_job(job_id)
        job.status = status
        if progress:
            job.progress = progress
        if step_count is not None:
            job.step_count = step_count
        if error_message:
            job.error_message = error_message
        if status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
            job.completed_at = datetime.utcnow()
        
        await self.session.flush()
        logger.info("job_status_updated", job_id=job_id, status=status.value, progress=progress)
        return job

    async def save_report(
        self,
        job_id: str,
        report_md: str,
        report_json: dict,
    ) -> ResearchJob:
        """Save job report.
        
        Args:
            job_id: Job identifier
            report_md: Markdown report
            report_json: JSON report data
            
        Returns:
            Updated job
        """
        job = await self.get_job(job_id)
        job.report_md = report_md
        job.report_json = report_json
        await self.session.flush()
        logger.info("job_report_saved", job_id=job_id)
        return job

    async def add_error(self, job_id: str, error: dict) -> None:
        """Add error to job error list.
        
        Args:
            job_id: Job identifier
            error: Error details
        """
        job = await self.get_job(job_id)
        if job.errors is None:
            job.errors = []
        job.errors.append(error)
        await self.session.flush()


class SourceURLRepository:
    """Repository for source URL operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.
        
        Args:
            session: Database session
        """
        self.session = session

    async def create_source(
        self,
        job_id: str,
        url: str,
        title: str | None = None,
        content: str | None = None,
        extra_metadata: dict | None = None,
        crawl_success: bool = False,
        crawl_error: str | None = None,
    ) -> SourceURL:
        """Create a source URL record.
        
        Args:
            job_id: Associated job ID
            url: Source URL
            title: Page title
            content: Page content
            extra_metadata: Additional metadata
            crawl_success: Whether crawl succeeded
            crawl_error: Crawl error message
            
        Returns:
            Created source URL
        """
        source = SourceURL(
            job_id=job_id,
            url=url,
            title=title,
            content=content,
            extra_metadata=extra_metadata,
            crawl_success=crawl_success,
            crawl_error=crawl_error,
        )
        self.session.add(source)
        await self.session.flush()
        return source

    async def get_sources_by_job(self, job_id: str) -> list[SourceURL]:
        """Get all sources for a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            List of source URLs
        """
        result = await self.session.execute(
            select(SourceURL).where(SourceURL.job_id == job_id)
        )
        return list(result.scalars().all())


class ExtractedEntityRepository:
    """Repository for extracted entity operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.
        
        Args:
            session: Database session
        """
        self.session = session

    async def create_entity(
        self,
        job_id: str,
        source_url_id: int,
        entity_type: str,
        entity_data: dict,
    ) -> ExtractedEntity:
        """Create an extracted entity.
        
        Args:
            job_id: Associated job ID
            source_url_id: Source URL ID
            entity_type: Type of entity
            entity_data: Entity data
            
        Returns:
            Created entity
        """
        entity = ExtractedEntity(
            job_id=job_id,
            source_url_id=source_url_id,
            entity_type=entity_type,
            entity_data=entity_data,
        )
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def get_entities_by_job(self, job_id: str) -> list[ExtractedEntity]:
        """Get all entities for a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            List of extracted entities
        """
        result = await self.session.execute(
            select(ExtractedEntity).where(ExtractedEntity.job_id == job_id)
        )
        return list(result.scalars().all())
