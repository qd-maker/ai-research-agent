"""Mode A Three-Phase Generator for Known-Entity Comparison.

This module implements Mode A's mandatory three-phase generation:
- Phase 1 (Structure): Generate empty table skeleton
- Phase 2 (Fill): Fill in table content
- Phase 3 (Summary): Generate conclusions
"""

from typing import Any

from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.tools.llm import get_llm_client

logger = get_logger(__name__)


class TableSkeleton(BaseModel):
    """Phase 1: Empty table skeleton structure."""
    
    competitors: list[str] = Field(
        ...,
        description="竞品列表（不含主产品，≥4个）",
        min_length=4,
    )
    dimensions: list[str] = Field(
        ...,
        description="对比维度列表（≥5个）",
        min_length=5,
    )
    main_product: str = Field(
        default="Notion",
        description="主产品名称",
    )


class FilledTable(BaseModel):
    """Phase 2: Filled table content as nested dict."""
    table: dict[str, dict[str, str]] = Field(
        ...,
        description="表格内容，格式: {维度: {产品: 内容}}，每个内容≤20字",
    )


class ComparisonSummary(BaseModel):
    """Phase 3: Summary conclusions."""
    key_differences: list[str] = Field(
        ...,
        description="关键差异（3-5条）",
        min_length=3,
        max_length=5,
    )
    suitable_for: list[str] = Field(
        ...,
        description="适合的用户群体（3-5条）",
        min_length=3,
    )
    not_suitable_for: list[str] = Field(
        ...,
        description="不适合的用户群体（2-4条）",
        min_length=2,
    )


