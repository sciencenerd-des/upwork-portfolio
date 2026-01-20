"""
Automated Report Generator - Source Package

This package contains the core modules for the report generation system:
- data_processor: Data loading, validation, and cleaning
- chart_generator: Chart creation and styling
- report_builder: PDF and Word document generation
- ai_insights: LLM-powered insights generation
- utils: Helper functions and utilities
"""

__version__ = "1.0.0"

# Lazy imports to avoid circular dependencies and allow incremental development
def __getattr__(name):
    if name == "DataProcessor":
        from .data_processor import DataProcessor
        return DataProcessor
    elif name == "ChartGenerator":
        from .chart_generator import ChartGenerator
        return ChartGenerator
    elif name == "ReportBuilder":
        from .report_builder import ReportBuilder
        return ReportBuilder
    elif name == "AIInsights":
        from .ai_insights import AIInsights
        return AIInsights
    elif name == "load_config":
        from .utils import load_config
        return load_config
    elif name == "format_currency":
        from .utils import format_currency
        return format_currency
    elif name == "format_number":
        from .utils import format_number
        return format_number
    elif name == "format_percentage":
        from .utils import format_percentage
        return format_percentage
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "DataProcessor",
    "ChartGenerator",
    "ReportBuilder",
    "AIInsights",
    "load_config",
    "format_currency",
    "format_number",
    "format_percentage",
]
