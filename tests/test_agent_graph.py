"""Test agent graph compilation."""

import pytest

from app.agents.graph import create_research_graph
from app.agents.state import AgentState


def test_graph_compilation() -> None:
    """Test that the research graph compiles successfully."""
    graph = create_research_graph()
    assert graph is not None


@pytest.mark.asyncio
async def test_graph_execution_stub() -> None:
    """Test basic graph execution with minimal state."""
    graph = create_research_graph()
    
    initial_state: AgentState = {
        "job_id": "test-job-123",
        "query": "Test query",
        "trace_id": "test-trace-123",
        "step_count": 0,
        "max_steps": 20,
        "max_urls": 5,
        "errors": [],
        "progress": "Testing",
    }
    
    # Execute graph (will use stub search results)
    final_state = await graph.ainvoke(initial_state)
    
    # Verify state was updated
    assert final_state["job_id"] == "test-job-123"
    assert final_state["step_count"] > 0
    assert "plan" in final_state or len(final_state.get("errors", [])) > 0
