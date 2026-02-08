"""Additional branch-heavy tests to increase functional coverage."""

from __future__ import annotations

import builtins
import io
import sys
import types
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import src
from src.ai_insights import AIInsights
from src.data_processor import DataProcessor, DataValidationError
from templates.financial_report import FinancialReportTemplate
from templates.inventory_report import InventoryReportTemplate
from templates.sales_report import SalesReportTemplate


def _sales_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]),
            "Product": ["A", "B", "A", "C"],
            "Category": ["X", "Y", "X", "Z"],
            "Quantity": [10, 5, 12, 7],
            "Revenue": [100.0, 0.0, 220.0, 120.0],
            "Region": ["North", "South", "North", "East"],
        }
    )


def _financial_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": pd.to_datetime(["2024-01-01", "2024-01-15", "2024-02-01", "2024-02-20"]),
            "Category": ["Services", "Rent", "Consulting", "Utilities"],
            "Amount": [5000.0, 1200.0, 5500.0, 1000.0],
            "Type": ["Income", "Expense", "Income", "Expense"],
        }
    )


def _inventory_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Product": ["Widget A", "Widget B", "Widget C"],
            "Category": ["Hardware", "Hardware", "Software"],
            "Quantity": [5, 40, 8],
            "Reorder_Level": [10, 20, 8],
            "Unit_Cost": [25.0, 10.0, 80.0],
        }
    )


class TestSourcePackageLazyExports:
    @pytest.mark.parametrize(
        "name",
        [
            "DataProcessor",
            "ChartGenerator",
            "ReportBuilder",
            "AIInsights",
            "load_config",
            "format_currency",
            "format_number",
            "format_percentage",
        ],
    )
    def test_lazy_exports_available(self, name):
        assert getattr(src, name) is not None

    def test_unknown_attribute_raises(self):
        with pytest.raises(AttributeError):
            getattr(src, "DOES_NOT_EXIST")


