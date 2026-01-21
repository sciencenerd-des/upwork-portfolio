"""
Comprehensive tests for report templates.
Covers optional sections, missing columns, edge cases, and insight toggles.
"""

import sys
import tempfile
from pathlib import Path
import pandas as pd
import numpy as np
import pytest
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from templates.sales_report import SalesReportTemplate
from templates.financial_report import FinancialReportTemplate
from templates.inventory_report import InventoryReportTemplate
from templates import get_template, TEMPLATES


class TestSalesReportTemplate:
    """Comprehensive tests for SalesReportTemplate."""

    @pytest.fixture
    def template(self):
        """Create template instance."""
        return SalesReportTemplate()

    @pytest.fixture
    def minimal_sales_data(self):
        """Create minimal sales DataFrame with only required columns."""
        return pd.DataFrame({
            "Date": pd.date_range("2024-01-01", periods=10, freq="D"),
            "Product": ["Product A"] * 5 + ["Product B"] * 5,
            "Revenue": np.random.uniform(100, 1000, 10),
        })

    @pytest.fixture
    def full_sales_data(self):
        """Create full sales DataFrame with all columns."""
        return pd.DataFrame({
            "Date": pd.date_range("2024-01-01", periods=20, freq="D"),
            "Product": ["Product A"] * 10 + ["Product B"] * 10,
            "Category": ["Electronics"] * 10 + ["Furniture"] * 10,
            "Quantity": np.random.randint(1, 50, 20),
            "Revenue": np.random.uniform(100, 1000, 20),
            "Region": np.random.choice(["North", "South", "East", "West"], 20),
        })

    @pytest.fixture
    def output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    def test_generate_with_minimal_data(self, template, minimal_sales_data, output_dir):
        """Test generation with minimal required columns."""
        result = template.generate(
            data_source=minimal_sales_data,
            output_dir=str(output_dir),
            formats=["pdf"],
            include_ai_insights=False,
        )

        assert "pdf" in result
        assert Path(result["pdf"]).exists()

    def test_generate_with_full_data(self, template, full_sales_data, output_dir):
        """Test generation with all columns."""
        result = template.generate(
            data_source=full_sales_data,
            output_dir=str(output_dir),
            formats=["pdf", "docx"],
            include_ai_insights=False,
        )

        assert "pdf" in result
        assert "docx" in result

    def test_generate_without_region(self, template, output_dir):
        """Test that regional breakdown is skipped when region column missing."""
        data = pd.DataFrame({
            "Date": pd.date_range("2024-01-01", periods=10, freq="D"),
            "Product": ["Product A"] * 5 + ["Product B"] * 5,
            "Revenue": np.random.uniform(100, 1000, 10),
        })

        result = template.generate(
            data_source=data,
            output_dir=str(output_dir),
            formats=["pdf"],
            include_ai_insights=False,
        )

        assert "pdf" in result

    def test_generate_with_insights_disabled(self, template, minimal_sales_data, output_dir):
        """Test generation with AI insights disabled."""
        result = template.generate(
            data_source=minimal_sales_data,
            output_dir=str(output_dir),
            formats=["pdf"],
            include_ai_insights=False,
        )

        assert Path(result["pdf"]).exists()

    def test_generate_with_custom_mapping(self, template, output_dir):
        """Test generation with custom column mapping."""
        data = pd.DataFrame({
            "sale_date": pd.date_range("2024-01-01", periods=10, freq="D"),
            "item": ["Item A"] * 5 + ["Item B"] * 5,
            "sales_amount": np.random.uniform(100, 1000, 10),
        })

        mapping = {
            "date": "sale_date",
            "product": "item",
            "revenue": "sales_amount",
        }

        result = template.generate(
            data_source=data,
            output_dir=str(output_dir),
            formats=["pdf"],
            include_ai_insights=False,
            column_mapping=mapping,
        )

        assert "pdf" in result

    def test_build_summary_section(self, template, full_sales_data):
        """Test building summary section."""
        template.processor.df = full_sales_data
        template.processor.set_template("sales")
        template.processor.auto_map_columns()
        df = template.processor.process_data()
        mapping = template.processor.column_mapping

        summary = template._build_summary_section(df, mapping)

        assert summary["type"] == "summary"
        assert summary["title"] == "Executive Summary"
        assert len(summary["metrics"]) >= 3

    def test_build_revenue_trend_missing_columns(self, template):
        """Test revenue trend returns None when columns missing."""
        df = pd.DataFrame({"Other": [1, 2, 3]})
        mapping = {}

        result = template._build_revenue_trend(df, mapping)
        assert result is None

    def test_build_product_performance_missing_columns(self, template):
        """Test product performance returns None when columns missing."""
        df = pd.DataFrame({"Other": [1, 2, 3]})
        mapping = {}

        result = template._build_product_performance(df, mapping)
        assert result is None

    def test_build_regional_breakdown_missing_columns(self, template):
        """Test regional breakdown returns None when columns missing."""
        df = pd.DataFrame({"Other": [1, 2, 3]})
        mapping = {}

        result = template._build_regional_breakdown(df, mapping)
        assert result is None


