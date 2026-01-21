"""
Comprehensive tests for utility functions in src/utils.py.
Covers all formatting, parsing, detection, sanitization, and helper functions.
"""

import os
import sys
import tempfile
from pathlib import Path
from datetime import datetime, date
import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import (
    get_project_root,
    load_config,
    get_templates_config,
    get_styles_config,
    format_currency,
    format_number,
    format_percentage,
    format_date,
    parse_date,
    detect_date_column,
    detect_numeric_column,
    clean_numeric_value,
    get_trend_direction,
    calculate_percentage_change,
    truncate_text,
    sanitize_filename,
    generate_report_filename,
    hex_to_rgb,
    rgb_to_hex,
    ensure_directory,
    get_file_size_mb,
    validate_file_size,
    get_period_label,
    aggregate_by_period,
)


class TestProjectRoot:
    """Tests for project root detection."""

    def test_get_project_root_returns_path(self):
        """Test that get_project_root returns a Path object."""
        root = get_project_root()
        assert isinstance(root, Path)

    def test_get_project_root_exists(self):
        """Test that the project root exists."""
        root = get_project_root()
        assert root.exists()

    def test_get_project_root_contains_expected_files(self):
        """Test that project root contains expected directories."""
        root = get_project_root()
        assert (root / "src").exists() or (root / "config").exists()