class TestDataProcessorBranchCoverage:
    def test_load_file_requires_filename_for_buffer(self):
        processor = DataProcessor()
        with pytest.raises(DataValidationError):
            processor.load_file(io.BytesIO(b"a,b\n1,2"))

    def test_load_file_excel_sheet_and_error_paths(self):
        processor = DataProcessor()

        expected = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            expected.to_excel(writer, index=False, sheet_name="Sheet2")
        buffer.seek(0)

        loaded = processor.load_file(buffer, file_name="test.xlsx", sheet_name="Sheet2")
        assert len(loaded) == 2

        with pytest.raises(DataValidationError):
            processor.load_file(io.BytesIO(b"not an excel file"), file_name="broken.xlsx")

    def test_load_file_row_limit_and_empty_validation(self):
        processor = DataProcessor()
        processor._settings["max_rows"] = 1

        with pytest.raises(DataValidationError):
            processor.load_file(io.BytesIO(b"a,b\n1,2\n3,4"), file_name="too_many.csv")

        processor._settings["max_rows"] = 100
        with pytest.raises(DataValidationError):
            processor.load_file(io.BytesIO(b"a,b\n"), file_name="empty.csv")

    def test_load_multiple_input_validation_and_read_errors(self):
        processor = DataProcessor()

        with pytest.raises(DataValidationError):
            processor.load_multiple_files([io.BytesIO(b"a,b\n1,2"), io.BytesIO(b"a,b\n3,4")])

        with pytest.raises(DataValidationError):
            processor.load_multiple_files(
                [io.BytesIO(b"a,b\n1,2"), io.BytesIO(b"a,b\n3,4")],
                file_names=["good.csv", "bad.txt"],
            )

        with pytest.raises(DataValidationError):
            processor.load_multiple_files(
                [io.BytesIO(b"a,b\n1,2"), io.BytesIO(b"not excel")],
                file_names=["good.csv", "bad.xlsx"],
            )

    def test_load_multiple_empty_mismatch_and_max_rows(self):
        processor = DataProcessor()

        with pytest.raises(DataValidationError):
            processor.load_multiple_files(
                [io.BytesIO(b"a,b\n"), io.BytesIO(b"a,b\n")],
                file_names=["empty1.csv", "empty2.csv"],
            )
        assert len(processor.validation_warnings) == 2

        merged = processor.load_multiple_files(
            [io.BytesIO(b"a,b\n1,2"), io.BytesIO(b"a,c\n3,4")],
            file_names=["left.csv", "right.csv"],
        )
        assert len(merged) == 2
        assert any("different columns" in warning for warning in processor.validation_warnings)

        processor._settings["max_rows"] = 1
        with pytest.raises(DataValidationError):
            processor.load_multiple_files(
                [io.BytesIO(b"a,b\n1,2"), io.BytesIO(b"a,b\n3,4")],
                file_names=["a.csv", "b.csv"],
            )

    def test_get_excel_sheets_error_branch(self):
        processor = DataProcessor()
        with pytest.raises(DataValidationError):
            processor.get_excel_sheets(io.BytesIO(b"bad excel"))

    def test_precondition_errors(self):
        processor = DataProcessor()

        with pytest.raises(DataValidationError):
            processor.detect_column_types()
        with pytest.raises(DataValidationError):
            processor.suggest_template()
        with pytest.raises(DataValidationError):
            processor.auto_map_columns()
        assert processor.validate_mapping()[0] is False
        with pytest.raises(DataValidationError):
            processor.process_data()
        with pytest.raises(DataValidationError):
            processor.get_preview()
        with pytest.raises(DataValidationError):
            processor.get_column_stats("x")
        with pytest.raises(DataValidationError):
            processor.get_summary_stats()
        with pytest.raises(DataValidationError):
            processor.get_mapped_data()
        with pytest.raises(DataValidationError):
            processor.fill_missing_values("drop")

    def test_process_data_conversion_warning_path(self, monkeypatch):
        processor = DataProcessor()
        processor.df = pd.DataFrame({"amount": [1, 2, 3]})
        processor.template_config = {"required_columns": {"amount": {"type": "numeric"}}, "optional_columns": {}}
        processor.column_mapping = {"amount": "amount"}

        def raise_clean(_):
            raise ValueError("cannot parse")

        monkeypatch.setattr("src.data_processor.clean_numeric_value", raise_clean)

        processed = processor.process_data()
        assert len(processed) == 3
        assert any("Could not convert column" in warning for warning in processor.validation_warnings)

    def test_stats_branches_and_date_range_variants(self):
        processor = DataProcessor()
        processor.df = pd.DataFrame(
            {
                "num": [1.0, 2.0, 3.0],
                "date": pd.to_datetime(["2024-01-01", "2024-01-03", "2024-01-05"]),
                "cat": ["x", "x", "y"],
            }
        )

        date_stats = processor.get_column_stats("date")
        cat_stats = processor.get_column_stats("cat")
        assert "range_days" in date_stats
        assert "top_values" in cat_stats

        with pytest.raises(DataValidationError):
            processor.get_column_stats("missing")

        processor.column_mapping = {}
        assert processor.get_date_range() == (None, None)

        processor.column_mapping = {"date": "date"}
        start, end = processor.get_date_range()
        assert start is not None and end is not None

        processor.df["date"] = ["bad", "date", "values"]
        assert processor.get_date_range() == (None, None)

    def test_fill_missing_mean_and_forward(self):
        processor = DataProcessor()
        processor.df = pd.DataFrame({"num": [1.0, None, 3.0], "label": [None, "A", None]})

        mean_df = processor.fill_missing_values("mean")
        assert mean_df["num"].isna().sum() == 0

        processor.df = pd.DataFrame({"num": [1.0, None, 3.0], "label": [None, "A", None]})
        forward_df = processor.fill_missing_values("forward")
        assert forward_df.iloc[2]["label"] == "A"


class _FakeCompletions:
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail

    def create(self, **kwargs):
        if self.should_fail:
            raise RuntimeError("api failure")
        return types.SimpleNamespace(
            choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="- one\n2. two\n* three"))]
        )


class _FakeClient:
    def __init__(self, should_fail: bool = False):
        self.chat = types.SimpleNamespace(completions=_FakeCompletions(should_fail=should_fail))