class TestFinancialReportTemplate:
    """Comprehensive tests for FinancialReportTemplate."""

    @pytest.fixture
    def template(self):
        """Create template instance."""
        return FinancialReportTemplate()

    @pytest.fixture
    def minimal_financial_data(self):
        """Create minimal financial DataFrame."""
        return pd.DataFrame({
            "Date": pd.date_range("2024-01-01", periods=20, freq="D"),
            "Category": ["Salary"] * 5 + ["Utilities"] * 5 + ["Sales"] * 5 + ["Rent"] * 5,
            "Amount": [5000] * 5 + [100] * 5 + [2000] * 5 + [1000] * 5,
            "Type": ["Income"] * 5 + ["Expense"] * 5 + ["Income"] * 5 + ["Expense"] * 5,
        })

    @pytest.fixture
    def output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    def test_generate_with_minimal_data(self, template, minimal_financial_data, output_dir):
        """Test generation with minimal required columns."""
        result = template.generate(
            data_source=minimal_financial_data,
            output_dir=str(output_dir),
            formats=["pdf"],
            include_ai_insights=False,
        )

        assert "pdf" in result
        assert Path(result["pdf"]).exists()

    def test_generate_both_formats(self, template, minimal_financial_data, output_dir):
        """Test generating both PDF and DOCX."""
        result = template.generate(
            data_source=minimal_financial_data,
            output_dir=str(output_dir),
            formats=["pdf", "docx"],
            include_ai_insights=False,
        )

        assert "pdf" in result
        assert "docx" in result

    def test_build_summary_with_loss(self, template):
        """Test summary section with net loss scenario."""
        data = pd.DataFrame({
            "Date": pd.date_range("2024-01-01", periods=10, freq="D"),
            "Category": ["Rent"] * 5 + ["Sales"] * 5,
            "Amount": [5000] * 5 + [1000] * 5,  # Expenses > Income
            "Type": ["Expense"] * 5 + ["Income"] * 5,
        })

        template.processor.df = data
        template.processor.set_template("financial")
        template.processor.auto_map_columns()
        df = template.processor.process_data()
        mapping = template.processor.column_mapping

        summary = template._build_summary_section(df, mapping)

        # Should include negative net profit
        assert summary["type"] == "summary"
        assert len(summary["metrics"]) >= 3

    def test_build_monthly_trend_missing_columns(self, template):
        """Test monthly trend returns None when columns missing."""
        df = pd.DataFrame({"Other": [1, 2, 3]})
        mapping = {}

        result = template._build_monthly_trend(df, mapping)
        assert result is None

    def test_build_expense_breakdown_no_expenses(self, template):
        """Test expense breakdown with no expense records."""
        data = pd.DataFrame({
            "Date": pd.date_range("2024-01-01", periods=5, freq="D"),
            "Category": ["Sales"] * 5,
            "Amount": [1000] * 5,
            "Type": ["Income"] * 5,  # No expenses
        })

        template.processor.df = data
        template.processor.set_template("financial")
        template.processor.auto_map_columns()
        df = template.processor.process_data()
        mapping = template.processor.column_mapping

        result = template._build_expense_breakdown(df, mapping)
        assert result is None

    def test_build_income_sources_no_income(self, template):
        """Test income sources with no income records."""
        data = pd.DataFrame({
            "Date": pd.date_range("2024-01-01", periods=5, freq="D"),
            "Category": ["Rent"] * 5,
            "Amount": [1000] * 5,
            "Type": ["Expense"] * 5,  # No income
        })

        template.processor.df = data
        template.processor.set_template("financial")
        template.processor.auto_map_columns()
        df = template.processor.process_data()
        mapping = template.processor.column_mapping

        result = template._build_income_sources(df, mapping)
        assert result is None


