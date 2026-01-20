"""
Automated Report Generator - Streamlit Application

Modern, clean UI inspired by Height, Clay, Sana AI
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import tempfile
import base64
import logging
from io import BytesIO

from src.data_processor import DataProcessor
from src.utils import load_config
from templates import get_template, TEMPLATES

# Import icon system
import sys
sys.path.insert(0, str(Path(__file__).parent / "assets"))
from icons import get_icon, TEMPLATE_ICONS, STATUS_ICONS, FILE_ICONS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# DATA LOADING (Cached)
# ============================================================================

@st.cache_data(show_spinner=False)
def load_and_validate_data(file_content: bytes, file_name: str, sheet_name: str = None) -> pd.DataFrame:
    """Load and validate data from file content."""
    import io
    ext = Path(file_name).suffix.lower()
    if ext == ".csv":
        df = pd.read_csv(io.BytesIO(file_content), encoding="utf-8")
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(io.BytesIO(file_content), sheet_name=sheet_name) if sheet_name else pd.read_excel(io.BytesIO(file_content))
    else:
        raise ValueError(f"Unsupported format: {ext}")
    df.columns = [str(col).strip() for col in df.columns]
    return df


@st.cache_data(show_spinner=False)
def get_excel_sheet_names(file_content: bytes) -> list:
    """Get sheet names from Excel file."""
    import io
    return pd.ExcelFile(io.BytesIO(file_content)).sheet_names


# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Automated Report Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================================
# CSS
# ============================================================================

def load_css():
    """Load CSS from external file."""
    css_path = Path(__file__).parent / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

load_css()


# ============================================================================
# SESSION STATE
# ============================================================================

def init_session_state():
    """Initialize session state."""
    defaults = {
        'step': 1,
        'uploaded_file': None,
        'df': None,
        'processor': None,
        'selected_template': None,
        'column_mapping': {},
        'generated_reports': {},
        'include_ai': True,
        'output_formats': ['pdf'],
        'missing_value_strategy': 'none',
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_html_block(html: str) -> None:
    """Render raw HTML safely without Markdown indentation issues."""
    cleaned = "\n".join(line.lstrip() for line in html.splitlines()).strip()
    st.markdown(cleaned, unsafe_allow_html=True)


def render_landing_hero():
    """Render animated landing hero section with Mobbin-inspired design."""
    render_html_block(f"""
    <div class="landing-hero">
        <!-- Mesh gradient background -->
        <div class="landing-hero__mesh"></div>
        
        <!-- Sweeping light beams -->
        <div class="light-beam light-beam--1"></div>
        <div class="light-beam light-beam--2"></div>
        <div class="light-beam light-beam--3"></div>
        
        <!-- Floating glass cards -->
        <div class="glass-card glass-card--1">
            <div class="glass-card__icon">{get_icon('chart-bar', size=20)}</div>
            <span>Analytics</span>
        </div>
        <div class="glass-card glass-card--2">
            <div class="glass-card__icon">{get_icon('sparkles', size=20)}</div>
            <span>AI Insights</span>
        </div>
        <div class="glass-card glass-card--3">
            <div class="glass-card__icon">{get_icon('file-text', size=20)}</div>
            <span>Reports</span>
        </div>
        
        <!-- Animated node network -->
        <svg class="node-network" viewBox="0 0 400 200" preserveAspectRatio="xMidYMid slice">
            <defs>
                <linearGradient id="nodeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#6366f1;stop-opacity:0.6" />
                    <stop offset="100%" style="stop-color:#a855f7;stop-opacity:0.3" />
                </linearGradient>
            </defs>
            <circle class="node node--1" cx="50" cy="40" r="4" fill="url(#nodeGrad)"/>
            <circle class="node node--2" cx="120" cy="80" r="3" fill="url(#nodeGrad)"/>
            <circle class="node node--3" cx="200" cy="30" r="5" fill="url(#nodeGrad)"/>
            <circle class="node node--4" cx="280" cy="70" r="3" fill="url(#nodeGrad)"/>
            <circle class="node node--5" cx="350" cy="50" r="4" fill="url(#nodeGrad)"/>
            <circle class="node node--6" cx="90" cy="150" r="3" fill="url(#nodeGrad)"/>
            <circle class="node node--7" cx="180" cy="120" r="4" fill="url(#nodeGrad)"/>
            <circle class="node node--8" cx="300" cy="160" r="3" fill="url(#nodeGrad)"/>
            <path class="node-line" d="M50,40 Q85,60 120,80" stroke="url(#nodeGrad)" stroke-width="1" fill="none"/>
            <path class="node-line" d="M120,80 Q160,55 200,30" stroke="url(#nodeGrad)" stroke-width="1" fill="none"/>
            <path class="node-line" d="M200,30 Q240,50 280,70" stroke="url(#nodeGrad)" stroke-width="1" fill="none"/>
            <path class="node-line" d="M280,70 Q315,60 350,50" stroke="url(#nodeGrad)" stroke-width="1" fill="none"/>
            <path class="node-line" d="M90,150 Q135,135 180,120" stroke="url(#nodeGrad)" stroke-width="1" fill="none"/>
            <path class="node-line" d="M180,120 Q240,140 300,160" stroke="url(#nodeGrad)" stroke-width="1" fill="none"/>
            <path class="node-line" d="M120,80 Q105,115 90,150" stroke="url(#nodeGrad)" stroke-width="1" fill="none"/>
            <path class="node-line" d="M280,70 Q290,115 300,160" stroke="url(#nodeGrad)" stroke-width="1" fill="none"/>
        </svg>
        
        <!-- Hero content -->
        <div class="landing-hero__content">
            <div class="landing-hero__badge reveal-up" style="animation-delay: 0.1s;">
                {get_icon('zap', size=12)}
                <span>Powered by AI</span>
            </div>
            <h1 class="landing-hero__title reveal-up" style="animation-delay: 0.2s;">
                Transform Data Into<br/>
                <span class="gradient-text">Stunning Reports</span>
            </h1>
            <p class="landing-hero__desc reveal-up" style="animation-delay: 0.3s;">
                Upload your spreadsheets and let AI generate beautiful, insight-rich reports in seconds. No design skills required.
            </p>
            <div class="landing-hero__cta reveal-up" style="animation-delay: 0.4s;">
                <a href="#upload" class="btn-primary-glow">
                    {get_icon('upload', size=16)}
                    <span>Start Generating</span>
                </a>
                <a href="#features" class="btn-ghost">
                    <span>See Features</span>
                    {get_icon('arrow-right', size=14)}
                </a>
            </div>
        </div>
    </div>
    """)


def render_bento_grid():
    """Render bento grid product preview section."""
    render_html_block(f"""
    <div class="bento-section" id="features">
        <div class="bento-header reveal-up">
            <span class="bento-label">Features</span>
            <h2 class="bento-title">Everything you need for<br/>professional reports</h2>
        </div>
        
        <div class="bento-grid">
            <!-- Large feature card -->
            <div class="bento-card bento-card--large reveal-up" style="animation-delay: 0.1s;">
                <div class="bento-card__visual">
                    <div class="bento-preview">
                        <div class="preview-chart">
                            <div class="chart-bar" style="height: 60%;"></div>
                            <div class="chart-bar" style="height: 80%;"></div>
                            <div class="chart-bar" style="height: 45%;"></div>
                            <div class="chart-bar" style="height: 90%;"></div>
                            <div class="chart-bar" style="height: 70%;"></div>
                        </div>
                    </div>
                </div>
                <div class="bento-card__content">
                    <div class="bento-card__icon">{get_icon('chart-bar', size=20)}</div>
                    <h3>Auto-Generated Charts</h3>
                    <p>AI analyzes your data structure and creates the perfect visualizations automatically.</p>
                </div>
            </div>
            
            <!-- Stacked cards -->
            <div class="bento-stack">
                <div class="bento-card bento-card--half reveal-up" style="animation-delay: 0.2s;">
                    <div class="bento-card__icon bento-card__icon--purple">{get_icon('sparkles', size=20)}</div>
                    <h3>AI Insights</h3>
                    <p>Get intelligent analysis and recommendations from your data.</p>
                    <div class="bento-pill-group">
                        <span class="bento-pill">Trends</span>
                        <span class="bento-pill">Anomalies</span>
                        <span class="bento-pill">Predictions</span>
                    </div>
                </div>
                <div class="bento-card bento-card--half reveal-up" style="animation-delay: 0.3s;">
                    <div class="bento-card__icon bento-card__icon--cyan">{get_icon('file-text', size=20)}</div>
                    <h3>Multiple Formats</h3>
                    <p>Export to PDF, DOCX, or share directly.</p>
                    <div class="format-icons">
                        <span class="format-icon format-icon--pdf">PDF</span>
                        <span class="format-icon format-icon--docx">DOCX</span>
                    </div>
                </div>
            </div>
            
            <!-- Wide card -->
            <div class="bento-card bento-card--wide reveal-up" style="animation-delay: 0.4s;">
                <div class="bento-card__content">
                    <div class="bento-card__icon bento-card__icon--green">{get_icon('zap', size=20)}</div>
                    <div>
                        <h3>Lightning Fast</h3>
                        <p>Generate comprehensive reports in under 30 seconds with our optimized pipeline.</p>
                    </div>
                </div>
                <div class="speed-visual">
                    <div class="speed-line"></div>
                    <div class="speed-dot"></div>
                </div>
            </div>
        </div>
    </div>
    """)


def render_cta_strip():
    """Render call-to-action strip before the main workflow."""
    render_html_block(f"""
    <div class="cta-strip reveal-up" id="upload">
        <div class="cta-strip__content">
            <div class="cta-strip__icon">{get_icon('upload', size=24)}</div>
            <div class="cta-strip__text">
                <h3>Ready to create your first report?</h3>
                <p>Upload your CSV or Excel file below to get started</p>
            </div>
        </div>
        <div class="cta-strip__arrow">
            {get_icon('arrow-down', size=20)}
        </div>
    </div>
    """)


def render_header():
    """Render header with animated AI-style background."""
    render_html_block(f"""
    <div class="app-header fade-in">
        <!-- Animated floating orbs -->
        <div class="orb-1"></div>
        <div class="orb-2"></div>
        <div class="orb-3"></div>
        <div class="orb-4"></div>

        <!-- Header content -->
        <div class="app-header__icon animate-glow">{get_icon('chart-bar', size=28)}</div>
        <div class="app-header__title">Automated Report Generator</div>
        <p class="app-header__subtitle" style="text-align: center; margin: 0 auto;">Transform your data into professional reports with AI-powered insights</p>
        <div class="app-header__tag">
            {get_icon('sparkles', size=14)}
            <span>AI-Powered</span>
        </div>
    </div>
    """)


def render_steps():
    """Render step indicator."""
    steps = [(1, "Upload"), (2, "Configure"), (3, "Generate"), (4, "Download")]
    html = '<div class="steps">'
    for i, (num, label) in enumerate(steps):
        if i > 0:
            line_class = "step__line--done" if num <= st.session_state.step else ""
            html += f'<div class="step__line {line_class}"></div>'

        if num < st.session_state.step:
            cls, num_content = "step--done", get_icon("check", 12)
        elif num == st.session_state.step:
            cls, num_content = "step--active", str(num)
        else:
            cls, num_content = "", str(num)

        html += f'<div class="step {cls}"><span class="step__num">{num_content}</span><span>{label}</span></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_alert(type: str, title: str, text: str = ""):
    """Render alert message."""
    icon = STATUS_ICONS.get(type, "info")
    text_html = f'<div class="alert__text">{text}</div>' if text else ''
    st.markdown(f"""
    <div class="alert alert--{type}">
        <div class="alert__icon">{get_icon(icon, 16)}</div>
        <div class="alert__body">
            <div class="alert__title">{title}</div>
            {text_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_section(title: str, desc: str = "", icon_name: str = None):
    """Render section header."""
    icon_html = f'<div class="section__icon">{get_icon(icon_name, 14)}</div>' if icon_name else ''
    desc_html = f'<p class="section__desc">{desc}</p>' if desc else ''
    st.markdown(f"""
    <div class="section__head">
        {icon_html}
        <div>
            <div class="section__title">{title}</div>
            {desc_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metric(label: str, value: str, icon_name: str = "chart-bar"):
    """Render metric card."""
    st.markdown(f"""
    <div class="metric">
        <div class="metric__icon">{get_icon(icon_name, 16)}</div>
        <div class="metric__val">{value}</div>
        <div class="metric__label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# STEP 1: UPLOAD
# ============================================================================

def render_step_1():
    """Step 1: Upload data."""
    render_section("Upload Your Data", "CSV or Excel files", "upload")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_files = st.file_uploader(
            "Choose files",
            type=['csv', 'xlsx', 'xls'],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

        if uploaded_files:
            try:
                processor = DataProcessor()
                file_contents = [f.getvalue() for f in uploaded_files]
                file_names = [f.name for f in uploaded_files]

                # Handle Excel sheets
                excel_sheets = {}
                for i, (content, name) in enumerate(zip(file_contents, file_names)):
                    if Path(name).suffix.lower() in ['.xlsx', '.xls']:
                        sheets = get_excel_sheet_names(content)
                        if len(sheets) > 1:
                            excel_sheets[i] = {'name': name, 'sheets': sheets}

                selected_sheets = {}
                if excel_sheets:
                    st.markdown("---")
                    render_section("Select Sheet", "", "table")
                    for idx, info in excel_sheets.items():
                        selected_sheets[idx] = st.selectbox(info['name'], info['sheets'], key=f"sheet_{idx}")

                # Load data
                if len(file_contents) == 1:
                    df = load_and_validate_data(file_contents[0], file_names[0], selected_sheets.get(0))
                    processor.df = df
                else:
                    dfs = [load_and_validate_data(c, n, selected_sheets.get(i)) for i, (c, n) in enumerate(zip(file_contents, file_names))]
                    processor.df = pd.concat(dfs, ignore_index=True)

                st.session_state.uploaded_file = uploaded_files
                st.session_state.df = processor.df
                st.session_state.processor = processor

                # Success
                st.markdown("---")
                render_alert("success", "Data loaded", f"{len(processor.df):,} rows • {len(processor.df.columns)} columns")

                # Preview
                st.markdown("---")
                render_section("Preview", "First 10 rows", "table")

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.markdown(f'<span class="badge badge--brand">{get_icon("grid", 10)} {len(processor.df):,} rows</span>', unsafe_allow_html=True)
                with col_b:
                    st.markdown(f'<span class="badge badge--brand">{get_icon("table", 10)} {len(processor.df.columns)} cols</span>', unsafe_allow_html=True)

                st.dataframe(processor.df.head(10), use_container_width=True, hide_index=True)

                # Template suggestion
                suggested, confidence = processor.suggest_template()
                if suggested:
                    st.markdown("---")
                    icon = TEMPLATE_ICONS.get(suggested, "file")
                    render_alert("info", "Suggested Template", f"<strong>{suggested.replace('_', ' ').title()}</strong> ({confidence:.0%} match)")
                    st.session_state.selected_template = suggested

                # Continue
                st.markdown("---")
                _, btn_col, _ = st.columns([1, 2, 1])
                with btn_col:
                    if st.button("Continue", type="primary", use_container_width=True):
                        st.session_state.step = 2
                        st.rerun()

            except Exception as e:
                render_alert("error", "Error", str(e))

    with col2:
        st.markdown(f"""
        <div class="sidebar">
            <div class="sidebar__head">{get_icon('lightbulb', 16)} Quick Start</div>
            <div class="sidebar__group">
                <div class="sidebar__label">Sample Files</div>
                <ul class="sidebar__list">
                    <li>sales_sample.csv</li>
                    <li>financial_sample.csv</li>
                    <li>inventory_sample.csv</li>
                </ul>
            </div>
            <div class="sidebar__group">
                <div class="sidebar__label">Formats</div>
                <ul class="sidebar__list">
                    <li>CSV (.csv)</li>
                    <li>Excel (.xlsx, .xls)</li>
                </ul>
            </div>
            <div class="sidebar__group">
                <div class="sidebar__label">Limits</div>
                <ul class="sidebar__list">
                    <li>200 MB max</li>
                    <li>500K rows max</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ============================================================================
# STEP 2: CONFIGURE
# ============================================================================

def render_step_2():
    """Step 2: Configure report."""
    render_section("Configure Report", "Select template and map columns", "settings")

    if st.session_state.processor is None:
        render_alert("warning", "No data", "Please upload data first.")
        if st.button("Back"):
            st.session_state.step = 1
            st.rerun()
        return

    processor = st.session_state.processor
    col1, col2 = st.columns([1, 1])

    with col1:
        render_section("Template", "", "file-text")
        templates_config = load_config("templates")

        for t in TEMPLATES.keys():
            t_info = templates_config['templates'][t]
            t_icon = TEMPLATE_ICONS.get(t, "file")
            is_sel = st.session_state.selected_template == t
            cls = "tpl-card--active" if is_sel else ""
            check = get_icon("check", 10) if is_sel else ""

            st.markdown(f"""
            <div class="tpl-card {cls}">
                <div class="tpl-card__icon">{get_icon(t_icon, 18)}</div>
                <div class="tpl-card__body">
                    <div class="tpl-card__name">{t_info['name']}</div>
                    <div class="tpl-card__info">{t_info.get('description', '')}</div>
                </div>
                <div class="tpl-card__check">{check}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Select" if not is_sel else "Selected", key=f"sel_{t}", type="primary" if is_sel else "secondary", use_container_width=True, disabled=is_sel):
                st.session_state.selected_template = t
                st.rerun()

    with col2:
        render_section("Column Mapping", "", "link")

        if st.session_state.selected_template:
            processor.set_template(st.session_state.selected_template)
            processor.auto_map_columns()

            template_config = templates_config['templates'].get(st.session_state.selected_template, {})
            required = list(template_config.get('required_columns', {}).keys())
            optional = list(template_config.get('optional_columns', {}).keys())

            mapping = {}
            cols = ['(None)'] + list(processor.df.columns)

            with st.expander(f"Required ({len(required)})", expanded=True):
                for field in required:
                    current = processor.column_mapping.get(field)
                    idx = cols.index(current) if current in cols else 0
                    st.markdown(f'<div class="field-row"><span class="field-row__dot field-row__dot--req"></span><span class="field-row__name">{field.replace("_", " ").title()}</span></div>', unsafe_allow_html=True)
                    sel = st.selectbox(field, cols, index=idx, key=f"m_{field}", label_visibility="collapsed")
                    if sel != '(None)':
                        mapping[field] = sel

            if optional:
                with st.expander(f"Optional ({len(optional)})"):
                    for field in optional:
                        current = processor.column_mapping.get(field)
                        idx = cols.index(current) if current in cols else 0
                        st.markdown(f'<div class="field-row"><span class="field-row__dot field-row__dot--opt"></span><span class="field-row__name">{field.replace("_", " ").title()}</span></div>', unsafe_allow_html=True)
                        sel = st.selectbox(field, cols, index=idx, key=f"m_{field}", label_visibility="collapsed")
                        if sel != '(None)':
                            mapping[field] = sel

            st.session_state.column_mapping = mapping
            processor.set_column_mapping(mapping)
            is_valid, errors, warnings = processor.validate_mapping()

            st.markdown("---")
            if errors:
                for e in errors:
                    render_alert("error", "Error", e)
            if warnings:
                for w in warnings:
                    render_alert("warning", "Warning", w)
            if is_valid:
                render_alert("success", "Valid", "All required fields mapped")

    # Options
    st.markdown("---")
    render_section("Options", "", "filter")

    opt1, opt2 = st.columns(2)
    with opt1:
        st.session_state.include_ai = st.checkbox("AI Insights", value=st.session_state.include_ai)
    with opt2:
        fmts = st.multiselect("Formats", ['pdf', 'docx'], default=st.session_state.output_formats)
        st.session_state.output_formats = fmts if fmts else ['pdf']

    # Navigation
    st.markdown("---")
    nav1, _, nav3 = st.columns([1, 1, 1])

    with nav1:
        if st.button("Back", use_container_width=True):
            st.session_state.step = 1
            st.rerun()

    with nav3:
        can_gen = is_valid and st.session_state.output_formats
        if st.button("Generate", type="primary", use_container_width=True, disabled=not can_gen):
            st.session_state.step = 3
            st.rerun()


# ============================================================================
# STEP 3: GENERATE
# ============================================================================

def render_step_3():
    """Step 3: Generate report."""
    render_section("Generating", "Processing your data", "zap")

    if st.session_state.processor is None or st.session_state.selected_template is None:
        render_alert("warning", "Missing config")
        if st.button("Start Over"):
            st.session_state.step = 1
            st.rerun()
        return

    st.markdown(f"""
    <div class="progress-box">
        <div class="progress-box__icon">{get_icon('zap', 24)}</div>
    </div>
    """, unsafe_allow_html=True)

    progress = st.progress(0)
    status = st.empty()

    try:
        template = get_template(st.session_state.selected_template)()

        with tempfile.TemporaryDirectory() as tmp:
            status.markdown("**Processing data...**")
            progress.progress(20)

            data = st.session_state.df.copy()
            if st.session_state.missing_value_strategy != 'none':
                st.session_state.processor.df = data
                data = st.session_state.processor.fill_missing_values(st.session_state.missing_value_strategy)

            status.markdown("**Generating charts...**")
            progress.progress(50)

            if st.session_state.include_ai:
                status.markdown("**AI analysis...**")
            progress.progress(75)

            status.markdown("**Building report...**")
            progress.progress(90)

            output_files = template.generate(
                data_source=data,
                output_dir=tmp,
                formats=st.session_state.output_formats,
                include_ai_insights=st.session_state.include_ai,
                column_mapping=st.session_state.column_mapping,
            )

            progress.progress(100)
            status.markdown("**Done!**")

            reports = {}
            for fmt, path in output_files.items():
                with open(path, 'rb') as f:
                    reports[fmt] = {'data': f.read(), 'filename': Path(path).name}

            st.session_state.generated_reports = reports
            st.session_state.step = 4
            st.rerun()

    except Exception as e:
        progress.empty()
        status.empty()
        render_alert("error", "Error", str(e))
        if st.button("Back"):
            st.session_state.step = 2
            st.rerun()


# ============================================================================
# STEP 4: DOWNLOAD
# ============================================================================

def render_step_4():
    """Step 4: Download reports."""
    render_section("Reports Ready", "Download your files", "download")

    if not st.session_state.generated_reports:
        render_alert("warning", "No reports")
        if st.button("Start Over"):
            st.session_state.step = 1
            st.rerun()
        return

    render_alert("success", "Success!", "Your reports are ready")
    st.markdown("---")

    cols = st.columns(len(st.session_state.generated_reports))
    for i, (fmt, data) in enumerate(st.session_state.generated_reports.items()):
        with cols[i]:
            size = len(data['data']) / 1024
            icon = FILE_ICONS.get(fmt, "file")
            icon_cls = f"dl-card__icon--{fmt}"

            st.markdown(f"""
            <div class="dl-card">
                <div class="dl-card__icon {icon_cls}">{get_icon(icon, 18)}</div>
                <div class="dl-card__body">
                    <div class="dl-card__name">{fmt.upper()} Report</div>
                    <div class="dl-card__meta">{data['filename']} • {size:.1f} KB</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.download_button(
                f"Download {fmt.upper()}",
                data=data['data'],
                file_name=data['filename'],
                mime='application/pdf' if fmt == 'pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                use_container_width=True,
            )

            if fmt == 'pdf':
                with st.expander("Preview"):
                    b64 = base64.b64encode(data['data']).decode()
                    st.markdown(f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="300" style="border-radius: 8px; border: 1px solid #e5e7eb;"></iframe>', unsafe_allow_html=True)

    # Summary
    st.markdown("---")
    render_section("Summary", "", "chart-pie")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric("Template", st.session_state.selected_template.replace('_', ' ').title(), TEMPLATE_ICONS.get(st.session_state.selected_template, "file"))
    with m2:
        render_metric("Rows", f"{len(st.session_state.df):,}", "database")
    with m3:
        render_metric("Formats", " + ".join(f.upper() for f in st.session_state.output_formats), "file")
    with m4:
        render_metric("AI", "Yes" if st.session_state.include_ai else "No", "sparkles")

    # New report
    st.markdown("---")
    _, btn, _ = st.columns([1, 2, 1])
    with btn:
        if st.button("New Report", type="primary", use_container_width=True):
            for key in ['step', 'uploaded_file', 'df', 'processor', 'selected_template', 'column_mapping', 'generated_reports']:
                st.session_state[key] = None if key != 'step' else 1
            st.session_state.column_mapping = {}
            st.session_state.generated_reports = {}
            st.rerun()


# ============================================================================
# FOOTER
# ============================================================================

def render_footer():
    """Render footer."""
    st.markdown(f"""
    <div class="app-footer">
        <div class="app-footer__brand">
            {get_icon('chart-bar', 12)}
            <span>Report Generator v1.0</span>
        </div>
        <p>Built with Streamlit • AI-Powered</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    init_session_state()
    
    # Render landing sections for step 1 (upload)
    if st.session_state.step == 1:
        render_landing_hero()
        render_bento_grid()
        render_cta_strip()
    
    render_header()
    render_steps()

    if st.session_state.step == 1:
        render_step_1()
    elif st.session_state.step == 2:
        render_step_2()
    elif st.session_state.step == 3:
        render_step_3()
    elif st.session_state.step == 4:
        render_step_4()

    render_footer()


if __name__ == "__main__":
    main()
