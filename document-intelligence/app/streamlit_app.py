"""Streamlit UI for Document Intelligence System.

A professional enterprise-grade interface for document processing,
OCR, entity extraction, summarization, and Q&A.
"""

from __future__ import annotations

import os
from typing import Any

import requests
import streamlit as st

from src.exporter import export_csv, export_excel, export_json
from src.pipeline import ProcessedDocument, run_pipeline
from src.qa_engine import answer_question

st.set_page_config(
    page_title="Document Intelligence System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def resolve_api_base_url() -> str:
    explicit = os.getenv("API_BASE_URL")
    if explicit:
        return explicit.rstrip("/")

    api_host = os.getenv("API_HOST")
    api_port = os.getenv("API_PORT")
    if api_host and api_port:
        return f"http://{api_host}:{api_port}"

    return "http://localhost:8000"


API_BASE_URL = resolve_api_base_url()

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

:root {
  --navy-900: #0f172a;
  --navy-800: #1e293b;
  --navy-700: #334155;
  --navy-600: #475569;
  --navy-500: #64748b;
  --navy-400: #94a3b8;
  --navy-300: #cbd5e1;
  --navy-200: #e2e8f0;
  --navy-100: #f1f5f9;
  --navy-50: #f8fafc;
  --accent-indigo: #6366f1;
  --accent-indigo-light: #818cf8;
  --accent-emerald: #10b981;
  --accent-amber: #f59e0b;
  --gradient-premium: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
}

html, body, [class*="css"], .stApp {
  font-family: 'DM Sans', sans-serif !important;
}

.stApp {
  background: var(--navy-50);
  color: var(--navy-800);
}

.block-container {
  max-width: 1400px;
  padding-top: 2rem;
  padding-bottom: 3rem;
}

/* Header Styles */
.system-header {
  background: white;
  border: 1px solid var(--navy-200);
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
}

.system-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--navy-900);
  margin-bottom: 1rem;
}

.system-title-icon {
  width: 36px;
  height: 36px;
  background: var(--gradient-premium);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
}

.status-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.85rem;
  background: var(--navy-50);
  border: 1px solid var(--navy-200);
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--navy-700);
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent-emerald);
}

.status-indicator.processing { background: var(--accent-amber); animation: pulse 2s infinite; }
.status-indicator.indigo { background: var(--accent-indigo); }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Panel Styles */
.panel-card {
  background: white;
  border: 1px solid var(--navy-200);
  border-radius: 12px;
  padding: 1.25rem;
  margin-bottom: 1rem;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--accent-indigo);
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--navy-100);
}

.panel-title-icon {
  font-size: 1rem;
}

/* Metric Styles */
.metric-card {
  background: var(--navy-50);
  border: 1px solid var(--navy-200);
  border-radius: 8px;
  padding: 0.85rem;
  margin-bottom: 0.75rem;
}

.metric-label {
  font-size: 0.75rem;
  color: var(--navy-500);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.metric-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--navy-900);
}

.metric-value.highlight {
  color: var(--accent-indigo);
}

/* File Uploader */
[data-testid="stFileUploader"] {
  border: 2px dashed var(--navy-300) !important;
  border-radius: 12px !important;
  background: var(--navy-50) !important;
}

[data-testid="stFileUploader"]:hover {
  border-color: var(--accent-indigo) !important;
  background: rgba(99, 102, 241, 0.05) !important;
}

/* Button Styles */
.stButton > button, .stDownloadButton > button {
  width: 100%;
  border: none !important;
  background: var(--accent-indigo) !important;
  color: white !important;
  border-radius: 8px !important;
  font-size: 0.85rem !important;
  font-weight: 600 !important;
  padding: 0.65rem 1rem !important;
  transition: all 0.2s ease !important;
}

.stButton > button:hover, .stDownloadButton > button:hover {
  background: #4f46e5 !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
}

.stButton > button:active {
  transform: translateY(0);
}

/* Secondary Button */
button[kind="secondary"] {
  background: white !important;
  border: 1px solid var(--navy-300) !important;
  color: var(--navy-700) !important;
}

button[kind="secondary"]:hover {
  background: var(--navy-50) !important;
  border-color: var(--navy-400) !important;
}

