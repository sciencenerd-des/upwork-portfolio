"""
Tests for the ReportBuilder module.
"""

import sys
from pathlib import Path
import pytest
import pandas as pd
import numpy as np
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.report_builder import ReportBuilder, ReportBuilderError
from src.chart_generator import ChartGenerator


class TestReportBuilderSetup:
    """Tests for report builder initialization."""

    def test_initialization(self):
        """Test ReportBuilder initializes correctly."""
        builder = ReportBuilder()

        assert builder is not None
        assert builder._styles is not None
        assert builder._pdf_config is not None
        assert builder._word_config is not None


class TestPDFGeneration:
    """Tests for PDF report generation."""

    def setup_method(self):
        """Setup for each test."""
        self.builder = ReportBuilder()
        self.output_dir = Path(__file__).parent.parent / "outputs"
        self.output_dir.mkdir(exist_ok=True)

    def teardown_method(self):
        """Cleanup after each test."""
        # Clean up generated test files
        for f in self.output_dir.glob("test_*.pdf"):
            f.unlink(missing_ok=True)

    def test_build_basic_pdf(self):
        """Test building a basic PDF report."""
        sections = [
            {
                "type": "text",
                "title": "Introduction",
                "text": "This is a test report generated automatically."
            }
        ]

        output_path = self.output_dir / "test_basic.pdf"
        result = self.builder.build_pdf(
            output_path,
            title="Test Report",
            sections=sections
        )

        assert Path(result).exists()
        assert Path(result).suffix == ".pdf"

    def test_build_pdf_with_metadata(self):
        """Test building PDF with metadata."""
        sections = [
            {
                "type": "text",
                "title": "Overview",
                "text": "Report with metadata."
            }
        ]

        output_path = self.output_dir / "test_metadata.pdf"
        result = self.builder.build_pdf(
            output_path,
            title="Test Report with Metadata",
            sections=sections,
            metadata={
                "date": "January 20, 2024",
                "period": "Q4 2023"
            }
        )

        assert Path(result).exists()

    def test_build_pdf_with_summary(self):
        """Test building PDF with summary metrics."""
        sections = [
            {
                "type": "summary",
                "title": "Key Metrics",
                "metrics": [
                    {"label": "Total Revenue", "value": "$250,000"},
                    {"label": "Units Sold", "value": "5,000"},
                    {"label": "Avg Order", "value": "$50"},
                    {"label": "Growth", "value": "+15%"},
                ]
            }
        ]

        output_path = self.output_dir / "test_summary.pdf"
        result = self.builder.build_pdf(
            output_path,
            title="Summary Report",
            sections=sections
        )

        assert Path(result).exists()

    def test_build_pdf_with_table(self):
        """Test building PDF with data table."""
        df = pd.DataFrame({
            "Product": ["A", "B", "C", "D"],
            "Revenue": [10000, 8000, 12000, 6000],
            "Units": [100, 80, 120, 60]
        })

        sections = [
            {
                "type": "table",
                "title": "Product Performance",
                "dataframe": df
            }
        ]

        output_path = self.output_dir / "test_table.pdf"
        result = self.builder.build_pdf(
            output_path,
            title="Table Report",
            sections=sections
        )

        assert Path(result).exists()

    def test_build_pdf_with_insights(self):
        """Test building PDF with insights."""
        sections = [
            {
                "type": "insights",
                "title": "AI Insights",
                "insights": [
                    "Revenue increased by 15% compared to last quarter.",
                    "Product A continues to lead sales with 35% market share.",
                    "Consider expanding to new regions for growth opportunities."
                ]
            }
        ]

        output_path = self.output_dir / "test_insights.pdf"
        result = self.builder.build_pdf(
            output_path,
            title="Insights Report",
            sections=sections
        )

        assert Path(result).exists()

    def test_build_pdf_with_chart(self):
        """Test building PDF with embedded chart."""
        # Generate a chart
        chart_gen = ChartGenerator()
        data = pd.DataFrame({
            "Category": ["A", "B", "C"],
            "Value": [100, 200, 150]
        })
        fig = chart_gen.create_bar_chart(data, "Category", "Value", title="Test Chart")
        chart_bytes = chart_gen.figure_to_bytes(fig)

        sections = [
            {
                "type": "chart",
                "title": "Revenue by Category",
                "image_bytes": chart_bytes,
                "caption": "Figure 1: Revenue distribution"
            }
        ]

        output_path = self.output_dir / "test_chart.pdf"
        result = self.builder.build_pdf(
            output_path,
            title="Chart Report",
            sections=sections
        )

        assert Path(result).exists()