class TestAIInsightsBranchCoverage:
    def test_initialization_success_import_error_and_generic_error_paths(self):
        fake_openai = types.SimpleNamespace(OpenAI=lambda **kwargs: _FakeClient())
        with patch.dict(sys.modules, {"openai": fake_openai}):
            ai = AIInsights(api_key="key", model="model-x")
            assert ai.is_available is True

        original_import = builtins.__import__

        def import_with_openai_error(name, *args, **kwargs):
            if name == "openai":
                raise ImportError("simulated import error")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=import_with_openai_error):
            ai = AIInsights(api_key="key")
            assert ai.is_available is False

        bad_openai = types.SimpleNamespace()  # No OpenAI attribute -> generic exception branch
        with patch.dict(sys.modules, {"openai": bad_openai}):
            ai = AIInsights(api_key="key")
            assert ai.is_available is False

    def test_generate_insights_ai_success_failure_and_unavailable(self):
        ai = AIInsights(api_key=None)
        ai._client = _FakeClient()
        ai._model = "model-x"

        success = ai.generate_insights({"total_revenue": 1000}, "sales", max_insights=3, use_ai=True)
        assert success == ["one", "two", "three"]
        assert ai.fallback_used is False

        ai._client = _FakeClient(should_fail=True)
        # Use different input to bypass cache and exercise failure fallback branch.
        fallback = ai.generate_insights({"total_revenue": 1001}, "sales", max_insights=3, use_ai=True)
        assert len(fallback) > 0
        assert ai.fallback_used is True
        assert "api failure" in ai.last_error

        ai._client = None
        unavailable = ai.generate_insights({"kpi": 42}, "unknown", max_insights=2, use_ai=True)
        assert len(unavailable) > 0
        assert ai.fallback_used is True
        assert "not available" in ai.last_error.lower()

    def test_prompt_builders_with_context(self):
        ai = AIInsights(api_key=None)

        sales_prompt = ai._build_sales_prompt(
            {"total_revenue": 1234, "trend_pct": 0.15},
            chart_descriptions=[{"title": "Revenue Trend", "description": "line"}],
            raw_data_context={
                "top_products": [{"name": "A", "revenue": 500}],
                "monthly_trend": [{"period": "2024-01", "revenue": 800}],
                "regional_breakdown": [{"name": "North", "revenue": 600, "pct": 60}],
            },
        )
        assert "Top 5 Products by Revenue" in sales_prompt
        assert "Charts Included in This Report" in sales_prompt

        financial_prompt = ai._build_financial_prompt(
            {"total_income": 2000, "total_expenses": 1500},
            chart_descriptions=[{"title": "Expense Breakdown", "description": "pie"}],
            raw_data_context={
                "expense_breakdown": [{"category": "Rent", "amount": 1000, "pct": 50}],
                "income_sources": [{"category": "Sales", "amount": 2000, "pct": 100}],
                "monthly_comparison": [{"period": "2024-01", "income": 2000, "expenses": 1500}],
            },
        )
        assert "Expense Breakdown by Category" in financial_prompt
        assert "Monthly Income vs Expenses" in financial_prompt

        inventory_prompt = ai._build_inventory_prompt(
            {"total_skus": 10, "total_value": 1000},
            chart_descriptions=[{"title": "Stock Levels", "description": "bar"}],
            raw_data_context={
                "reorder_alerts": [{"product": "P1", "quantity": 2, "reorder_level": 10}],
                "category_stock": [{"category": "Hardware", "units": 5, "value": 500}],
                "top_value_items": [{"product": "P1", "value": 400}],
            },
        )
        assert "Items Requiring Immediate Reorder" in inventory_prompt
        assert "Highest Value Items" in inventory_prompt

        generic_prompt = ai._build_generic_prompt(
            {"total_revenue": 100, "profit_pct": 0.2, "label": "ok"},
            chart_descriptions=[{"title": "Overview", "description": "summary"}],
        )
        assert "Data Summary" in generic_prompt
        assert "Charts Included in This Report" in generic_prompt

    def test_parse_and_generic_generation_branches(self):
        ai = AIInsights(api_key=None)
        parsed = ai._parse_insights("- bullet\n1. number\n2) alt\n3: colon\n* star", max_insights=5)
        assert len(parsed) == 5

        many = ai._generate_generic_insights(
            {
                "total_a": 1,
                "total_b": 2,
                "total_c": 3,
                "total_d": 4,
                "total_e": 5,
                "total_f": 6,
                "growth_pct": 0.12,
            }
        )
        assert len(many) == 5

        empty = ai._generate_generic_insights({"name": "x", "zero": 0})
        assert empty == ["Data analysis completed. No significant patterns detected."]

    def test_summary_edge_cases(self):
        ai = AIInsights(api_key=None)

        sales_df = pd.DataFrame({"Date": ["2024-01-01", "2024-01-02"], "Revenue": [0, 100], "Product": ["A", "B"], "Region": ["N", "S"]})
        sales_summary = ai.calculate_sales_summary(
            sales_df,
            {"date": "Date", "revenue": "Revenue", "product": "Product", "region": "Region"},
        )
        assert sales_summary["trend_direction"] == "stable"
        assert sales_summary["trend_pct"] == 0

        financial_df = pd.DataFrame(
            {
                "Date": ["2024-01-01", "2024-01-02"],
                "Amount": [500, 700],
                "Type": ["Expense", "Expense"],
                "Category": ["Rent", "Utilities"],
            }
        )
        financial_summary = ai.calculate_financial_summary(
            financial_df,
            {"date": "Date", "amount": "Amount", "transaction_type": "Type", "category": "Category"},
        )
        assert financial_summary["profit_margin"] == 0


