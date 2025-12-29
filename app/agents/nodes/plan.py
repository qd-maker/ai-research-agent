"""Plan node: Generate research plan and dimensions."""

from typing import Any

from pydantic import BaseModel, Field

from app.agents.state import AgentState
from app.core.logging import get_logger
from app.tools.llm import get_llm_client

logger = get_logger(__name__)


class EntityModelMapping(BaseModel):
    """实体与代表模型的映射。"""
    entity: str = Field(..., description="公司/组织名称")
    representative_model: str = Field(..., description="代表模型名（必须是模型名，不是产品名）")


class ResearchPlan(BaseModel):
    """投资级研究计划。"""

    # Step -1: 研究模式分类（最先判断，严格）
    research_mode: str = Field(
        ...,
        description="研究模式：A(已知竞品对比) / B(市场分析) / C(概念型/早期)",
    )
    mode_confidence: float = Field(
        default=0.8,
        description="模式判断置信度 0.0-1.0",
        ge=0.0,
        le=1.0,
    )
    mode_reason: str = Field(
        ...,
        description="模式判断理由（一句话）",
    )
    suggested_layer: str = Field(
        ...,
        description="建议研究层级：Application / Platform / Model / Network / Market",
    )
    risk_note: str = Field(
        default="",
        description="风险提醒（如果该问题容易失败或误解）",
    )
    
    # Step 0: 可行性评估
    feasibility_assessment: str = Field(
        ...,
        description="研究可行性评估（一句话说明是否适合做结构化对比）",
    )
    
    # Step 1: 研究层级锁定
    research_level: str = Field(
        ...,
        description="研究层级：Model(基础模型) / Platform(平台框架) / Application(应用)",
    )
    
    # Step 1.5: 层级校正（如果需要）
    layer_correction_needed: bool = Field(
        default=False,
        description="是否需要层级校正（有效实体<3或50%以上无代表对象时为True）",
    )
    corrected_level: str = Field(
        default="",
        description="校正后的研究层级（如果需要校正）",
    )
    correction_reason: str = Field(
        default="",
        description="层级校正原因说明",
    )
    
    # Step 2: 研究对象定义
    entity_type: str = Field(
        ...,
        description="核心研究对象类型",
    )
    entity_criteria: list[str] = Field(
        ...,
        description="实体必须满足的条件",
        min_length=1,
    )
    excluded_types: list[str] = Field(
        ...,
        description="必须排除的对象类型",
        min_length=1,
    )
    
    # Step 3: 实体-模型映射（Canonical Entity List）
    entity_model_mapping: list[EntityModelMapping] = Field(
        ...,
        description="实体与代表模型的映射列表（3-15个）",
        min_length=3,
        max_length=15,
    )
    
    # Step 4: 搜索关键词
    search_keywords: list[str] = Field(
        ...,
        description="用于搜索的关键词",
        min_length=1,
    )


