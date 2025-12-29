"""LangGraph workflow definition."""

from typing import Any, Literal

from langgraph.graph import END, StateGraph

from app.agents.nodes import (
    compare_node,
    crawl_node,
    extract_node,
    filter_urls_node,
    plan_node,
    report_node,
    search_node,
)
from app.agents.state import AgentState
from app.core.errors import StepLimitExceededError
from app.core.logging import get_logger

logger = get_logger(__name__)


def check_step_limit(state: AgentState) -> Literal["continue", "stop"]:
    """Check if step limit has been exceeded.
    
    Args:
        state: Current agent state
        
    Returns:
        "continue" if within limit, "stop" if exceeded
    """
    step_count = state.get("step_count", 0)
    max_steps = state.get("max_steps", 20)
    
    if step_count >= max_steps:
        logger.error(
            "step_limit_exceeded",
            job_id=state.get("job_id"),
            step_count=step_count,
            max_steps=max_steps,
        )
        return "stop"
    
    return "continue"


def should_continue_after_plan(state: AgentState) -> Literal["search", "stop"]:
    """Decide whether to continue after planning.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node or stop
    """
    if check_step_limit(state) == "stop":
        return "stop"
    
    # Check if plan was created successfully
    if not state.get("plan"):
        logger.warning("plan_missing", job_id=state.get("job_id"))
        return "stop"
    
    return "search"


def should_continue_after_search(state: AgentState) -> Literal["filter", "stop"]:
    """Decide whether to continue after search.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node or stop
    """
    if check_step_limit(state) == "stop":
        return "stop"
    
    # Check if URLs were found
    if not state.get("urls"):
        logger.warning("no_urls_found", job_id=state.get("job_id"))
        return "stop"
    
    return "filter"


def should_continue_after_filter(state: AgentState) -> Literal["crawl", "stop"]:
    """Decide whether to continue after filtering.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node or stop
    """
    if check_step_limit(state) == "stop":
        return "stop"
    
    # Check if filtered URLs exist
    if not state.get("filtered_urls"):
        logger.warning("no_filtered_urls", job_id=state.get("job_id"))
        return "stop"
    
    return "crawl"


def should_continue_after_crawl(state: AgentState) -> Literal["extract", "stop"]:
    """Decide whether to continue after crawling.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node or stop
    """
    if check_step_limit(state) == "stop":
        return "stop"
    
    # Check if any pages were crawled successfully
    pages = state.get("pages", [])
    successful_pages = [p for p in pages if p.get("success", False)]
    
    if not successful_pages:
        logger.warning("no_successful_crawls", job_id=state.get("job_id"))
        return "stop"
    
    return "extract"


def should_continue_after_extract(state: AgentState) -> Literal["compare", "stop"]:
    """Decide whether to continue after extraction.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node or stop
    """
    if check_step_limit(state) == "stop":
        return "stop"
    
    # Continue even if no entities (will generate empty report)
    return "compare"


def should_continue_after_compare(state: AgentState) -> Literal["report", "stop"]:
    """Decide whether to continue after comparison.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node or stop
    """
    if check_step_limit(state) == "stop":
        return "stop"
    
    return "report"


def create_research_graph() -> StateGraph:
    """Create the research agent workflow graph.
    
    Returns:
        Compiled StateGraph
    """
    # Create graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("plan", plan_node)
    workflow.add_node("search", search_node)
    workflow.add_node("filter", filter_urls_node)
    workflow.add_node("crawl", crawl_node)
    workflow.add_node("extract", extract_node)
    workflow.add_node("compare", compare_node)
    workflow.add_node("report", report_node)
    
    # Set entry point
    workflow.set_entry_point("plan")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "plan",
        should_continue_after_plan,
        {
            "search": "search",
            "stop": END,
        },
    )
    
    workflow.add_conditional_edges(
        "search",
        should_continue_after_search,
        {
            "filter": "filter",
            "stop": END,
        },
    )
    
    workflow.add_conditional_edges(
        "filter",
        should_continue_after_filter,
        {
            "crawl": "crawl",
            "stop": END,
        },
    )
    
    workflow.add_conditional_edges(
        "crawl",
        should_continue_after_crawl,
        {
            "extract": "extract",
            "stop": END,
        },
    )
    
    workflow.add_conditional_edges(
        "extract",
        should_continue_after_extract,
        {
            "compare": "compare",
            "stop": END,
        },
    )
    
    workflow.add_conditional_edges(
        "compare",
        should_continue_after_compare,
        {
            "report": "report",
            "stop": END,
        },
    )
    
    # Report is the final node
    workflow.add_edge("report", END)
    
    # Compile graph
    return workflow.compile()


# Global graph instance
_research_graph: Any | None = None


def get_research_graph() -> Any:
    """Get the compiled research graph.
    
    Returns:
        Compiled research graph
    """
    global _research_graph
    if _research_graph is None:
        _research_graph = create_research_graph()
        logger.info("research_graph_compiled")
    return _research_graph