class TestInventoryReportTemplate:
    """Comprehensive tests for InventoryReportTemplate."""

    @pytest.fixture
    def template(self):
        """Create template instance."""
        return InventoryReportTemplate()

    @pytest.fixture
    def minimal_inventory_data(self):
        """Create minimal inventory DataFrame."""
        return pd.DataFrame({
            "Product": [f"Product {i}" for i in range(10)],
            "Quantity": np.random.randint(10, 100, 10),
            "Reorder_Level": [20] * 10,
            "Unit_Cost": np.random.uniform(10, 100, 10),
        })

    @pytest.fixture
    def inventory_with_alerts(self):
        """Create inventory data with reorder alerts."""
        return pd.DataFrame({
            "Product": [f"Product {i}" for i in range(10)],
            "Category": ["Electronics"] * 5 + ["Furniture"] * 5,
            "Quantity": [5, 10, 15, 100, 200, 3, 8, 150, 200, 250],  # Some below reorder
            "Reorder_Level": [20] * 10,
            "Unit_Cost": np.random.uniform(10, 100, 10),
        })

    @pytest.fixture
    def output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    def test_generate_with_minimal_data(self, template, minimal_inventory_data, output_dir):
        """Test generation with minimal required columns."""
        result = template.generate(
            data_source=minimal_inventory_data,
            output_dir=str(output_dir),
            formats=["pdf"],
            include_ai_insights=False,
        )

        assert "pdf" in result

    def test_generate_with_alerts(self, template, inventory_with_alerts, output_dir):
        """Test generation with reorder alerts."""
        result = template.generate(
            data_source=inventory_with_alerts,
            output_dir=str(output_dir),
            formats=["pdf"],
            include_ai_insights=False,
        )

        assert "pdf" in result

    def test_build_reorder_alerts_none_below(self, template):
        """Test reorder alerts when all items above threshold."""
        data = pd.DataFrame({
            "Product": [f"Product {i}" for i in range(5)],
            "Quantity": [100, 200, 300, 400, 500],  # All above reorder
            "Reorder_Level": [20] * 5,
            "Unit_Cost": [10] * 5,
        })

        template.processor.df = data
        template.processor.set_template("inventory")
        template.processor.auto_map_columns()
        df = template.processor.process_data()
        mapping = template.processor.column_mapping

        result = template._build_reorder_alerts(df, mapping)

        # Should return text section when no alerts
        assert result is not None
        assert result["type"] == "text"
        assert "No reorder alerts" in result["text"]

    def test_build_reorder_alerts_with_alerts(self, template, inventory_with_alerts):
        """Test reorder alerts when items below threshold."""
        template.processor.df = inventory_with_alerts
        template.processor.set_template("inventory")
        template.processor.auto_map_columns()
        df = template.processor.process_data()
        mapping = template.processor.column_mapping

        result = template._build_reorder_alerts(df, mapping)

        # Should return table section with alerts
        assert result is not None
        assert result["type"] == "table"
        assert "Shortage" in result["dataframe"].columns

    def test_build_stock_status_missing_columns(self, template):
        """Test stock status returns None when columns missing."""
        df = pd.DataFrame({"Other": [1, 2, 3]})
        mapping = {}

        result = template._build_stock_status(df, mapping)
        assert result is None

    def test_build_value_distribution_missing_columns(self, template):
        """Test value distribution returns None when columns missing."""
        df = pd.DataFrame({"Other": [1, 2, 3]})
        mapping = {}

        result = template._build_value_distribution(df, mapping)
        assert result is None

    def test_build_summary_all_metrics(self, template, inventory_with_alerts):
        """Test that summary includes all expected metrics."""
        template.processor.df = inventory_with_alerts
        template.processor.set_template("inventory")
        template.processor.auto_map_columns()
        df = template.processor.process_data()
        mapping = template.processor.column_mapping

        summary = template._build_summary_section(df, mapping)

        assert summary["type"] == "summary"
        assert len(summary["metrics"]) >= 3
        
        metric_labels = [m["label"] for m in summary["metrics"]]
        assert "Total SKUs" in metric_labels


