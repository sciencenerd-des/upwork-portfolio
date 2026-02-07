"""
Automated Report Generator - Streamlit Application.

A step-by-step wizard for generating professional PDF and Word reports
from CSV/Excel data with AI-powered insights.
"""

import base64
import html
from pathlib import Path
import tempfile

import pandas as pd
import streamlit as st

from src.ai_insights import AIInsights
from src.data_processor import DataProcessor
from src.utils import load_config
from templates import TEMPLATES, get_template


ASSETS_DIR = Path(__file__).parent / "assets"
STYLE_PATH = ASSETS_DIR / "styles.css"


# Page configuration
st.set_page_config(
    page_title="Automated Report Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def load_custom_styles() -> None:
    """Load the enterprise theme stylesheet."""
    if STYLE_PATH.exists():
        css = STYLE_PATH.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def init_session_state() -> None:
    """Initialize session state variables."""
    if "step" not in st.session_state:
        st.session_state.step = 1
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
    if "df" not in st.session_state:
        st.session_state.df = None
    if "processor" not in st.session_state:
        st.session_state.processor = None
    if "selected_template" not in st.session_state:
        st.session_state.selected_template = None
    if "column_mapping" not in st.session_state:
        st.session_state.column_mapping = {}
    if "generated_reports" not in st.session_state:
        st.session_state.generated_reports = {}
    if "include_ai" not in st.session_state:
        st.session_state.include_ai = True
    if "output_formats" not in st.session_state:
        st.session_state.output_formats = ["pdf"]
    if "ai_insights_preview" not in st.session_state:
        st.session_state.ai_insights_preview = []


def reset_workflow() -> None:
    """Reset workflow state for a new report run."""
    st.session_state.step = 1
    st.session_state.uploaded_file = None
    st.session_state.df = None
    st.session_state.processor = None
    st.session_state.selected_template = None
    st.session_state.column_mapping = {}
    st.session_state.generated_reports = {}
    st.session_state.ai_insights_preview = []


def build_ai_insights_preview(df: pd.DataFrame, template_name: str, mapping: dict) -> list[str]:
    """Build a short AI insights list to display in the UI."""
    if df is None or not template_name or not mapping:
        return []

    insights_engine = AIInsights()
    calculators = {
        "sales": insights_engine.calculate_sales_summary,
        "financial": insights_engine.calculate_financial_summary,
        "inventory": insights_engine.calculate_inventory_summary,
    }

    calculate_summary = calculators.get(template_name)
    if calculate_summary is None:
        return []

    summary = calculate_summary(df.copy(), mapping)
    return insights_engine.generate_insights(
        summary,
        template_type=template_name,
        max_insights=5,
        use_ai=insights_engine.is_available,
    )


def render_header() -> None:
    """Render the main enterprise header."""
    st.markdown(
        """
        <div class="hero-shell fade-in">
            <span class="hero-badge">Enterprise Professional</span>
            <h1>Automated Report Generator</h1>
            <p>Turns 4 hours of manual Excel work into 30 seconds with reliable, executive-ready reporting.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_step_indicator() -> None:
    """Render the step progress indicator."""
    steps = [
        ("1", "Upload Data"),
        ("2", "Configure"),
        ("3", "Generate"),
        ("4", "Download"),
    ]

    html_steps = '<div class="step-shell fade-in">'
    for i, (num, label) in enumerate(steps, 1):
        if i < st.session_state.step:
            status = "completed"
            icon = "✓"
        elif i == st.session_state.step:
            status = "active"
            icon = num
        else:
            status = "pending"
            icon = num

        html_steps += f"""
        <div class="step-pill {status}">
            <span class="step-pill-number">{icon}</span>
            <span>{label}</span>
        </div>
        """
    html_steps += "</div>"

    st.markdown(html_steps, unsafe_allow_html=True)


def render_step_1_upload() -> None:
    """Render Step 1: Data Upload."""
    st.markdown(
        """
        <div class="section-title fade-in">
            <h3>Step 1: Upload Your Data</h3>
            <p>Upload one or more CSV/Excel files. Multiple files are merged into a single analysis-ready dataset.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([2, 1], gap="large")

    with col1:
        with st.container(border=True):
            st.markdown("#### Data Upload")
            uploaded_files = st.file_uploader(
                "Choose file(s)",
                type=["csv", "xlsx", "xls"],
                help="Supported formats: CSV, Excel (.xlsx, .xls). Upload multiple files to combine them.",
                accept_multiple_files=True,
            )

            if uploaded_files:
                try:
                    processor = DataProcessor()

                    tmp_paths = []
                    file_names = []
                    for uploaded_file in uploaded_files:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                            tmp.write(uploaded_file.getvalue())
                            tmp_paths.append(tmp.name)
                            file_names.append(uploaded_file.name)

                    if len(tmp_paths) == 1:
                        processor.load_file(tmp_paths[0])
                    else:
                        processor.load_multiple_files(tmp_paths, file_names)

                    st.session_state.uploaded_file = uploaded_files
                    st.session_state.df = processor.df
                    st.session_state.processor = processor
                    st.session_state.ai_insights_preview = []

                    if len(uploaded_files) == 1:
                        st.success(
                            f"Loaded **{file_names[0]}** ({len(processor.df):,} rows, {len(processor.df.columns)} columns)"
                        )
                    else:
                        st.success(
                            f"Combined **{len(uploaded_files)} files** ({len(processor.df):,} rows, {len(processor.df.columns)} columns)"
                        )
                        with st.expander("Files loaded"):
                            for name in file_names:
                                st.markdown(f"- {name}")

                    if processor.validation_warnings:
                        for warning in processor.validation_warnings:
                            st.warning(warning)

                    st.markdown("#### Data Preview")
                    st.dataframe(processor.df.head(10), use_container_width=True)

                    st.markdown("#### Detected Columns")
                    col_types = processor.detect_column_types()
                    col_df = pd.DataFrame(
                        [
                            {
                                "Column": col,
                                "Type": col_types.get(col, "unknown").capitalize(),
                                "Sample Values": ", ".join(
                                    str(v) for v in processor.df[col].dropna().head(3).tolist()
                                ),
                            }
                            for col in processor.df.columns
                        ]
                    )
                    st.dataframe(col_df, use_container_width=True, hide_index=True)

                    suggested, confidence = processor.suggest_template()
                    if suggested:
                        st.info(
                            f"Suggested template: **{suggested.replace('_', ' ').title()} Report** ({confidence:.0%} confidence)"
                        )
                        st.session_state.selected_template = suggested

                    st.markdown("---")
                    if st.button("Continue to Configuration", type="primary", use_container_width=True):
                        st.session_state.step = 2
                        st.rerun()

                except Exception as exc:
                    st.error(f"Error loading file: {exc}")
                    st.markdown(
                        """
                        **Troubleshooting tips:**
                        - Make sure the file is a valid CSV or Excel file
                        - Check that the file is not corrupted or password-protected
                        - Ensure the file contains data with headers
                        """
                    )

    with col2:
        with st.container(border=True):
            st.markdown("#### Quick Start")
            st.markdown(
                """
                **Sample data available:**
                - `sample_data/sales_sample.csv`
                - `sample_data/financial_sample.csv`
                - `sample_data/inventory_sample.csv`
                """
            )

            st.markdown("#### Supported Formats")
            st.markdown(
                """
                - **CSV** and **Excel** (`.xlsx`, `.xls`)
                - **Multiple files** can be combined
                - **Max size:** 10MB per file
                - **Max rows:** 500,000 total
                """
            )


def render_step_2_configure() -> None:
    """Render Step 2: Configuration."""
    st.markdown(
        """
        <div class="section-title fade-in">
            <h3>Step 2: Configure Your Report</h3>
            <p>Select a template, validate column mappings, and choose output options.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.processor is None:
        st.warning("Please upload data first.")
        if st.button("Go Back to Upload"):
            st.session_state.step = 1
            st.rerun()
        return

    processor = st.session_state.processor
    templates_config = load_config("templates")
    template_options = list(TEMPLATES.keys())
    template_display = {
        template_name: templates_config["templates"][template_name]["name"]
        for template_name in template_options
    }

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        with st.container(border=True):
            st.markdown("#### Report Template")

            selected = st.radio(
                "Choose a template",
                template_options,
                format_func=lambda x: template_display.get(x, x),
                index=template_options.index(st.session_state.selected_template)
                if st.session_state.selected_template in template_options
                else 0,
                help="Select the report type that best matches your data.",
            )
            st.session_state.selected_template = selected

            template_info = templates_config["templates"].get(selected, {})
            st.markdown(f"**Description:** {template_info.get('description', 'N/A')}")
            st.markdown("**Required Columns**")
            for field, info in template_info.get("required_columns", {}).items():
                st.markdown(f"- {field.replace('_', ' ').title()}: {info.get('type', 'any')}")

    with col2:
        with st.container(border=True):
            st.markdown("#### Column Mapping")
            st.markdown("Map your dataset fields to template inputs.")

            processor.set_template(selected)
            processor.auto_map_columns()

            template_config = templates_config["templates"].get(selected, {})
            all_fields = list(template_config.get("required_columns", {}).keys()) + list(
                template_config.get("optional_columns", {}).keys()
            )

            column_mapping = {}
            data_columns = ["(None)"] + list(processor.df.columns)

            for field in all_fields:
                is_required = field in template_config.get("required_columns", {})
                current_mapping = processor.column_mapping.get(field)
                default_idx = data_columns.index(current_mapping) if current_mapping in data_columns else 0

                label = field.replace("_", " ").title()
                if is_required:
                    label += " *"

                selected_col = st.selectbox(
                    label,
                    data_columns,
                    index=default_idx,
                    key=f"map_{field}",
                )

                if selected_col != "(None)":
                    column_mapping[field] = selected_col

            st.session_state.column_mapping = column_mapping
            processor.set_column_mapping(column_mapping)
            is_valid, errors, warnings = processor.validate_mapping()

            if errors:
                for error in errors:
                    st.error(error)
            if warnings:
                for warning in warnings:
                    st.warning(warning)
            if is_valid:
                st.success("Column mapping is valid.")

    with st.container(border=True):
        st.markdown("#### Generation Options")

        opt_col1, opt_col2 = st.columns(2)
        with opt_col1:
            st.session_state.include_ai = st.checkbox(
                "Include AI-Generated Insights",
                value=st.session_state.include_ai,
                help="Uses OpenRouter when configured; otherwise falls back to statistical insights.",
            )

        with opt_col2:
            format_options = st.multiselect(
                "Output Formats",
                ["pdf", "docx"],
                default=st.session_state.output_formats,
                help="Select one or more output formats.",
            )
            st.session_state.output_formats = format_options if format_options else ["pdf"]

        st.markdown("---")
        nav_col1, _, nav_col3 = st.columns([1, 1, 1])

        with nav_col1:
            if st.button("Back to Upload", use_container_width=True):
                st.session_state.step = 1
                st.rerun()

        with nav_col3:
            if is_valid and st.session_state.output_formats:
                if st.button("Generate Report", type="primary", use_container_width=True):
                    st.session_state.step = 3
                    st.rerun()
            else:
                st.button("Generate Report", type="primary", use_container_width=True, disabled=True)
                if not is_valid:
                    st.caption("Fix validation errors to continue.")
                elif not st.session_state.output_formats:
                    st.caption("Select at least one output format.")


def render_step_3_generate() -> None:
    """Render Step 3: Report Generation."""
    st.markdown(
        """
        <div class="section-title fade-in">
            <h3>Step 3: Generating Report</h3>
            <p>Compiling analytics, charts, and narrative sections into professional output files.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.processor is None or st.session_state.selected_template is None:
        st.warning("Please complete the previous steps first.")
        if st.button("Start Over"):
            reset_workflow()
            st.rerun()
        return

    with st.container(border=True):
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            template_class = get_template(st.session_state.selected_template)
            template = template_class()

            with tempfile.TemporaryDirectory() as tmp_dir:
                status_text.text("Processing data...")
                progress_bar.progress(20)

                status_text.text("Generating charts...")
                progress_bar.progress(40)

                if st.session_state.include_ai:
                    status_text.text("Generating AI insights...")
                else:
                    status_text.text("Skipping AI insights (disabled)")
                progress_bar.progress(60)

                status_text.text("Building report...")
                progress_bar.progress(80)

                output_files = template.generate(
                    data_source=st.session_state.df,
                    output_dir=tmp_dir,
                    formats=st.session_state.output_formats,
                    include_ai_insights=st.session_state.include_ai,
                    column_mapping=st.session_state.column_mapping,
                )

                if st.session_state.include_ai:
                    status_text.text("Preparing AI insights preview...")
                    progress_bar.progress(90)
                    st.session_state.ai_insights_preview = build_ai_insights_preview(
                        st.session_state.df,
                        st.session_state.selected_template,
                        st.session_state.column_mapping,
                    )
                else:
                    st.session_state.ai_insights_preview = []

                generated_reports = {}
                for fmt, filepath in output_files.items():
                    with open(filepath, "rb") as file_handle:
                        generated_reports[fmt] = {
                            "data": file_handle.read(),
                            "filename": Path(filepath).name,
                        }

                st.session_state.generated_reports = generated_reports

                progress_bar.progress(100)
                status_text.text("Report generated successfully.")

                st.session_state.step = 4
                st.rerun()

        except Exception as exc:
            progress_bar.empty()
            status_text.empty()
            st.error(f"Error generating report: {exc}")
            st.markdown(
                """
                **Troubleshooting tips:**
                - Check that column mapping is valid
                - Ensure data types are compatible with required fields
                - Disable AI insights if no API key is configured
                """
            )
            if st.button("Back to Configuration"):
                st.session_state.step = 2
                st.rerun()


def render_ai_insights_panel() -> None:
    """Render AI insights preview panel in Step 4."""
    with st.container(border=True):
        st.markdown("#### AI Insights")

        if not st.session_state.include_ai:
            st.info("AI insights were disabled for this report run.")
            return

        insights = st.session_state.ai_insights_preview or []
        if not insights:
            st.info("Insights were not available in this run. Add an OpenRouter API key for model-generated analysis.")
            return

        for idx, insight in enumerate(insights, start=1):
            safe_text = html.escape(insight)
            st.markdown(
                f"<div class='insight-row'><span>{idx}.</span><p>{safe_text}</p></div>",
                unsafe_allow_html=True,
            )


def render_step_4_download() -> None:
    """Render Step 4: Download Reports."""
    st.markdown(
        """
        <div class="section-title fade-in">
            <h3>Step 4: Download and Review</h3>
            <p>Your reports are generated. Download files, preview PDF output, and review AI highlights.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.generated_reports:
        st.warning("No reports have been generated yet.")
        if st.button("Start Over"):
            reset_workflow()
            st.rerun()
        return

    st.success("Your reports are ready for download.")

    col1, col2 = st.columns(2, gap="large")
    for i, (fmt, report_data) in enumerate(st.session_state.generated_reports.items()):
        col = col1 if i % 2 == 0 else col2

        with col:
            with st.container(border=True):
                st.markdown(f"#### {fmt.upper()} Report")

                file_size = len(report_data["data"]) / 1024
                st.markdown(f"**Filename:** `{report_data['filename']}`")
                st.markdown(f"**Size:** {file_size:.1f} KB")

                st.download_button(
                    label=f"Download {fmt.upper()}",
                    data=report_data["data"],
                    file_name=report_data["filename"],
                    mime="application/pdf"
                    if fmt == "pdf"
                    else "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )

                if fmt == "pdf":
                    with st.expander("Preview PDF"):
                        b64_pdf = base64.b64encode(report_data["data"]).decode()
                        pdf_display = (
                            f'<iframe src="data:application/pdf;base64,{b64_pdf}" '
                            "width='100%' height='640' type='application/pdf'></iframe>"
                        )
                        st.markdown(pdf_display, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("#### Report Summary")
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

        with summary_col1:
            st.metric("Template", st.session_state.selected_template.replace("_", " ").title())
        with summary_col2:
            st.metric("Data Rows", f"{len(st.session_state.df):,}")
        with summary_col3:
            st.metric("Formats", ", ".join(fmt.upper() for fmt in st.session_state.output_formats))
        with summary_col4:
            st.metric("AI Insights", "Yes" if st.session_state.include_ai else "No")

    render_ai_insights_panel()

    if st.button("Generate Another Report", type="primary", use_container_width=True):
        reset_workflow()
        st.rerun()


def main() -> None:
    """Main application entry point."""
    init_session_state()
    load_custom_styles()
    render_header()
    render_step_indicator()

    if st.session_state.step == 1:
        render_step_1_upload()
    elif st.session_state.step == 2:
        render_step_2_configure()
    elif st.session_state.step == 3:
        render_step_3_generate()
    elif st.session_state.step == 4:
        render_step_4_download()

    st.markdown(
        "<p class='app-footer'>Automated Report Generator v1.0 | Built with Streamlit and OpenRouter AI</p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
