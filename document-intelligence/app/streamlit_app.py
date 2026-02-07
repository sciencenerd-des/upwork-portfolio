"""Streamlit UI for document intelligence demo."""

from __future__ import annotations

import os
from typing import Any

import requests
import streamlit as st

from src.exporter import export_csv, export_excel, export_json
from src.pipeline import ProcessedDocument, run_pipeline
from src.qa_engine import answer_question

st.set_page_config(
    page_title="Document Intelligence Terminal",
    page_icon="⌁",
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
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap');

:root {
  --terminal-bg: #0c0c0c;
  --terminal-green: #00ff88;
  --terminal-cyan: #00d4ff;
  --terminal-red: #ff5f56;
  --terminal-yellow: #ffbd2e;
  --terminal-dim: #2a2a2a;
  --terminal-muted: #7b7b7b;
  --terminal-text: #d9d9d9;
}

html, body, [class*="css"], .stApp {
  font-family: 'JetBrains Mono', monospace !important;
}

.stApp {
  background: var(--terminal-bg);
  color: var(--terminal-text);
}

.stApp::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 999;
  background: repeating-linear-gradient(
    0deg,
    rgba(255,255,255,0.02),
    rgba(255,255,255,0.02) 1px,
    transparent 1px,
    transparent 2px
  );
}

.block-container {
  max-width: 1300px;
  padding-top: 1rem;
  padding-bottom: 3rem;
}

.terminal-header {
  border: 1px solid var(--terminal-dim);
  background: rgba(0,0,0,0.6);
  padding: 0.85rem 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
}

.command-line {
  color: var(--terminal-green);
  font-size: 0.92rem;
  letter-spacing: 0.03em;
}

.command-line .prefix {
  color: var(--terminal-cyan);
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.6rem;
  margin-top: 0.75rem;
}

.status-pill {
  border: 1px solid var(--terminal-dim);
  border-radius: 6px;
  padding: 0.45rem 0.6rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.76rem;
  color: var(--terminal-text);
  background: rgba(255,255,255,0.02);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: var(--terminal-green);
  animation: pulse-dot 1.6s ease-in-out infinite;
}

.status-dot.cyan { background: var(--terminal-cyan); }
.status-dot.yellow { background: var(--terminal-yellow); }
.status-dot.red { background: var(--terminal-red); }

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.85); }
}

.panel-title {
  color: var(--terminal-cyan);
  font-size: 0.82rem;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  border: 1px solid var(--terminal-dim);
  border-radius: 6px;
  padding: 0.6rem 0.75rem;
  margin: 0.65rem 0;
  background: rgba(0, 212, 255, 0.06);
}

.metric-row {
  border: 1px solid var(--terminal-dim);
  border-radius: 6px;
  padding: 0.55rem 0.7rem;
  margin-bottom: 0.45rem;
  background: rgba(255,255,255,0.02);
}

.metric-label {
  color: var(--terminal-muted);
  font-size: 0.72rem;
}

.metric-value {
  color: var(--terminal-green);
  font-size: 1.1rem;
  font-weight: 700;
}

.terminal-note {
  color: var(--terminal-muted);
  font-size: 0.73rem;
  margin-top: 0.25rem;
}

[data-testid="stFileUploader"] {
  border: 1px solid var(--terminal-dim);
  border-radius: 6px;
  background: rgba(255,255,255,0.01);
}

.stButton > button, .stDownloadButton > button {
  width: 100%;
  border: 1px solid var(--terminal-cyan);
  background: transparent;
  color: var(--terminal-cyan);
  border-radius: 4px;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 0.55rem 0.75rem;
}

.stButton > button:hover, .stDownloadButton > button:hover {
  border-color: var(--terminal-green);
  color: var(--terminal-green);
}

.stTextInput > div > div > input,
.stTextArea textarea {
  background: #090909 !important;
  color: var(--terminal-text) !important;
  border: 1px solid var(--terminal-dim) !important;
}

div[data-testid="stMarkdownContainer"] code {
  color: var(--terminal-green);
}

hr {
  border-color: var(--terminal-dim);
}