class TestTemplateRegistry:
    """Tests for the template registry."""

    def test_get_sales_template(self):
        """Test getting sales template."""
        template_class = get_template("sales")
        assert template_class.__name__ == "SalesReportTemplate"

    def test_get_financial_template(self):
        """Test getting financial template."""
        template_class = get_template("financial")
        assert template_class.__name__ == "FinancialReportTemplate"

    def test_get_inventory_template(self):
        """Test getting inventory template."""
        template_class = get_template("inventory")
        assert template_class.__name__ == "InventoryReportTemplate"

    def test_get_invalid_template(self):
        """Test getting invalid template raises error."""
        with pytest.raises(KeyError):
            get_template("nonexistent")

    def test_templates_dict_contents(self):
        """Test TEMPLATES dictionary has all expected keys."""
        assert "sales" in TEMPLATES
        assert "financial" in TEMPLATES
        assert "inventory" in TEMPLATES


class TestTemplateEdgeCases:
    """Tests for edge cases in template generation."""

    @pytest.fixture
    def output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    def test_single_row_data(self, output_dir):
        """Test template with single row of data."""
        template = SalesReportTemplate()
        data = pd.DataFrame({
            "Date": [datetime.now()],
            "Product": ["Only Product"],
            "Revenue": [1000.0],
        })

        result = template.generate(
            data_source=data,
            output_dir=str(output_dir),
            formats=["pdf"],
            include_ai_insights=False,
        )

        assert "pdf" in result

    def test_large_dataset(self, output_dir):
        """Test template with larger dataset."""
        template = SalesReportTemplate()
        n = 1000

        data = pd.DataFrame({
            "Date": pd.date_range("2024-01-01", periods=n, freq="H"),
            "Product": np.random.choice([f"Product {i}" for i in range(20)], n),
            "Revenue": np.random.uniform(10, 1000, n),
            "Quantity": np.random.randint(1, 100, n),
            "Region": np.random.choice(["North", "South", "East", "West"], n),
        })

        result = template.generate(
            data_source=data,
            output_dir=str(output_dir),
            formats=["pdf"],
            include_ai_insights=False,
        )

        assert "pdf" in result

    def test_data_with_nulls(self, output_dir):
        """Test template with null values in data."""
        template = SalesReportTemplate()

        data = pd.DataFrame({
            "Date": pd.date_range("2024-01-01", periods=10, freq="D"),
            "Product": ["A", "B", None, "D", "E", "F", None, "H", "I", "J"],
            "Revenue": [100, None, 300, 400, None, 600, 700, 800, None, 1000],
        })

        result = template.generate(
            data_source=data,
            output_dir=str(output_dir),
            formats=["pdf"],
            include_ai_insights=False,
        )

        assert "pdf" in result

    def test_zero_values(self, output_dir):
        """Test template with zero values."""
        template = FinancialReportTemplate()

        data = pd.DataFrame({
            "Date": pd.date_range("2024-01-01", periods=10, freq="D"),
            "Category": ["Sales"] * 5 + ["Rent"] * 5,
            "Amount": [0, 0, 0, 0, 0, 100, 200, 300, 400, 500],  # Some zeros
            "Type": ["Income"] * 5 + ["Expense"] * 5,
        })

        result = template.generate(
            data_source=data,
            output_dir=str(output_dir),
            formats=["pdf"],
            include_ai_insights=False,
        )

        assert "pdf" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
