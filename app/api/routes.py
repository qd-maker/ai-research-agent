"""API routes."""

from fastapi import APIRouter, HTTPException, Response

from app.api.schemas import (
    HealthResponse,
    JobReportResponse,
    JobStatusResponse,
    ResearchRequest,
    ResearchResponse,
)
from app.core.errors import JobNotFoundError
from app.core.logging import get_logger
from app.services.jobs import get_job_service
from app.services.reporting import get_reporting_service

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint.
    
    Returns:
        Health status
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
    )


@router.post("/research", response_model=ResearchResponse, status_code=202)
async def create_research_job(request: ResearchRequest) -> ResearchResponse:
    """Create a new research job.
    
    Args:
        request: Research request
        
    Returns:
        Research job response
    """
    logger.info("research_request_received", query=request.query)
    
    try:
        job_service = get_job_service()
        job_id = await job_service.create_job(query=request.query)
        
        return ResearchResponse(
            job_id=job_id,
            query=request.query,
            status="pending",
            message=f"Research job created successfully. Job ID: {job_id}",
        )
        
    except Exception as e:
        logger.error("research_request_failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create research job: {str(e)}",
        ) from e


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    """Get job status and progress.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Job status
    """
    logger.info("job_status_request", job_id=job_id)
    
    try:
        job_service = get_job_service()
        status = await job_service.get_job_status(job_id)
        
        return JobStatusResponse(**status)
        
    except JobNotFoundError as e:
        logger.warning("job_not_found", job_id=job_id)
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.error("job_status_request_failed", job_id=job_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job status: {str(e)}",
        ) from e


@router.get("/reports/{job_id}", response_model=JobReportResponse)
async def get_job_report(job_id: str) -> JobReportResponse:
    """Get job report.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Job report
    """
    logger.info("job_report_request", job_id=job_id)
    
    try:
        job_service = get_job_service()
        report = await job_service.get_job_report(job_id)
        
        return JobReportResponse(**report)
        
    except JobNotFoundError as e:
        logger.warning("job_not_found", job_id=job_id)
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.error("job_report_request_failed", job_id=job_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job report: {str(e)}",
        ) from e


@router.get("/reports/{job_id}/markdown")
async def get_job_report_markdown(job_id: str) -> Response:
    """Get job report as Markdown file.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Markdown file
    """
    logger.info("job_report_markdown_request", job_id=job_id)
    
    try:
        job_service = get_job_service()
        report = await job_service.get_job_report(job_id)
        
        if not report["report_md"]:
            raise HTTPException(status_code=404, detail="Report not yet generated")
        
        return Response(
            content=report["report_md"],
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename={job_id}_report.md"
            },
        )
        
    except JobNotFoundError as e:
        logger.warning("job_not_found", job_id=job_id)
        raise HTTPException(status_code=404, detail=str(e)) from e
    except HTTPException:
        raise
    except Exception as e:
        logger.error("job_report_markdown_request_failed", job_id=job_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get markdown report: {str(e)}",
        ) from e


@router.get("/reports/{job_id}/csv")
async def get_job_report_csv(job_id: str) -> Response:
    """Get job comparison table as CSV file.
    
    Args:
        job_id: Job identifier
        
    Returns:
        CSV file
    """
    logger.info("job_report_csv_request", job_id=job_id)
    
    try:
        job_service = get_job_service()
        report = await job_service.get_job_report(job_id)
        
        if not report["report_json"]:
            raise HTTPException(status_code=404, detail="Report not yet generated")
        
        # Generate CSV from comparison table
        reporting_service = get_reporting_service()
        comparison_table = report["report_json"].get("comparison_table", {})
        csv_content = await reporting_service.generate_csv(comparison_table)
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={job_id}_comparison.csv"
            },
        )
        
    except JobNotFoundError as e:
        logger.warning("job_not_found", job_id=job_id)
        raise HTTPException(status_code=404, detail=str(e)) from e
    except HTTPException:
        raise
    except Exception as e:
        logger.error("job_report_csv_request_failed", job_id=job_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get CSV report: {str(e)}",
        ) from e
