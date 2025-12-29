"""Mode E Generator for Macro / Framework Judgment.

This module implements Mode E's framework-based analysis:
- Long-term trend analysis
- Macro system understanding
- Scenario-based thinking
- NOT predictions, but frameworks for understanding
"""

from typing import Any

from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.tools.llm import get_llm_client

logger = get_logger(__name__)


class ModeEOutput(BaseModel):
    """Mode E complete output structure."""
    
    problem_essence: str = Field(
        ...,
        description="问题本质：为什么这是一个长期、多变量、不可精确预测的问题",
    )
    core_drivers: dict[str, str] = Field(
        ...,
        description="核心驱动变量：3-5个关键因素及其作用机制，格式: {变量名: 解释}",
    )
    key_uncertainties: list[str] = Field(
        ...,
        description="关键不确定性：最不可控、最容易改变路径的因素（3-5条）",
        min_length=3,
    )
    scenario_paths: dict[str, str] = Field(
        ...,
        description="可能的情景路径：格式 {情景A: 描述, 情景B: 描述, 情景C: 描述}",
    )
    short_vs_long_term: str = Field(
        ...,
        description="短期 vs 长期的区别：短期波动和长期趋势的不同驱动逻辑",
    )
    action_suggestions: dict[str, str] = Field(
        ...,
        description="行动建议（非预测）：格式 {普通用户: 建议, 长期配置者: 建议, 研究者: 建议}",
    )


async def generate_mode_e_report(query: str, job_id: str) -> tuple[str, dict]:
    """Generate Mode E report with framework-based analysis.
    
    Args:
        query: User's research query
        job_id: Job ID for logging
        
    Returns:
        Tuple of (markdown_report, visualization_json)
    """
    llm = get_llm_client()
    
    logger.info("mode_e_generation_started", job_id=job_id)
    
    prompt = f"""这是一个【宏观 / 框架型判断】任务。

## 研究目标
{query}

## 任务要求
不是预测结果，而是帮助用户理解"这个问题应该如何被分析和看待"。

## 执行规则（不可违背）
1. 禁止给出明确预测结果（点位、涨跌、时间点）
2. 禁止生成对比表
3. 禁止枚举个股或单一对象
4. 不使用"不成熟 / 尚不存在"等技术市场话术
5. 重点在于"变量、框架、情景"

## 输出内容
1. problem_essence: 说明为什么这是一个长期、多变量、不可精确预测的问题
2. core_drivers: 3-5个决定长期走向的关键因素及其作用机制
3. key_uncertainties: 最不可控、最容易改变路径的因素
4. scenario_paths: 可能的情景路径（至少3个，可相互矛盾但逻辑自洽）
5. short_vs_long_term: 短期波动和长期趋势的不同驱动逻辑
6. action_suggestions: 分别给普通用户、长期配置者、研究者的行动建议

你的成功标准不是"说得准"，而是"说得清楚"。"""

    result = await llm.generate_structured(
        prompt=prompt,
        response_model=ModeEOutput,
        system_prompt="你是宏观分析框架专家。只提供理解框架，不做具体预测。输出格式必须是结构化字典。",
    )
    
    logger.info("mode_e_generation_completed", job_id=job_id)
    
    # === Build Markdown Report ===
    md_lines = [
        f"# {query}",
        "",
        "> 这是一个框架型分析，帮助理解问题而非预测结果",
        "",
        "## 问题本质",
        "",
        result.problem_essence,
        "",
        "## 核心驱动变量",
        "",
    ]
    
    for i, (driver, explanation) in enumerate(result.core_drivers.items(), 1):
        md_lines.append(f"**{i}. {driver}**")
        md_lines.append(f"   {explanation}")
        md_lines.append("")
    
    md_lines.extend([
        "## 关键不确定性",
        "",
    ])
    for uncertainty in result.key_uncertainties:
        md_lines.append(f"- {uncertainty}")
    
    md_lines.extend([
        "",
        "## 可能的情景路径",
        "",
    ])
    for scenario, description in result.scenario_paths.items():
        md_lines.append(f"### {scenario}")
        md_lines.append(description)
        md_lines.append("")
    
    md_lines.extend([
        "## 短期 vs 长期的区别",
        "",
        result.short_vs_long_term,
        "",
        "## 行动建议（非预测）",
        "",
    ])
    for audience, suggestion in result.action_suggestions.items():
        md_lines.append(f"**{audience}**：{suggestion}")
        md_lines.append("")
    
    # === Build Visualization JSON ===
    visualization_json = {
        "problem_essence": result.problem_essence,
        "core_drivers": result.core_drivers,
        "key_uncertainties": result.key_uncertainties,
        "scenario_paths": result.scenario_paths,
        "action_suggestions": result.action_suggestions,
    }
    
    return "\n".join(md_lines), visualization_json
