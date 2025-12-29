"""API request and response schemas."""

from typing import Any

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    """Request to create a research job."""

    query: str = Field(
        ...,
        description="Research query",
        min_length=1,
        max_length=512,
        examples=["Notion competitors analysis"],
    )


class ResearchResponse(BaseModel):
    """Response after creating a research job."""

    job_id: str = Field(..., description="Unique job identifier")
    query: str = Field(..., description="Research query")
    status: str = Field(..., description="Job status")
    message: str = Field(..., description="Human-readable message")


class JobStatusResponse(BaseModel):
    """Job status response."""

    job_id: str = Field(..., description="Job identifier")
    query: str = Field(..., description="Research query")
    status: str = Field(..., description="Job status")
    progress: str = Field(..., description="Progress description")
    step_count: int = Field(..., description="Current step count")
    max_steps: int = Field(..., description="Maximum steps")
    errors: list[dict[str, Any]] = Field(default_factory=list, description="Errors encountered")
    error_message: str | None = Field(None, description="Error message if failed")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    completed_at: str | None = Field(None, description="Completion timestamp")


class JobReportResponse(BaseModel):
    """Job report response."""

    job_id: str = Field(..., description="Job identifier")
    query: str = Field(..., description="Research query")
    status: str = Field(..., description="Job status")
    report_md: str | None = Field(None, description="Markdown report")
    report_json: dict[str, Any] | None = Field(None, description="JSON report data")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
