"""
AI Insights Module for the Automated Report Generator.

This module handles:
- Integration with OpenRouter API for AI-powered insights
- Generating narrative insights from data summaries
- Identifying trends, anomalies, and recommendations
- Fallback to basic statistical insights when API is unavailable
"""

import os
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import pandas as pd
import numpy as np

from .utils import (
    format_currency,
    format_number,
    format_percentage,
    get_trend_direction,
    calculate_percentage_change,
)


class AIInsightsError(Exception):
    """Exception raised for AI insights generation errors."""
    pass


class AIInsights:
    """
    Generates AI-powered narrative insights from data.

    Uses OpenRouter API for generating insights, with
    fallback to basic statistical analysis when API is unavailable.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AIInsights generator.

        Args:
            api_key: OpenRouter API key. If not provided, will look for
                    OPENROUTER_API_KEY environment variable.
        """
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        self._client = None
        self._model = "openai/gpt-5-nano"  # GPT-5 Nano via OpenRouter

        if self.api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.api_key,
                )
            except ImportError:
                pass  # Will use fallback
            except Exception:
                pass  # Will use fallback

    @property
    def is_available(self) -> bool:
        """Check if AI insights are available."""
        return self._client is not None

    def generate_insights(
        self,
        data_summary: Dict[str, Any],
        template_type: str,
        max_insights: int = 5,
        use_ai: bool = True,
        chart_descriptions: Optional[List[Dict[str, str]]] = None,
        raw_data_context: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        Generate insights from data summary.

        Args:
            data_summary: Dictionary containing summarized data metrics
            template_type: Type of report template (sales, financial, inventory)
            max_insights: Maximum number of insights to generate
            use_ai: Whether to use AI (True) or fallback to basic analysis
            chart_descriptions: List of dicts with chart titles and descriptions
            raw_data_context: Additional context from raw data analysis

        Returns:
            List of insight strings
        """
        if use_ai and self.is_available:
            try:
                return self._generate_ai_insights(
                    data_summary, template_type, max_insights,
                    chart_descriptions, raw_data_context
                )
            except Exception as e:
                # Fallback to basic analysis on any error
                pass

        return self._generate_basic_insights(data_summary, template_type, max_insights)

    def _generate_ai_insights(
        self,
        data_summary: Dict[str, Any],
        template_type: str,
        max_insights: int,
        chart_descriptions: Optional[List[Dict[str, str]]] = None,
        raw_data_context: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """Generate insights using OpenRouter API."""
        prompt = self._build_prompt(
            data_summary, template_type,
            chart_descriptions, raw_data_context
        )

        response = self._client.chat.completions.create(
            model=self._model,
            max_tokens=1500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = response.choices[0].message.content
        insights = self._parse_insights(response_text, max_insights)

        return insights

    def _build_prompt(
        self,
        data_summary: Dict[str, Any],
        template_type: str,
        chart_descriptions: Optional[List[Dict[str, str]]] = None,
        raw_data_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build the prompt for AI insight generation."""
        template_prompts = {
            "sales": self._build_sales_prompt,
            "financial": self._build_financial_prompt,
            "inventory": self._build_inventory_prompt,
        }

        builder = template_prompts.get(template_type, self._build_generic_prompt)
        return builder(data_summary, chart_descriptions, raw_data_context)

    def _build_sales_prompt(
        self,
        data_summary: Dict[str, Any],
        chart_descriptions: Optional[List[Dict[str, str]]] = None,
        raw_data_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build prompt for sales insights."""
        # Build chart context section
        chart_section = ""
        if chart_descriptions:
            chart_section = "\n\nCharts Included in This Report:\n"
            for chart in chart_descriptions:
                chart_section += f"- {chart.get('title', 'Chart')}: {chart.get('description', '')}\n"

        # Build detailed data context section
        data_context_section = ""
        if raw_data_context:
            data_context_section = "\n\nDetailed Data Analysis:\n"
            if raw_data_context.get('top_products'):
                data_context_section += "Top 5 Products by Revenue:\n"
                for i, prod in enumerate(raw_data_context['top_products'][:5], 1):
                    data_context_section += f"  {i}. {prod['name']}: {format_currency(prod['revenue'])}\n"
            if raw_data_context.get('monthly_trend'):
                data_context_section += "\nMonthly Revenue Trend:\n"
                for month_data in raw_data_context['monthly_trend'][-6:]:
                    data_context_section += f"  {month_data['period']}: {format_currency(month_data['revenue'])}\n"
            if raw_data_context.get('regional_breakdown'):
                data_context_section += "\nRegional Performance:\n"
                for region in raw_data_context['regional_breakdown']:
                    data_context_section += f"  {region['name']}: {format_currency(region['revenue'])} ({format_percentage(region['pct']/100)})\n"

        return f"""You are a senior analyst at a top-tier consulting firm (McKinsey, Bloomberg, Berkshire Capital). You are preparing executive-level insights for a sales performance report. Your analysis will be presented to C-suite executives and must reflect the highest standards of professional consulting.

The report includes executive summary metrics, trend charts, product performance visualizations, and regional breakdowns. Your insights must reference specific data points and charts to support your analysis.

DATA SUMMARY:
- Total Revenue: {format_currency(data_summary.get('total_revenue', 0))}
- Total Units Sold: {format_number(data_summary.get('total_units', 0))}
- Number of Transactions: {format_number(data_summary.get('transaction_count', 0))}
- Average Order Value: {format_currency(data_summary.get('avg_order_value', 0))}
- Date Range: {data_summary.get('start_date', 'N/A')} to {data_summary.get('end_date', 'N/A')}
- Top Product: {data_summary.get('top_product', 'N/A')} ({format_percentage(data_summary.get('top_product_pct', 0)/100)} of revenue)
- Top Region: {data_summary.get('top_region', 'N/A')} ({format_percentage(data_summary.get('top_region_pct', 0)/100)} of revenue)
- Revenue Trend: {data_summary.get('trend_direction', 'stable')} ({format_percentage(data_summary.get('trend_pct', 0))} change)
{chart_section}{data_context_section}

Based on this data and the charts in the report, provide 4-5 specific, actionable insights. Your insights should:
1. Reference specific numbers and percentages from the data
2. Mention relevant charts when discussing trends or comparisons (e.g., "As shown in the Revenue Trend chart...")
3. Identify patterns, anomalies, or opportunities
4. Provide concrete recommendations based on the analysis

Format each insight as a bullet point starting with "- ". Each insight should be 1-2 sentences and use professional business language."""

    def _build_financial_prompt(
        self,
        data_summary: Dict[str, Any],
        chart_descriptions: Optional[List[Dict[str, str]]] = None,
        raw_data_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build prompt for financial insights."""
        # Build chart context section
        chart_section = ""
        if chart_descriptions:
            chart_section = "\n\nCharts Included in This Report:\n"
            for chart in chart_descriptions:
                chart_section += f"- {chart.get('title', 'Chart')}: {chart.get('description', '')}\n"

        # Build detailed data context section
        data_context_section = ""
        if raw_data_context:
            data_context_section = "\n\nDetailed Data Analysis:\n"
            if raw_data_context.get('expense_breakdown'):
                data_context_section += "Expense Breakdown by Category:\n"
                for cat in raw_data_context['expense_breakdown'][:5]:
                    data_context_section += f"  {cat['category']}: {format_currency(cat['amount'])} ({format_percentage(cat['pct']/100)})\n"
            if raw_data_context.get('income_sources'):
                data_context_section += "\nIncome Sources:\n"
                for src in raw_data_context['income_sources'][:5]:
                    data_context_section += f"  {src['category']}: {format_currency(src['amount'])} ({format_percentage(src['pct']/100)})\n"
            if raw_data_context.get('monthly_comparison'):
                data_context_section += "\nMonthly Income vs Expenses:\n"
                for month_data in raw_data_context['monthly_comparison'][-6:]:
                    data_context_section += f"  {month_data['period']}: Income {format_currency(month_data['income'])}, Expenses {format_currency(month_data['expenses'])}\n"

        return f"""You are a senior financial analyst at a top-tier consulting firm (McKinsey, Bloomberg, Berkshire Capital). You are preparing executive-level insights for a financial performance report. Your analysis will be presented to the CFO and Board of Directors and must reflect the highest standards of financial consulting.

The report includes financial overview metrics, income vs expenses trend charts, expense breakdown visualizations, and month-over-month comparisons. Your insights must reference specific figures and charts to support your analysis.

FINANCIAL SUMMARY:
- Total Income: {format_currency(data_summary.get('total_income', 0))}
- Total Expenses: {format_currency(data_summary.get('total_expenses', 0))}
- Net Profit: {format_currency(data_summary.get('net_profit', 0))}
- Profit Margin: {format_percentage(data_summary.get('profit_margin', 0))}
- Date Range: {data_summary.get('start_date', 'N/A')} to {data_summary.get('end_date', 'N/A')}
- Largest Expense Category: {data_summary.get('top_expense_category', 'N/A')} ({format_percentage(data_summary.get('top_expense_pct', 0)/100)} of expenses)
- Largest Income Source: {data_summary.get('top_income_source', 'N/A')} ({format_percentage(data_summary.get('top_income_pct', 0)/100)} of income)
- Month-over-Month Change: {format_percentage(data_summary.get('mom_change', 0))}
{chart_section}{data_context_section}

Based on this data and the charts in the report, provide 4-5 specific, actionable insights. Your insights should:
1. Reference specific numbers and percentages from the data
2. Mention relevant charts when discussing trends (e.g., "The Income vs Expenses trend chart shows...")
3. Assess financial health and identify risks or opportunities
4. Provide concrete recommendations for cost optimization or revenue growth

Format each insight as a bullet point starting with "- ". Each insight should be 1-2 sentences and use professional financial language."""

    def _build_inventory_prompt(
        self,
        data_summary: Dict[str, Any],
        chart_descriptions: Optional[List[Dict[str, str]]] = None,
        raw_data_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build prompt for inventory insights."""
        # Build chart context section
        chart_section = ""
        if chart_descriptions:
            chart_section = "\n\nCharts Included in This Report:\n"
            for chart in chart_descriptions:
                chart_section += f"- {chart.get('title', 'Chart')}: {chart.get('description', '')}\n"

        # Build detailed data context section
        data_context_section = ""
        if raw_data_context:
            data_context_section = "\n\nDetailed Data Analysis:\n"
            if raw_data_context.get('reorder_alerts'):
                data_context_section += "Items Requiring Immediate Reorder:\n"
                for item in raw_data_context['reorder_alerts'][:5]:
                    data_context_section += f"  {item['product']}: {format_number(item['quantity'])} units (reorder level: {format_number(item['reorder_level'])})\n"
            if raw_data_context.get('category_stock'):
                data_context_section += "\nStock by Category:\n"
                for cat in raw_data_context['category_stock']:
                    data_context_section += f"  {cat['category']}: {format_number(cat['units'])} units, {format_currency(cat['value'])}\n"
            if raw_data_context.get('top_value_items'):
                data_context_section += "\nHighest Value Items:\n"
                for item in raw_data_context['top_value_items'][:5]:
                    data_context_section += f"  {item['product']}: {format_currency(item['value'])}\n"

        return f"""You are a senior supply chain analyst at a top-tier consulting firm (McKinsey, Bloomberg, Berkshire Capital). You are preparing executive-level insights for an inventory management report. Your analysis will be presented to the COO and Supply Chain leadership and must reflect the highest standards of operational consulting.

The report includes inventory metrics, stock status by category charts, reorder alert tables, and value distribution visualizations. Your insights must reference specific data points and charts to support your analysis.

INVENTORY SUMMARY:
- Total SKUs: {format_number(data_summary.get('total_skus', 0))}
- Total Units in Stock: {format_number(data_summary.get('total_units', 0))}
- Total Inventory Value: {format_currency(data_summary.get('total_value', 0))}
- Items Below Reorder Level: {format_number(data_summary.get('items_below_reorder', 0))}
- Average Stock Level: {format_number(data_summary.get('avg_stock_level', 0))} units per SKU
- Highest Value Category: {data_summary.get('top_value_category', 'N/A')} ({format_percentage(data_summary.get('top_value_pct', 0)/100)} of total value)
- Lowest Stock Category: {data_summary.get('lowest_stock_category', 'N/A')}
{chart_section}{data_context_section}

Based on this data and the charts in the report, provide 4-5 specific, actionable insights. Your insights should:
1. Reference specific numbers from the data
2. Mention relevant charts when discussing stock levels or distributions (e.g., "The Stock Status chart indicates...")
3. Highlight urgent reorder needs and stock risks
4. Provide concrete recommendations for inventory optimization

Format each insight as a bullet point starting with "- ". Each insight should be 1-2 sentences and use supply chain management language."""

    def _build_generic_prompt(
        self,
        data_summary: Dict[str, Any],
        chart_descriptions: Optional[List[Dict[str, str]]] = None,
        raw_data_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build a generic prompt for unknown template types."""
        summary_lines = []
        for key, value in data_summary.items():
            if isinstance(value, (int, float)):
                if 'pct' in key.lower() or 'percentage' in key.lower():
                    summary_lines.append(f"- {key}: {format_percentage(value)}")
                elif 'revenue' in key.lower() or 'cost' in key.lower() or 'amount' in key.lower():
                    summary_lines.append(f"- {key}: {format_currency(value)}")
                else:
                    summary_lines.append(f"- {key}: {format_number(value)}")
            else:
                summary_lines.append(f"- {key}: {value}")

        # Build chart context section
        chart_section = ""
        if chart_descriptions:
            chart_section = "\n\nCharts Included in This Report:\n"
            for chart in chart_descriptions:
                chart_section += f"- {chart.get('title', 'Chart')}: {chart.get('description', '')}\n"

        return f"""You are a senior analyst at a top-tier consulting firm (like McKinsey or Bloomberg). Analyze the following data and provide executive-level insights that would be appropriate for C-suite presentation.

Data Summary:
{chr(10).join(summary_lines)}
{chart_section}

Provide 4-5 insights in bullet point format starting with "- ". Your insights should:
1. Reference specific data points and percentages
2. Identify key patterns, risks, and opportunities
3. Provide strategic recommendations
4. Use precise, professional language

Each insight should be 1-2 sentences."""

    def _parse_insights(self, response_text: str, max_insights: int) -> List[str]:
        """Parse AI response into list of insights."""
        lines = response_text.strip().split('\n')
        insights = []

        for line in lines:
            line = line.strip()
            # Look for bullet points
            if line.startswith('- ') or line.startswith('• ') or line.startswith('* '):
                insight = line[2:].strip()
                if insight:
                    insights.append(insight)
            # Also handle numbered lists
            elif len(line) > 2 and line[0].isdigit() and line[1] in '.):':
                insight = line[2:].strip()
                if insight:
                    insights.append(insight)

        return insights[:max_insights]

    def _generate_basic_insights(
        self,
        data_summary: Dict[str, Any],
        template_type: str,
        max_insights: int,
    ) -> List[str]:
        """Generate basic statistical insights without AI."""
        generators = {
            "sales": self._generate_basic_sales_insights,
            "financial": self._generate_basic_financial_insights,
            "inventory": self._generate_basic_inventory_insights,
        }

        generator = generators.get(template_type, self._generate_generic_insights)
        return generator(data_summary)[:max_insights]

    def _generate_basic_sales_insights(self, data_summary: Dict[str, Any]) -> List[str]:
        """Generate professional sales insights with chart references."""
        insights = []

        total_revenue = data_summary.get('total_revenue', 0)
        transaction_count = data_summary.get('transaction_count', 0)
        avg_value = data_summary.get('avg_order_value', 0)
        top_product = data_summary.get('top_product')
        top_product_pct = data_summary.get('top_product_pct', 0)
        top_region = data_summary.get('top_region')
        top_region_pct = data_summary.get('top_region_pct', 0)
        trend = data_summary.get('trend_direction', 'stable')
        trend_pct = data_summary.get('trend_pct', 0)

        # Strategic revenue analysis with trend reference
        if total_revenue > 0 and trend != 'stable':
            trend_word = "growth" if trend == 'up' else "decline"
            trend_action = "capitalize on this momentum by expanding high-performing product lines" if trend == 'up' else "conduct root cause analysis and implement corrective measures"
            insights.append(
                f"As illustrated in the Revenue Trend chart, the business achieved {format_currency(total_revenue)} "
                f"in total revenue with a {format_percentage(abs(trend_pct))} {trend_word} trajectory. "
                f"Recommendation: {trend_action}."
            )
        elif total_revenue > 0:
            insights.append(
                f"The Revenue Trend chart shows {format_currency(total_revenue)} in total revenue across "
                f"{format_number(transaction_count)} transactions, yielding an average transaction value of "
                f"{format_currency(avg_value)}—a key metric for customer lifetime value optimization."
            )

        # Product concentration analysis with chart reference
        if top_product and top_product_pct > 0:
            concentration_risk = "high" if top_product_pct > 40 else "moderate" if top_product_pct > 25 else "healthy"
            if top_product_pct > 40:
                recommendation = "diversify revenue streams to mitigate single-product dependency risk"
            else:
                recommendation = "maintain product mix while exploring growth opportunities in secondary products"
            insights.append(
                f"The Product Performance chart reveals '{top_product}' commands {format_percentage(top_product_pct/100)} "
                f"of total revenue, indicating {concentration_risk} product concentration. "
                f"Strategic recommendation: {recommendation}."
            )

        # Regional performance analysis with chart reference
        if top_region and top_region_pct > 0:
            insights.append(
                f"Regional analysis depicted in the Revenue by Region chart identifies {top_region} as the "
                f"dominant market, contributing {format_percentage(top_region_pct/100)} of total revenue. "
                f"Consider replicating successful strategies from {top_region} across underperforming regions."
            )

        # Transaction efficiency analysis
        if avg_value > 0 and transaction_count > 0:
            insights.append(
                f"With an average order value of {format_currency(avg_value)} across {format_number(transaction_count)} "
                f"transactions, there is opportunity to implement upselling and cross-selling initiatives "
                f"to increase basket size by 15-20%."
            )

        # Growth opportunity synthesis
        if trend == 'up' and top_product:
            insights.append(
                f"The positive revenue trajectory combined with strong performance from '{top_product}' "
                f"suggests favorable market conditions. Recommend accelerating investment in marketing "
                f"and inventory to capture additional market share."
            )
        elif trend == 'down':
            insights.append(
                f"The declining revenue trend warrants immediate attention. Recommend conducting customer "
                f"churn analysis, competitive benchmarking, and pricing optimization review within the next 30 days."
            )

        return insights

    def _generate_basic_financial_insights(self, data_summary: Dict[str, Any]) -> List[str]:
        """Generate professional financial insights with chart references."""
        insights = []

        total_income = data_summary.get('total_income', 0)
        total_expenses = data_summary.get('total_expenses', 0)
        net_profit = data_summary.get('net_profit', 0)
        profit_margin = data_summary.get('profit_margin', 0)
        top_expense = data_summary.get('top_expense_category')
        top_expense_pct = data_summary.get('top_expense_pct', 0)
        top_income = data_summary.get('top_income_source')
        top_income_pct = data_summary.get('top_income_pct', 0)
        mom_change = data_summary.get('mom_change', 0)

        # Profitability analysis with margin context
        if net_profit > 0:
            margin_assessment = "strong" if profit_margin > 0.20 else "moderate" if profit_margin > 0.10 else "thin"
            margin_action = "reinvest in growth initiatives" if profit_margin > 0.20 else "focus on operational efficiency to expand margins"
            insights.append(
                f"The Monthly Income vs Expenses trend demonstrates healthy financial performance with "
                f"{format_currency(net_profit)} net profit and a {format_percentage(profit_margin)} margin—"
                f"considered {margin_assessment} for the industry. Recommendation: {margin_action}."
            )
        elif net_profit < 0:
            insights.append(
                f"Critical: The Income vs Expenses analysis reveals a net loss of {format_currency(abs(net_profit))}. "
                f"Immediate action required: implement cost reduction program targeting 15-20% expense reduction "
                f"while preserving revenue-generating activities."
            )

        # Expense structure analysis with chart reference
        if top_expense and top_expense_pct > 0:
            expense_ratio = total_expenses / total_income if total_income > 0 else 0
            risk_level = "elevated" if expense_ratio > 0.8 else "manageable" if expense_ratio > 0.6 else "healthy"
            insights.append(
                f"The Expense Breakdown chart identifies '{top_expense}' as the primary cost driver at "
                f"{format_percentage(top_expense_pct/100)} of total expenses. With an expense-to-income ratio "
                f"of {format_percentage(expense_ratio)} ({risk_level}), recommend conducting zero-based "
                f"budgeting review of {top_expense} to identify 10-15% cost optimization opportunities."
            )

        # Revenue concentration and diversification analysis
        if top_income and top_income_pct > 0:
            concentration_risk = "high dependency risk" if top_income_pct > 50 else "moderate concentration" if top_income_pct > 30 else "well-diversified"
            insights.append(
                f"The Income by Source visualization shows '{top_income}' contributing {format_percentage(top_income_pct/100)} "
                f"of total revenue, indicating {concentration_risk}. Strategic recommendation: develop secondary "
                f"revenue streams to reduce single-source dependency and improve business resilience."
            )

        # Period-over-period performance analysis
        if mom_change != 0:
            direction = "improvement" if mom_change > 0 else "deterioration"
            outlook = "positive momentum suggests opportunity for strategic investment" if mom_change > 0 else "corrective action required to reverse negative trajectory"
            insights.append(
                f"Period-over-period analysis indicates {format_percentage(abs(mom_change))} {direction} in "
                f"financial performance. Assessment: {outlook}. Recommend establishing monthly financial "
                f"review cadence to monitor key performance indicators."
            )

        # Cash flow and working capital recommendation
        if total_income > 0 and total_expenses > 0:
            insights.append(
                f"With {format_currency(total_income)} in income against {format_currency(total_expenses)} in expenses, "
                f"recommend maintaining 3-6 months of operating expenses as cash reserves and implementing "
                f"rolling 13-week cash flow forecasting for improved financial planning visibility."
            )

        return insights

    def _generate_basic_inventory_insights(self, data_summary: Dict[str, Any]) -> List[str]:
        """Generate professional inventory insights with chart references."""
        insights = []

        total_skus = data_summary.get('total_skus', 0)
        total_units = data_summary.get('total_units', 0)
        total_value = data_summary.get('total_value', 0)
        below_reorder = data_summary.get('items_below_reorder', 0)
        avg_stock = data_summary.get('avg_stock_level', 0)
        top_category = data_summary.get('top_value_category')
        top_category_pct = data_summary.get('top_value_pct', 0)
        low_category = data_summary.get('lowest_stock_category')

        # Inventory valuation and efficiency analysis
        if total_units > 0 and total_value > 0:
            avg_unit_value = total_value / total_units
            insights.append(
                f"The Stock Levels by Category chart shows {format_number(total_units)} units across "
                f"{format_number(total_skus)} SKUs, representing {format_currency(total_value)} in inventory value. "
                f"Average unit value of {format_currency(avg_unit_value)} suggests opportunity to optimize "
                f"working capital through strategic inventory reduction of slow-moving items."
            )

        # Critical reorder analysis with urgency assessment
        if below_reorder > 0:
            reorder_pct = (below_reorder / total_skus * 100) if total_skus > 0 else 0
            urgency = "CRITICAL" if reorder_pct > 20 else "HIGH PRIORITY" if reorder_pct > 10 else "ATTENTION REQUIRED"
            insights.append(
                f"{urgency}: The Reorder Alerts table identifies {format_number(below_reorder)} SKUs "
                f"({format_percentage(reorder_pct/100)} of portfolio) at or below safety stock levels. "
                f"Immediate procurement action required to prevent stockouts and lost sales. "
                f"Recommend expedited orders within 48-72 hours for critical items."
            )
        else:
            insights.append(
                f"Inventory health check: All {format_number(total_skus)} SKUs maintain stock levels above "
                f"reorder thresholds. This positions the business well for demand fulfillment. "
                f"Recommend quarterly review of reorder points to ensure alignment with demand patterns."
            )

        # Category concentration and value distribution analysis
        if top_category and top_category_pct > 0:
            concentration_assessment = "concentrated" if top_category_pct > 40 else "moderately distributed" if top_category_pct > 25 else "well-balanced"
            insights.append(
                f"The Inventory Value by Category visualization reveals '{top_category}' represents "
                f"{format_percentage(top_category_pct/100)} of total inventory value—a {concentration_assessment} "
                f"portfolio. Recommend implementing ABC analysis to optimize inventory investment allocation "
                f"and establish differentiated service levels by category."
            )

        # Low stock category risk assessment
        if low_category:
            insights.append(
                f"Category risk assessment: '{low_category}' exhibits lowest stock levels as shown in the "
                f"Stock Status chart. Evaluate demand forecasts and supplier lead times for this category. "
                f"If high-velocity items, recommend safety stock increase of 20-30% to mitigate stockout risk."
            )

        # Working capital and inventory turnover recommendation
        if total_value > 0 and avg_stock > 0:
            insights.append(
                f"With {format_currency(total_value)} in inventory capital deployed, recommend implementing "
                f"inventory turnover targets by category and establishing monthly slow-moving inventory "
                f"reviews to identify candidates for markdown, liquidation, or discontinuation."
            )

        return insights

    def _generate_generic_insights(self, data_summary: Dict[str, Any]) -> List[str]:
        """Generate generic insights for unknown template types."""
        insights = []

        # Find numeric values and generate basic insights
        for key, value in data_summary.items():
            if isinstance(value, (int, float)) and value != 0:
                if 'total' in key.lower():
                    insights.append(f"Total {key.replace('_', ' ')}: {format_number(value)}")
                elif 'pct' in key.lower() or 'percentage' in key.lower():
                    insights.append(f"{key.replace('_', ' ')}: {format_percentage(value)}")

            if len(insights) >= 5:
                break

        if not insights:
            insights.append("Data analysis completed. No significant patterns detected.")

        return insights

    def calculate_sales_summary(self, df: pd.DataFrame, mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Calculate summary metrics for sales data.

        Args:
            df: DataFrame with sales data
            mapping: Column mapping from template

        Returns:
            Dictionary of summary metrics
        """
        summary = {}

        date_col = mapping.get('date')
        revenue_col = mapping.get('revenue')
        quantity_col = mapping.get('quantity')
        product_col = mapping.get('product')
        region_col = mapping.get('region')

        # Basic metrics
        if revenue_col and revenue_col in df.columns:
            summary['total_revenue'] = df[revenue_col].sum()
            summary['avg_order_value'] = df[revenue_col].mean()

        if quantity_col and quantity_col in df.columns:
            summary['total_units'] = df[quantity_col].sum()

        summary['transaction_count'] = len(df)

        # Date range
        if date_col and date_col in df.columns:
            dates = pd.to_datetime(df[date_col], errors='coerce')
            summary['start_date'] = dates.min().strftime('%Y-%m-%d') if dates.notna().any() else 'N/A'
            summary['end_date'] = dates.max().strftime('%Y-%m-%d') if dates.notna().any() else 'N/A'

            # Calculate trend
            if revenue_col and len(df) > 1:
                df_sorted = df.sort_values(date_col)
                mid_point = len(df_sorted) // 2
                first_half = df_sorted.iloc[:mid_point][revenue_col].sum()
                second_half = df_sorted.iloc[mid_point:][revenue_col].sum()

                if first_half > 0:
                    change = (second_half - first_half) / first_half
                    summary['trend_direction'] = get_trend_direction(second_half, first_half)
                    summary['trend_pct'] = change
                else:
                    summary['trend_direction'] = 'stable'
                    summary['trend_pct'] = 0

        # Top product
        if product_col and revenue_col and product_col in df.columns:
            product_revenue = df.groupby(product_col)[revenue_col].sum()
            top_product = product_revenue.idxmax()
            summary['top_product'] = top_product
            summary['top_product_pct'] = (product_revenue[top_product] / product_revenue.sum()) * 100

        # Top region
        if region_col and revenue_col and region_col in df.columns:
            region_revenue = df.groupby(region_col)[revenue_col].sum()
            top_region = region_revenue.idxmax()
            summary['top_region'] = top_region
            summary['top_region_pct'] = (region_revenue[top_region] / region_revenue.sum()) * 100

        return summary

    def calculate_financial_summary(self, df: pd.DataFrame, mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Calculate summary metrics for financial data.

        Args:
            df: DataFrame with financial data
            mapping: Column mapping from template

        Returns:
            Dictionary of summary metrics
        """
        summary = {}

        date_col = mapping.get('date')
        amount_col = mapping.get('amount')
        type_col = mapping.get('transaction_type')
        category_col = mapping.get('category')

        if amount_col and type_col and amount_col in df.columns and type_col in df.columns:
            # Normalize type column
            df_copy = df.copy()
            df_copy[type_col] = df_copy[type_col].str.lower()

            income_mask = df_copy[type_col].str.contains('income', na=False)
            expense_mask = df_copy[type_col].str.contains('expense', na=False)

            summary['total_income'] = df_copy.loc[income_mask, amount_col].sum()
            summary['total_expenses'] = df_copy.loc[expense_mask, amount_col].sum()
            summary['net_profit'] = summary['total_income'] - summary['total_expenses']

            if summary['total_income'] > 0:
                summary['profit_margin'] = summary['net_profit'] / summary['total_income']
            else:
                summary['profit_margin'] = 0

            # Top expense category
            if category_col and category_col in df.columns:
                expense_by_cat = df_copy.loc[expense_mask].groupby(category_col)[amount_col].sum()
                if len(expense_by_cat) > 0:
                    top_expense = expense_by_cat.idxmax()
                    summary['top_expense_category'] = top_expense
                    summary['top_expense_pct'] = (expense_by_cat[top_expense] / expense_by_cat.sum()) * 100

                income_by_cat = df_copy.loc[income_mask].groupby(category_col)[amount_col].sum()
                if len(income_by_cat) > 0:
                    top_income = income_by_cat.idxmax()
                    summary['top_income_source'] = top_income
                    summary['top_income_pct'] = (income_by_cat[top_income] / income_by_cat.sum()) * 100

        # Date range
        if date_col and date_col in df.columns:
            dates = pd.to_datetime(df[date_col], errors='coerce')
            summary['start_date'] = dates.min().strftime('%Y-%m-%d') if dates.notna().any() else 'N/A'
            summary['end_date'] = dates.max().strftime('%Y-%m-%d') if dates.notna().any() else 'N/A'

        return summary

    def calculate_inventory_summary(self, df: pd.DataFrame, mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Calculate summary metrics for inventory data.

        Args:
            df: DataFrame with inventory data
            mapping: Column mapping from template

        Returns:
            Dictionary of summary metrics
        """
        summary = {}

        product_col = mapping.get('product')
        category_col = mapping.get('category')
        quantity_col = mapping.get('quantity')
        reorder_col = mapping.get('reorder_level')
        cost_col = mapping.get('unit_cost')

        summary['total_skus'] = len(df)

        if quantity_col and quantity_col in df.columns:
            summary['total_units'] = df[quantity_col].sum()
            summary['avg_stock_level'] = df[quantity_col].mean()

        # Calculate total value
        if quantity_col and cost_col and quantity_col in df.columns and cost_col in df.columns:
            df_copy = df.copy()
            df_copy['_value'] = df_copy[quantity_col] * df_copy[cost_col]
            summary['total_value'] = df_copy['_value'].sum()

            # Top value category
            if category_col and category_col in df.columns:
                value_by_cat = df_copy.groupby(category_col)['_value'].sum()
                if len(value_by_cat) > 0:
                    top_cat = value_by_cat.idxmax()
                    summary['top_value_category'] = top_cat
                    summary['top_value_pct'] = (value_by_cat[top_cat] / value_by_cat.sum()) * 100

        # Items below reorder level
        if quantity_col and reorder_col and quantity_col in df.columns and reorder_col in df.columns:
            below_reorder = df[df[quantity_col] <= df[reorder_col]]
            summary['items_below_reorder'] = len(below_reorder)

            # Lowest stock category
            if category_col and category_col in df.columns:
                stock_by_cat = df.groupby(category_col)[quantity_col].sum()
                if len(stock_by_cat) > 0:
                    summary['lowest_stock_category'] = stock_by_cat.idxmin()

        return summary