class TestConfigLoading:
    """Tests for configuration loading."""

    def test_load_templates_config(self):
        """Test loading templates configuration."""
        config = get_templates_config()
        assert isinstance(config, dict)
        assert "templates" in config or "settings" in config

    def test_load_styles_config(self):
        """Test loading styles configuration."""
        config = get_styles_config()
        assert isinstance(config, dict)

    def test_load_config_file_not_found(self):
        """Test that missing config raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent_config_file")


class TestFormatCurrency:
    """Tests for currency formatting."""

    def test_format_currency_positive(self):
        """Test formatting positive currency values."""
        assert format_currency(1234.56) == "$1,234.56"

    def test_format_currency_negative(self):
        """Test formatting negative currency values."""
        assert format_currency(-1234.56) == "-$1,234.56"

    def test_format_currency_zero(self):
        """Test formatting zero."""
        assert format_currency(0) == "$0.00"

    def test_format_currency_none(self):
        """Test formatting None value."""
        assert format_currency(None) == "$0.00"

    def test_format_currency_custom_symbol(self):
        """Test formatting with custom currency symbol."""
        assert format_currency(1000, symbol="€") == "€1,000.00"

    def test_format_currency_large_number(self):
        """Test formatting large numbers."""
        assert format_currency(1234567.89) == "$1,234,567.89"

    def test_format_currency_integer(self):
        """Test formatting integer input."""
        assert format_currency(100) == "$100.00"


class TestFormatNumber:
    """Tests for number formatting."""

    def test_format_number_integer(self):
        """Test formatting integer."""
        assert format_number(1234567) == "1,234,567"

    def test_format_number_with_decimals(self):
        """Test formatting with decimals."""
        assert format_number(1234.5678, decimals=2) == "1,234.57"

    def test_format_number_none(self):
        """Test formatting None."""
        assert format_number(None) == "0"

    def test_format_number_zero(self):
        """Test formatting zero."""
        assert format_number(0) == "0"

    def test_format_number_float_no_decimals(self):
        """Test formatting float with no decimals."""
        assert format_number(1234.99, decimals=0) == "1,234"


class TestFormatPercentage:
    """Tests for percentage formatting."""

    def test_format_percentage_decimal(self):
        """Test formatting decimal as percentage."""
        assert format_percentage(0.15) == "15.0%"

    def test_format_percentage_none(self):
        """Test formatting None."""
        assert format_percentage(None) == "0.0%"

    def test_format_percentage_zero(self):
        """Test formatting zero."""
        assert format_percentage(0) == "0.0%"

    def test_format_percentage_custom_decimals(self):
        """Test formatting with custom decimal places."""
        assert format_percentage(0.1567, decimals=2) == "15.67%"

    def test_format_percentage_one_hundred(self):
        """Test formatting 100%."""
        assert format_percentage(1.0) == "100.0%"

    def test_format_percentage_negative(self):
        """Test formatting negative percentage."""
        assert format_percentage(-0.05) == "-5.0%"


class TestFormatDate:
    """Tests for date formatting."""

    def test_format_date_datetime(self):
        """Test formatting datetime object."""
        dt = datetime(2024, 1, 15, 10, 30)
        assert format_date(dt) == "January 15, 2024"

    def test_format_date_date(self):
        """Test formatting date object."""
        d = date(2024, 1, 15)
        assert format_date(d) == "January 15, 2024"

    def test_format_date_string(self):
        """Test formatting date string."""
        result = format_date("2024-01-15")
        assert "2024" in result or result == ""

    def test_format_date_none_result(self):
        """Test formatting invalid string returns empty."""
        result = format_date("invalid date string")
        assert result == "" or "invalid" in result.lower()

    def test_format_date_custom_format(self):
        """Test formatting with custom format."""
        dt = datetime(2024, 1, 15)
        assert format_date(dt, "%Y-%m-%d") == "2024-01-15"


class TestParseDate:
    """Tests for date parsing."""

    def test_parse_date_iso(self):
        """Test parsing ISO format date."""
        result = parse_date("2024-01-15")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_date_us_format(self):
        """Test parsing US format date."""
        result = parse_date("01/15/2024")
        assert result is not None

    def test_parse_date_invalid(self):
        """Test parsing invalid date returns None."""
        result = parse_date("not a date")
        assert result is None

    def test_parse_date_custom_formats(self):
        """Test parsing with custom formats."""
        result = parse_date("15-Jan-2024", formats=["%d-%b-%Y"])
        assert result is not None
        assert result.day == 15

    def test_parse_date_with_whitespace(self):
        """Test parsing date with whitespace."""
        result = parse_date("  2024-01-15  ")
        assert result is not None


class TestDetectDateColumn:
    """Tests for date column detection."""

    def test_detect_date_column_dates(self):
        """Test detecting date column with valid dates."""
        values = ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]
        assert detect_date_column(values) is True

    def test_detect_date_column_not_dates(self):
        """Test detecting non-date column."""
        values = ["hello", "world", "test", "data"]
        assert detect_date_column(values) is False

    def test_detect_date_column_empty(self):
        """Test detecting empty list."""
        assert detect_date_column([]) is False

    def test_detect_date_column_mixed(self):
        """Test detecting mixed values (mostly dates)."""
        values = ["2024-01-01", "2024-01-02", "not a date", "2024-01-03"]
        # 75% are dates, should pass 70% threshold
        assert detect_date_column(values) is True

    def test_detect_date_column_with_none(self):
        """Test detecting dates with None values."""
        values = [None, "2024-01-01", None, "2024-01-02"]
        assert detect_date_column(values) is True


class TestDetectNumericColumn:
    """Tests for numeric column detection."""

    def test_detect_numeric_column_integers(self):
        """Test detecting integer column."""
        values = [1, 2, 3, 4, 5]
        assert detect_numeric_column(values) is True

    def test_detect_numeric_column_floats(self):
        """Test detecting float column."""
        values = [1.5, 2.5, 3.5, 4.5]
        assert detect_numeric_column(values) is True

    def test_detect_numeric_column_strings(self):
        """Test detecting non-numeric column."""
        values = ["hello", "world", "test"]
        assert detect_numeric_column(values) is False

    def test_detect_numeric_column_currency(self):
        """Test detecting currency strings as numeric."""
        values = ["$1,000", "$2,000", "$3,000"]
        assert detect_numeric_column(values) is True

    def test_detect_numeric_column_empty(self):
        """Test detecting empty list."""
        assert detect_numeric_column([]) is False

    def test_detect_numeric_column_percentages(self):
        """Test detecting percentage strings."""
        values = ["10%", "20%", "30%"]
        assert detect_numeric_column(values) is True


class TestCleanNumericValue:
    """Tests for numeric value cleaning."""

    def test_clean_numeric_integer(self):
        """Test cleaning integer."""
        assert clean_numeric_value(100) == 100.0

    def test_clean_numeric_float(self):
        """Test cleaning float."""
        assert clean_numeric_value(100.5) == 100.5

    def test_clean_numeric_currency_string(self):
        """Test cleaning currency string."""
        assert clean_numeric_value("$1,234.56") == 1234.56

    def test_clean_numeric_percentage_string(self):
        """Test cleaning percentage string."""
        assert clean_numeric_value("15%") == 15.0

    def test_clean_numeric_none(self):
        """Test cleaning None."""
        assert clean_numeric_value(None) is None

    def test_clean_numeric_invalid(self):
        """Test cleaning invalid string."""
        assert clean_numeric_value("not a number") is None


class TestTrendDirection:
    """Tests for trend direction calculation."""

    def test_trend_up(self):
        """Test upward trend detection."""
        assert get_trend_direction(110, 100) == "up"

    def test_trend_down(self):
        """Test downward trend detection."""
        assert get_trend_direction(90, 100) == "down"

    def test_trend_stable(self):
        """Test stable trend detection."""
        assert get_trend_direction(100, 100) == "stable"

    def test_trend_previous_zero_current_positive(self):
        """Test trend with previous zero and current positive."""
        assert get_trend_direction(100, 0) == "up"

    def test_trend_previous_zero_current_zero(self):
        """Test trend with both zero."""
        assert get_trend_direction(0, 0) == "stable"

    def test_trend_within_threshold(self):
        """Test trend within threshold is stable."""
        assert get_trend_direction(100.5, 100, threshold=0.01) == "stable"


class TestPercentageChange:
    """Tests for percentage change calculation."""

    def test_percentage_increase(self):
        """Test percentage increase."""
        assert calculate_percentage_change(110, 100) == pytest.approx(0.1)

    def test_percentage_decrease(self):
        """Test percentage decrease."""
        assert calculate_percentage_change(90, 100) == pytest.approx(-0.1)

    def test_percentage_no_change(self):
        """Test no percentage change."""
        assert calculate_percentage_change(100, 100) == 0

    def test_percentage_previous_zero_current_positive(self):
        """Test percentage change with previous zero."""
        assert calculate_percentage_change(100, 0) == float('inf')

    def test_percentage_both_zero(self):
        """Test percentage change with both zero."""
        assert calculate_percentage_change(0, 0) is None


class TestTruncateText:
    """Tests for text truncation."""

    def test_truncate_short_text(self):
        """Test that short text is not truncated."""
        assert truncate_text("hello", max_length=10) == "hello"

    def test_truncate_long_text(self):
        """Test truncating long text."""
        result = truncate_text("hello world", max_length=8)
        assert len(result) == 8
        assert result.endswith("...")

    def test_truncate_custom_suffix(self):
        """Test truncating with custom suffix."""
        result = truncate_text("hello world", max_length=10, suffix=">>")
        assert result.endswith(">>")

    def test_truncate_exact_length(self):
        """Test text at exact max length."""
        assert truncate_text("hello", max_length=5) == "hello"


class TestSanitizeFilename:
    """Tests for filename sanitization."""

    def test_sanitize_normal_filename(self):
        """Test sanitizing normal filename."""
        assert sanitize_filename("report.pdf") == "report.pdf"

    def test_sanitize_with_invalid_chars(self):
        """Test sanitizing filename with invalid characters."""
        result = sanitize_filename("file:name<test>.pdf")
        assert ":" not in result
        assert "<" not in result
        assert ">" not in result

    def test_sanitize_with_spaces(self):
        """Test sanitizing filename with leading/trailing spaces."""
        result = sanitize_filename("  report.pdf  ")
        assert not result.startswith(" ")
        assert not result.endswith(" ")

    def test_sanitize_empty_returns_default(self):
        """Test sanitizing empty filename returns default."""
        assert sanitize_filename("...") == "report"


class TestGenerateReportFilename:
    """Tests for report filename generation."""

    def test_generate_with_timestamp(self):
        """Test generating filename with timestamp."""
        result = generate_report_filename("Sales Report", "pdf", include_timestamp=True)
        assert result.startswith("sales_report_")
        assert result.endswith(".pdf")

    def test_generate_without_timestamp(self):
        """Test generating filename without timestamp."""
        result = generate_report_filename("Sales Report", "pdf", include_timestamp=False)
        assert result == "sales_report.pdf"

    def test_generate_docx_format(self):
        """Test generating docx filename."""
        result = generate_report_filename("Report", "docx", include_timestamp=False)
        assert result.endswith(".docx")


class TestColorConversions:
    """Tests for color conversion functions."""

    def test_hex_to_rgb(self):
        """Test converting hex to RGB."""
        assert hex_to_rgb("#FF0000") == (255, 0, 0)
        assert hex_to_rgb("#00FF00") == (0, 255, 0)
        assert hex_to_rgb("#0000FF") == (0, 0, 255)

    def test_hex_to_rgb_without_hash(self):
        """Test converting hex without hash."""
        assert hex_to_rgb("FF0000") == (255, 0, 0)

    def test_rgb_to_hex(self):
        """Test converting RGB to hex."""
        assert rgb_to_hex((255, 0, 0)) == "#ff0000"
        assert rgb_to_hex((0, 255, 0)) == "#00ff00"

    def test_roundtrip_conversion(self):
        """Test roundtrip hex -> rgb -> hex."""
        original = "#2563eb"
        rgb = hex_to_rgb(original)
        back = rgb_to_hex(rgb)
        assert back.lower() == original.lower()


class TestEnsureDirectory:
    """Tests for directory creation."""

    def test_ensure_directory_creates(self):
        """Test that directory is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "new_subdir"
            result = ensure_directory(new_dir)
            assert result.exists()
            assert result.is_dir()

    def test_ensure_directory_existing(self):
        """Test with existing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = ensure_directory(tmpdir)
            assert result.exists()

    def test_ensure_directory_nested(self):
        """Test creating nested directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "level1" / "level2" / "level3"
            result = ensure_directory(new_dir)
            assert result.exists()


