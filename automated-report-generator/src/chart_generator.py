"""
Chart Generator Module for the Automated Report Generator.

This module handles:
- Creating line charts for trend visualization
- Creating bar charts for comparisons
- Creating pie charts for distribution analysis
- Applying professional styling based on configuration
- Exporting charts as PNG images for report embedding
"""

import io
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import seaborn as sns
import pandas as pd
import numpy as np

from .utils import get_styles_config, hex_to_rgb, format_currency, format_number


class ChartGenerator:
    """
    Generates professional charts for reports.

    Supports line charts, bar charts, and pie charts with
    configurable styling based on the styles.yaml configuration.
    """

    def __init__(self):
        """Initialize the ChartGenerator with styling configuration."""
        self._styles = get_styles_config()
        self._colors = self._styles.get("colors", {})
        self._chart_palette = self._styles.get("chart_palette", [])
        self._chart_config = self._styles.get("charts", {})

        # Set up matplotlib style
        self._setup_style()

    def _setup_style(self):
        """Configure matplotlib with professional styling."""
        plt.style.use('seaborn-v0_8-whitegrid')

        # Set default font sizes
        font_config = self._chart_config.get("font", {})
        plt.rcParams.update({
            'font.family': font_config.get("family", "sans-serif"),
            'font.size': font_config.get("label_size", 11),
            'axes.titlesize': font_config.get("title_size", 14),
            'axes.labelsize': font_config.get("label_size", 11),
            'xtick.labelsize': font_config.get("tick_size", 10),
            'ytick.labelsize': font_config.get("tick_size", 10),
            'legend.fontsize': font_config.get("legend_size", 10),
            'figure.titlesize': font_config.get("title_size", 14),
        })

    def _get_figure_size(self, size_type: str = "default") -> Tuple[int, int]:
        """Get figure size from configuration."""
        sizes = self._chart_config.get("figure_size", {})
        return tuple(sizes.get(size_type, [10, 6]))

    def _get_dpi(self) -> int:
        """Get DPI from configuration."""
        return self._chart_config.get("dpi", 150)

    def _apply_common_styling(self, ax: plt.Axes, title: str):
        """Apply common styling to an axis."""
        ax.set_title(title, fontweight='bold', pad=15, color=self._colors.get("text", "#111827"))

        # Grid styling
        grid_config = self._chart_config.get("grid", {})
        if grid_config.get("show", True):
            ax.grid(True, alpha=grid_config.get("alpha", 0.3),
                   linestyle=grid_config.get("style", "--"))
        else:
            ax.grid(False)

        # Remove top and right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    def create_line_chart(
        self,
        data: pd.DataFrame,
        x_column: str,
        y_columns: Union[str, List[str]],
        title: str = "Line Chart",
        x_label: str = "",
        y_label: str = "",
        aggregation: Optional[str] = None,
        date_format: Optional[str] = None,
        show_markers: bool = True,
        show_legend: bool = True,
    ) -> Figure:
        """
        Create a line chart for trend visualization.

        Args:
            data: DataFrame containing the data
            x_column: Column name for x-axis (usually dates)
            y_columns: Column name(s) for y-axis values
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            aggregation: Aggregation method ('sum', 'mean', 'count')
            date_format: Format string for date axis
            show_markers: Whether to show data point markers
            show_legend: Whether to show legend

        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=self._get_figure_size("default"),
                               dpi=self._get_dpi())

        # Ensure y_columns is a list
        if isinstance(y_columns, str):
            y_columns = [y_columns]

        # Prepare data
        plot_data = data.copy()

        # Check if x_column is datetime
        if pd.api.types.is_datetime64_any_dtype(plot_data[x_column]):
            plot_data = plot_data.sort_values(x_column)

            # Aggregate if requested
            if aggregation:
                plot_data = plot_data.groupby(x_column)[y_columns].agg(aggregation).reset_index()

        line_config = self._chart_config.get("line", {})

        for i, y_col in enumerate(y_columns):
            color = self._chart_palette[i % len(self._chart_palette)]

            if show_markers:
                ax.plot(plot_data[x_column], plot_data[y_col],
                       color=color,
                       linewidth=line_config.get("width", 2.5),
                       marker='o',
                       markersize=line_config.get("marker_size", 6),
                       label=y_col)
            else:
                ax.plot(plot_data[x_column], plot_data[y_col],
                       color=color,
                       linewidth=line_config.get("width", 2.5),
                       label=y_col)

        # Format x-axis for dates
        if pd.api.types.is_datetime64_any_dtype(plot_data[x_column]):
            if date_format:
                ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
            else:
                # Auto-format based on date range
                date_range = (plot_data[x_column].max() - plot_data[x_column].min()).days
                if date_range <= 30:
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                elif date_range <= 90:
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                else:
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

            plt.xticks(rotation=45, ha='right')

        # Labels
        if x_label:
            ax.set_xlabel(x_label)
        if y_label:
            ax.set_ylabel(y_label)

        # Legend
        if show_legend and len(y_columns) > 1:
            legend_config = self._chart_config.get("legend", {})
            ax.legend(loc=legend_config.get("location", "best"),
                     frameon=legend_config.get("frameon", True),
                     framealpha=legend_config.get("framealpha", 0.9))

        self._apply_common_styling(ax, title)
        plt.tight_layout()

        return fig

    def create_bar_chart(
        self,
        data: pd.DataFrame,
        category_column: str,
        value_column: str,
        title: str = "Bar Chart",
        x_label: str = "",
        y_label: str = "",
        orientation: str = "vertical",
        limit: int = 10,
        sort_by_value: bool = True,
        show_values: bool = True,
        color: Optional[str] = None,
    ) -> Figure:
        """
        Create a bar chart for category comparisons.

        Args:
            data: DataFrame containing the data
            category_column: Column name for categories
            value_column: Column name for values
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            orientation: 'vertical' or 'horizontal'
            limit: Maximum number of bars to show
            sort_by_value: Whether to sort bars by value
            show_values: Whether to show value labels on bars
            color: Optional specific color for bars

        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=self._get_figure_size("default"),
                               dpi=self._get_dpi())

        # Prepare data - aggregate by category
        plot_data = data.groupby(category_column)[value_column].sum().reset_index()

        if sort_by_value:
            plot_data = plot_data.sort_values(value_column, ascending=False)

        # Limit to top N
        plot_data = plot_data.head(limit)

        bar_config = self._chart_config.get("bar", {})
        bar_color = color or self._colors.get("primary", "#2563EB")

        if orientation == "horizontal":
            # Reverse for horizontal so highest is at top
            plot_data = plot_data.iloc[::-1]
            bars = ax.barh(plot_data[category_column], plot_data[value_column],
                          color=bar_color,
                          edgecolor=bar_config.get("edge_color", "white"),
                          linewidth=bar_config.get("edge_width", 0.5))

            if show_values:
                for bar, value in zip(bars, plot_data[value_column]):
                    ax.text(value + (max(plot_data[value_column]) * 0.01),
                           bar.get_y() + bar.get_height()/2,
                           format_number(value),
                           va='center', fontsize=9)

            if x_label:
                ax.set_xlabel(x_label)
            if y_label:
                ax.set_ylabel(y_label)

        else:  # vertical
            bars = ax.bar(plot_data[category_column], plot_data[value_column],
                         color=bar_color,
                         width=bar_config.get("width", 0.7),
                         edgecolor=bar_config.get("edge_color", "white"),
                         linewidth=bar_config.get("edge_width", 0.5))

            if show_values:
                for bar, value in zip(bars, plot_data[value_column]):
                    ax.text(bar.get_x() + bar.get_width()/2,
                           bar.get_height() + (max(plot_data[value_column]) * 0.01),
                           format_number(value),
                           ha='center', va='bottom', fontsize=9)

            plt.xticks(rotation=45, ha='right')

            if x_label:
                ax.set_xlabel(x_label)
            if y_label:
                ax.set_ylabel(y_label)

        self._apply_common_styling(ax, title)
        plt.tight_layout()

        return fig

    def create_grouped_bar_chart(
        self,
        data: pd.DataFrame,
        category_column: str,
        value_columns: List[str],
        title: str = "Grouped Bar Chart",
        x_label: str = "",
        y_label: str = "",
        show_legend: bool = True,
    ) -> Figure:
        """
        Create a grouped bar chart for comparing multiple series.

        Args:
            data: DataFrame containing the data
            category_column: Column name for categories
            value_columns: List of column names for values
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            show_legend: Whether to show legend

        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=self._get_figure_size("default"),
                               dpi=self._get_dpi())

        x = np.arange(len(data[category_column]))
        width = 0.8 / len(value_columns)

        bar_config = self._chart_config.get("bar", {})

        for i, col in enumerate(value_columns):
            offset = (i - len(value_columns)/2 + 0.5) * width
            bars = ax.bar(x + offset, data[col],
                         width=width,
                         label=col,
                         color=self._chart_palette[i % len(self._chart_palette)],
                         edgecolor=bar_config.get("edge_color", "white"),
                         linewidth=bar_config.get("edge_width", 0.5))

        ax.set_xticks(x)
        ax.set_xticklabels(data[category_column], rotation=45, ha='right')

        if x_label:
            ax.set_xlabel(x_label)
        if y_label:
            ax.set_ylabel(y_label)

        if show_legend:
            legend_config = self._chart_config.get("legend", {})
            ax.legend(loc=legend_config.get("location", "best"),
                     frameon=legend_config.get("frameon", True))

        self._apply_common_styling(ax, title)
        plt.tight_layout()

        return fig

    def create_pie_chart(
        self,
        data: pd.DataFrame,
        category_column: str,
        value_column: str,
        title: str = "Pie Chart",
        limit: int = 8,
        show_percentages: bool = True,
        show_legend: bool = True,
        explode_largest: bool = False,
    ) -> Figure:
        """
        Create a pie chart for distribution visualization.

        Args:
            data: DataFrame containing the data
            category_column: Column name for categories
            value_column: Column name for values
            title: Chart title
            limit: Maximum number of slices (others grouped as "Other")
            show_percentages: Whether to show percentage labels
            show_legend: Whether to show legend
            explode_largest: Whether to explode the largest slice

        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=self._get_figure_size("pie"),
                               dpi=self._get_dpi())

        # Prepare data - aggregate by category
        plot_data = data.groupby(category_column)[value_column].sum().reset_index()
        plot_data = plot_data.sort_values(value_column, ascending=False)

        # Group small slices into "Other"
        if len(plot_data) > limit:
            top_data = plot_data.head(limit - 1)
            other_value = plot_data.iloc[limit-1:][value_column].sum()
            other_row = pd.DataFrame({
                category_column: ["Other"],
                value_column: [other_value]
            })
            plot_data = pd.concat([top_data, other_row], ignore_index=True)

        pie_config = self._chart_config.get("pie", {})

        # Explode configuration
        explode = None
        if explode_largest:
            explode = [pie_config.get("explode_max", 0.05)] + [0] * (len(plot_data) - 1)

        # Colors
        colors = self._chart_palette[:len(plot_data)]

        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            plot_data[value_column],
            labels=plot_data[category_column] if not show_legend else None,
            autopct=pie_config.get("autopct", "%1.1f%%") if show_percentages else None,
            startangle=pie_config.get("start_angle", 90),
            colors=colors,
            explode=explode,
            shadow=pie_config.get("shadow", False),
            pctdistance=0.75,
        )

        # Style the percentage labels
        if show_percentages:
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)

        # Add legend
        if show_legend:
            legend_config = self._chart_config.get("legend", {})
            ax.legend(wedges, plot_data[category_column],
                     loc='center left',
                     bbox_to_anchor=(1, 0.5),
                     frameon=legend_config.get("frameon", True))

        ax.set_title(title, fontweight='bold', pad=15,
                    color=self._colors.get("text", "#111827"))

        plt.tight_layout()

        return fig

    def create_trend_chart_with_aggregation(
        self,
        data: pd.DataFrame,
        date_column: str,
        value_column: str,
        title: str = "Trend Chart",
        y_label: str = "",
        period: str = "auto",
        aggregation: str = "sum",
        show_markers: bool = True,
    ) -> Figure:
        """
        Create a line chart with automatic date aggregation.

        Args:
            data: DataFrame containing the data
            date_column: Column name for dates
            value_column: Column name for values
            title: Chart title
            y_label: Y-axis label
            period: Aggregation period ('daily', 'weekly', 'monthly', 'auto')
            aggregation: Aggregation method ('sum', 'mean', 'count')
            show_markers: Whether to show data point markers

        Returns:
            matplotlib Figure object
        """
        plot_data = data.copy()

        # Ensure date column is datetime
        plot_data[date_column] = pd.to_datetime(plot_data[date_column])
        plot_data = plot_data.sort_values(date_column)

        # Determine period if auto
        if period == "auto":
            date_range = (plot_data[date_column].max() - plot_data[date_column].min()).days
            if date_range <= 31:
                period = "daily"
            elif date_range <= 90:
                period = "weekly"
            else:
                period = "monthly"

        # Aggregate by period
        if period == "daily":
            plot_data['period'] = plot_data[date_column].dt.date
        elif period == "weekly":
            plot_data['period'] = plot_data[date_column].dt.to_period('W').dt.start_time
        else:  # monthly
            plot_data['period'] = plot_data[date_column].dt.to_period('M').dt.start_time

        agg_data = plot_data.groupby('period')[value_column].agg(aggregation).reset_index()
        agg_data['period'] = pd.to_datetime(agg_data['period'])

        return self.create_line_chart(
            agg_data,
            x_column='period',
            y_columns=value_column,
            title=title,
            y_label=y_label,
            show_markers=show_markers,
            show_legend=False,
        )

    def save_figure(
        self,
        fig: Figure,
        filepath: Union[str, Path],
        format: str = "png",
        transparent: bool = False,
    ) -> str:
        """
        Save a figure to file.

        Args:
            fig: matplotlib Figure object
            filepath: Output file path
            format: Output format (png, pdf, svg)
            transparent: Whether to use transparent background

        Returns:
            Path to saved file
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        fig.savefig(
            filepath,
            format=format,
            dpi=self._get_dpi(),
            bbox_inches='tight',
            transparent=transparent,
            facecolor='white' if not transparent else 'none',
        )

        plt.close(fig)
        return str(filepath)

    def figure_to_bytes(self, fig: Figure, format: str = "png") -> bytes:
        """
        Convert a figure to bytes for embedding.

        Args:
            fig: matplotlib Figure object
            format: Output format (png, pdf, svg)

        Returns:
            Image bytes
        """
        buf = io.BytesIO()
        fig.savefig(
            buf,
            format=format,
            dpi=self._get_dpi(),
            bbox_inches='tight',
            facecolor='white',
        )
        buf.seek(0)
        plt.close(fig)
        return buf.getvalue()

    def figure_to_base64(self, fig: Figure, format: str = "png") -> str:
        """
        Convert a figure to base64 string for web embedding.

        Args:
            fig: matplotlib Figure object
            format: Output format

        Returns:
            Base64 encoded string
        """
        import base64
        image_bytes = self.figure_to_bytes(fig, format)
        return base64.b64encode(image_bytes).decode('utf-8')

    def close_all(self):
        """Close all open figures to free memory."""
        plt.close('all')
