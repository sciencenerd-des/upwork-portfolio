"""
Utility functions for the Automated Report Generator.

This module provides helper functions for configuration loading,
data formatting, date handling, and other common operations.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
import yaml


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def load_config(config_name: str) -> Dict[str, Any]:
    """
    Load a YAML configuration file.

    Args:
        config_name: Name of the config file (without .yaml extension)

    Returns:
        Dictionary containing the configuration

    Raises:
        FileNotFoundError: If the config file doesn't exist
        yaml.YAMLError: If the config file is invalid
    """
    config_path = get_project_root() / "config" / f"{config_name}.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_templates_config() -> Dict[str, Any]:
    """Load and return the templates configuration."""
    return load_config("templates")


def get_styles_config() -> Dict[str, Any]:
    """Load and return the styles configuration."""
    return load_config("styles")


def format_currency(value: Union[int, float], symbol: str = "$") -> str:
    """
    Format a number as currency.

    Args:
        value: The numeric value to format
        symbol: Currency symbol (default: $)

    Returns:
        Formatted currency string
    """
    if value is None:
        return f"{symbol}0.00"

    if value < 0:
        return f"-{symbol}{abs(value):,.2f}"
    return f"{symbol}{value:,.2f}"


def format_number(value: Union[int, float], decimals: int = 0) -> str:
    """
    Format a number with thousand separators.

    Args:
        value: The numeric value to format
        decimals: Number of decimal places

    Returns:
        Formatted number string
    """
    if value is None:
        return "0"

    if decimals == 0:
        return f"{int(value):,}"
    return f"{value:,.{decimals}f}"


def format_percentage(value: Union[int, float], decimals: int = 1) -> str:
    """
    Format a number as percentage.

    Args:
        value: The numeric value (as decimal, e.g., 0.15 for 15%)
        decimals: Number of decimal places

    Returns:
        Formatted percentage string
    """
    if value is None:
        return "0.0%"

    return f"{value * 100:.{decimals}f}%"


def format_date(dt: Union[datetime, date, str], format_str: str = "%B %d, %Y") -> str:
    """
    Format a date object or string to a readable format.

    Args:
        dt: Date object or string to format
        format_str: Output format string

    Returns:
        Formatted date string
    """
    if isinstance(dt, str):
        dt = parse_date(dt)

    if dt is None:
        return ""

    if isinstance(dt, datetime):
        return dt.strftime(format_str)
    elif isinstance(dt, date):
        return dt.strftime(format_str)

    return str(dt)


def parse_date(date_str: str, formats: Optional[List[str]] = None) -> Optional[datetime]:
    """
    Parse a date string using multiple format patterns.

    Args:
        date_str: The date string to parse
        formats: List of format patterns to try

    Returns:
        Parsed datetime object or None if parsing fails
    """
    if formats is None:
        config = get_templates_config()
        formats = config.get("settings", {}).get("date_formats", [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%m-%d-%Y",
        ])

    for fmt in formats:
        try:
            return datetime.strptime(str(date_str).strip(), fmt)
        except (ValueError, TypeError):
            continue

    return None


def detect_date_column(values: List[Any]) -> bool:
    """
    Detect if a list of values represents dates.

    Args:
        values: List of values to check

    Returns:
        True if the values appear to be dates
    """
    # Sample the first 10 non-null values
    sample = [v for v in values[:100] if v is not None and str(v).strip()][:10]

    if not sample:
        return False

    parsed_count = sum(1 for v in sample if parse_date(str(v)) is not None)
    return parsed_count >= len(sample) * 0.7  # 70% threshold


def detect_numeric_column(values: List[Any]) -> bool:
    """
    Detect if a list of values represents numeric data.

    Args:
        values: List of values to check

    Returns:
        True if the values appear to be numeric
    """
    # Sample the first 10 non-null values
    sample = [v for v in values[:100] if v is not None and str(v).strip()][:10]

    if not sample:
        return False

    numeric_count = 0
    for v in sample:
        try:
            # Remove currency symbols and commas
            cleaned = str(v).replace("$", "").replace(",", "").replace("%", "").strip()
            float(cleaned)
            numeric_count += 1
        except (ValueError, TypeError):
            continue

    return numeric_count >= len(sample) * 0.7  # 70% threshold


def clean_numeric_value(value: Any) -> Optional[float]:
    """
    Clean and convert a value to a numeric type.

    Args:
        value: The value to clean

    Returns:
        Float value or None if conversion fails
    """
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    try:
        # Remove currency symbols, commas, and percentage signs
        cleaned = str(value).replace("$", "").replace(",", "").replace("%", "").strip()
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def get_trend_direction(current: float, previous: float, threshold: float = 0.01) -> str:
    """
    Determine the trend direction between two values.

    Args:
        current: Current value
        previous: Previous value
        threshold: Minimum percentage change to consider significant

    Returns:
        'up', 'down', or 'stable'
    """
    if previous == 0:
        return "stable" if current == 0 else "up"

    change = (current - previous) / abs(previous)

    if change > threshold:
        return "up"
    elif change < -threshold:
        return "down"
    return "stable"


def calculate_percentage_change(current: float, previous: float) -> Optional[float]:
    """
    Calculate percentage change between two values.

    Args:
        current: Current value
        previous: Previous value

    Returns:
        Percentage change as a decimal (e.g., 0.15 for 15% increase)
    """
    if previous == 0:
        return None if current == 0 else float('inf')

    return (current - previous) / abs(previous)


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.

    Args:
        filename: The filename to sanitize

    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")

    # Remove leading/trailing spaces and dots
    filename = filename.strip(". ")

    return filename or "report"


def generate_report_filename(
    template_name: str,
    format_type: str,
    include_timestamp: bool = True
) -> str:
    """
    Generate a standardized report filename.

    Args:
        template_name: Name of the report template
        format_type: File format (pdf, docx)
        include_timestamp: Whether to include timestamp

    Returns:
        Generated filename
    """
    base_name = sanitize_filename(template_name.lower().replace(" ", "_"))

    if include_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}.{format_type}"

    return f"{base_name}.{format_type}"


def hex_to_rgb(hex_color: str) -> tuple:
    """
    Convert a hex color to RGB tuple.

    Args:
        hex_color: Hex color string (e.g., '#2563EB')

    Returns:
        RGB tuple (r, g, b) with values 0-255
    """
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple) -> str:
    """
    Convert an RGB tuple to hex color.

    Args:
        rgb: RGB tuple (r, g, b) with values 0-255

    Returns:
        Hex color string
    """
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_size_mb(file_path: Union[str, Path]) -> float:
    """
    Get the size of a file in megabytes.

    Args:
        file_path: Path to the file

    Returns:
        File size in MB
    """
    return os.path.getsize(file_path) / (1024 * 1024)


def validate_file_size(file_path: Union[str, Path], max_size_mb: float = 10) -> bool:
    """
    Validate that a file is within the size limit.

    Args:
        file_path: Path to the file
        max_size_mb: Maximum allowed size in MB

    Returns:
        True if file is within limit
    """
    return get_file_size_mb(file_path) <= max_size_mb


def get_period_label(start_date: datetime, end_date: datetime) -> str:
    """
    Generate a human-readable period label.

    Args:
        start_date: Start of the period
        end_date: End of the period

    Returns:
        Period description string
    """
    if start_date.year == end_date.year:
        if start_date.month == end_date.month:
            return f"{start_date.strftime('%B %Y')}"
        return f"{start_date.strftime('%b')} - {end_date.strftime('%b %Y')}"
    return f"{start_date.strftime('%b %Y')} - {end_date.strftime('%b %Y')}"


def aggregate_by_period(
    dates: List[datetime],
    values: List[float],
    period: str = "auto"
) -> tuple:
    """
    Determine the best aggregation period based on date range.

    Args:
        dates: List of dates
        values: Corresponding values
        period: 'auto', 'daily', 'weekly', or 'monthly'

    Returns:
        Tuple of (period_name, aggregation_func_name)
    """
    if not dates:
        return "daily", "D"

    if period != "auto":
        period_map = {
            "daily": ("daily", "D"),
            "weekly": ("weekly", "W"),
            "monthly": ("monthly", "M"),
        }
        return period_map.get(period, ("daily", "D"))

    # Auto-detect based on date range
    date_range = (max(dates) - min(dates)).days

    if date_range <= 31:
        return "daily", "D"
    elif date_range <= 90:
        return "weekly", "W"
    else:
        return "monthly", "M"