class TestWordGeneration:
    """Tests for Word document generation."""

    def setup_method(self):
        """Setup for each test."""
        self.builder = ReportBuilder()
        self.output_dir = Path(__file__).parent.parent / "outputs"
        self.output_dir.mkdir(exist_ok=True)

    def teardown_method(self):
        """Cleanup after each test."""
        # Clean up generated test files
        for f in self.output_dir.glob("test_*.docx"):
            f.unlink(missing_ok=True)

    def test_build_basic_word(self):
        """Test building a basic Word document."""
        sections = [
            {
                "type": "text",
                "title": "Introduction",
                "text": "This is a test report generated automatically."
            }
        ]

        output_path = self.output_dir / "test_basic.docx"
        result = self.builder.build_word(
            output_path,
            title="Test Report",
            sections=sections
        )

        assert Path(result).exists()
        assert Path(result).suffix == ".docx"

    def test_build_word_with_metadata(self):
        """Test building Word document with metadata."""
        sections = [
            {
                "type": "text",
                "title": "Overview",
                "text": "Report with metadata."
            }
        ]

        output_path = self.output_dir / "test_metadata.docx"
        result = self.builder.build_word(
            output_path,
            title="Test Report with Metadata",
            sections=sections,
            metadata={
                "date": "January 20, 2024",
                "period": "Q4 2023"
            }
        )

        assert Path(result).exists()

    def test_build_word_with_summary(self):
        """Test building Word document with summary metrics."""
        sections = [
            {
                "type": "summary",
                "title": "Key Metrics",
                "metrics": [
                    {"label": "Total Revenue", "value": "$250,000"},
                    {"label": "Units Sold", "value": "5,000"},
                    {"label": "Avg Order", "value": "$50"},
                    {"label": "Growth", "value": "+15%"},
                ]
            }
        ]

        output_path = self.output_dir / "test_summary.docx"
        result = self.builder.build_word(
            output_path,
            title="Summary Report",
            sections=sections
        )

        assert Path(result).exists()

    def test_build_word_with_table(self):
        """Test building Word document with data table."""
        df = pd.DataFrame({
            "Product": ["A", "B", "C", "D"],
            "Revenue": [10000, 8000, 12000, 6000],
            "Units": [100, 80, 120, 60]
        })

        sections = [
            {
                "type": "table",
                "title": "Product Performance",
                "dataframe": df
            }
        ]

        output_path = self.output_dir / "test_table.docx"
        result = self.builder.build_word(
            output_path,
            title="Table Report",
            sections=sections
        )

        assert Path(result).exists()

    def test_build_word_with_insights(self):
        """Test building Word document with insights."""
        sections = [
            {
                "type": "insights",
                "title": "AI Insights",
                "insights": [
                    "Revenue increased by 15% compared to last quarter.",
                    "Product A continues to lead sales with 35% market share.",
                    "Consider expanding to new regions for growth opportunities."
                ]
            }
        ]

        output_path = self.output_dir / "test_insights.docx"
        result = self.builder.build_word(
            output_path,
            title="Insights Report",
            sections=sections
        )

        assert Path(result).exists()

    def test_build_word_with_chart(self):
        """Test building Word document with embedded chart."""
        # Generate a chart
        chart_gen = ChartGenerator()
        data = pd.DataFrame({
            "Category": ["A", "B", "C"],
            "Value": [100, 200, 150]
        })
        fig = chart_gen.create_bar_chart(data, "Category", "Value", title="Test Chart")
        chart_bytes = chart_gen.figure_to_bytes(fig)

        sections = [
            {
                "type": "chart",
                "title": "Revenue by Category",
                "image_bytes": chart_bytes,
                "caption": "Figure 1: Revenue distribution"
            }
        ]

        output_path = self.output_dir / "test_chart.docx"
        result = self.builder.build_word(
            output_path,
            title="Chart Report",
            sections=sections
        )

        assert Path(result).exists()


class TestMultiFormatGeneration:
    """Tests for generating reports in multiple formats."""

    def setup_method(self):
        """Setup for each test."""
        self.builder = ReportBuilder()
        self.output_dir = Path(__file__).parent.parent / "outputs"
        self.output_dir.mkdir(exist_ok=True)

    def teardown_method(self):
        """Cleanup after each test."""
        # Clean up generated test files
        for f in self.output_dir.glob("test_*"):
            if f.suffix in [".pdf", ".docx"]:
                f.unlink(missing_ok=True)

    def test_build_both_formats(self):
        """Test building reports in both PDF and Word formats."""
        sections = [
            {
                "type": "text",
                "title": "Introduction",
                "text": "Multi-format test report."
            },
            {
                "type": "summary",
                "title": "Summary",
                "metrics": [
                    {"label": "Metric 1", "value": "100"},
                    {"label": "Metric 2", "value": "200"},
                ]
            }
        ]

        results = self.builder.build_report(
            self.output_dir,
            title="Multi-Format Report",
            sections=sections,
            template_name="test_multi",
            formats=["pdf", "docx"]
        )

        assert "pdf" in results
        assert "docx" in results
        assert Path(results["pdf"]).exists()
        assert Path(results["docx"]).exists()