class TestFileSizeHelpers:
    """Tests for file size utilities."""

    def test_get_file_size_mb(self):
        """Test getting file size in MB."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"x" * 1024 * 1024)  # 1 MB
            f.flush()
            size = get_file_size_mb(f.name)
            assert 0.9 < size < 1.1
            os.unlink(f.name)

    def test_validate_file_size_within_limit(self):
        """Test validating file within size limit."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"small file")
            f.flush()
            assert validate_file_size(f.name, max_size_mb=10) is True
            os.unlink(f.name)

    def test_validate_file_size_exceeds_limit(self):
        """Test validating file exceeding size limit."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"x" * 1024 * 1024)  # 1 MB
            f.flush()
            assert validate_file_size(f.name, max_size_mb=0.5) is False
            os.unlink(f.name)


class TestPeriodLabel:
    """Tests for period label generation."""

    def test_same_month_year(self):
        """Test label for same month and year."""
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 31)
        assert get_period_label(start, end) == "January 2024"

    def test_different_months_same_year(self):
        """Test label for different months in same year."""
        start = datetime(2024, 1, 1)
        end = datetime(2024, 3, 31)
        assert "Jan" in get_period_label(start, end)
        assert "Mar" in get_period_label(start, end)

    def test_different_years(self):
        """Test label for different years."""
        start = datetime(2023, 11, 1)
        end = datetime(2024, 2, 28)
        result = get_period_label(start, end)
        assert "2023" in result
        assert "2024" in result


class TestAggregatePeriod:
    """Tests for period aggregation."""

    def test_aggregate_auto_daily(self):
        """Test auto-detection of daily aggregation."""
        dates = [datetime(2024, 1, i) for i in range(1, 15)]
        values = list(range(14))
        name, freq = aggregate_by_period(dates, values, period="auto")
        assert name == "daily"

    def test_aggregate_auto_weekly(self):
        """Test auto-detection of weekly aggregation."""
        dates = [datetime(2024, 1, 1) + __import__('datetime').timedelta(days=i) for i in range(60)]
        values = list(range(60))
        name, freq = aggregate_by_period(dates, values, period="auto")
        assert name == "weekly"

    def test_aggregate_auto_monthly(self):
        """Test auto-detection of monthly aggregation."""
        dates = [datetime(2024, 1, 1) + __import__('datetime').timedelta(days=i) for i in range(120)]
        values = list(range(120))
        name, freq = aggregate_by_period(dates, values, period="auto")
        assert name == "monthly"

    def test_aggregate_explicit_weekly(self):
        """Test explicit weekly aggregation."""
        dates = [datetime(2024, 1, i) for i in range(1, 10)]
        values = list(range(9))
        name, freq = aggregate_by_period(dates, values, period="weekly")
        assert name == "weekly"
        assert freq == "W"

    def test_aggregate_empty_dates(self):
        """Test aggregation with empty dates."""
        name, freq = aggregate_by_period([], [], period="auto")
        assert name == "daily"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
