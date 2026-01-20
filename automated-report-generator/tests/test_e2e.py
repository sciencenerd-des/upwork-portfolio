"""
End-to-End Tests for the Automated Report Generator.

Tests the complete workflow from data loading to report generation
for all three template types.
"""

import pytest
import os
import sys
from pathlib import Path
import tempfile
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_processor import DataProcessor
from src.chart_generator import ChartGenerator
from src.report_builder import ReportBuilder
from src.ai_insights import AIInsights
from templates import get_template, TEMPLATES


class TestEndToEndSalesReport:
    """End-to-end tests for sales report generation."""

    @pytest.fixture
    def sales_data_path(self):
        """Get path to sales sample data."""
        return Path(__file__).parent.parent / "sample_data" / "sales_sample.csv"

    @pytest.fixture
    def output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    def test_full_sales_report_pdf(self, sales_data_path, output_dir):
        """Test complete PDF report generation for sales data."""
        assert sales_data_path.exists(), f"Sample data not found: {sales_data_path}"

        template = get_template("sales")()
        result = template.generate(
            data_source=str(sales_data_path),
            output_dir=str(output_dir),
            formats=["pdf"],
            include_ai_insights=False,  # Skip AI to avoid API calls
        )

        assert "pdf" in result
        assert Path(result["pdf"]).exists()
        assert Path(result["pdf"]).stat().st_size > 1000  # Should be a real PDF

    def test_full_sales_report_docx(self, sales_data_path, output_dir):
        """Test complete Word report generation for sales data."""
        template = get_template("sales")()
        result = template.generate(
            data_source=str(sales_data_path),
            output_dir=str(output_dir),
            formats=["docx"],
            include_ai_insights=False,
        )

        assert "docx" in result
        assert Path(result["docx"]).exists()
        assert Path(result["docx"]).stat().st_size > 1000

    def test_full_sales_report_both_formats(self, sales_data_path, output_dir):
        """Test generating both PDF and Word formats."""
        template = get_template("sales")()
        result = template.generate(
            data_source=str(sales_data_path),
            output_dir=str(output_dir),
            formats=["pdf", "docx"],
            include_ai_insights=False,
        )

        assert "pdf" in result
        assert "docx" in result
        assert Path(result["pdf"]).exists()
        assert Path(result["docx"]).exists()

    def test_sales_report_with_dataframe(self, sales_data_path, output_dir):
        """Test report generation from DataFrame input."""
        df = pd.read_csv(sales_data_path)

        template = get_template("sales")()
        result = template.generate(
            data_source=df,
            output_dir=str(output_dir),
            formats=["pdf"],
            include_ai_insights=False,
        )

        assert "pdf" in result
        assert Path(result["pdf"]).exists()

    def test_sales_report_custom_mapping(self, sales_data_path, output_dir):
        """Test report with custom column mapping."""
        template = get_template("sales")()
        custom_mapping = {
            "date": "Date",
            "product": "Product",
            "category": "Category",
            "quantity": "Quantity",
            "revenue": "Revenue",
            "region": "Region",
        }

        result = template.generate(
            data_source=str(sales_data_path),
            output_dir=str(output_dir),
            formats=["pdf"],
            include_ai_insights=False,
            column_mapping=custom_mapping,
        )

        assert "pdf" in result
        assert Path(result["pdf"]).exists()


class TestEndToEndFinancialReport:
    """End-to-end tests for financial report generation."""

    @pytest.fixture
    def financial_data_path(self):
        """Get path to financial sample data."""
        return Path(__file__).parent.parent / "sample_data" / "financial_sample.csv"

    @pytest.fixture
    def output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    def test_full_financial_report_pdf(self, financial_data_path, output_dir):
        """Test complete PDF report generation for financial data."""
        assert financial_data_path.exists()

        template = get_template("financial")()
        result = template.generate(
            data_source=str(financial_data_path),
            output_dir=str(output_dir),
            formats=["pdf"],
            include_ai_insights=False,
        )

        assert "pdf" in result
        assert Path(result["pdf"]).exists()
        assert Path(result["pdf"]).stat().st_size > 1000

    def test_full_financial_report_docx(self, financial_data_path, output_dir):
        """Test complete Word report generation for financial data."""
        template = get_template("financial")()
        result = template.generate(
            data_source=str(financial_data_path),
            output_dir=str(output_dir),
            formats=["docx"],
            include_ai_insights=False,
        )

        assert "docx" in result
        assert Path(result["docx"]).exists()

    def test_financial_report_both_formats(self, financial_data_path, output_dir):
        """Test generating both formats for financial report."""
        template = get_template("financial")()
        result = template.generate(
            data_source=str(financial_data_path),
            output_dir=str(output_dir),
            formats=["pdf", "docx"],
            include_ai_insights=False,
        )

        assert len(result) == 2
        for fmt, path in result.items():
            assert Path(path).exists()


