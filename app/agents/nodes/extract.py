"""Extract node: Extract structured data from crawled pages."""

from typing import Any

from pydantic import BaseModel, Field

from app.agents.state import AgentState
from app.core.logging import get_logger
from app.tools.llm import get_llm_client

logger = get_logger(__name__)


class ExtractedEntity(BaseModel):
    """使用固定对比维度的实体信息提取模型。"""

    # 固定的11个对比维度
    company: str = Field(..., description="公司/组织名称")
    product_name: str = Field(default="", description="代表产品/模型名称")
    release_date: str = Field(default="未知", description="发布时间/成立时间")
    positioning: str = Field(default="未知", description="产品定位（如：通用/专业/开源）")
    tech_specs: str = Field(default="未知", description="核心技术参数")
    business_model: str = Field(default="未知", description="商业模式（如：API/ToC/ToB/开源）")
    pricing: str = Field(default="未知/未公开", description="定价区间")
    advantages: str = Field(default="", description="主要优势（1-3条）")
    disadvantages: str = Field(default="", description="主要劣势（1-3条）")
    target_users: str = Field(default="未知", description="目标用户群体")
    market_judgment: str = Field(default="", description="市场判断（一句话）")


async def extract_node(state: AgentState) -> dict[str, Any]:
    """Extract structured data from crawled pages.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with extracted entities
    """
    job_id = state["job_id"]
    pages = state.get("pages", [])
    plan = state.get("plan", {})
    
    logger.info("extract_node_started", job_id=job_id, page_count=len(pages))
    
    try:
        llm = get_llm_client()
        entities = []
        
        # Extract from successful pages only
        successful_pages = [p for p in pages if p.get("success", False)]
        
        for page in successful_pages:
            try:
                # Get locked entity list from plan
                canonical_entities = plan.get("canonical_entities", [])
                canonical_str = "、".join(canonical_entities) if canonical_entities else "无"
                entity_type = plan.get("entity_type", "产品/服务")
                excluded_types = plan.get("excluded_types", [])
                excluded_str = "、".join(excluded_types[:5]) if excluded_types else "无"
                
                prompt = f"""你是专业行业研究分析师。从网页内容中提取【已锁定实体】的信息。

## ⚠️ 重要规则（实体驱动研究）
你只能提取以下【已锁定实体】的信息：
{canonical_str}

如果网页内容不属于以上实体，返回空内容（company填"不匹配"）。
❌ 禁止引入新实体
❌ 禁止提取锁定列表之外的公司信息

## 研究对象类型
{entity_type}

## 必须排除的类型
{excluded_str}

## 网页信息
页面标题: {page.get('title', 'Unknown')}
URL: {page.get('url', '')}

内容:
{page.get('content', '')[:4000]}

## 提取要求
1. 只提取【已锁定实体】的信息
2. 使用固定的11个维度：公司、产品名、发布时间、定位、技术参数、商业模式、定价、优势、劣势、目标用户、市场判断
3. 信息不足时填写"未公开"
4. 所有输出必须使用中文
5. 如果网页不包含任何锁定实体信息，company填"不匹配\""""
                
                extracted = await llm.generate_structured(
                    prompt=prompt,
                    response_model=ExtractedEntity,
                    system_prompt="你是实体驱动研究专家。只提取已锁定实体的信息，丢弃不属于锁定列表的内容。用中文输出。",
                )
                
                # Filter out non-matching entities
                if extracted.company == "不匹配" or not extracted.company:
                    logger.info("entity_filtered_not_in_canonical_list", job_id=job_id, url=page["url"])
                    continue
                
                entity_data = extracted.model_dump()
                entity_data["source_url"] = page["url"]
                entity_data["source_title"] = page.get("title", "")
                
                entities.append(entity_data)
                
                logger.info(
                    "entity_extracted",
                    job_id=job_id,
                    url=page["url"],
                    entity_name=extracted.company,
                )
                
            except Exception as e:
                logger.warning(
                    "entity_extraction_failed",
                    job_id=job_id,
                    url=page.get("url"),
                    error=str(e),
                )
                # Continue with other pages
                continue
        
        logger.info(
            "extract_node_completed",
            job_id=job_id,
            entities_extracted=len(entities),
        )
        
        return {
            "entities": entities,
            "step_count": state.get("step_count", 0) + 1,
            "progress": f"Extracted {len(entities)} entities from {len(successful_pages)} pages",
        }
        
    except Exception as e:
        logger.error("extract_node_failed", job_id=job_id, error=str(e))
        errors = state.get("errors", [])
        errors.append({
            "node": "extract",
            "error": str(e),
            "error_type": type(e).__name__,
        })
        return {
            "entities": [],
            "errors": errors,
            "step_count": state.get("step_count", 0) + 1,
            "progress": "Extraction failed",
        }
