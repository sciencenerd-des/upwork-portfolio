"""
Report Templates Package for the Automated Report Generator.

This package contains report templates that orchestrate
the full report generation workflow for specific report types.
"""

from .sales_report import SalesReportTemplate
from .financial_report import FinancialReportTemplate
from .inventory_report import InventoryReportTemplate

__all__ = [
    "SalesReportTemplate",
    "FinancialReportTemplate",
    "InventoryReportTemplate",
]

# Template registry for easy lookup
TEMPLATES = {
    "sales": SalesReportTemplate,
    "financial": FinancialReportTemplate,
    "inventory": InventoryReportTemplate,
}


def get_template(template_name: str):
    """
    Get a template class by name.

    Args:
        template_name: Name of the template (sales, financial, inventory)

    Returns:
        Template class

    Raises:
        KeyError: If template name is not found
    """
    if template_name not in TEMPLATES:
        available = ", ".join(TEMPLATES.keys())
        raise KeyError(f"Template '{template_name}' not found. Available: {available}")
    return TEMPLATES[template_name]