class _FallbackAI:
    def __init__(self):
        self.is_available = False
        self.fallback_used = True
        self.last_error = "simulated api outage"

    def calculate_sales_summary(self, *args, **kwargs):
        return {"total_revenue": 1000}

    def calculate_financial_summary(self, *args, **kwargs):
        return {"total_income": 1000}

    def calculate_inventory_summary(self, *args, **kwargs):
        return {"total_skus": 10}

    def generate_insights(self, *args, **kwargs):
        return ["Fallback insight"]


class TestTemplateInsightAndErrorBranches:
    def test_sales_insights_section_fallback_note(self):
        template = SalesReportTemplate()
        template.ai_insights = _FallbackAI()
        df = _sales_df()
        mapping = {
            "date": "Date",
            "product": "Product",
            "category": "Category",
            "quantity": "Quantity",
            "revenue": "Revenue",
            "region": "Region",
        }

        section = template._build_insights_section(df, mapping)

        assert section["title"] == "Statistical Insights"
        assert "fallback_note" in section
        assert section["error_detail"] == "simulated api outage"

    def test_financial_insights_section_fallback_note(self):
        template = FinancialReportTemplate()
        template.ai_insights = _FallbackAI()
        df = _financial_df()
        mapping = {
            "date": "Date",
            "category": "Category",
            "amount": "Amount",
            "transaction_type": "Type",
        }

        section = template._build_insights_section(df, mapping)

        assert section["title"] == "Statistical Insights"
        assert "fallback_note" in section
        assert section["error_detail"] == "simulated api outage"

    def test_inventory_insights_section_fallback_note(self):
        template = InventoryReportTemplate()
        template.ai_insights = _FallbackAI()
        df = _inventory_df()
        mapping = {
            "product": "Product",
            "category": "Category",
            "quantity": "Quantity",
            "reorder_level": "Reorder_Level",
            "unit_cost": "Unit_Cost",
        }

        section = template._build_insights_section(df, mapping)

        assert section["title"] == "Statistical Insights"
        assert "fallback_note" in section
        assert section["error_detail"] == "simulated api outage"

    @pytest.mark.parametrize(
        "template_cls,data",
        [
            (SalesReportTemplate, _sales_df()),
            (FinancialReportTemplate, _financial_df()),
            (InventoryReportTemplate, _inventory_df()),
        ],
    )
    def test_generate_raises_on_invalid_mapping(self, template_cls, data, tmp_path):
        template = template_cls()
        template.processor.validate_mapping = MagicMock(return_value=(False, ["missing required mapping"], []))

        with pytest.raises(ValueError):
            template.generate(
                data_source=data,
                output_dir=str(tmp_path),
                formats=["pdf"],
                include_ai_insights=False,
            )

    def test_chart_exception_paths_return_none(self):
        sales = SalesReportTemplate()
        sales.chart_gen.create_trend_chart_with_aggregation = MagicMock(side_effect=RuntimeError("boom"))
        assert (
            sales._build_revenue_trend(
                _sales_df(),
                {"date": "Date", "revenue": "Revenue"},
            )
            is None
        )

        financial = FinancialReportTemplate()
        financial.chart_gen.create_line_chart = MagicMock(side_effect=RuntimeError("boom"))
        assert (
            financial._build_monthly_trend(
                _financial_df(),
                {"date": "Date", "amount": "Amount", "transaction_type": "Type"},
            )
            is None
        )

        inventory = InventoryReportTemplate()
        inventory.chart_gen.create_bar_chart = MagicMock(side_effect=RuntimeError("boom"))
        assert (
            inventory._build_stock_status(
                _inventory_df(),
                {"category": "Category", "quantity": "Quantity"},
            )
            is None
        )
