"""Reporting service for generating and exporting reports."""

import csv
import io
import json
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)


class ReportingService:
    """Service for generating and exporting reports in various formats."""

    async def generate_csv(self, comparison_table: dict[str, dict[str, Any]]) -> str:
        """Generate CSV from comparison table.
        
        Args:
            comparison_table: Comparison table data
            
        Returns:
            CSV string
        """
        if not comparison_table:
            return ""
        
        # Get all product names
        product_names = set()
        for dim_data in comparison_table.values():
            product_names.update(dim_data.keys())
        product_names = sorted(product_names)
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["Dimension"] + product_names)
        
        # Write rows
        for dimension, products in comparison_table.items():
            row = [dimension]
            for product in product_names:
                value = products.get(product, "N/A")
                # Handle lists and dicts
                if isinstance(value, (list, dict)):
                    value = json.dumps(value)
                row.append(str(value))
            writer.writerow(row)
        
        csv_content = output.getvalue()
        output.close()
        
        logger.info("csv_generated", row_count=len(comparison_table))
        return csv_content

    async def generate_json(self, report_data: dict[str, Any]) -> str:
        """Generate formatted JSON from report data.
        
        Args:
            report_data: Report data
            
        Returns:
            Formatted JSON string
        """
        json_str = json.dumps(report_data, indent=2, ensure_ascii=False)
        logger.info("json_generated", size=len(json_str))
        return json_str

    async def save_report_files(
        self,
        job_id: str,
        report_md: str,
        report_json: dict[str, Any],
        comparison_table: dict[str, dict[str, Any]],
        output_dir: str = "./reports",
    ) -> dict[str, str]:
        """Save report files to disk.
        
        Args:
            job_id: Job identifier
            report_md: Markdown report
            report_json: JSON report data
            comparison_table: Comparison table
            output_dir: Output directory
            
        Returns:
            Dictionary of file paths
        """
        import os
        from pathlib import Path
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        file_paths = {}
        
        # Save Markdown
        md_path = os.path.join(output_dir, f"{job_id}_report.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(report_md)
        file_paths["markdown"] = md_path
        
        # Save JSON
        json_path = os.path.join(output_dir, f"{job_id}_report.json")
        json_str = await self.generate_json(report_json)
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(json_str)
        file_paths["json"] = json_path
        
        # Save CSV
        csv_path = os.path.join(output_dir, f"{job_id}_comparison.csv")
        csv_str = await self.generate_csv(comparison_table)
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            f.write(csv_str)
        file_paths["csv"] = csv_path
        
        logger.info("report_files_saved", job_id=job_id, file_count=len(file_paths))
        return file_paths


# Global reporting service instance
_reporting_service: ReportingService | None = None


def get_reporting_service() -> ReportingService:
    """Get the global reporting service instance.
    
    Returns:
        ReportingService: Global reporting service
    """
    global _reporting_service
    if _reporting_service is None:
        _reporting_service = ReportingService()
    return _reporting_service
