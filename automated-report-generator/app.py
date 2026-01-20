"""
Automated Report Generator - Streamlit Application

A step-by-step wizard for generating professional PDF and Word reports
from CSV/Excel data with AI-powered insights.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import tempfile
import base64
from io import BytesIO

from src.data_processor import DataProcessor
from src.utils import load_config
from templates import get_template, TEMPLATES


# Page configuration
st.set_page_config(
    page_title="Automated Report Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Header styling */
    .main-header {
        text-align: center;
        padding: 1rem 0 2rem 0;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 2rem;
    }

    .main-header h1 {
        color: #1e3a5f;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    .main-header p {
        color: #666;
        font-size: 1.1rem;
    }

    /* Step indicator styling */
    .step-container {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
        gap: 0;
    }

    .step {
        display: flex;
        align-items: center;
        padding: 0.75rem 1.5rem;
        background: #f5f5f5;
        color: #888;
        font-weight: 500;
        border: 1px solid #e0e0e0;
    }

    .step.active {
        background: #2563eb;
        color: white;
        border-color: #2563eb;
    }

    .step.completed {
        background: #10b981;
        color: white;
        border-color: #10b981;
    }

    .step-number {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: rgba(255,255,255,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 0.75rem;
        font-weight: bold;
    }

    .step.active .step-number,
    .step.completed .step-number {
        background: rgba(255,255,255,0.3);
    }

    /* Card styling */
    .stCard {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }

    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }

    /* Success message styling */
    .success-box {
        background: #d1fae5;
        border: 1px solid #10b981;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }

    /* Error message styling */
    .error-box {
        background: #fee2e2;
        border: 1px solid #ef4444;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }

    /* Warning message styling */
    .warning-box {
        background: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }

    /* Metric styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 1.25rem;
        color: white;
        text-align: center;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }

    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Data preview table */
    .dataframe {
        font-size: 0.9rem;
    }

    /* Template card */
    .template-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.25rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.2s;
    }

    .template-card:hover {
        border-color: #2563eb;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
    }

    .template-card.selected {
        border-color: #2563eb;
        background: #eff6ff;
    }

    .template-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e3a5f;
        margin-bottom: 0.5rem;
    }

    .template-description {
        color: #666;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'processor' not in st.session_state:
        st.session_state.processor = None
    if 'selected_template' not in st.session_state:
        st.session_state.selected_template = None
    if 'column_mapping' not in st.session_state:
        st.session_state.column_mapping = {}
    if 'generated_reports' not in st.session_state:
        st.session_state.generated_reports = {}
    if 'include_ai' not in st.session_state:
        st.session_state.include_ai = True
    if 'output_formats' not in st.session_state:
        st.session_state.output_formats = ['pdf']


def render_header():
    """Render the main header."""
    st.markdown("""
    <div class="main-header">
        <h1>Automated Report Generator</h1>
        <p>Transform your data into professional reports with AI-powered insights</p>
    </div>
    """, unsafe_allow_html=True)


def render_step_indicator():
    """Render the step progress indicator."""
    steps = [
        ("1", "Upload Data"),
        ("2", "Configure"),
        ("3", "Generate"),
        ("4", "Download"),
    ]

    html = '<div class="step-container">'
    for i, (num, label) in enumerate(steps, 1):
        if i < st.session_state.step:
            status = "completed"
            icon = "✓"
        elif i == st.session_state.step:
            status = "active"
            icon = num
        else:
            status = ""
            icon = num

        html += f'''
        <div class="step {status}">
            <span class="step-number">{icon}</span>
            {label}
        </div>
        '''
    html += '</div>'

    st.markdown(html, unsafe_allow_html=True)


def render_step_1_upload():
    """Render Step 1: Data Upload."""
    st.markdown("### Step 1: Upload Your Data")
    st.markdown("Upload one or more CSV/Excel files to get started. Multiple files will be combined into a single dataset.")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_files = st.file_uploader(
            "Choose file(s)",
            type=['csv', 'xlsx', 'xls'],
            help="Supported formats: CSV, Excel (.xlsx, .xls). Upload multiple files to combine them.",
            accept_multiple_files=True,
        )

        if uploaded_files:
            try:
                # Create processor and load data
                processor = DataProcessor()

                # Save files temporarily and collect paths
                tmp_paths = []
                file_names = []
                for uploaded_file in uploaded_files:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_paths.append(tmp.name)
                        file_names.append(uploaded_file.name)

                # Load single or multiple files
                if len(tmp_paths) == 1:
                    processor.load_file(tmp_paths[0])
                else:
                    processor.load_multiple_files(tmp_paths, file_names)

                # Store in session
                st.session_state.uploaded_file = uploaded_files
                st.session_state.df = processor.df
                st.session_state.processor = processor

                # Show success message
                if len(uploaded_files) == 1:
                    st.success(f"Successfully loaded **{file_names[0]}** ({len(processor.df):,} rows, {len(processor.df.columns)} columns)")
                else:
                    st.success(f"Successfully combined **{len(uploaded_files)} files** ({len(processor.df):,} total rows, {len(processor.df.columns)} columns)")
                    with st.expander("Files loaded"):
                        for name in file_names:
                            st.markdown(f"- {name}")

                # Show any warnings from loading
                if processor.validation_warnings:
                    for warning in processor.validation_warnings:
                        st.warning(warning)

                # Data preview
                st.markdown("#### Data Preview")
                st.dataframe(processor.df.head(10), use_container_width=True)

                # Column info
                st.markdown("#### Detected Columns")
                col_types = processor.detect_column_types()

                col_df = pd.DataFrame([
                    {
                        "Column": col,
                        "Type": col_types.get(col, "unknown").capitalize(),
                        "Sample Values": ", ".join(str(v) for v in processor.df[col].dropna().head(3).tolist())
                    }
                    for col in processor.df.columns
                ])
                st.dataframe(col_df, use_container_width=True, hide_index=True)

                # Suggest template
                suggested, confidence = processor.suggest_template()
                if suggested:
                    st.info(f"**Suggested Template:** {suggested.replace('_', ' ').title()} Report (confidence: {confidence:.0%})")
                    st.session_state.selected_template = suggested

                # Continue button
                st.markdown("---")
                if st.button("Continue to Configuration", type="primary", use_container_width=True):
                    st.session_state.step = 2
                    st.rerun()

            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
                st.markdown("""
                **Troubleshooting tips:**
                - Make sure your file is a valid CSV or Excel file
                - Check that the file isn't corrupted or password-protected
                - Ensure the file contains data with headers
                """)

    with col2:
        st.markdown("#### Quick Start")
        st.markdown("""
        **Sample data available:**

        Try our demo with sample data files in the `sample_data/` folder:
        - `sales_sample.csv` - Sales transactions
        - `financial_sample.csv` - Financial records
        - `inventory_sample.csv` - Inventory data
        """)

        st.markdown("#### Supported Formats")
        st.markdown("""
        - **CSV** - Comma-separated values
        - **Excel** - .xlsx and .xls files
        - **Multiple files** - Upload and combine
        - **Max size:** 10MB per file
        - **Max rows:** 500,000 total
        """)


def render_step_2_configure():
    """Render Step 2: Configuration."""
    st.markdown("### Step 2: Configure Your Report")

    if st.session_state.processor is None:
        st.warning("Please upload data first.")
        if st.button("Go Back to Upload"):
            st.session_state.step = 1
            st.rerun()
        return

    processor = st.session_state.processor

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### Select Report Template")

        # Template selection
        templates_config = load_config("templates")
        template_options = list(TEMPLATES.keys())

        # Format template names for display
        template_display = {
            t: templates_config['templates'][t]['name']
            for t in template_options
        }

        selected = st.radio(
            "Choose a template:",
            template_options,
            format_func=lambda x: template_display.get(x, x),
            index=template_options.index(st.session_state.selected_template) if st.session_state.selected_template in template_options else 0,
            help="Select the type of report that best matches your data"
        )
        st.session_state.selected_template = selected

        # Template description
        template_info = templates_config['templates'].get(selected, {})
        st.markdown(f"**Description:** {template_info.get('description', 'N/A')}")

        # Required columns info
        required = template_info.get('required_columns', {})
        st.markdown("**Required columns:**")
        for field, info in required.items():
            st.markdown(f"- {field.replace('_', ' ').title()}: {info.get('type', 'any')}")

    with col2:
        st.markdown("#### Column Mapping")
        st.markdown("Map your data columns to the template fields:")

        # Set template and auto-map
        processor.set_template(selected)
        processor.auto_map_columns()

        # Get column mapping
        template_config = templates_config['templates'].get(selected, {})
        all_fields = list(template_config.get('required_columns', {}).keys()) + list(template_config.get('optional_columns', {}).keys())

        column_mapping = {}
        data_columns = ['(None)'] + list(processor.df.columns)

        for field in all_fields:
            is_required = field in template_config.get('required_columns', {})
            current_mapping = processor.column_mapping.get(field)
            default_idx = data_columns.index(current_mapping) if current_mapping in data_columns else 0

            label = f"{field.replace('_', ' ').title()}"
            if is_required:
                label += " *"

            selected_col = st.selectbox(
                label,
                data_columns,
                index=default_idx,
                key=f"map_{field}"
            )

            if selected_col != '(None)':
                column_mapping[field] = selected_col

        st.session_state.column_mapping = column_mapping

        # Validate mapping
        processor.set_column_mapping(column_mapping)
        is_valid, errors, warnings = processor.validate_mapping()

        if errors:
            for error in errors:
                st.error(f"{error}")

        if warnings:
            for warning in warnings:
                st.warning(f"{warning}")

        if is_valid:
            st.success("Column mapping is valid!")

    # Generation options
    st.markdown("---")
    st.markdown("#### Generation Options")

    opt_col1, opt_col2 = st.columns(2)

    with opt_col1:
        st.session_state.include_ai = st.checkbox(
            "Include AI-Generated Insights",
            value=st.session_state.include_ai,
            help="Generate intelligent insights using OpenRouter API (requires API key)"
        )

    with opt_col2:
        format_options = st.multiselect(
            "Output Formats",
            ['pdf', 'docx'],
            default=st.session_state.output_formats,
            help="Select one or more output formats"
        )
        st.session_state.output_formats = format_options if format_options else ['pdf']

    # Navigation buttons
    st.markdown("---")
    nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])

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
                st.caption("Fix validation errors to continue")
            elif not st.session_state.output_formats:
                st.caption("Select at least one output format")


def render_step_3_generate():
    """Render Step 3: Report Generation."""
    st.markdown("### Step 3: Generating Report")

    if st.session_state.processor is None or st.session_state.selected_template is None:
        st.warning("Please complete the previous steps first.")
        if st.button("Start Over"):
            st.session_state.step = 1
            st.rerun()
        return

    # Progress container
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Get template class
        template_class = get_template(st.session_state.selected_template)
        template = template_class()

        # Create temp output directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            status_text.text("Processing data...")
            progress_bar.progress(20)

            status_text.text("Generating charts...")
            progress_bar.progress(40)

            if st.session_state.include_ai:
                status_text.text("Generating AI insights...")
            progress_bar.progress(60)

            status_text.text("Building report...")
            progress_bar.progress(80)

            # Generate the report
            output_files = template.generate(
                data_source=st.session_state.df,
                output_dir=tmp_dir,
                formats=st.session_state.output_formats,
                include_ai_insights=st.session_state.include_ai,
                column_mapping=st.session_state.column_mapping,
            )

            progress_bar.progress(100)
            status_text.text("Report generated successfully!")

            # Read generated files into memory
            generated_reports = {}
            for fmt, filepath in output_files.items():
                with open(filepath, 'rb') as f:
                    generated_reports[fmt] = {
                        'data': f.read(),
                        'filename': Path(filepath).name,
                    }

            st.session_state.generated_reports = generated_reports

            # Auto-advance to download step
            st.session_state.step = 4
            st.rerun()

    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"Error generating report: {str(e)}")
        st.markdown("""
        **Troubleshooting tips:**
        - Check that your column mapping is correct
        - Ensure your data doesn't have too many missing values
        - Try disabling AI insights if you don't have an API key
        """)

        if st.button("Back to Configuration"):
            st.session_state.step = 2
            st.rerun()


def render_step_4_download():
    """Render Step 4: Download Reports."""
    st.markdown("### Step 4: Download Your Reports")

    if not st.session_state.generated_reports:
        st.warning("No reports have been generated yet.")
        if st.button("Start Over"):
            st.session_state.step = 1
            st.rerun()
        return

    st.success("Your reports are ready for download!")

    # Display download options
    col1, col2 = st.columns(2)

    for i, (fmt, report_data) in enumerate(st.session_state.generated_reports.items()):
        col = col1 if i % 2 == 0 else col2

        with col:
            st.markdown(f"#### {fmt.upper()} Report")

            # File info
            file_size = len(report_data['data']) / 1024  # KB
            st.markdown(f"**Filename:** {report_data['filename']}")
            st.markdown(f"**Size:** {file_size:.1f} KB")

            # Download button
            st.download_button(
                label=f"Download {fmt.upper()}",
                data=report_data['data'],
                file_name=report_data['filename'],
                mime='application/pdf' if fmt == 'pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                use_container_width=True,
            )

            # PDF Preview (only for PDF)
            if fmt == 'pdf':
                with st.expander("Preview PDF"):
                    # Convert to base64 for iframe display
                    b64 = base64.b64encode(report_data['data']).decode()
                    pdf_display = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="600" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)

    # Summary
    st.markdown("---")
    st.markdown("### Report Summary")

    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

    with summary_col1:
        st.metric("Template", st.session_state.selected_template.replace('_', ' ').title())

    with summary_col2:
        st.metric("Data Rows", f"{len(st.session_state.df):,}")

    with summary_col3:
        st.metric("Formats", ", ".join(f.upper() for f in st.session_state.output_formats))

    with summary_col4:
        st.metric("AI Insights", "Yes" if st.session_state.include_ai else "No")

    # Start over button
    st.markdown("---")
    if st.button("Generate Another Report", type="primary", use_container_width=True):
        # Reset session state
        st.session_state.step = 1
        st.session_state.uploaded_file = None
        st.session_state.df = None
        st.session_state.processor = None
        st.session_state.selected_template = None
        st.session_state.column_mapping = {}
        st.session_state.generated_reports = {}
        st.rerun()


def main():
    """Main application entry point."""
    init_session_state()
    render_header()
    render_step_indicator()

    # Render current step
    if st.session_state.step == 1:
        render_step_1_upload()
    elif st.session_state.step == 2:
        render_step_2_configure()
    elif st.session_state.step == 3:
        render_step_3_generate()
    elif st.session_state.step == 4:
        render_step_4_download()

    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #888; font-size: 0.9rem;'>"
        "Automated Report Generator v1.0 | Built with Streamlit and OpenRouter AI"
        "</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
