"""
Financial Report Template for the Automated Report Generator.

This template generates comprehensive financial reports with:
- Financial overview with key metrics
- Monthly income vs expenses trend
- Expense breakdown by category
- Income sources analysis
- Month-over-month comparison table
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
    get_period_label,
)


class FinancialReportTemplate:
    """
    Template for generating financial summary reports.

    Orchestrates data processing, chart generation, insights,
    and report building for financial data.
    """

    def __init__(self):
        """Initialize the template with required components."""
        self.processor = DataProcessor()
        self.chart_gen = ChartGenerator()
        self.report_builder = ReportBuilder()
        self.ai_insights = AIInsights()

        self.template_name = "financial"
        self.report_title = "Financial Summary Report"

    def generate(
        self,
        data_source: Union[str, Path, pd.DataFrame],
        output_dir: Union[str, Path],
        formats: List[str] = ["pdf", "docx"],
        include_ai_insights: bool = True,
        column_mapping: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """
        Generate a complete financial report.

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

        # 1. Financial Overview
        summary_section = self._build_summary_section(df, mapping)
        sections.append(summary_section)

        # 2. Monthly Trend
        trend_chart = self._build_monthly_trend(df, mapping)
        if trend_chart:
            sections.append(trend_chart)

        # 3. Expense Breakdown
        expense_chart = self._build_expense_breakdown(df, mapping)
        if expense_chart:
            sections.append(expense_chart)

        # 4. Income Sources
        income_chart = self._build_income_sources(df, mapping)
        if income_chart:
            sections.append(income_chart)

        # 5. Month-over-Month Comparison
        mom_table = self._build_mom_comparison(df, mapping)
        if mom_table:
            sections.append(mom_table)

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
        """Build financial overview section with key metrics."""
        metrics = []

        amount_col = mapping.get("amount")
        type_col = mapping.get("transaction_type")

        if not amount_col or not type_col:
            return {"type": "summary", "title": "Financial Overview", "metrics": metrics}

        # Normalize transaction type
        df_copy = df.copy()
        df_copy[type_col] = df_copy[type_col].str.lower()

        income_mask = df_copy[type_col].str.contains('income', na=False)
        expense_mask = df_copy[type_col].str.contains('expense', na=False)

        total_income = df_copy.loc[income_mask, amount_col].sum()
        total_expenses = df_copy.loc[expense_mask, amount_col].sum()
        net_profit = total_income - total_expenses
        profit_margin = (net_profit / total_income * 100) if total_income > 0 else 0

        # Total Income
        metrics.append({
            "label": "Total Income",
            "value": format_currency(total_income),
        })

        # Total Expenses
        metrics.append({
            "label": "Total Expenses",
            "value": format_currency(total_expenses),
        })

        # Net Profit
        metrics.append({
            "label": "Net Profit",
            "value": format_currency(net_profit),
        })

        # Profit Margin
        metrics.append({
            "label": "Profit Margin",
            "value": f"{profit_margin:.1f}%",
        })

        return {
            "type": "summary",
            "title": "Financial Overview",
            "metrics": metrics,
        }

    def _build_monthly_trend(
        self,
        df: pd.DataFrame,
        mapping: Dict[str, str],
    ) -> Optional[Dict[str, Any]]:
        """Build monthly income vs expenses trend chart."""
        date_col = mapping.get("date")
        amount_col = mapping.get("amount")
        type_col = mapping.get("transaction_type")

        if not all([date_col, amount_col, type_col]):
            return None

        if not all(c in df.columns for c in [date_col, amount_col, type_col]):
            return None

        try:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col])
            df_copy['month'] = df_copy[date_col].dt.to_period('M').dt.to_timestamp()
            df_copy[type_col] = df_copy[type_col].str.lower()

            # Aggregate by month and type
            income_mask = df_copy[type_col].str.contains('income', na=False)
            expense_mask = df_copy[type_col].str.contains('expense', na=False)

            monthly_income = df_copy[income_mask].groupby('month')[amount_col].sum()
            monthly_expenses = df_copy[expense_mask].groupby('month')[amount_col].sum()

            # Combine into DataFrame
            trend_df = pd.DataFrame({
                'Month': monthly_income.index,
                'Income': monthly_income.values,
                'Expenses': monthly_expenses.reindex(monthly_income.index, fill_value=0).values,
            })

            fig = self.chart_gen.create_line_chart(
                trend_df,
                x_column='Month',
                y_columns=['Income', 'Expenses'],
                title="Monthly Income vs Expenses",
                y_label="Amount ($)",
                show_legend=True,
            )

            chart_bytes = self.chart_gen.figure_to_bytes(fig)

            return {
                "type": "chart",
                "title": "Monthly Trend",
                "image_bytes": chart_bytes,
                "caption": "Income and expenses comparison by month",
            }
        except Exception:
            return None

    def _build_expense_breakdown(
        self,
        df: pd.DataFrame,
        mapping: Dict[str, str],
    ) -> Optional[Dict[str, Any]]:
        """Build expense breakdown pie chart."""
        category_col = mapping.get("category")
        amount_col = mapping.get("amount")
        type_col = mapping.get("transaction_type")

        if not all([category_col, amount_col, type_col]):
            return None

        if not all(c in df.columns for c in [category_col, amount_col, type_col]):
            return None

        try:
            df_copy = df.copy()
            df_copy[type_col] = df_copy[type_col].str.lower()
            expense_mask = df_copy[type_col].str.contains('expense', na=False)
            expenses_df = df_copy[expense_mask]

            if len(expenses_df) == 0:
                return None

            fig = self.chart_gen.create_pie_chart(
                expenses_df,
                category_column=category_col,
                value_column=amount_col,
                title="Expense Breakdown",
                show_legend=True,
                show_percentages=True,
            )

            chart_bytes = self.chart_gen.figure_to_bytes(fig)

            return {
                "type": "chart",
                "title": "Expense Breakdown",
                "image_bytes": chart_bytes,
                "caption": "Distribution of expenses by category",
            }
        except Exception:
            return None

    def _build_income_sources(
        self,
        df: pd.DataFrame,
        mapping: Dict[str, str],
    ) -> Optional[Dict[str, Any]]:
        """Build income sources bar chart."""
        category_col = mapping.get("category")
        amount_col = mapping.get("amount")
        type_col = mapping.get("transaction_type")

        if not all([category_col, amount_col, type_col]):
            return None

        if not all(c in df.columns for c in [category_col, amount_col, type_col]):
            return None

        try:
            df_copy = df.copy()
            df_copy[type_col] = df_copy[type_col].str.lower()
            income_mask = df_copy[type_col].str.contains('income', na=False)
            income_df = df_copy[income_mask]

            if len(income_df) == 0:
                return None

            fig = self.chart_gen.create_bar_chart(
                income_df,
                category_column=category_col,
                value_column=amount_col,
                title="Income by Source",
                y_label="Amount ($)",
                orientation="horizontal",
                sort_by_value=True,
            )

            chart_bytes = self.chart_gen.figure_to_bytes(fig)

            return {
                "type": "chart",
                "title": "Income Sources",
                "image_bytes": chart_bytes,
                "caption": "Income breakdown by category",
            }
        except Exception:
            return None

    def _build_mom_comparison(
        self,
        df: pd.DataFrame,
        mapping: Dict[str, str],
    ) -> Optional[Dict[str, Any]]:
        """Build month-over-month comparison table."""
        date_col = mapping.get("date")
        amount_col = mapping.get("amount")
        type_col = mapping.get("transaction_type")

        if not all([date_col, amount_col, type_col]):
            return None

        try:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col])
            df_copy['month'] = df_copy[date_col].dt.to_period('M').dt.to_timestamp()
            df_copy[type_col] = df_copy[type_col].str.lower()

            income_mask = df_copy[type_col].str.contains('income', na=False)
            expense_mask = df_copy[type_col].str.contains('expense', na=False)

            monthly_income = df_copy[income_mask].groupby('month')[amount_col].sum()
            monthly_expenses = df_copy[expense_mask].groupby('month')[amount_col].sum()

            # Create comparison table
            months = sorted(set(monthly_income.index) | set(monthly_expenses.index))
            table_data = []

            for month in months:
                income = monthly_income.get(month, 0)
                expenses = monthly_expenses.get(month, 0)
                net = income - expenses

                table_data.append({
                    "Month": month.strftime("%b %Y"),
                    "Income": income,
                    "Expenses": expenses,
                    "Net": net,
                })

            table_df = pd.DataFrame(table_data)

            return {
                "type": "table",
                "title": "Month-over-Month Comparison",
                "dataframe": table_df,
            }
        except Exception:
            return None

    def _build_insights_section(
        self,
        df: pd.DataFrame,
        mapping: Dict[str, str],
    ) -> Dict[str, Any]:
        """Build AI insights section."""
        # Calculate summary for AI
        summary = self.ai_insights.calculate_financial_summary(df, mapping)

        # Build chart descriptions for context
        chart_descriptions = [
            {
                "title": "Monthly Income vs Expenses",
                "description": "Line chart comparing monthly income and expenses trends over time"
            },
            {
                "title": "Expense Breakdown",
                "description": "Pie chart showing distribution of expenses across different categories"
            },
            {
                "title": "Income by Source",
                "description": "Horizontal bar chart showing income amounts by category/source"
            },
        ]

        # Build raw data context for detailed analysis
        raw_data_context = {}

        amount_col = mapping.get("amount")
        type_col = mapping.get("transaction_type")
        category_col = mapping.get("category")
        date_col = mapping.get("date")

        if amount_col and type_col and amount_col in df.columns and type_col in df.columns:
            df_copy = df.copy()
            df_copy[type_col] = df_copy[type_col].str.lower()

            income_mask = df_copy[type_col].str.contains('income', na=False)
            expense_mask = df_copy[type_col].str.contains('expense', na=False)

            # Expense breakdown by category
            if category_col and category_col in df.columns:
                expense_by_cat = df_copy[expense_mask].groupby(category_col)[amount_col].sum().sort_values(ascending=False)
                total_expenses = expense_by_cat.sum()
                raw_data_context['expense_breakdown'] = [
                    {"category": cat, "amount": amt, "pct": (amt / total_expenses) * 100 if total_expenses > 0 else 0}
                    for cat, amt in expense_by_cat.items()
                ]

                # Income sources
                income_by_cat = df_copy[income_mask].groupby(category_col)[amount_col].sum().sort_values(ascending=False)
                total_income = income_by_cat.sum()
                raw_data_context['income_sources'] = [
                    {"category": cat, "amount": amt, "pct": (amt / total_income) * 100 if total_income > 0 else 0}
                    for cat, amt in income_by_cat.items()
                ]

            # Monthly comparison
            if date_col and date_col in df.columns:
                df_copy[date_col] = pd.to_datetime(df_copy[date_col])
                df_copy['_month'] = df_copy[date_col].dt.to_period('M')

                monthly_income = df_copy[income_mask].groupby('_month')[amount_col].sum()
                monthly_expenses = df_copy[expense_mask].groupby('_month')[amount_col].sum()

                all_months = sorted(set(monthly_income.index) | set(monthly_expenses.index))
                raw_data_context['monthly_comparison'] = [
                    {
                        "period": str(month),
                        "income": monthly_income.get(month, 0),
                        "expenses": monthly_expenses.get(month, 0)
                    }
                    for month in all_months
                ]

        # Generate insights with full context
        insights = self.ai_insights.generate_insights(
            summary,
            template_type="financial",
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
