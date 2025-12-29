"""Mode D Generator for System Configuration / Solution Recommendations.

This module implements Mode D's solution recommendation generation:
- Scenario-based configuration recommendations
- Complete system solutions (not individual product analysis)
- Actionable purchase/implementation guides
"""

from typing import Any

from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.tools.llm import get_llm_client

logger = get_logger(__name__)


class ModeDOutput(BaseModel):
    """Mode D complete output structure using simple nested dict."""
    
    # Format: {"场景名": {"预算": "...", "配置": {"CPU": {...}, ...}, "适合": "...", "理由": "..."}}
    solutions: dict[str, dict[str, Any]] = Field(
        ...,
        description="方案字典，格式: {场景名: {budget: 预算区间, configs: {组件: {model: 型号, reason: 理由}}, target: 适合人群, reason: 推荐理由}}",
    )
    selection_principles: list[str] = Field(
        ...,
        description="选型原则说明（3-5条）",
        min_length=3,
        max_length=5,
    )


async def generate_mode_d_report(query: str, job_id: str) -> tuple[str, dict]:
    """Generate Mode D report with solution recommendations.
    
    Args:
        query: User's research query
        job_id: Job ID for logging
        
    Returns:
        Tuple of (markdown_report, visualization_json)
    """
    llm = get_llm_client()
    
    logger.info("mode_d_generation_started", job_id=job_id)
    
    prompt = f"""这是一个【系统配置 / 方案推荐】任务。

## 研究目标
{query}

## 任务要求
为用户提供可以【直接照着购买或实施】的完整方案。

## 输出格式（严格）
返回 solutions 字典，格式如下：
{{
    "游戏向（8000-10000元）": {{
        "budget": "8000-10000元",
        "configs": {{
            "CPU": {{"model": "Intel i5-14600KF", "reason": "性价比高"}},
            "GPU": {{"model": "RTX 4070", "reason": "光追性能强"}},
            "主板": {{"model": "B760", "reason": "兼容性好"}},
            "内存": {{"model": "DDR5 32GB", "reason": "容量充足"}},
            "存储": {{"model": "1TB NVMe SSD", "reason": "速度快"}}
        }},
        "target": "游戏玩家",
        "reason": "高帧率游戏体验"
    }},
    "生产力向（...）": {{...}},
    "综合均衡向（...）": {{...}}
}}

## 规则
1. 至少3个场景方案
2. 每个方案至少5个组件
3. 只输出具体型号，不要分析市场
4. 不要生成对比表"""

    result = await llm.generate_structured(
        prompt=prompt,
        response_model=ModeDOutput,
        system_prompt="你是系统配置专家。输出格式必须是嵌套字典，不要输出文本。",
    )
    
    logger.info(
        "mode_d_generation_completed",
        job_id=job_id,
        solutions=len(result.solutions),
    )
    
    # === Build Markdown Report ===
    md_lines = [
        f"# {query}",
        "",
        "> 以下方案可直接照着购买或实施",
        "",
    ]
    
    # Output each solution
    for i, (scenario, solution) in enumerate(result.solutions.items(), 1):
        budget = solution.get("budget", "未知")
        configs = solution.get("configs", {})
        target = solution.get("target", "")
        reason = solution.get("reason", "")
        
        md_lines.extend([
            f"## 方案 {chr(64+i)}：{scenario}",
            "",
        ])
        
        for component, config in configs.items():
            if isinstance(config, dict):
                model = config.get("model", "")
                comp_reason = config.get("reason", "")
                md_lines.append(f"- **{component}**：{model} — {comp_reason}")
            else:
                md_lines.append(f"- **{component}**：{config}")
        
        md_lines.extend([
            "",
            f"**适合人群**：{target}",
            "",
            f"**推荐理由**：{reason}",
            "",
            "---",
            "",
        ])
    
    # Output selection principles
    md_lines.extend([
        "## 选型原则说明",
        "",
    ])
    for i, principle in enumerate(result.selection_principles, 1):
        md_lines.append(f"{i}. {principle}")
    
    md_lines.append("")
    
    # === Build Visualization JSON ===
    visualization_json = {
        "solutions": result.solutions,
        "selection_principles": result.selection_principles,
    }
    
    return "\n".join(md_lines), visualization_json
