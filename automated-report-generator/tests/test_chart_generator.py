"""
Tests for the ChartGenerator module.
"""

import sys
from pathlib import Path
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.chart_generator import ChartGenerator
from src.data_processor import DataProcessor


class TestChartGeneratorSetup:
    """Tests for chart generator initialization."""

    def test_initialization(self):
        """Test ChartGenerator initializes correctly."""
        generator = ChartGenerator()

        assert generator._styles is not None
        assert generator._colors is not None
        assert generator._chart_palette is not None
        assert len(generator._chart_palette) > 0


class TestLineCharts:
    """Tests for line chart generation."""

    def setup_method(self):
        """Setup for each test."""
        self.generator = ChartGenerator()
        self.sample_data_dir = Path(__file__).parent.parent / "sample_data"

        # Create sample time series data
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        self.time_series_data = pd.DataFrame({
            'Date': dates,
            'Revenue': np.random.randint(1000, 5000, 30),
            'Quantity': np.random.randint(10, 100, 30),
        })

    def test_create_line_chart_single_series(self):
        """Test creating a line chart with single series."""
        fig = self.generator.create_line_chart(
            self.time_series_data,
            x_column='Date',
            y_columns='Revenue',
            title='Revenue Over Time'
        )

        assert fig is not None
        assert len(fig.axes) > 0
        self.generator.close_all()

    def test_create_line_chart_multiple_series(self):
        """Test creating a line chart with multiple series."""
        fig = self.generator.create_line_chart(
            self.time_series_data,
            x_column='Date',
            y_columns=['Revenue', 'Quantity'],
            title='Revenue and Quantity Over Time',
            show_legend=True
        )

        assert fig is not None
        self.generator.close_all()

    def test_create_line_chart_with_labels(self):
        """Test creating a line chart with axis labels."""
        fig = self.generator.create_line_chart(
            self.time_series_data,
            x_column='Date',
            y_columns='Revenue',
            title='Revenue Over Time',
            x_label='Date',
            y_label='Revenue ($)'
        )

        assert fig is not None
        ax = fig.axes[0]
        assert ax.get_xlabel() == 'Date'
        assert ax.get_ylabel() == 'Revenue ($)'
        self.generator.close_all()

    def test_create_line_chart_no_markers(self):
        """Test creating a line chart without markers."""
        fig = self.generator.create_line_chart(
            self.time_series_data,
            x_column='Date',
            y_columns='Revenue',
            title='Revenue Over Time',
            show_markers=False
        )

        assert fig is not None
        self.generator.close_all()


class TestBarCharts:
    """Tests for bar chart generation."""

    def setup_method(self):
        """Setup for each test."""
        self.generator = ChartGenerator()

        # Create sample categorical data
        self.category_data = pd.DataFrame({
            'Product': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'],
            'Sales': [15000, 12000, 18000, 9000, 11000],
            'Quantity': [150, 120, 180, 90, 110],
        })

    def test_create_bar_chart_vertical(self):
        """Test creating a vertical bar chart."""
        fig = self.generator.create_bar_chart(
            self.category_data,
            category_column='Product',
            value_column='Sales',
            title='Sales by Product',
            orientation='vertical'
        )

        assert fig is not None
        self.generator.close_all()

    def test_create_bar_chart_horizontal(self):
        """Test creating a horizontal bar chart."""
        fig = self.generator.create_bar_chart(
            self.category_data,
            category_column='Product',
            value_column='Sales',
            title='Sales by Product',
            orientation='horizontal'
        )

        assert fig is not None
        self.generator.close_all()

    def test_create_bar_chart_with_limit(self):
        """Test creating a bar chart with limited bars."""
        # Create data with more categories
        large_data = pd.DataFrame({
            'Product': [f'Product {i}' for i in range(20)],
            'Sales': np.random.randint(5000, 20000, 20),
        })

        fig = self.generator.create_bar_chart(
            large_data,
            category_column='Product',
            value_column='Sales',
            title='Top 5 Products',
            limit=5
        )

        assert fig is not None
        self.generator.close_all()

    def test_create_bar_chart_sorted(self):
        """Test creating a sorted bar chart."""
        fig = self.generator.create_bar_chart(
            self.category_data,
            category_column='Product',
            value_column='Sales',
            title='Sales by Product (Sorted)',
            sort_by_value=True
        )

        assert fig is not None
        self.generator.close_all()

    def test_create_bar_chart_no_values(self):
        """Test creating a bar chart without value labels."""
        fig = self.generator.create_bar_chart(
            self.category_data,
            category_column='Product',
            value_column='Sales',
            title='Sales by Product',
            show_values=False
        )

        assert fig is not None
        self.generator.close_all()