async def generate_mode_a_report(query: str, job_id: str) -> tuple[str, dict]:
    """Generate Mode A report using three-phase approach.
    
    Args:
        query: User's research query
        job_id: Job ID for logging
        
    Returns:
        Tuple of (markdown_report, visualization_json)
    """
    llm = get_llm_client()
    
    # === Phase 1: Generate Table Skeleton ===
    logger.info("mode_a_phase1_started", job_id=job_id)
    
    phase1_prompt = f"""你正在执行一个【已知竞品对比】任务。

你的唯一任务是：
👉 生成一个【横向对比表的骨架结构】。

【研究主题】
{query}

【强制规则】
1. 只允许输出一个 Markdown 表格
2. 表格列数 ≥ 5（Notion + 至少 4 个竞品）
3. 表格行数 ≥ 5
4. 所有单元格内容必须为空
5. 不允许输出任何解释性文字

【必须包含的竞品】
- Notion
- Coda
- Confluence
- Airtable
- 飞书文档

【必须包含的维度（行）】
- 产品定位
- 核心功能
- 协作能力
- 目标用户
- 定价模式

只输出表格骨架，不要任何其他内容。"""

    skeleton = await llm.generate_structured(
        prompt=phase1_prompt,
        response_model=TableSkeleton,
        system_prompt="你是产品竞品分析师。只输出对比表骨架结构，不填充内容，不输出解释文字。",
    )
    
    logger.info(
        "mode_a_phase1_completed",
        job_id=job_id,
        competitors=len(skeleton.competitors),
        dimensions=len(skeleton.dimensions),
    )
    
    # Build product list
    all_products = [skeleton.main_product] + skeleton.competitors
    
    # === Phase 2: Fill Table Content ===
    logger.info("mode_a_phase2_started", job_id=job_id)
    
    # Build skeleton table for prompt
    skeleton_table = "| 维度 | " + " | ".join(all_products) + " |\n"
    skeleton_table += "|" + "|".join(["---"] * (len(all_products) + 1)) + "|\n"
    for dim in skeleton.dimensions:
        skeleton_table += f"| {dim} |" + " |" * len(all_products) + "\n"
    
    phase2_prompt = f"""你将收到一个【已经存在的竞品对比表结构】。

你的任务是：
👉 为表格中的每一个空单元格填写内容。

【已有表格结构】
{skeleton_table}

【填写规则】
1. 不允许新增或删除任何行或列
2. 每个单元格内容 ≤ 20 字
3. 允许使用概括性和模糊表达，例如：
   - 强 / 中 / 弱
   - 偏向个人 / 偏向团队
   - 功能全面 / 偏文档 / 偏数据
4. 所有内容必须是字符串
5. 只输出填写完成后的表格，不要解释文字

【再次强调】
- 不要改变表格结构
- 输出格式必须是嵌套字典：{{"维度1": {{"产品1": "内容", "产品2": "内容"}}}}
- 不要输出总结

为每个产品的每个维度提供内容。"""

    filled = await llm.generate_structured(
        prompt=phase2_prompt,
        response_model=FilledTable,
        system_prompt="你是产品竞品分析师。只填充表格内容，每格≤20字，输出格式为嵌套字典。",
    )
    
    logger.info("mode_a_phase2_completed", job_id=job_id)
    
    # Use table data directly from response
    table_data = filled.table
    
    # Build filled table markdown for Phase 3
    filled_table_md = "| 维度 | " + " | ".join(all_products) + " |\n"
    filled_table_md += "|" + "|".join(["---"] * (len(all_products) + 1)) + "|\n"
    for dim in skeleton.dimensions:
        row = f"| {dim} |"
        for product in all_products:
            content = table_data.get(dim, {}).get(product, "—")
            row += f" {content} |"
        filled_table_md += row + "\n"
    
    # === Phase 3: Generate Summary ===
    logger.info("mode_a_phase3_started", job_id=job_id)
    
    phase3_prompt = f"""基于上面的竞品对比表，请输出总结性分析。

【对比表】
{filled_table_md}

【输出要求】
1. 关键差异总结（3-5 条）
2. {skeleton.main_product} 适合谁
3. {skeleton.main_product} 不适合谁

【写作风格】
- 面向真实用户决策
- 不夸张、不营销
- 不重复表格内容"""

    summary = await llm.generate_structured(
        prompt=phase3_prompt,
        response_model=ComparisonSummary,
        system_prompt="你是产品竞品分析师。面向真实用户决策，不夸张、不营销、不重复表格内容。",
    )
    
    logger.info("mode_a_phase3_completed", job_id=job_id)
    
    # === Build Final Markdown Report ===
    md_lines = [
        f"# {query}",
        "",
        "## 核心对比表",
        "",
    ]
    
    # Build table header
    header = "| 维度 | " + " | ".join(all_products) + " |"
    separator = "| --- | " + " | ".join(["---"] * len(all_products)) + " |"
    md_lines.extend([header, separator])
    
    # Build table rows
    for dim in skeleton.dimensions:
        row = f"| **{dim}** |"
        for product in all_products:
            content = table_data.get(dim, {}).get(product, "—")
            row += f" {content} |"
        md_lines.append(row)
    
    md_lines.append("")
    
    # Add summary
    md_lines.extend([
        "## 关键差异总结",
        "",
    ])
    for i, diff in enumerate(summary.key_differences, 1):
        md_lines.append(f"{i}. {diff}")
    
    md_lines.extend([
        "",
        f"### {skeleton.main_product} 适合谁",
        "",
    ])
    for item in summary.suitable_for:
        md_lines.append(f"- {item}")
    
    md_lines.extend([
        "",
        f"### {skeleton.main_product} 不适合谁",
        "",
    ])
    for item in summary.not_suitable_for:
        md_lines.append(f"- {item}")
    
    md_lines.append("")
    
    # === Build Visualization-Friendly JSON ===
    visualization_json = {
        "dimensions": [],
        "highlights": [],
    }
    
    # Build dimensions array
    for dim in skeleton.dimensions:
        dim_data = {
            "name": dim,
            "comparisons": []
        }
        for product in all_products:
            value = table_data.get(dim, {}).get(product, "—")
            dim_data["comparisons"].append({
                "product": product,
                "value": value
            })
        visualization_json["dimensions"].append(dim_data)
    
    # Build highlights for main product
    visualization_json["highlights"].append({
        "product": skeleton.main_product,
        "strengths": summary.suitable_for[:3],
        "weaknesses": summary.not_suitable_for[:2],
    })
    
    return "\n".join(md_lines), visualization_json
