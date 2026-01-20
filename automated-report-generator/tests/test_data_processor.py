"""
Tests for the DataProcessor module.
"""

import sys
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_processor import DataProcessor, DataValidationError


class TestDataProcessorLoading:
    """Tests for data loading functionality."""

    def setup_method(self):
        """Setup for each test."""
        self.processor = DataProcessor()
        self.sample_data_dir = Path(__file__).parent.parent / "sample_data"

    def test_load_sales_csv(self):
        """Test loading sales sample CSV."""
        df = self.processor.load_file(self.sample_data_dir / "sales_sample.csv")

        assert df is not None
        assert len(df) > 0
        assert "Date" in df.columns
        assert "Product" in df.columns
        assert "Revenue" in df.columns

    def test_load_financial_csv(self):
        """Test loading financial sample CSV."""
        df = self.processor.load_file(self.sample_data_dir / "financial_sample.csv")

        assert df is not None
        assert len(df) > 0
        assert "Category" in df.columns
        assert "Amount" in df.columns
        assert "Type" in df.columns

    def test_load_inventory_csv(self):
        """Test loading inventory sample CSV."""
        df = self.processor.load_file(self.sample_data_dir / "inventory_sample.csv")

        assert df is not None
        assert len(df) > 0
        assert "Product" in df.columns
        assert "Quantity" in df.columns
        assert "Unit_Cost" in df.columns

    def test_load_invalid_format(self):
        """Test loading unsupported file format."""
        with pytest.raises(DataValidationError) as exc_info:
            self.processor.load_file("test.txt", file_name="test.txt")

        assert "Unsupported file format" in str(exc_info.value)


class TestDataProcessorColumnTypes:
    """Tests for column type detection."""

    def setup_method(self):
        """Setup for each test."""
        self.processor = DataProcessor()
        self.sample_data_dir = Path(__file__).parent.parent / "sample_data"

    def test_detect_column_types_sales(self):
        """Test column type detection for sales data."""
        self.processor.load_file(self.sample_data_dir / "sales_sample.csv")
        types = self.processor.detect_column_types()

        assert types["Date"] == "datetime"
        assert types["Revenue"] == "numeric"
        assert types["Quantity"] == "numeric"
        assert types["Product"] == "string"

    def test_detect_column_types_financial(self):
        """Test column type detection for financial data."""
        self.processor.load_file(self.sample_data_dir / "financial_sample.csv")
        types = self.processor.detect_column_types()

        assert types["Date"] == "datetime"
        assert types["Amount"] == "numeric"
        assert types["Category"] == "string"


class TestDataProcessorTemplates:
    """Tests for template functionality."""

    def setup_method(self):
        """Setup for each test."""
        self.processor = DataProcessor()
        self.sample_data_dir = Path(__file__).parent.parent / "sample_data"

    def test_suggest_template_sales(self):
        """Test template suggestion for sales data."""
        self.processor.load_file(self.sample_data_dir / "sales_sample.csv")
        template, confidence = self.processor.suggest_template()

        assert template == "sales"
        assert confidence > 0.5

    def test_suggest_template_financial(self):
        """Test template suggestion for financial data."""
        self.processor.load_file(self.sample_data_dir / "financial_sample.csv")
        template, confidence = self.processor.suggest_template()

        assert template == "financial"
        assert confidence > 0.5

    def test_suggest_template_inventory(self):
        """Test template suggestion for inventory data."""
        self.processor.load_file(self.sample_data_dir / "inventory_sample.csv")
        template, confidence = self.processor.suggest_template()

        assert template == "inventory"
        assert confidence > 0.5

    def test_set_template(self):
        """Test setting template."""
        self.processor.set_template("sales")

        assert self.processor.template_config is not None
        assert "required_columns" in self.processor.template_config

    def test_set_invalid_template(self):
        """Test setting invalid template."""
        with pytest.raises(DataValidationError) as exc_info:
            self.processor.set_template("nonexistent")

        assert "not found" in str(exc_info.value)


class TestDataProcessorMapping:
    """Tests for column mapping functionality."""

    def setup_method(self):
        """Setup for each test."""
        self.processor = DataProcessor()
        self.sample_data_dir = Path(__file__).parent.parent / "sample_data"

    def test_auto_map_columns_sales(self):
        """Test automatic column mapping for sales data."""
        self.processor.load_file(self.sample_data_dir / "sales_sample.csv")
        self.processor.set_template("sales")
        mapping = self.processor.auto_map_columns()

        assert mapping["date"] == "Date"
        assert mapping["product"] == "Product"
        assert mapping["quantity"] == "Quantity"
        assert mapping["revenue"] == "Revenue"
        assert mapping["region"] == "Region"
        assert mapping["category"] == "Category"

    def test_auto_map_columns_financial(self):
        """Test automatic column mapping for financial data."""
        self.processor.load_file(self.sample_data_dir / "financial_sample.csv")
        self.processor.set_template("financial")
        mapping = self.processor.auto_map_columns()

        assert mapping["date"] == "Date"
        assert mapping["category"] == "Category"
        assert mapping["amount"] == "Amount"
        assert mapping["transaction_type"] == "Type"

    def test_validate_mapping_valid(self):
        """Test validation of valid mapping."""
        self.processor.load_file(self.sample_data_dir / "sales_sample.csv")
        self.processor.set_template("sales")
        self.processor.auto_map_columns()

        is_valid, errors, warnings = self.processor.validate_mapping()

        assert is_valid
        assert len(errors) == 0

    def test_validate_mapping_missing_required(self):
        """Test validation with missing required fields."""
        self.processor.load_file(self.sample_data_dir / "sales_sample.csv")
        self.processor.set_template("sales")
        self.processor.column_mapping = {"date": "Date"}  # Missing other required fields

        is_valid, errors, warnings = self.processor.validate_mapping()

        assert not is_valid
        assert len(errors) > 0