/* Input Styles */
.stTextInput > div > div > input,
.stTextArea textarea {
  background: white !important;
  color: var(--navy-800) !important;
  border: 1px solid var(--navy-300) !important;
  border-radius: 8px !important;
  font-family: 'DM Sans', sans-serif !important;
}

.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
  border-color: var(--accent-indigo) !important;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
}

/* DataFrames */
[data-testid="stDataFrame"] {
  border: 1px solid var(--navy-200) !important;
  border-radius: 8px !important;
}

/* Code Blocks */
div[data-testid="stMarkdownContainer"] code {
  background: var(--navy-100) !important;
  color: var(--navy-700) !important;
  border-radius: 4px !important;
  padding: 0.2rem 0.4rem !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.85rem !important;
}

/* Summary Points */
.summary-point {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: var(--navy-700);
}

.summary-point::before {
  content: "•";
  color: var(--accent-indigo);
  font-weight: bold;
}

/* Q&A Chat */
.chat-item {
  background: var(--navy-50);
  border: 1px solid var(--navy-200);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.chat-question {
  font-weight: 600;
  color: var(--navy-900);
  margin-bottom: 0.5rem;
}

.chat-answer {
  color: var(--navy-700);
  line-height: 1.6;
  margin-bottom: 0.5rem;
}

.chat-meta {
  font-size: 0.8rem;
  color: var(--navy-500);
  padding-top: 0.5rem;
  border-top: 1px solid var(--navy-200);
}

/* Footer */
.system-footer {
  font-size: 0.8rem;
  color: var(--navy-500);
  text-align: center;
  padding-top: 1.5rem;
  margin-top: 2rem;
  border-top: 1px solid var(--navy-200);
}

/* Responsive */
@media (max-width: 768px) {
  .block-container {
    padding-top: 1rem;
  }
  
  .system-header {
    padding: 1rem;
  }
  
  .status-row {
    grid-template-columns: 1fr;
  }
}
</style>
"""


def init_state() -> None:
    defaults: dict[str, Any] = {
        "processed": None,
        "mode": "local",
        "qa_history": [],
        "last_error": "",
        "last_question": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_header() -> None:
    st.markdown(THEME_CSS, unsafe_allow_html=True)
    st.markdown(
        """
<div class="system-header">
  <div class="system-title">
    <div class="system-title-icon">📄</div>
    <span>Document Intelligence System</span>
  </div>
  <div class="status-row">
    <div class="status-badge">
      <span class="status-indicator"></span>
      OCR Engine Online
    </div>
    <div class="status-badge">
      <span class="status-indicator indigo"></span>
      Entity Extractor Active
    </div>
    <div class="status-badge">
      <span class="status-indicator indigo"></span>
      Q&A System Ready
    </div>
    <div class="status-badge">
      <span class="status-indicator processing"></span>
      Export Module Ready
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def process_via_api(file_name: str, file_bytes: bytes) -> dict[str, Any]:
    files = {"file": (file_name, file_bytes, "application/octet-stream")}
    response = requests.post(f"{API_BASE_URL}/process", files=files, timeout=180)
    response.raise_for_status()
    payload = response.json()
    payload["full_text"] = payload.get("text_preview", "")
    payload["chunks"] = []
    return payload


def process_locally(file_name: str, file_bytes: bytes) -> dict[str, Any]:
    result: ProcessedDocument = run_pipeline(file_bytes, file_name)
    payload = result.response_payload()
    payload["full_text"] = result.text
    payload["chunks"] = result.chunks
    return payload


def process_document(file_name: str, file_bytes: bytes) -> None:
    st.session_state["last_error"] = ""
    with st.spinner("Processing document... Ingest → OCR → Extract → Summarize"):
        try:
            payload = process_via_api(file_name, file_bytes)
            st.session_state["mode"] = "api"
        except Exception:
            payload = process_locally(file_name, file_bytes)
            st.session_state["mode"] = "local"

    st.session_state["processed"] = payload
    st.session_state["qa_history"] = []


def run_qa(question: str) -> None:
    processed = st.session_state.get("processed")
    if not processed or not question.strip():
        return

    mode = st.session_state.get("mode", "local")

    try:
        if mode == "api":
            response = requests.post(
                f"{API_BASE_URL}/qa",
                json={
                    "document_id": processed["document_id"],
                    "question": question,
                },
                timeout=90,
            )
            response.raise_for_status()
            payload = response.json()
        else:
            qa_result = answer_question(question, processed.get("chunks", []))
            payload = {
                "answer": qa_result["answer"],
                "sources": qa_result["sources"],
                "confidence": qa_result["confidence"],
            }

        st.session_state["qa_history"].append(
            {
                "question": question,
                "answer": payload["answer"],
                "sources": payload.get("sources", []),
                "confidence": payload.get("confidence", 0.0),
            }
        )
    except Exception as exc:
        st.session_state["last_error"] = f"Q&A failed: {exc}"


def render_upload_panel() -> None:
    with st.container():
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title"><span class="panel-title-icon">📤</span>Document Upload</div>', unsafe_allow_html=True)
        
        st.write("**Upload any document to extract structured data**")
        st.caption("Supports: PDF, PNG, JPG, TIFF | No templates required")
        
        uploaded_file = st.file_uploader(
            "Drag and drop or click to browse",
            type=["pdf", "png", "jpg", "jpeg", "tif", "tiff"],
            label_visibility="collapsed",
        )

        process_click = st.button(
            "🚀 Process Document",
            key="process-btn",
            use_container_width=True,
        )

        if process_click and uploaded_file is not None:
            process_document(uploaded_file.name, uploaded_file.getvalue())
        elif process_click and uploaded_file is None:
            st.session_state["last_error"] = "Please upload a document before processing."
        
        st.markdown('</div>', unsafe_allow_html=True)


def render_status_panel() -> None:
    with st.container():
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title"><span class="panel-title-icon">📊</span>Processing Metrics</div>', unsafe_allow_html=True)
        
        processed = st.session_state.get("processed")

        if not processed:
            st.info("Upload a document to see processing metrics.")
        else:
            metrics = [
                ("Pages", str(processed.get("page_count", "-"))),
                ("Words", str(processed.get("word_count", "-"))),
                ("Processing Mode", processed.get("processing_mode", "-")),
                ("Connection", st.session_state.get("mode", "local").upper()),
            ]

            for label, value in metrics:
                highlight = "highlight" if label in ["Pages", "Words"] else ""
                st.markdown(
                    f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value {highlight}'>{value}</div></div>",
                    unsafe_allow_html=True,
                )
        
        st.markdown('</div>', unsafe_allow_html=True)


def render_ocr_panel() -> None:
    processed = st.session_state.get("processed")
    if not processed:
        return

    with st.container():
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title"><span class="panel-title-icon">🔍</span>Extracted Text</div>', unsafe_allow_html=True)
        
        text_content = processed.get("full_text", "")
        preview_text = text_content[:2000] + ("..." if len(text_content) > 2000 else "")
        
        st.text_area(
            "OCR Output Preview",
            value=preview_text,
            height=200,
            key="ocr-preview",
            label_visibility="collapsed",
        )
        
        if len(text_content) > 2000:
            st.caption(f"Showing first 2,000 characters of {len(text_content):,} total characters")
        
        st.markdown('</div>', unsafe_allow_html=True)


def render_entity_panel() -> None:
    processed = st.session_state.get("processed")
    if not processed:
        return

    with st.container():
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title"><span class="panel-title-icon">📋</span>Extracted Entities</div>', unsafe_allow_html=True)

        entities = processed.get("entities", {})
        if entities:
            for entity_type, values in entities.items():
                with st.expander(f"**{entity_type.replace('_', ' ').title()}** ({len(values)} found)"):
                    if values:
                        st.dataframe(values, use_container_width=True, hide_index=True)
                    else:
                        st.caption("No matches found for this entity type.")
        else:
            st.info("No entities extracted yet. Process a document to see results.")
        
        st.markdown('</div>', unsafe_allow_html=True)


def render_qa_panel() -> None:
    processed = st.session_state.get("processed")
    if not processed:
        return

    with st.container():
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title"><span class="panel-title-icon">💬</span>Ask the Document</div>', unsafe_allow_html=True)
        
        st.caption("Ask questions about your document content. The system uses RAG to find relevant passages and generate answers.")

        question = st.text_input(
            "Your Question",
            value=st.session_state.get("last_question", ""),
            placeholder="e.g., What is the total amount on the invoice?",
            label_visibility="collapsed",
        )
        st.session_state["last_question"] = question

        run_click = st.button("Ask Question", key="qa-run", use_container_width=True)
        if run_click and question.strip():
            run_qa(question)

        if st.session_state.get("qa_history"):
            st.markdown("---")
            st.markdown("**Recent Questions & Answers**")
            
            for item in reversed(st.session_state["qa_history"][-4:]):
                st.markdown(
                    f"""
                    <div class="chat-item">
                        <div class="chat-question">Q: {item['question']}</div>
                        <div class="chat-answer">{item['answer']}</div>
                        <div class="chat-meta">
                            Sources: {', '.join(item['sources']) if item['sources'] else 'N/A'} | 
                            Confidence: {item['confidence']:.0%}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        
        st.markdown('</div>', unsafe_allow_html=True)


def render_export_panel() -> None:
    processed = st.session_state.get("processed")
    if not processed:
        return

    with st.container():
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title"><span class="panel-title-icon">📥</span>Export Results</div>', unsafe_allow_html=True)
        
        st.caption("Download extracted data in your preferred format")

        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                "📄 JSON",
                data=export_json(processed).decode("utf-8"),
                file_name=f"{processed['filename'].rsplit('.', 1)[0]}_data.json",
                mime="application/json",
                use_container_width=True,
                key="export-json",
            )
        
        with col2:
            st.download_button(
                "📊 CSV",
                data=export_csv(processed.get("entities", {})).decode("utf-8"),
                file_name=f"{processed['filename'].rsplit('.', 1)[0]}_data.csv",
                mime="text/csv",
                use_container_width=True,
                key="export-csv",
            )
        
        with col3:
            st.download_button(
                "📈 Excel",
                data=export_excel(
                    filename=processed.get("filename", "document"),
                    summary=processed.get("summary", ""),
                    key_points=processed.get("key_points", []),
                    entities=processed.get("entities", {}),
                ),
                file_name=f"{processed['filename'].rsplit('.', 1)[0]}_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="export-xlsx",
            )
        
        st.markdown('</div>', unsafe_allow_html=True)


def render_summary_panel() -> None:
    processed = st.session_state.get("processed")
    if not processed:
        return

    with st.container():
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title"><span class="panel-title-icon">📝</span>Document Summary</div>', unsafe_allow_html=True)
        
        summary = processed.get("summary", "")
        if summary:
            st.write(summary)
        else:
            st.info("No summary generated yet.")
        
        key_points = processed.get("key_points", [])
        if key_points:
            st.markdown("**Key Points:**")
            for point in key_points:
                st.markdown(f"<div class='summary-point'>{point}</div>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)


def render_empty_state() -> None:
    with st.container():
        st.markdown('<div class="panel-card" style="text-align: center; padding: 3rem;">', unsafe_allow_html=True)
        st.markdown("## 📄 Document Intelligence System")
        st.write("Transform unstructured documents into structured data")
        st.markdown("""
        **Key Features:**
        - 📤 Upload PDFs, images, and scanned documents
        - 🔍 OCR engine with 95%+ accuracy
        - 📋 Automatic entity extraction (dates, amounts, names, IDs)
        - 📝 AI-powered document summarization
        - 💬 Natural language Q&A with source citations
        - 📊 Export to JSON, CSV, and Excel
        """)
        st.caption("Upload a document to get started →")
        st.markdown('</div>', unsafe_allow_html=True)


def main() -> None:
    init_state()
    render_header()

    if st.session_state.get("last_error"):
        st.error(st.session_state["last_error"])

    # Main content area
    processed = st.session_state.get("processed")
    
    if not processed:
        # Show empty state with upload centered
        render_empty_state()
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            render_upload_panel()
    else:
        # Full layout when document is processed
        left, right = st.columns([1.8, 1.2], gap="large")

        with left:
            render_upload_panel()
            render_ocr_panel()
            render_qa_panel()

        with right:
            render_status_panel()
            render_summary_panel()
            render_entity_panel()
            render_export_panel()

    st.markdown(
        f"""
        <div class="system-footer">
            API Endpoint: <code>{API_BASE_URL}</code> | 
            Document Intelligence System v1.0 | 
            Processing Mode: {st.session_state.get("mode", "local").upper()}
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
