"""
Inventory Report Template for the Automated Report Generator.

This template generates comprehensive inventory reports with:
- Inventory summary with key metrics
- Stock status by category chart
- Reorder alerts table
- Value distribution by category chart
- Top items by value table
- AI-generated insights
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import pandas as pd
import numpy as np

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
)


class InventoryReportTemplate:
    """
    Template for generating inventory analysis reports.

    Orchestrates data processing, chart generation, insights,
    and report building for inventory data.
    """

    def __init__(self):
        """Initialize the template with required components."""
        self.processor = DataProcessor()
        self.chart_gen = ChartGenerator()
        self.report_builder = ReportBuilder()
        self.ai_insights = AIInsights()

        self.template_name = "inventory"
        self.report_title = "Inventory Report"

    def generate(
        self,
        data_source: Union[str, Path, pd.DataFrame],
        output_dir: Union[str, Path],
        formats: List[str] = ["pdf", "docx"],
        include_ai_insights: bool = True,
        column_mapping: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """
        Generate a complete inventory report.

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
        metadata = {
            "date": datetime.now().strftime("%B %d, %Y"),
            "period": "Current Snapshot",
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

        # 1. Inventory Summary
        summary_section = self._build_summary_section(df, mapping)
        sections.append(summary_section)

        # 2. Stock Status by Category
        stock_chart = self._build_stock_status(df, mapping)
        if stock_chart:
            sections.append(stock_chart)

        # 3. Reorder Alerts
        reorder_table = self._build_reorder_alerts(df, mapping)
        if reorder_table:
            sections.append(reorder_table)

        # 4. Value Distribution
        value_chart = self._build_value_distribution(df, mapping)
        if value_chart:
            sections.append(value_chart)

        # 5. Top Items by Value
        top_items_table = self._build_top_items(df, mapping)
        sections.append(top_items_table)

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
        """Build inventory summary section with key metrics."""
        metrics = []

        product_col = mapping.get("product")
        quantity_col = mapping.get("quantity")
        reorder_col = mapping.get("reorder_level")
        cost_col = mapping.get("unit_cost")

        # Total SKUs
        metrics.append({
            "label": "Total SKUs",
            "value": format_number(len(df)),
        })

        # Total Units
        if quantity_col and quantity_col in df.columns:
            total_units = df[quantity_col].sum()
            metrics.append({
                "label": "Total Units",
                "value": format_number(int(total_units)),
            })

        # Total Value
        if quantity_col and cost_col and all(c in df.columns for c in [quantity_col, cost_col]):
            total_value = (df[quantity_col] * df[cost_col]).sum()
            metrics.append({
                "label": "Total Value",
                "value": format_currency(total_value),
            })

        # Items Below Reorder
        if quantity_col and reorder_col and all(c in df.columns for c in [quantity_col, reorder_col]):
            below_reorder = len(df[df[quantity_col] <= df[reorder_col]])
            metrics.append({
                "label": "Below Reorder",
                "value": format_number(below_reorder),
            })

        return {
            "type": "summary",
            "title": "Inventory Summary",
            "metrics": metrics,
        }

    def _build_stock_status(
        self,
        df: pd.DataFrame,
        mapping: Dict[str, str],
    ) -> Optional[Dict[str, Any]]:
        """Build stock status by category chart."""
        category_col = mapping.get("category")
        quantity_col = mapping.get("quantity")

        if not category_col or not quantity_col:
            return None

        if category_col not in df.columns or quantity_col not in df.columns:
            return None

        try:
            fig = self.chart_gen.create_bar_chart(
                df,
                category_column=category_col,
                value_column=quantity_col,
                title="Stock Levels by Category",
                y_label="Quantity",
                orientation="horizontal",
                sort_by_value=True,
            )

            chart_bytes = self.chart_gen.figure_to_bytes(fig)

            return {
                "type": "chart",
                "title": "Stock Status by Category",
                "image_bytes": chart_bytes,
                "caption": "Total stock quantity grouped by category",
            }
        except Exception:
            return None

    def _build_reorder_alerts(
        self,
        df: pd.DataFrame,
        mapping: Dict[str, str],
    ) -> Optional[Dict[str, Any]]:
        """Build reorder alerts table."""
        product_col = mapping.get("product")
        category_col = mapping.get("category")
        quantity_col = mapping.get("quantity")
        reorder_col = mapping.get("reorder_level")

        if not all([product_col, quantity_col, reorder_col]):
            return None

        if not all(c in df.columns for c in [product_col, quantity_col, reorder_col]):
            return None

        try:
            # Filter items at or below reorder level
            below_reorder = df[df[quantity_col] <= df[reorder_col]].copy()

            if len(below_reorder) == 0:
                # No items below reorder, show message
                return {
                    "type": "text",
                    "title": "Reorder Alerts",
                    "text": "All items are above their minimum stock levels. No reorder alerts at this time.",
                }

            # Select relevant columns
            display_cols = [product_col]
            if category_col and category_col in df.columns:
                display_cols.append(category_col)
            display_cols.extend([quantity_col, reorder_col])

            # Calculate shortage
            below_reorder['Shortage'] = below_reorder[reorder_col] - below_reorder[quantity_col]

            table_df = below_reorder[display_cols + ['Shortage']].copy()
            table_df = table_df.sort_values('Shortage', ascending=False).head(15)

            return {
                "type": "table",
                "title": "Reorder Alerts",
                "dataframe": table_df,
            }
        except Exception:
            return None

    def _build_value_distribution(
        self,
        df: pd.DataFrame,
        mapping: Dict[str, str],
    ) -> Optional[Dict[str, Any]]:
        """Build inventory value distribution pie chart."""
        category_col = mapping.get("category")
        quantity_col = mapping.get("quantity")
        cost_col = mapping.get("unit_cost")

        if not all([category_col, quantity_col, cost_col]):
            return None

        if not all(c in df.columns for c in [category_col, quantity_col, cost_col]):
            return None

        try:
            # Calculate value per row
            df_copy = df.copy()
            df_copy['_value'] = df_copy[quantity_col] * df_copy[cost_col]

            fig = self.chart_gen.create_pie_chart(
                df_copy,
                category_column=category_col,
                value_column='_value',
                title="Inventory Value by Category",
                show_legend=True,
                show_percentages=True,
            )

            chart_bytes = self.chart_gen.figure_to_bytes(fig)

            return {
                "type": "chart",
                "title": "Value Distribution",
                "image_bytes": chart_bytes,
                "caption": "Inventory value distribution across categories",
            }
        except Exception:
            return None

    def _build_top_items(
        self,
        df: pd.DataFrame,
        mapping: Dict[str, str],
    ) -> Dict[str, Any]:
        """Build top items by value table."""
        product_col = mapping.get("product")
        category_col = mapping.get("category")
        quantity_col = mapping.get("quantity")
        cost_col = mapping.get("unit_cost")

        # Select columns for display
        display_cols = []
        for field in ["product", "category", "quantity", "unit_cost"]:
            col = mapping.get(field)
            if col and col in df.columns:
                display_cols.append(col)

        if not display_cols:
            display_cols = list(df.columns)[:5]

        table_df = df[display_cols].copy()

        # Calculate and add value column if possible
        if quantity_col and cost_col and all(c in df.columns for c in [quantity_col, cost_col]):
            table_df['Total Value'] = df[quantity_col] * df[cost_col]
            table_df = table_df.sort_values('Total Value', ascending=False)
        elif quantity_col and quantity_col in df.columns:
            table_df = table_df.sort_values(quantity_col, ascending=False)

        table_df = table_df.head(15)

        return {
            "type": "table",
            "title": "Top Items by Value",
            "dataframe": table_df,
        }

    def _build_insights_section(
        self,
        df: pd.DataFrame,
        mapping: Dict[str, str],
    ) -> Dict[str, Any]:
        """Build AI insights section."""
        # Calculate summary for AI
        summary = self.ai_insights.calculate_inventory_summary(df, mapping)

        # Build chart descriptions for context
        chart_descriptions = [
            {
                "title": "Stock Levels by Category",
                "description": "Horizontal bar chart showing total stock quantity grouped by product category"
            },
            {
                "title": "Inventory Value by Category",
                "description": "Pie chart showing the distribution of inventory value across different categories"
            },
        ]

        # Build raw data context for detailed analysis
        raw_data_context = {}

        product_col = mapping.get("product")
        category_col = mapping.get("category")
        quantity_col = mapping.get("quantity")
        reorder_col = mapping.get("reorder_level")
        cost_col = mapping.get("unit_cost")

        # Reorder alerts - items at or below reorder level
        if product_col and quantity_col and reorder_col:
            if all(c in df.columns for c in [product_col, quantity_col, reorder_col]):
                below_reorder = df[df[quantity_col] <= df[reorder_col]].copy()
                below_reorder = below_reorder.sort_values(quantity_col)
                raw_data_context['reorder_alerts'] = [
                    {
                        "product": row[product_col],
                        "quantity": row[quantity_col],
                        "reorder_level": row[reorder_col]
                    }
                    for _, row in below_reorder.head(10).iterrows()
                ]

        # Stock by category
        if category_col and quantity_col and cost_col:
            if all(c in df.columns for c in [category_col, quantity_col, cost_col]):
                df_copy = df.copy()
                df_copy['_value'] = df_copy[quantity_col] * df_copy[cost_col]
                category_data = df_copy.groupby(category_col).agg({
                    quantity_col: 'sum',
                    '_value': 'sum'
                }).sort_values('_value', ascending=False)

                raw_data_context['category_stock'] = [
                    {"category": cat, "units": int(row[quantity_col]), "value": row['_value']}
                    for cat, row in category_data.iterrows()
                ]

        # Top value items
        if product_col and quantity_col and cost_col:
            if all(c in df.columns for c in [product_col, quantity_col, cost_col]):
                df_copy = df.copy()
                df_copy['_value'] = df_copy[quantity_col] * df_copy[cost_col]
                top_items = df_copy.nlargest(10, '_value')
                raw_data_context['top_value_items'] = [
                    {"product": row[product_col], "value": row['_value']}
                    for _, row in top_items.iterrows()
                ]

        # Generate insights with full context
        insights = self.ai_insights.generate_insights(
            summary,
            template_type="inventory",
            max_insights=5,
            use_ai=self.ai_insights.is_available,
            chart_descriptions=chart_descriptions,
            raw_data_context=raw_data_context,
        )

        # Track if fallback was used
        section = {
            "type": "insights",
            "title": "AI-Generated Insights" if not self.ai_insights.fallback_used else "Statistical Insights",
            "insights": insights,
        }

        # Add a note if fallback was used
        if self.ai_insights.fallback_used:
            section["fallback_note"] = "AI insights were not available. Using statistical analysis instead."
            if self.ai_insights.last_error:
                section["error_detail"] = self.ai_insights.last_error

        return section