@media (max-width: 900px) {
  .block-container {
    padding-top: 0.5rem;
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
<div class="terminal-header">
  <div class="command-line"><span class="prefix">root@doc-intel:/workspace$</span> ./run_pipeline --mode data-focused</div>
  <div class="status-grid">
    <div class="status-pill"><span class="status-dot"></span>OCR ENGINE ONLINE</div>
    <div class="status-pill"><span class="status-dot cyan"></span>ENTITY EXTRACTOR ACTIVE</div>
    <div class="status-pill"><span class="status-dot yellow"></span>Q&A CONTEXT WINDOW READY</div>
    <div class="status-pill"><span class="status-dot"></span>EXPORT MODULE IDLE</div>
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
    with st.spinner("[PIPELINE] ingest -> ocr -> entities -> summary"):
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
    st.markdown('<div class="panel-title">[UPLOAD CONSOLE] :: Document Ingestion</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Accepted formats: PDF, PNG, JPG, TIFF",
        type=["pdf", "png", "jpg", "jpeg", "tif", "tiff"],
    )

    process_click = st.button(
        "Execute OCR + Extraction",
        key="process-btn",
        use_container_width=True,
    )

    if process_click and uploaded_file is not None:
        process_document(uploaded_file.name, uploaded_file.getvalue())
    elif process_click and uploaded_file is None:
        st.session_state["last_error"] = "Upload a document before executing the pipeline."


def render_status_panel() -> None:
    st.markdown('<div class="panel-title">[STATUS BOARD] :: Runtime Metrics</div>', unsafe_allow_html=True)
    processed = st.session_state.get("processed")

    if not processed:
        st.info("No document processed yet.")
        return

    metrics = [
        ("Pages", str(processed.get("page_count", "-"))),
        ("Words", str(processed.get("word_count", "-"))),
        ("Mode", processed.get("processing_mode", "-")),
        ("Profile", st.session_state.get("mode", "local").upper()),
    ]

    for label, value in metrics:
        st.markdown(
            f"<div class='metric-row'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div></div>",
            unsafe_allow_html=True,
        )


def render_ocr_panel() -> None:
    processed = st.session_state.get("processed")
    if not processed:
        return

    st.markdown('<div class="panel-title">[OCR PROCESSING] :: Text Output</div>', unsafe_allow_html=True)
    st.text_area(
        "Text preview",
        value=processed.get("full_text", "")[:2000],
        height=250,
        key="ocr-preview",
    )


def render_entity_panel() -> None:
    processed = st.session_state.get("processed")
    if not processed:
        return

    st.markdown(
        '<div class="panel-title">[ENTITY EXTRACTION] :: Structured Signals</div>',
        unsafe_allow_html=True,
    )

    entities = processed.get("entities", {})
    for entity_type, values in entities.items():
        st.markdown(f"`{entity_type.upper()}` ({len(values)})")
        if values:
            st.dataframe(values, use_container_width=True, hide_index=True)
        else:
            st.caption("No matches.")


def render_qa_panel() -> None:
    processed = st.session_state.get("processed")
    if not processed:
        return

    st.markdown('<div class="panel-title">[Q&A CHAT] :: Ask the Document</div>', unsafe_allow_html=True)

    question = st.text_input(
        "Question",
        value=st.session_state.get("last_question", ""),
        placeholder="e.g. What is the invoice total and due date?",
    )
    st.session_state["last_question"] = question

    run_click = st.button("Run Query", key="qa-run", use_container_width=True)
    if run_click and question.strip():
        run_qa(question)

    if st.session_state.get("qa_history"):
        for item in st.session_state["qa_history"][-4:]:
            st.markdown(f"**Q:** {item['question']}")
            st.markdown(f"**A:** {item['answer']}")
            st.caption(
                f"Sources: {', '.join(item['sources']) if item['sources'] else 'None'} | Confidence: {item['confidence']}"
            )
            st.markdown("---")


def render_export_panel() -> None:
    processed = st.session_state.get("processed")
    if not processed:
        return

    st.markdown('<div class="panel-title">[EXPORT] :: JSON / CSV / XLSX</div>', unsafe_allow_html=True)

    if st.session_state.get("mode") == "api":
        doc_id = processed["document_id"]
        for ext, label, mime in [
            ("json", "Download JSON", "application/json"),
            ("csv", "Download CSV", "text/csv"),
            (
                "xlsx",
                "Download Excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ),
        ]:
            try:
                response = requests.get(
                    f"{API_BASE_URL}/export/{doc_id}/{ext}", timeout=90
                )
                response.raise_for_status()
                st.download_button(
                    label,
                    data=response.content,
                    file_name=f"{processed['filename'].rsplit('.', 1)[0]}_entities.{ext}",
                    mime=mime,
                    use_container_width=True,
                )
            except Exception:
                st.caption(f"Failed to fetch `{ext}` export from API. Falling back to local.")
                break

    st.download_button(
        "Download JSON (Local)",
        data=export_json(processed).decode("utf-8"),
        file_name=f"{processed['filename'].rsplit('.', 1)[0]}_entities.json",
        mime="application/json",
        use_container_width=True,
        key="local-json",
    )
    st.download_button(
        "Download CSV (Local)",
        data=export_csv(processed.get("entities", {})).decode("utf-8"),
        file_name=f"{processed['filename'].rsplit('.', 1)[0]}_entities.csv",
        mime="text/csv",
        use_container_width=True,
        key="local-csv",
    )
    st.download_button(
        "Download Excel (Local)",
        data=export_excel(
            filename=processed.get("filename", "document"),
            summary=processed.get("summary", ""),
            key_points=processed.get("key_points", []),
            entities=processed.get("entities", {}),
        ),
        file_name=f"{processed['filename'].rsplit('.', 1)[0]}_entities.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        key="local-xlsx",
    )


def render_summary_panel() -> None:
    processed = st.session_state.get("processed")
    if not processed:
        return

    st.markdown(
        '<div class="panel-title">[SUMMARY ENGINE] :: Executive Abstract</div>',
        unsafe_allow_html=True,
    )
    st.write(processed.get("summary", "No summary available."))
    for point in processed.get("key_points", []):
        st.markdown(f"- {point}")


def main() -> None:
    init_state()
    render_header()

    if st.session_state.get("last_error"):
        st.error(st.session_state["last_error"])

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
        f"<div class='terminal-note'>API endpoint target: <code>{API_BASE_URL}</code> | Theme: Concept 3 / Data-focused terminal.</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