class TestComplexReport:
    """Tests for complex reports with multiple section types."""

    def setup_method(self):
        """Setup for each test."""
        self.builder = ReportBuilder()
        self.chart_gen = ChartGenerator()
        self.output_dir = Path(__file__).parent.parent / "outputs"
        self.output_dir.mkdir(exist_ok=True)

    def teardown_method(self):
        """Cleanup after each test."""
        for f in self.output_dir.glob("test_complex*"):
            f.unlink(missing_ok=True)

    def test_build_complex_pdf(self):
        """Test building a complex PDF with all section types."""
        # Generate chart
        data = pd.DataFrame({
            "Category": ["A", "B", "C", "D"],
            "Value": [100, 150, 120, 80]
        })
        fig = self.chart_gen.create_bar_chart(data, "Category", "Value", title="Test")
        chart_bytes = self.chart_gen.figure_to_bytes(fig)

        # Table data
        table_df = pd.DataFrame({
            "Item": ["Item 1", "Item 2", "Item 3"],
            "Quantity": [10, 20, 15],
            "Price": [99.99, 149.99, 79.99]
        })

        sections = [
            {
                "type": "text",
                "title": "Executive Summary",
                "text": "This report provides a comprehensive analysis of our business performance."
            },
            {
                "type": "summary",
                "title": "Key Metrics",
                "metrics": [
                    {"label": "Revenue", "value": "$1.2M"},
                    {"label": "Growth", "value": "+25%"},
                    {"label": "Customers", "value": "5,000"},
                    {"label": "NPS", "value": "72"},
                ]
            },
            {
                "type": "chart",
                "title": "Performance by Category",
                "image_bytes": chart_bytes,
                "caption": "Figure 1: Category breakdown"
            },
            {
                "type": "table",
                "title": "Top Items",
                "dataframe": table_df
            },
            {
                "type": "insights",
                "title": "AI-Generated Insights",
                "insights": [
                    "Strong revenue growth indicates market demand.",
                    "Customer base expanded significantly this quarter.",
                    "Consider investing in Category A for maximum ROI."
                ]
            }
        ]

        output_path = self.output_dir / "test_complex.pdf"
        result = self.builder.build_pdf(
            output_path,
            title="Comprehensive Business Report",
            sections=sections,
            metadata={
                "date": "January 20, 2024",
                "period": "Q4 2023"
            }
        )

        assert Path(result).exists()
        # Check file size is reasonable (should be > 10KB for complex report)
        assert Path(result).stat().st_size > 10000

    def test_build_complex_word(self):
        """Test building a complex Word document with all section types."""
        # Generate chart
        data = pd.DataFrame({
            "Category": ["A", "B", "C", "D"],
            "Value": [100, 150, 120, 80]
        })
        fig = self.chart_gen.create_bar_chart(data, "Category", "Value", title="Test")
        chart_bytes = self.chart_gen.figure_to_bytes(fig)

        # Table data
        table_df = pd.DataFrame({
            "Item": ["Item 1", "Item 2", "Item 3"],
            "Quantity": [10, 20, 15],
            "Price": [99.99, 149.99, 79.99]
        })

        sections = [
            {
                "type": "text",
                "title": "Executive Summary",
                "text": "This report provides a comprehensive analysis of our business performance."
            },
            {
                "type": "summary",
                "title": "Key Metrics",
                "metrics": [
                    {"label": "Revenue", "value": "$1.2M"},
                    {"label": "Growth", "value": "+25%"},
                ]
            },
            {
                "type": "chart",
                "title": "Performance by Category",
                "image_bytes": chart_bytes,
                "caption": "Figure 1: Category breakdown"
            },
            {
                "type": "table",
                "title": "Top Items",
                "dataframe": table_df
            },
            {
                "type": "insights",
                "title": "AI-Generated Insights",
                "insights": [
                    "Strong revenue growth indicates market demand.",
                    "Customer base expanded significantly this quarter."
                ]
            }
        ]

        output_path = self.output_dir / "test_complex.docx"
        result = self.builder.build_word(
            output_path,
            title="Comprehensive Business Report",
            sections=sections,
            metadata={
                "date": "January 20, 2024",
                "period": "Q4 2023"
            }
        )

        assert Path(result).exists()
        # Check file size is reasonable
        assert Path(result).stat().st_size > 5000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
