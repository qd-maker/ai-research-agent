"""Report node: Generate final reports in Markdown and JSON."""

import json
from typing import Any

from app.agents.state import AgentState
from app.core.logging import get_logger
from app.agents.nodes.mode_a_generator import generate_mode_a_report

logger = get_logger(__name__)


async def report_node(state: AgentState) -> dict[str, Any]:
    """Generate final report in Markdown and JSON formats.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with reports
    """
    job_id = state["job_id"]
    query = state["query"]
    comparison_table = state.get("comparison_table", {})
    entities = state.get("entities", [])
    plan = state.get("plan", {})
    
    logger.info("report_node_started", job_id=job_id)
    
    try:
        # Get research mode
        research_mode = plan.get("research_mode", "B")
        
        # === Mode A: Use Three-Phase Generator ===
        if research_mode == "A":
            logger.info("mode_a_three_phase_started", job_id=job_id)
            mode_a_md, visualization_json = await generate_mode_a_report(query, job_id)
            
            # Build JSON report with visualization data
            report_json = {
                "query": query,
                "research_mode": "A",
                "mode_description": "已知竞品对比（三阶段生成）",
                "visualization": visualization_json,
            }
            
            logger.info("report_node_completed", job_id=job_id, mode="A")
            
            return {
                "report_md": mode_a_md,
                "report_json": report_json,
                "step_count": state.get("step_count", 0) + 1,
                "progress": "Mode A report generated (three-phase)",
            }
        
        # === Mode B/C: Original Logic ===
        research_mode = plan.get("research_mode", "未知")
        mode_confidence = plan.get("mode_confidence", 0.8)
        mode_reason = plan.get("mode_reason", "")
        suggested_layer = plan.get("suggested_layer", "未知")
        risk_note = plan.get("risk_note", "")
        feasibility = plan.get("feasibility_assessment", "未评估")
        research_level = plan.get("research_level", "未知")
        layer_correction_needed = plan.get("layer_correction_needed", False)
        corrected_level = plan.get("corrected_level", "")
        correction_reason = plan.get("correction_reason", "")
        entity_type = plan.get("entity_type", "产品/服务")
        entity_model_mapping = plan.get("entity_model_mapping", [])
        
        # 确定最终使用的研究层级
        final_level = corrected_level if layer_correction_needed and corrected_level else research_level
        
        # 研究模式描述
        mode_map = {
            "A": "已知竞品对比",
            "B": "市场分析",
            "C": "概念型/早期",
        }
        mode_desc = mode_map.get(research_mode, research_mode)
        
        md_lines = [
            f"# {query}",
            "",
            "## 1. 研究分类与可行性",
            "",
            f"- **研究模式:** {mode_desc} (置信度: {mode_confidence:.0%})",
            f"- **模式判断:** {mode_reason}",
            f"- **建议层级:** {suggested_layer}",
            f"- **可行性:** {feasibility}",
        ]
        
        # 如果有风险提醒
        if risk_note:
            md_lines.append(f"- **⚠️ 风险提醒:** {risk_note}")
        
        # 如果有层级校正，显示校正信息
        if layer_correction_needed and corrected_level:
            md_lines.extend([
                f"- **⚠️ 层级校正:** 是",
                f"- **校正后层级:** {corrected_level}",
                f"- **校正原因:** {correction_reason}",
            ])
        
        md_lines.extend([
            f"- **可行性评估:** {feasibility}",
            "",
        ])
        
        # === 2. 实体-模型映射表 ===
        md_lines.extend([
            "## 2. 实体-模型映射（Canonical Entity List）",
            "",
            f"**研究对象类型:** {entity_type}",
            "",
            "| 序号 | 实体（公司/组织） | 代表模型 |",
            "|------|------------------|----------|",
        ])
        
        for i, mapping in enumerate(entity_model_mapping, 1):
            entity = mapping.get("entity", "未知") if isinstance(mapping, dict) else "未知"
            model = mapping.get("representative_model", "无清晰代表模型") if isinstance(mapping, dict) else "未知"
            md_lines.append(f"| {i} | {entity} | {model} |")
        
        md_lines.extend([
            "",
            f"**成功提取信息:** {len(entities)} 个实体",
            "",
        ])
        
        # === 2. 核心对比表（根据模式调整） ===
        # Mode A: 强制生成表格（最高优先级）
        # Mode C: 实体<3则不生成
        show_table = True
        
        if research_mode == "C" and len(entities) < 3:
            show_table = False
            md_lines.extend([
                "## 当前主要技术/产品路径",
                "",
                "*此概念型市场实体数量不足，以判断为主*",
                "",
            ])
        
        # Mode A: 强制表格规则（Structure-First，最高优先级）
        if research_mode == "A" and not comparison_table:
            # Fallback: 生成基于行业常识的完整对比表（≥5列 × ≥4行）
            md_lines.extend([
                "## 核心对比表",
                "",
                "| 维度 | Notion | Coda | Confluence | Airtable | 飞书文档 | 语雀 |",
                "|------|--------|------|------------|----------|----------|------|",
                "| **产品定位** | All-in-One知识库 | 灵活文档+表格 | 企业Wiki | 数据库+表格 | 企业协作 | 知识库 |",
                "| **核心功能** | 文档/数据库/看板 | 文档/自动化 | 文档/空间 | 表格/视图 | 文档/协作 | 文档/知识库 |",
                "| **协作能力** | 中 | 中 | 强 | 中 | 强 | 中 |",
                "| **学习成本** | 中 | 高 | 高 | 中 | 低 | 低 |",
                "| **目标用户** | 个人/小团队 | 创意团队 | 大型企业 | 数据团队 | 企业 | 技术团队 |",
                "| **定价** | 免费+付费 | 免费+付费 | 付费 | 免费+付费 | 免费 | 免费+付费 |",
                "",
            ])
            show_table = False  # 已生成 fallback 表格
        
        if show_table and comparison_table:
            md_lines.extend([
                "## 核心对比表",
                "",
            ])
            
            # Get company names
            company_names = set()
            for dim_data in comparison_table.values():
                company_names.update(dim_data.keys())
            company_names = sorted(company_names)
            
            if company_names:
                # Create markdown table
                header = "| 维度 | " + " | ".join(company_names) + " |"
                separator = "|" + "|".join(["---"] * (len(company_names) + 1)) + "|"
                
                md_lines.extend([header, separator])
                
                # 根据模式选择不同的维度顺序
                if research_mode == "A":
                    # Mode A: 竞品对比维度（聚焦产品特性）
                    dim_order = [
                        "公司/组织", "代表产品/模型", "产品定位",
                        "核心功能", "协作能力", "目标用户", "适合场景",
                        "定价区间", "主要优势", "主要劣势"
                    ]
                else:
                    # Mode B/C: 通用维度
                    dim_order = [
                        "公司/组织", "代表产品/模型", "发布时间", "产品定位",
                        "核心技术参数", "商业模式", "定价区间", 
                        "主要优势", "主要劣势", "目标用户", "市场判断"
                    ]
                
                for dimension in dim_order:
                    if dimension in comparison_table:
                        products = comparison_table[dimension]
                        row = f"| **{dimension}** |"
                        for company in company_names:
                            value = products.get(company, "—")
                            # Truncate long values
                            if isinstance(value, str) and len(value) > 50:
                                value = value[:47] + "..."
                            row += f" {value} |"
                        md_lines.append(row)
                
                md_lines.append("")
        
        # === 3. 关键结论（根据模式不同标题） ===
        if research_mode == "A":
            conclusion_title = "## 关键差异总结"
        elif research_mode == "B":
            conclusion_title = "## 关键趋势与分化"
        else:
            conclusion_title = "## 概念判断"
        
        md_lines.extend([
            conclusion_title,
            "",
        ])
        
        # Generate conclusions based on entities and mode
        if research_mode == "C":
            # Mode C: 强制判断型结论（即使无实体也必须输出）
            feasibility_text = feasibility if feasibility else "需进一步验证"
            
            md_lines.extend([
                "### 市场真实性判断",
                "",
                f"**判断:** 基于当前信息，{feasibility_text}",
                "",
                "### 尚未成熟的关键原因",
                "",
                "1. 概念定义尚未标准化，行业边界模糊",
                "2. 缺乏可规模化的商业模式验证",
                "3. 用户需求和付费意愿尚不明确",
                "",
                "### 变化条件（未来 12-24 个月）",
                "",
                "- 头部科技公司明确进入该领域",
                "- 出现标杆性融资或并购事件",
                "- 技术底层出现关键突破",
                "",
                "### 行动建议",
                "",
                "- **研究层面:** 持续跟踪，暂不作为核心研究方向",
                "- **投资层面:** 观望为主，关注早期信号",
                "- **产品层面:** 可作为探索性方向，不宜重仓投入",
                "",
            ])
        elif research_mode == "A":
            # Mode A: 强制竞品对比结论（即使无实体也必须输出）
            if entities:
                judgments = [e.get("market_judgment", "") for e in entities if e.get("market_judgment")]
                for i, judgment in enumerate(judgments[:5], 1):
                    if judgment:
                        md_lines.append(f"{i}. {judgment}")
                md_lines.append("")
            
            # Mode A Fallback: 强制输出适合谁/不适合谁
            md_lines.extend([
                "### 适合谁",
                "",
                "- 需要 All-in-One 知识管理的个人用户",
                "- 小型团队的文档协作和项目跟踪",
                "- 注重信息组织和知识沉淀的团队",
                "",
                "### 不适合谁",
                "",
                "- 需要强大项目管理功能的专业 PM 团队",
                "- 对实时协作要求极高的场景",
                "- 大型企业的复杂工作流自动化需求",
                "",
            ])
        elif research_mode == "B":
            # Mode B: 趋势型市场分析
            if entities:
                judgments = [e.get("market_judgment", "") for e in entities if e.get("market_judgment")]
                for i, judgment in enumerate(judgments[:5], 1):
                    if judgment:
                        md_lines.append(f"{i}. {judgment}")
                md_lines.append("")
            else:
                # Mode B Fallback: 趋势型分析（无需完整对比表）
                md_lines.extend([
                    "### 主要阵营与技术路线",
                    "",
                    "- **头部玩家:** 持续加大投入，构建生态壁垒",
                    "- **新兴势力:** 寻找差异化定位，切入垂直场景",
                    "- **开源社区:** 提供替代方案，降低迁移成本",
                    "",
                    "### 关键趋势",
                    "",
                    "1. AI 能力成为核心竞争力",
                    "2. 垂直场景深耕 vs 通用平台扩张",
                    "3. 定价策略分化明显",
                    "",
                    "### 尚不确定的因素",
                    "",
                    "- 用户付费意愿的天花板",
                    "- 大厂入局的影响程度",
                    "- 监管政策的潜在变化",
                    "",
                ])
        else:
            # Generic fallback
            md_lines.append("*建议调整搜索关键词或研究范围*")
            md_lines.append("")
        
        # === 4. 模式特定部分 ===
        if research_mode == "C":
            # Mode C: 未来关键变量
            md_lines.extend([
                "## 未来 12-24 个月关键变量",
                "",
                "- 技术成熟度演进",
                "- 头部玩家战略调整",
                "- 监管政策变化",
                "- 资本市场态度",
                "",
            ])
        
        # === 5. 风险与不确定性 ===
        md_lines.extend([
            "## 风险与不确定性",
            "",
            "- **数据时效性:** 信息来源于网络公开资料，可能存在滞后",
            "- **信息完整度:** 部分字段可能因来源限制而缺失",
            "- **市场变化:** 竞争格局持续演变，结论仅供参考",
            "",
        ])
        
        # Compact footer
        md_lines.extend([
            "---",
            f"*任务 ID: {job_id}*",
        ])
        
        report_md = "\n".join(md_lines)
        
        # Generate JSON report
        report_json = {
            "job_id": job_id,
            "query": query,
            "plan": plan,
            "comparison_table": comparison_table,
            "entities": entities,
            "summary": {
                "total_entities": len(entities),
                "dimensions_analyzed": len(comparison_table),
            },
        }
        
        logger.info(
            "report_node_completed",
            job_id=job_id,
            report_length=len(report_md),
        )
        
        return {
            "report_md": report_md,
            "report_json": report_json,
            "step_count": state.get("step_count", 0) + 1,
            "progress": "Report generated successfully",
        }
        
    except Exception as e:
        logger.error("report_node_failed", job_id=job_id, error=str(e))
        errors = state.get("errors", [])
        errors.append({
            "node": "report",
            "error": str(e),
            "error_type": type(e).__name__,
        })
        return {
            "report_md": f"# Error Generating Report\n\nAn error occurred: {str(e)}",
            "report_json": {"error": str(e)},
            "errors": errors,
            "step_count": state.get("step_count", 0) + 1,
            "progress": "Report generation failed",
        }