async def plan_node(state: AgentState) -> dict[str, Any]:
    """生成投资级研究计划。
    
    核心原则：先判断可行性，再锁定实体，最后为实体找证据。
    """
    job_id = state["job_id"]
    query = state["query"]
    
    logger.info("plan_node_started", job_id=job_id, query=query)
    
    try:
        llm = get_llm_client()
        
        prompt = f"""你是一个"研究问题分类器（Research Classifier）"。
你的唯一任务是判断用户问题应该用哪种研究模式处理。

## 研究问题
{query}

---

## Step -1: 研究模式分类（严格，最先判断）

### Mode A：已知竞品对比（Known-Entity Comparison）
特征：
- 明确点名 ≥1 个具体产品/公司（如 Notion、飞书、iPhone、ChatGPT）
- 或包含关键词：竞品 / 对比 / vs / 替代 / alternatives / 类似

用户真实意图：👉 "我已经知道这些东西，请你直接帮我对比"

行为规则（强制）：
- 实体来自行业常识，不需要验证
- 实体数量必须 ≥ 5
- 核心对比表必须包含 ≥ 3 个实体
- ❌ 不允许输出"无法生成结论"或"提取失败"
- ✅ 必须生成对比表

### Mode B：成熟 / 半成熟市场分析（Market Analysis）
特征：
- 描述一个相对清晰的市场或赛道
- 实体数量有限但可枚举
- 通常包含：市场 / 行业 / 格局 / 现状 / 分析 / 大模型

用户真实意图：👉 "帮我理解这个市场现在是什么状态"

行为规则：
- 需要列举主要玩家
- 可以生成对比表
- 允许部分字段缺失

### Mode C：概念型 / 早期市场判断（Concept / Early Market）
特征：
- 概念模糊或高度前沿
- 实体不清晰
- 经常由两个热点词拼接（如 Web3 + AI）

用户真实意图：👉 "这个东西到底成不成立？"

行为规则：
- 允许"不适合对比"结论
- 以判断为主，表格为辅

请填写 research_mode (A/B/C)、mode_confidence (0-1)、mode_reason、suggested_layer、risk_note。

## Step 0: 可行性评估
给出一句话评估：是否适合做结构化对比研究？

## Step 1: 研究层级锁定
明确研究层级：
- Model（基础模型）
- Platform（平台/框架）
- Application（应用）

⚠️ 严禁跨层级混用！

## Step 1.5: 层级校正规则（强制检查）
如果在指定研究层级下：
- 有效实体 < 3 个
- 或 50% 以上实体无清晰代表对象

你必须：
1. 设置 layer_correction_needed = true
2. 在 corrected_level 填写信息密度更高的层级
3. 在 correction_reason 说明原因

示例：
"Web3 + AI 在基础模型层尚未形成市场，因此转向【去中心化AI平台层】进行分析。"

然后基于校正后的层级重新生成实体列表。

## Step 2: 研究对象定义
1. 确定核心研究对象类型
2. 定义实体必须满足的条件
3. 列出必须排除的类型（应用/搜索/浏览器/工具不能充当模型）

## Step 3: 实体-模型映射【核心】
对于每个实体，返回一个包含 entity 和 representative_model 字段的对象。

格式要求（必须严格遵守）：
entity_model_mapping 必须是对象数组，每个对象包含：
- "entity": "公司/组织名称"
- "representative_model": "代表模型名"

示例：
[
  {{"entity": "OpenAI", "representative_model": "GPT-4o"}},
  {{"entity": "Anthropic", "representative_model": "Claude 3.5"}},
  {{"entity": "Google DeepMind", "representative_model": "Gemini 1.5"}}
]

如果无法明确模型名，representative_model 填 "无清晰代表模型"。
❌ 禁止用字符串格式如 "OpenAI → GPT-4o"！必须用JSON对象！

## Step 4: 搜索关键词
必须包含实体名称 + 评测/对比/分析等词

所有输出必须使用中文。"""
        
        plan = await llm.generate_structured(
            prompt=prompt,
            response_model=ResearchPlan,
            system_prompt="你是投资级研究顾问。首先判断研究可行性，再锁定实体-模型映射。如果市场不成熟，必须明确指出。用中文输出。",
        )
        
        plan_dict = plan.model_dump()
        
        # Extract entity names for backward compatibility
        plan_dict["canonical_entities"] = [m.entity for m in plan.entity_model_mapping]
        
        logger.info(
            "plan_node_completed",
            job_id=job_id,
            research_mode=plan.research_mode,
            entity_count=len(plan.entity_model_mapping),
            keywords_count=len(plan.search_keywords),
        )
        
        return {
            "plan": plan_dict,
            "step_count": state.get("step_count", 0) + 1,
            "progress": f"Mode {plan.research_mode}: {len(plan.entity_model_mapping)} entities",
        }
        
    except Exception as e:
        logger.error("plan_node_failed", job_id=job_id, error=str(e))
        errors = state.get("errors", [])
        errors.append({
            "node": "plan",
            "error": str(e),
            "error_type": type(e).__name__,
        })
        return {
            "errors": errors,
            "step_count": state.get("step_count", 0) + 1,
            "progress": "Plan generation failed",
        }
