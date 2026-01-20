"""
Tests for the AIInsights module.
"""

import sys
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai_insights import AIInsights, AIInsightsError
from src.data_processor import DataProcessor


class TestAIInsightsSetup:
    """Tests for AI insights initialization."""

    def test_initialization_without_api_key(self):
        """Test AIInsights initializes without API key."""
        insights = AIInsights()

        assert insights is not None
        # Without API key, AI insights won't be available
        # (unless ANTHROPIC_API_KEY env var is set)

    def test_is_available_property(self):
        """Test is_available property."""
        insights = AIInsights(api_key=None)

        # Should be False without valid API key
        assert isinstance(insights.is_available, bool)


class TestBasicSalesInsights:
    """Tests for basic sales insights generation."""

    def setup_method(self):
        """Setup for each test."""
        self.insights = AIInsights()

        self.sales_summary = {
            'total_revenue': 250000,
            'total_units': 5000,
            'transaction_count': 500,
            'avg_order_value': 500,
            'start_date': '2024-01-01',
            'end_date': '2024-03-15',
            'top_product': 'Laptop Pro 15',
            'top_product_pct': 35,
            'top_region': 'North',
            'top_region_pct': 28,
            'trend_direction': 'up',
            'trend_pct': 0.15,
        }

    def test_generate_basic_sales_insights(self):
        """Test generating basic sales insights."""
        insights = self.insights.generate_insights(
            self.sales_summary,
            template_type='sales',
            use_ai=False
        )

        assert isinstance(insights, list)
        assert len(insights) > 0
        assert len(insights) <= 5

    def test_insights_contain_relevant_info(self):
        """Test that insights contain relevant information."""
        insights = self.insights.generate_insights(
            self.sales_summary,
            template_type='sales',
            use_ai=False
        )

        # Join all insights to check content
        all_text = ' '.join(insights).lower()

        # Should mention revenue or performance
        assert 'revenue' in all_text or 'sales' in all_text or 'performance' in all_text

    def test_upward_trend_insight(self):
        """Test that upward trend is mentioned."""
        insights = self.insights.generate_insights(
            self.sales_summary,
            template_type='sales',
            use_ai=False
        )

        all_text = ' '.join(insights).lower()
        assert 'up' in all_text or 'growth' in all_text or 'increase' in all_text

    def test_downward_trend_insight(self):
        """Test that downward trend generates appropriate insight."""
        summary = self.sales_summary.copy()
        summary['trend_direction'] = 'down'
        summary['trend_pct'] = -0.10

        insights = self.insights.generate_insights(
            summary,
            template_type='sales',
            use_ai=False
        )

        all_text = ' '.join(insights).lower()
        assert 'down' in all_text or 'declin' in all_text or 'investigat' in all_text


class TestBasicFinancialInsights:
    """Tests for basic financial insights generation."""

    def setup_method(self):
        """Setup for each test."""
        self.insights = AIInsights()

        self.financial_summary = {
            'total_income': 500000,
            'total_expenses': 350000,
            'net_profit': 150000,
            'profit_margin': 0.30,
            'start_date': '2024-01-01',
            'end_date': '2024-03-15',
            'top_expense_category': 'Salaries',
            'top_expense_pct': 45,
            'top_income_source': 'Product Sales',
            'top_income_pct': 80,
            'mom_change': 0.05,
        }

    def test_generate_basic_financial_insights(self):
        """Test generating basic financial insights."""
        insights = self.insights.generate_insights(
            self.financial_summary,
            template_type='financial',
            use_ai=False
        )

        assert isinstance(insights, list)
        assert len(insights) > 0
        assert len(insights) <= 5

    def test_profit_insight(self):
        """Test that profit information is included."""
        insights = self.insights.generate_insights(
            self.financial_summary,
            template_type='financial',
            use_ai=False
        )

        all_text = ' '.join(insights).lower()
        assert 'profit' in all_text or 'margin' in all_text

    def test_loss_insight(self):
        """Test insight generation for loss scenario."""
        summary = self.financial_summary.copy()
        summary['net_profit'] = -50000
        summary['total_expenses'] = 550000

        insights = self.insights.generate_insights(
            summary,
            template_type='financial',
            use_ai=False
        )

        all_text = ' '.join(insights).lower()
        assert 'loss' in all_text or 'cost' in all_text or 'reduction' in all_text


class TestBasicInventoryInsights:
    """Tests for basic inventory insights generation."""

    def setup_method(self):
        """Setup for each test."""
        self.insights = AIInsights()

        self.inventory_summary = {
            'total_skus': 150,
            'total_units': 12000,
            'total_value': 450000,
            'items_below_reorder': 8,
            'avg_stock_level': 80,
            'top_value_category': 'Electronics',
            'top_value_pct': 55,
            'lowest_stock_category': 'Furniture',
        }

    def test_generate_basic_inventory_insights(self):
        """Test generating basic inventory insights."""
        insights = self.insights.generate_insights(
            self.inventory_summary,
            template_type='inventory',
            use_ai=False
        )

        assert isinstance(insights, list)
        assert len(insights) > 0
        assert len(insights) <= 5

    def test_reorder_alert_insight(self):
        """Test that reorder alert is mentioned when items below level."""
        insights = self.insights.generate_insights(
            self.inventory_summary,
            template_type='inventory',
            use_ai=False
        )

        all_text = ' '.join(insights).lower()
        assert 'reorder' in all_text or 'alert' in all_text or 'below' in all_text

    def test_healthy_inventory_insight(self):
        """Test insight when all items above reorder level."""
        summary = self.inventory_summary.copy()
        summary['items_below_reorder'] = 0

        insights = self.insights.generate_insights(
            summary,
            template_type='inventory',
            use_ai=False
        )

        all_text = ' '.join(insights).lower()
        assert 'healthy' in all_text or 'above' in all_text or 'all items' in all_text