class TestEndToEndInventoryReport:
    """End-to-end tests for inventory report generation."""

    @pytest.fixture
    def inventory_data_path(self):
        """Get path to inventory sample data."""
        return Path(__file__).parent.parent / "sample_data" / "inventory_sample.csv"

    @pytest.fixture
    def output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    def test_full_inventory_report_pdf(self, inventory_data_path, output_dir):
        """Test complete PDF report generation for inventory data."""
        assert inventory_data_path.exists()

        template = get_template("inventory")()
        result = template.generate(
            data_source=str(inventory_data_path),
            output_dir=str(output_dir),
            formats=["pdf"],
            include_ai_insights=False,
        )

        assert "pdf" in result
        assert Path(result["pdf"]).exists()
        assert Path(result["pdf"]).stat().st_size > 1000

    def test_full_inventory_report_docx(self, inventory_data_path, output_dir):
        """Test complete Word report generation for inventory data."""
        template = get_template("inventory")()
        result = template.generate(
            data_source=str(inventory_data_path),
            output_dir=str(output_dir),
            formats=["docx"],
            include_ai_insights=False,
        )

        assert "docx" in result
        assert Path(result["docx"]).exists()

    def test_inventory_report_both_formats(self, inventory_data_path, output_dir):
        """Test generating both formats for inventory report."""
        template = get_template("inventory")()
        result = template.generate(
            data_source=str(inventory_data_path),
            output_dir=str(output_dir),
            formats=["pdf", "docx"],
            include_ai_insights=False,
        )

        assert len(result) == 2
        for fmt, path in result.items():
            assert Path(path).exists()


class TestDataProcessorIntegration:
    """Integration tests for data processor with templates."""

    @pytest.fixture
    def sample_data_dir(self):
        """Get sample data directory."""
        return Path(__file__).parent.parent / "sample_data"

    def test_sales_data_auto_mapping(self, sample_data_dir):
        """Test auto column mapping for sales data."""
        processor = DataProcessor()
        processor.load_file(str(sample_data_dir / "sales_sample.csv"))
        processor.set_template("sales")
        processor.auto_map_columns()

        # Validate
        is_valid, errors, warnings = processor.validate_mapping()
        assert is_valid, f"Validation failed: {errors}"

        # Check key mappings
        assert "date" in processor.column_mapping
        assert "revenue" in processor.column_mapping

    def test_financial_data_auto_mapping(self, sample_data_dir):
        """Test auto column mapping for financial data."""
        processor = DataProcessor()
        processor.load_file(str(sample_data_dir / "financial_sample.csv"))
        processor.set_template("financial")
        processor.auto_map_columns()

        is_valid, errors, warnings = processor.validate_mapping()
        assert is_valid, f"Validation failed: {errors}"

        assert "date" in processor.column_mapping
        assert "amount" in processor.column_mapping
        assert "transaction_type" in processor.column_mapping

    def test_inventory_data_auto_mapping(self, sample_data_dir):
        """Test auto column mapping for inventory data."""
        processor = DataProcessor()
        processor.load_file(str(sample_data_dir / "inventory_sample.csv"))
        processor.set_template("inventory")
        processor.auto_map_columns()

        is_valid, errors, warnings = processor.validate_mapping()
        assert is_valid, f"Validation failed: {errors}"

        assert "product" in processor.column_mapping
        assert "quantity" in processor.column_mapping


class TestChartGeneratorIntegration:
    """Integration tests for chart generator with real data."""

    @pytest.fixture
    def sales_df(self):
        """Load sales sample data."""
        path = Path(__file__).parent.parent / "sample_data" / "sales_sample.csv"
        return pd.read_csv(path)

    def test_revenue_trend_chart(self, sales_df):
        """Test generating revenue trend chart from sales data."""
        chart_gen = ChartGenerator()

        # Convert date column
        sales_df['Date'] = pd.to_datetime(sales_df['Date'])

        fig = chart_gen.create_trend_chart_with_aggregation(
            sales_df,
            date_column='Date',
            value_column='Revenue',
            title='Revenue Trend',
            period='auto',
        )

        assert fig is not None

        # Convert to bytes
        chart_bytes = chart_gen.figure_to_bytes(fig)
        assert len(chart_bytes) > 1000

    def test_product_performance_chart(self, sales_df):
        """Test generating product performance bar chart."""
        chart_gen = ChartGenerator()

        fig = chart_gen.create_bar_chart(
            sales_df,
            category_column='Product',
            value_column='Revenue',
            title='Top Products',
            limit=10,
        )

        assert fig is not None

    def test_regional_pie_chart(self, sales_df):
        """Test generating regional breakdown pie chart."""
        chart_gen = ChartGenerator()

        fig = chart_gen.create_pie_chart(
            sales_df,
            category_column='Region',
            value_column='Revenue',
            title='Revenue by Region',
        )

        assert fig is not None


