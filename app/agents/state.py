"""Agent state definition for LangGraph."""

from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    """State for the research agent workflow.
    
    This state is passed between all nodes in the LangGraph workflow.
    """
    
    # Job metadata
    job_id: str
    query: str
    trace_id: str
    
    # Planning
    plan: dict[str, Any]  # Research plan with dimensions/criteria
    
    # Search & URLs
    urls: list[str]  # Candidate URLs from search
    filtered_urls: list[str]  # URLs after filtering/deduplication
    
    # Crawling
    pages: list[dict[str, Any]]  # Crawled page data
    
    # Extraction
    entities: list[dict[str, Any]]  # Extracted structured data
    
    # Comparison & Reporting
    comparison_table: dict[str, Any]  # Comparison table structure
    report_md: str  # Markdown report
    report_json: dict[str, Any]  # JSON report data
    
    # Guardrails & Control
    step_count: int  # Current step number
    max_steps: int  # Maximum allowed steps
    max_urls: int  # Maximum URLs to process
    
    # Error tracking
    errors: list[dict[str, Any]]  # List of errors encountered
    
    # Progress tracking
    progress: str  # Human-readable progress message