class TestGroupedBarCharts:
    """Tests for grouped bar chart generation."""

    def setup_method(self):
        """Setup for each test."""
        self.generator = ChartGenerator()

        self.grouped_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr'],
            'Income': [50000, 55000, 48000, 62000],
            'Expenses': [35000, 38000, 32000, 40000],
        })

    def test_create_grouped_bar_chart(self):
        """Test creating a grouped bar chart."""
        fig = self.generator.create_grouped_bar_chart(
            self.grouped_data,
            category_column='Month',
            value_columns=['Income', 'Expenses'],
            title='Income vs Expenses'
        )

        assert fig is not None
        self.generator.close_all()


class TestPieCharts:
    """Tests for pie chart generation."""

    def setup_method(self):
        """Setup for each test."""
        self.generator = ChartGenerator()

        self.pie_data = pd.DataFrame({
            'Category': ['Electronics', 'Furniture', 'Clothing', 'Food', 'Other'],
            'Revenue': [45000, 28000, 22000, 15000, 8000],
        })

    def test_create_pie_chart(self):
        """Test creating a pie chart."""
        fig = self.generator.create_pie_chart(
            self.pie_data,
            category_column='Category',
            value_column='Revenue',
            title='Revenue Distribution'
        )

        assert fig is not None
        self.generator.close_all()

    def test_create_pie_chart_with_legend(self):
        """Test creating a pie chart with legend."""
        fig = self.generator.create_pie_chart(
            self.pie_data,
            category_column='Category',
            value_column='Revenue',
            title='Revenue Distribution',
            show_legend=True
        )

        assert fig is not None
        self.generator.close_all()

    def test_create_pie_chart_with_explode(self):
        """Test creating a pie chart with exploded largest slice."""
        fig = self.generator.create_pie_chart(
            self.pie_data,
            category_column='Category',
            value_column='Revenue',
            title='Revenue Distribution',
            explode_largest=True
        )

        assert fig is not None
        self.generator.close_all()

    def test_create_pie_chart_with_limit(self):
        """Test creating a pie chart with limited slices."""
        # Create data with many categories
        large_data = pd.DataFrame({
            'Category': [f'Category {i}' for i in range(15)],
            'Revenue': np.random.randint(5000, 20000, 15),
        })

        fig = self.generator.create_pie_chart(
            large_data,
            category_column='Category',
            value_column='Revenue',
            title='Revenue Distribution',
            limit=5
        )

        assert fig is not None
        self.generator.close_all()


class TestTrendCharts:
    """Tests for trend chart with aggregation."""

    def setup_method(self):
        """Setup for each test."""
        self.generator = ChartGenerator()

        # Create sample time series data with multiple entries per day
        dates = []
        values = []
        for day in range(60):
            date = datetime(2024, 1, 1) + timedelta(days=day)
            for _ in range(np.random.randint(3, 8)):
                dates.append(date)
                values.append(np.random.randint(100, 500))

        self.daily_data = pd.DataFrame({
            'Date': dates,
            'Revenue': values,
        })

    def test_create_trend_chart_auto_period(self):
        """Test creating a trend chart with auto period detection."""
        fig = self.generator.create_trend_chart_with_aggregation(
            self.daily_data,
            date_column='Date',
            value_column='Revenue',
            title='Revenue Trend',
            period='auto'
        )

        assert fig is not None
        self.generator.close_all()

    def test_create_trend_chart_daily(self):
        """Test creating a daily trend chart."""
        fig = self.generator.create_trend_chart_with_aggregation(
            self.daily_data,
            date_column='Date',
            value_column='Revenue',
            title='Daily Revenue',
            period='daily'
        )

        assert fig is not None
        self.generator.close_all()

    def test_create_trend_chart_weekly(self):
        """Test creating a weekly trend chart."""
        fig = self.generator.create_trend_chart_with_aggregation(
            self.daily_data,
            date_column='Date',
            value_column='Revenue',
            title='Weekly Revenue',
            period='weekly'
        )

        assert fig is not None
        self.generator.close_all()

    def test_create_trend_chart_monthly(self):
        """Test creating a monthly trend chart."""
        fig = self.generator.create_trend_chart_with_aggregation(
            self.daily_data,
            date_column='Date',
            value_column='Revenue',
            title='Monthly Revenue',
            period='monthly'
        )

        assert fig is not None
        self.generator.close_all()