class TestReportBuilderIntegration:
    """Integration tests for report builder with real content."""

    @pytest.fixture
    def output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    @pytest.fixture
    def sample_sections(self):
        """Create sample report sections."""
        return [
            {
                "type": "summary",
                "title": "Executive Summary",
                "metrics": [
                    {"label": "Total Revenue", "value": "$125,432"},
                    {"label": "Total Units", "value": "1,234"},
                    {"label": "Avg Order Value", "value": "$101.65"},
                    {"label": "Growth Rate", "value": "+15.3%"},
                ],
            },
            {
                "type": "text",
                "title": "Overview",
                "text": "This report provides a comprehensive analysis of sales performance.",
            },
            {
                "type": "table",
                "title": "Top Products",
                "dataframe": pd.DataFrame({
                    "Product": ["Widget A", "Widget B", "Widget C"],
                    "Revenue": [5000, 4000, 3000],
                    "Quantity": [100, 80, 60],
                }),
            },
            {
                "type": "insights",
                "title": "Key Insights",
                "insights": [
                    "Sales increased by 15% compared to previous period.",
                    "Widget A remains the best-selling product.",
                    "Regional expansion contributed to growth.",
                ],
            },
        ]

    def test_build_pdf_report(self, output_dir, sample_sections):
        """Test building a complete PDF report."""
        builder = ReportBuilder()
        result = builder.build_report(
            output_dir=str(output_dir),
            title="Sales Report",
            sections=sample_sections,
            template_name="sales",
            formats=["pdf"],
        )

        assert "pdf" in result
        assert Path(result["pdf"]).exists()
        assert Path(result["pdf"]).stat().st_size > 1000

    def test_build_docx_report(self, output_dir, sample_sections):
        """Test building a complete Word report."""
        builder = ReportBuilder()
        result = builder.build_report(
            output_dir=str(output_dir),
            title="Sales Report",
            sections=sample_sections,
            template_name="sales",
            formats=["docx"],
        )

        assert "docx" in result
        assert Path(result["docx"]).exists()


class TestAIInsightsIntegration:
    """Integration tests for AI insights generation."""

    @pytest.fixture
    def sales_df(self):
        """Load sales sample data."""
        path = Path(__file__).parent.parent / "sample_data" / "sales_sample.csv"
        return pd.read_csv(path)

    def test_sales_summary_calculation(self, sales_df):
        """Test calculating sales summary for AI."""
        ai = AIInsights()
        mapping = {
            "date": "Date",
            "product": "Product",
            "category": "Category",
            "quantity": "Quantity",
            "revenue": "Revenue",
            "region": "Region",
        }

        summary = ai.calculate_sales_summary(sales_df, mapping)

        assert "total_revenue" in summary
        assert summary["total_revenue"] > 0
        # Check for top product info
        assert "top_product" in summary or "top_products" in summary

    def test_basic_insights_generation(self, sales_df):
        """Test generating basic insights without AI."""
        ai = AIInsights()
        mapping = {
            "date": "Date",
            "revenue": "Revenue",
            "quantity": "Quantity",
        }

        summary = ai.calculate_sales_summary(sales_df, mapping)
        insights = ai.generate_insights(
            summary,
            template_type="sales",
            max_insights=5,
            use_ai=False,  # Use basic generation
        )

        assert len(insights) > 0
        assert all(isinstance(i, str) for i in insights)


class TestTemplateRegistry:
    """Test template registry functionality."""

    def test_get_all_templates(self):
        """Test getting all available templates."""
        assert "sales" in TEMPLATES
        assert "financial" in TEMPLATES
        assert "inventory" in TEMPLATES

    def test_get_template_by_name(self):
        """Test getting template class by name."""
        sales_template = get_template("sales")
        assert sales_template.__name__ == "SalesReportTemplate"

        financial_template = get_template("financial")
        assert financial_template.__name__ == "FinancialReportTemplate"

        inventory_template = get_template("inventory")
        assert inventory_template.__name__ == "InventoryReportTemplate"

    def test_invalid_template_raises_error(self):
        """Test that invalid template name raises KeyError."""
        with pytest.raises(KeyError):
            get_template("nonexistent")


class TestPerformance:
    """Performance tests to ensure reports generate within time limits."""

    @pytest.fixture
    def large_sales_df(self):
        """Create a larger sales DataFrame for performance testing."""
        import numpy as np
        np.random.seed(42)

        n = 5000  # 5000 rows
        dates = pd.date_range(start='2024-01-01', periods=365, freq='D')

        df = pd.DataFrame({
            'Date': np.random.choice(dates, n),
            'Product': np.random.choice([f'Product {i}' for i in range(20)], n),
            'Category': np.random.choice(['Electronics', 'Clothing', 'Food', 'Home'], n),
            'Quantity': np.random.randint(1, 50, n),
            'Revenue': np.random.uniform(10, 500, n).round(2),
            'Region': np.random.choice(['North', 'South', 'East', 'West'], n),
        })
        return df

    @pytest.fixture
    def output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    def test_large_dataset_performance(self, large_sales_df, output_dir):
        """Test that report generation completes within 30 seconds for 5000 rows."""
        import time

        template = get_template("sales")()

        start_time = time.time()
        result = template.generate(
            data_source=large_sales_df,
            output_dir=str(output_dir),
            formats=["pdf"],
            include_ai_insights=False,
        )
        elapsed_time = time.time() - start_time

        assert elapsed_time < 30, f"Report generation took {elapsed_time:.1f}s (> 30s limit)"
        assert Path(result["pdf"]).exists()
