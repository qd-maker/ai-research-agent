"""Compare node: Generate comparison table."""

from typing import Any

from app.agents.state import AgentState
from app.core.logging import get_logger

logger = get_logger(__name__)


async def compare_node(state: AgentState) -> dict[str, Any]:
    """Generate comparison table from extracted entities.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with comparison table
    """
    job_id = state["job_id"]
    entities = state.get("entities", [])
    plan = state.get("plan", {})
    
    logger.info("compare_node_started", job_id=job_id, entity_count=len(entities))
    
    try:
        if not entities:
            logger.warning("compare_node_no_entities", job_id=job_id)
            return {
                "comparison_table": {},
                "step_count": state.get("step_count", 0) + 1,
                "progress": "No entities to compare",
            }
        
        # Build comparison table with dimensions based on research mode
        # Structure: { dimension: { company_name: value } }
        
        # Get research mode from plan
        research_mode = plan.get("research_mode", "B")
        
        # Select dimensions based on research mode
        if research_mode == "A":
            # Mode A: 竞品对比维度（聚焦产品特性）
            FIXED_DIMENSIONS = [
                ("公司/组织", "company"),
                ("代表产品/模型", "product_name"),
                ("产品定位", "positioning"),
                ("核心功能", "tech_specs"),      # 复用tech_specs
                ("协作能力", "business_model"),  # 复用business_model
                ("目标用户", "target_users"),
                ("适合场景", "market_judgment"), # 复用market_judgment
                ("定价区间", "pricing"),
                ("主要优势", "advantages"),
                ("主要劣势", "disadvantages"),
            ]
        else:
            # Mode B/C: 通用维度
            FIXED_DIMENSIONS = [
                ("公司/组织", "company"),
                ("代表产品/模型", "product_name"),
                ("发布时间", "release_date"),
                ("产品定位", "positioning"),
                ("核心技术参数", "tech_specs"),
                ("商业模式", "business_model"),
                ("定价区间", "pricing"),
                ("主要优势", "advantages"),
                ("主要劣势", "disadvantages"),
                ("目标用户", "target_users"),
                ("市场判断", "market_judgment"),
            ]
        
        comparison_table: dict[str, dict[str, Any]] = {}
        
        # Initialize all fixed dimensions
        for dim_name, _ in FIXED_DIMENSIONS:
            comparison_table[dim_name] = {}
        
        # Populate table from entities
        for entity in entities:
            company_name = entity.get("company", "未知")
            
            # Map entity fields to fixed dimensions
            for dim_name, field_name in FIXED_DIMENSIONS:
                value = entity.get(field_name, "未知/未公开")
                if value:
                    comparison_table[dim_name][company_name] = value
        
        logger.info(
            "compare_node_completed",
            job_id=job_id,
            dimension_count=len(comparison_table),
            product_count=len(entities),
        )
        
        return {
            "comparison_table": comparison_table,
            "step_count": state.get("step_count", 0) + 1,
            "progress": f"Created comparison table with {len(entities)} products",
        }
        
    except Exception as e:
        logger.error("compare_node_failed", job_id=job_id, error=str(e))
        errors = state.get("errors", [])
        errors.append({
            "node": "compare",
            "error": str(e),
            "error_type": type(e).__name__,
        })
        return {
            "comparison_table": {},
            "errors": errors,
            "step_count": state.get("step_count", 0) + 1,
            "progress": "Comparison failed",
        }
