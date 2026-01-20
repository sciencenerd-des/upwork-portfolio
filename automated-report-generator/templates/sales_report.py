"""
Sales Report Template for the Automated Report Generator.

This template generates comprehensive sales reports with:
- Executive summary with key metrics
- Revenue trend chart
- Product performance chart
- Regional breakdown chart (if data available)
- Detailed transaction table
- AI-generated insights
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_processor import DataProcessor
from src.chart_generator import ChartGenerator
from src.report_builder import ReportBuilder
from src.ai_insights import AIInsights
from src.utils import (
    format_currency,
    format_number,
    format_percentage,
    get_period_label,
)


class SalesReportTemplate:
    """
    Template for generating sales analysis reports.

    Orchestrates data processing, chart generation, insights,
    and report building for sales data.
    """

    def __init__(self):
        """Initialize the template with required components."""
        self.processor = DataProcessor()
        self.chart_gen = ChartGenerator()
        self.report_builder = ReportBuilder()
        self.ai_insights = AIInsights()

        self.template_name = "sales"
        self.report_title = "Sales Report"

    def generate(
        self,
        data_source: Union[str, Path, pd.DataFrame],
        output_dir: Union[str, Path],
        formats: List[str] = ["pdf", "docx"],
        include_ai_insights: bool = True,
        column_mapping: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """
        Generate a complete sales report.

        Args:
            data_source: Path to data file or DataFrame
            output_dir: Directory for output files
            formats: List of output formats to generate
            include_ai_insights: Whether to include AI-generated insights
            column_mapping: Optional manual column mapping

        Returns:
            Dictionary mapping format to output file path
        """
        # Load and process data
        if isinstance(data_source, pd.DataFrame):
            self.processor.df = data_source
        else:
            self.processor.load_file(data_source)

        self.processor.set_template(self.template_name)

        if column_mapping:
            self.processor.set_column_mapping(column_mapping)
        else:
            self.processor.auto_map_columns()

        # Validate mapping
        is_valid, errors, warnings = self.processor.validate_mapping()
        if not is_valid:
            raise ValueError(f"Invalid column mapping: {', '.join(errors)}")

        # Process data
        df = self.processor.process_data()
        mapping = self.processor.column_mapping

        # Build report sections
        sections = self._build_sections(df, mapping, include_ai_insights)

        # Get metadata
        start_date, end_date = self.processor.get_date_range()
        metadata = {
            "date": datetime.now().strftime("%B %d, %Y"),
            "period": get_period_label(start_date, end_date) if start_date else "N/A",
        }

        # Generate reports
        return self.report_builder.build_report(
            output_dir=output_dir,
            title=self.report_title,
            sections=sections,
            template_name=self.template_name,
            formats=formats,
            metadata=metadata,
        )

    def _build_sections(
        self,
        df: pd.DataFrame,
        mapping: Dict[str, str],
        include_ai_insights: bool,
    ) -> List[Dict[str, Any]]:
        """Build all report sections."""
        sections = []

        # 1. Executive Summary
        summary_section = self._build_summary_section(df, mapping)
        sections.append(summary_section)

        # 2. Revenue Trend
        revenue_chart = self._build_revenue_trend(df, mapping)
        if revenue_chart:
            sections.append(revenue_chart)

        # 3. Product Performance
        product_chart = self._build_product_performance(df, mapping)
        if product_chart:
            sections.append(product_chart)

        # 4. Regional Breakdown (if region data available)
        if mapping.get("region") and mapping["region"] in df.columns:
            region_chart = self._build_regional_breakdown(df, mapping)
            if region_chart:
                sections.append(region_chart)

        # 5. Detailed Data Table
        table_section = self._build_data_table(df, mapping)
        sections.append(table_section)

        # 6. AI Insights
        if include_ai_insights:
            insights_section = self._build_insights_section(df, mapping)
            sections.append(insights_section)

        return sections

    def _build_summary_section(
        self,
        df: pd.DataFrame,
        mapping: Dict[str, str],
    ) -> Dict[str, Any]:
        """Build executive summary section with key metrics."""
        metrics = []

        revenue_col = mapping.get("revenue")
        quantity_col = mapping.get("quantity")
        date_col = mapping.get("date")

        # Total Revenue
        if revenue_col and revenue_col in df.columns:
            total_revenue = df[revenue_col].sum()
            metrics.append({
                "label": "Total Revenue",
                "value": format_currency(total_revenue),
            })

        # Total Units
        if quantity_col and quantity_col in df.columns:
            total_units = df[quantity_col].sum()
            metrics.append({
                "label": "Units Sold",
                "value": format_number(int(total_units)),
            })

        # Transaction Count
        metrics.append({
            "label": "Transactions",
            "value": format_number(len(df)),
        })

        # Average Order Value
        if revenue_col and revenue_col in df.columns:
            avg_value = df[revenue_col].mean()
            metrics.append({
                "label": "Avg Order Value",
                "value": format_currency(avg_value),
            })

        return {
            "type": "summary",
            "title": "Executive Summary",
            "metrics": metrics,
        }

    def _build_revenue_trend(
        self,
        df: pd.DataFrame,
        mapping: Dict[str, str],
    ) -> Optional[Dict[str, Any]]:
        """Build revenue trend chart section."""
        date_col = mapping.get("date")
        revenue_col = mapping.get("revenue")

        if not date_col or not revenue_col:
            return None

        if date_col not in df.columns or revenue_col not in df.columns:
            return None

        try:
            fig = self.chart_gen.create_trend_chart_with_aggregation(
                df,
                date_column=date_col,
                value_column=revenue_col,
                title="Revenue Trend",
                y_label="Revenue ($)",
                period="auto",
                aggregation="sum",
            )

            chart_bytes = self.chart_gen.figure_to_bytes(fig)

            return {
                "type": "chart",
                "title": "Revenue Trend",
                "image_bytes": chart_bytes,
                "caption": "Revenue over time aggregated by period",
            }
        except Exception:
            return None

    def _build_product_performance(
        self,
        df: pd.DataFrame,
        mapping: Dict[str, str],
    ) -> Optional[Dict[str, Any]]:
        """Build product performance chart section."""
        product_col = mapping.get("product")
        revenue_col = mapping.get("revenue")

        if not product_col or not revenue_col:
            return None

        if product_col not in df.columns or revenue_col not in df.columns:
            return None

        try:
            fig = self.chart_gen.create_bar_chart(
                df,
                category_column=product_col,
                value_column=revenue_col,
                title="Top Products by Revenue",
                y_label="Revenue ($)",
                orientation="horizontal",
                limit=10,
                sort_by_value=True,
            )

            chart_bytes = self.chart_gen.figure_to_bytes(fig)

            return {
                "type": "chart",
                "title": "Product Performance",
                "image_bytes": chart_bytes,
                "caption": "Top 10 products ranked by total revenue",
            }
        except Exception:
            return None

    def _build_regional_breakdown(
        self,
        df: pd.DataFrame,
        mapping: Dict[str, str],
    ) -> Optional[Dict[str, Any]]:
        """Build regional breakdown pie chart section."""
        region_col = mapping.get("region")
        revenue_col = mapping.get("revenue")

        if not region_col or not revenue_col:
            return None

        if region_col not in df.columns or revenue_col not in df.columns:
            return None

        try:
            fig = self.chart_gen.create_pie_chart(
                df,
                category_column=region_col,
                value_column=revenue_col,
                title="Revenue by Region",
                show_legend=True,
                show_percentages=True,
            )

            chart_bytes = self.chart_gen.figure_to_bytes(fig)

            return {
                "type": "chart",
                "title": "Regional Breakdown",
                "image_bytes": chart_bytes,
                "caption": "Revenue distribution across regions",
            }
        except Exception:
            return None

    def _build_data_table(
        self,
        df: pd.DataFrame,
        mapping: Dict[str, str],
    ) -> Dict[str, Any]:
        """Build detailed data table section."""
        revenue_col = mapping.get("revenue")

        # Select columns for display
        display_cols = []
        for field in ["date", "product", "category", "quantity", "revenue", "region"]:
            col = mapping.get(field)
            if col and col in df.columns:
                display_cols.append(col)

        if not display_cols:
            display_cols = list(df.columns)[:6]

        # Sort by revenue and take top 20
        table_df = df[display_cols].copy()
        if revenue_col and revenue_col in table_df.columns:
            table_df = table_df.sort_values(revenue_col, ascending=False)

        table_df = table_df.head(20)

        return {
            "type": "table",
            "title": "Top Transactions",
            "dataframe": table_df,
        }

    def _build_insights_section(
        self,
        df: pd.DataFrame,
        mapping: Dict[str, str],
    ) -> Dict[str, Any]:
        """Build AI insights section."""
        # Calculate summary for AI
        summary = self.ai_insights.calculate_sales_summary(df, mapping)

        # Build chart descriptions for context
        chart_descriptions = [
            {
                "title": "Revenue Trend",
                "description": "Line chart showing revenue over time, aggregated by period (daily/weekly/monthly based on date range)"
            },
            {
                "title": "Top Products by Revenue",
                "description": "Horizontal bar chart showing the top 10 products ranked by total revenue contribution"
            },
        ]

        # Add regional chart if data available
        if mapping.get("region") and mapping["region"] in df.columns:
            chart_descriptions.append({
                "title": "Revenue by Region",
                "description": "Pie chart showing revenue distribution across different regions"
            })

        # Build raw data context for detailed analysis
        raw_data_context = {}

        # Top products detail
        product_col = mapping.get("product")
        revenue_col = mapping.get("revenue")
        if product_col and revenue_col and product_col in df.columns and revenue_col in df.columns:
            product_revenue = df.groupby(product_col)[revenue_col].sum().sort_values(ascending=False)
            raw_data_context['top_products'] = [
                {"name": name, "revenue": rev}
                for name, rev in product_revenue.head(10).items()
            ]

        # Monthly trend detail
        date_col = mapping.get("date")
        if date_col and revenue_col and date_col in df.columns and revenue_col in df.columns:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col])
            df_copy['_month'] = df_copy[date_col].dt.to_period('M')
            monthly_rev = df_copy.groupby('_month')[revenue_col].sum()
            raw_data_context['monthly_trend'] = [
                {"period": str(period), "revenue": rev}
                for period, rev in monthly_rev.items()
            ]

        # Regional breakdown detail
        region_col = mapping.get("region")
        if region_col and revenue_col and region_col in df.columns and revenue_col in df.columns:
            region_revenue = df.groupby(region_col)[revenue_col].sum().sort_values(ascending=False)
            total_revenue = region_revenue.sum()
            raw_data_context['regional_breakdown'] = [
                {"name": name, "revenue": rev, "pct": (rev / total_revenue) * 100}
                for name, rev in region_revenue.items()
            ]

        # Generate insights with full context
        insights = self.ai_insights.generate_insights(
            summary,
            template_type="sales",
            max_insights=5,
            use_ai=self.ai_insights.is_available,
            chart_descriptions=chart_descriptions,
            raw_data_context=raw_data_context,
        )

        return {
            "type": "insights",
            "title": "AI-Generated Insights",
            "insights": insights,
        }