class TestSummaryCalculations:
    """Tests for data summary calculations."""

    def setup_method(self):
        """Setup for each test."""
        self.insights = AIInsights()
        self.processor = DataProcessor()
        self.sample_data_dir = Path(__file__).parent.parent / "sample_data"

    def test_calculate_sales_summary(self):
        """Test calculating sales summary from data."""
        df = self.processor.load_file(self.sample_data_dir / "sales_sample.csv")
        self.processor.set_template("sales")
        mapping = self.processor.auto_map_columns()
        df = self.processor.process_data()

        summary = self.insights.calculate_sales_summary(df, mapping)

        assert 'total_revenue' in summary
        assert summary['total_revenue'] > 0
        assert 'total_units' in summary
        assert 'transaction_count' in summary
        assert 'top_product' in summary

    def test_calculate_financial_summary(self):
        """Test calculating financial summary from data."""
        df = self.processor.load_file(self.sample_data_dir / "financial_sample.csv")
        self.processor.set_template("financial")
        mapping = self.processor.auto_map_columns()
        df = self.processor.process_data()

        summary = self.insights.calculate_financial_summary(df, mapping)

        assert 'total_income' in summary
        assert summary['total_income'] > 0
        assert 'total_expenses' in summary
        assert 'net_profit' in summary
        assert 'profit_margin' in summary

    def test_calculate_inventory_summary(self):
        """Test calculating inventory summary from data."""
        df = self.processor.load_file(self.sample_data_dir / "inventory_sample.csv")
        self.processor.set_template("inventory")
        mapping = self.processor.auto_map_columns()
        df = self.processor.process_data()

        summary = self.insights.calculate_inventory_summary(df, mapping)

        assert 'total_skus' in summary
        assert summary['total_skus'] > 0
        assert 'total_units' in summary
        assert 'total_value' in summary
        assert 'items_below_reorder' in summary


class TestInsightLimits:
    """Tests for insight count limits."""

    def setup_method(self):
        """Setup for each test."""
        self.insights = AIInsights()

        self.sample_summary = {
            'total_revenue': 100000,
            'total_units': 1000,
            'transaction_count': 100,
            'avg_order_value': 1000,
            'top_product': 'Product A',
            'top_product_pct': 30,
        }

    def test_max_insights_limit(self):
        """Test that max_insights parameter is respected."""
        for max_count in [1, 2, 3, 5]:
            insights = self.insights.generate_insights(
                self.sample_summary,
                template_type='sales',
                max_insights=max_count,
                use_ai=False
            )

            assert len(insights) <= max_count


class TestGenericInsights:
    """Tests for generic insight generation."""

    def setup_method(self):
        """Setup for each test."""
        self.insights = AIInsights()

    def test_unknown_template_type(self):
        """Test insight generation for unknown template type."""
        summary = {
            'total_value': 50000,
            'count': 100,
            'percentage': 0.25,
        }

        insights = self.insights.generate_insights(
            summary,
            template_type='unknown',
            use_ai=False
        )

        assert isinstance(insights, list)
        assert len(insights) > 0


class TestEndToEndInsights:
    """End-to-end tests for insight generation."""

    def setup_method(self):
        """Setup for each test."""
        self.insights = AIInsights()
        self.processor = DataProcessor()
        self.sample_data_dir = Path(__file__).parent.parent / "sample_data"

    def test_full_sales_pipeline(self):
        """Test full pipeline: load data -> calculate summary -> generate insights."""
        # Load and process data
        df = self.processor.load_file(self.sample_data_dir / "sales_sample.csv")
        self.processor.set_template("sales")
        mapping = self.processor.auto_map_columns()
        df = self.processor.process_data()

        # Calculate summary
        summary = self.insights.calculate_sales_summary(df, mapping)

        # Generate insights
        insights_list = self.insights.generate_insights(
            summary,
            template_type='sales',
            use_ai=False
        )

        assert len(insights_list) > 0
        # Insights should be meaningful strings
        for insight in insights_list:
            assert isinstance(insight, str)
            assert len(insight) > 10

    def test_full_financial_pipeline(self):
        """Test full pipeline for financial data."""
        df = self.processor.load_file(self.sample_data_dir / "financial_sample.csv")
        self.processor.set_template("financial")
        mapping = self.processor.auto_map_columns()
        df = self.processor.process_data()

        summary = self.insights.calculate_financial_summary(df, mapping)
        insights_list = self.insights.generate_insights(
            summary,
            template_type='financial',
            use_ai=False
        )

        assert len(insights_list) > 0

    def test_full_inventory_pipeline(self):
        """Test full pipeline for inventory data."""
        df = self.processor.load_file(self.sample_data_dir / "inventory_sample.csv")
        self.processor.set_template("inventory")
        mapping = self.processor.auto_map_columns()
        df = self.processor.process_data()

        summary = self.insights.calculate_inventory_summary(df, mapping)
        insights_list = self.insights.generate_insights(
            summary,
            template_type='inventory',
            use_ai=False
        )

        assert len(insights_list) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