class TestChartExport:
    """Tests for chart export functionality."""

    def setup_method(self):
        """Setup for each test."""
        self.generator = ChartGenerator()
        self.output_dir = Path(__file__).parent.parent / "outputs"
        self.output_dir.mkdir(exist_ok=True)

        self.sample_data = pd.DataFrame({
            'Category': ['A', 'B', 'C'],
            'Value': [100, 200, 150],
        })

    def test_save_figure_png(self):
        """Test saving figure as PNG."""
        fig = self.generator.create_bar_chart(
            self.sample_data,
            category_column='Category',
            value_column='Value',
            title='Test Chart'
        )

        filepath = self.output_dir / "test_chart.png"
        saved_path = self.generator.save_figure(fig, filepath, format='png')

        assert Path(saved_path).exists()
        # Cleanup
        Path(saved_path).unlink()

    def test_figure_to_bytes(self):
        """Test converting figure to bytes."""
        fig = self.generator.create_bar_chart(
            self.sample_data,
            category_column='Category',
            value_column='Value',
            title='Test Chart'
        )

        image_bytes = self.generator.figure_to_bytes(fig)

        assert isinstance(image_bytes, bytes)
        assert len(image_bytes) > 0
        # PNG signature
        assert image_bytes[:8] == b'\x89PNG\r\n\x1a\n'

    def test_figure_to_base64(self):
        """Test converting figure to base64."""
        fig = self.generator.create_bar_chart(
            self.sample_data,
            category_column='Category',
            value_column='Value',
            title='Test Chart'
        )

        base64_str = self.generator.figure_to_base64(fig)

        assert isinstance(base64_str, str)
        assert len(base64_str) > 0


class TestChartWithRealData:
    """Tests using real sample data files."""

    def setup_method(self):
        """Setup for each test."""
        self.generator = ChartGenerator()
        self.processor = DataProcessor()
        self.sample_data_dir = Path(__file__).parent.parent / "sample_data"

    def test_sales_data_line_chart(self):
        """Test creating line chart from sales sample data."""
        df = self.processor.load_file(self.sample_data_dir / "sales_sample.csv")
        self.processor.set_template("sales")
        self.processor.auto_map_columns()
        df = self.processor.process_data()

        fig = self.generator.create_trend_chart_with_aggregation(
            df,
            date_column='Date',
            value_column='Revenue',
            title='Sales Revenue Trend',
            y_label='Revenue ($)'
        )

        assert fig is not None
        self.generator.close_all()

    def test_sales_data_bar_chart(self):
        """Test creating bar chart from sales sample data."""
        df = self.processor.load_file(self.sample_data_dir / "sales_sample.csv")
        self.processor.set_template("sales")
        self.processor.auto_map_columns()
        df = self.processor.process_data()

        fig = self.generator.create_bar_chart(
            df,
            category_column='Product',
            value_column='Revenue',
            title='Revenue by Product',
            limit=10
        )

        assert fig is not None
        self.generator.close_all()

    def test_sales_data_pie_chart(self):
        """Test creating pie chart from sales sample data."""
        df = self.processor.load_file(self.sample_data_dir / "sales_sample.csv")
        self.processor.set_template("sales")
        self.processor.auto_map_columns()
        df = self.processor.process_data()

        fig = self.generator.create_pie_chart(
            df,
            category_column='Region',
            value_column='Revenue',
            title='Revenue by Region'
        )

        assert fig is not None
        self.generator.close_all()

    def test_inventory_data_bar_chart(self):
        """Test creating bar chart from inventory sample data."""
        df = self.processor.load_file(self.sample_data_dir / "inventory_sample.csv")

        fig = self.generator.create_bar_chart(
            df,
            category_column='Category',
            value_column='Quantity',
            title='Stock Levels by Category',
            orientation='horizontal'
        )

        assert fig is not None
        self.generator.close_all()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