class TestDataProcessorProcessing:
    """Tests for data processing functionality."""

    def setup_method(self):
        """Setup for each test."""
        self.processor = DataProcessor()
        self.sample_data_dir = Path(__file__).parent.parent / "sample_data"

    def test_process_data_sales(self):
        """Test processing sales data."""
        self.processor.load_file(self.sample_data_dir / "sales_sample.csv")
        self.processor.set_template("sales")
        self.processor.auto_map_columns()

        df = self.processor.process_data()

        assert df is not None
        # Check date column is datetime
        assert pd.api.types.is_datetime64_any_dtype(df["Date"])
        # Check numeric columns are numeric
        assert pd.api.types.is_numeric_dtype(df["Revenue"])
        assert pd.api.types.is_numeric_dtype(df["Quantity"])

    def test_get_preview(self):
        """Test getting data preview."""
        self.processor.load_file(self.sample_data_dir / "sales_sample.csv")

        preview = self.processor.get_preview(5)

        assert len(preview) == 5
        assert list(preview.columns) == list(self.processor.df.columns)

    def test_get_column_stats_numeric(self):
        """Test getting statistics for numeric column."""
        self.processor.load_file(self.sample_data_dir / "sales_sample.csv")
        self.processor.set_template("sales")
        self.processor.auto_map_columns()
        self.processor.process_data()

        stats = self.processor.get_column_stats("Revenue")

        assert "count" in stats
        assert "min" in stats
        assert "max" in stats
        assert "mean" in stats
        assert stats["min"] > 0
        assert stats["max"] > stats["min"]

    def test_get_summary_stats(self):
        """Test getting summary statistics."""
        self.processor.load_file(self.sample_data_dir / "sales_sample.csv")

        stats = self.processor.get_summary_stats()

        assert stats["row_count"] > 0
        assert stats["column_count"] > 0
        assert len(stats["columns"]) == stats["column_count"]

    def test_get_date_range(self):
        """Test getting date range."""
        self.processor.load_file(self.sample_data_dir / "sales_sample.csv")
        self.processor.set_template("sales")
        self.processor.auto_map_columns()
        self.processor.process_data()

        start_date, end_date = self.processor.get_date_range()

        assert start_date is not None
        assert end_date is not None
        assert end_date >= start_date


class TestDataProcessorMissingValues:
    """Tests for missing value handling."""

    def setup_method(self):
        """Setup for each test."""
        self.processor = DataProcessor()

    def test_fill_missing_drop(self):
        """Test dropping rows with missing values."""
        # Create test data with missing values
        df = pd.DataFrame({
            "A": [1, 2, None, 4],
            "B": ["a", None, "c", "d"]
        })
        self.processor.df = df

        result = self.processor.fill_missing_values("drop")

        assert len(result) == 2  # Only rows without any missing values

    def test_fill_missing_zero(self):
        """Test filling numeric columns with zero."""
        df = pd.DataFrame({
            "A": [1.0, 2.0, None, 4.0],
            "B": ["a", "b", "c", "d"]
        })
        self.processor.df = df

        result = self.processor.fill_missing_values("zero")

        assert result["A"].iloc[2] == 0


class TestMultipleFileLoading:
    """Tests for multiple file loading functionality."""

    def setup_method(self):
        """Setup for each test."""
        self.processor = DataProcessor()
        self.sample_data_dir = Path(__file__).parent.parent / "sample_data"

    def test_load_multiple_same_files(self):
        """Test loading multiple copies of the same file."""
        files = [
            self.sample_data_dir / "sales_sample.csv",
            self.sample_data_dir / "sales_sample.csv",
        ]
        df = self.processor.load_multiple_files(files)

        # Should have double the rows
        single_df = pd.read_csv(self.sample_data_dir / "sales_sample.csv")
        assert len(df) == len(single_df) * 2

    def test_load_single_file_via_multiple(self):
        """Test that single file works through load_multiple_files."""
        files = [self.sample_data_dir / "sales_sample.csv"]
        df = self.processor.load_multiple_files(files)

        single_df = pd.read_csv(self.sample_data_dir / "sales_sample.csv")
        assert len(df) == len(single_df)

    def test_load_multiple_empty_list(self):
        """Test that empty list raises error."""
        with pytest.raises(DataValidationError):
            self.processor.load_multiple_files([])

    def test_load_multiple_preserves_columns(self):
        """Test that columns are preserved after combining."""
        files = [
            self.sample_data_dir / "sales_sample.csv",
            self.sample_data_dir / "sales_sample.csv",
        ]
        df = self.processor.load_multiple_files(files)

        expected_cols = ['Date', 'Product', 'Category', 'Quantity', 'Revenue', 'Region']
        for col in expected_cols:
            assert col in df.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
