"""
Streamlit UI for Document Intelligence System

Interactive web interface for:
- Document upload and processing
- Summary and key points display
- Entity extraction visualization
- RAG-based Q&A chat
- Export functionality
"""

import io
import time
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_settings
from app.models import DocumentStatus, ExportFormat
from src.document_store import get_document_store
from src.document_loader import get_document_loader
from src.ocr_engine import get_ocr_engine
from src.text_processor import get_text_processor
from src.entity_extractor import get_entity_extractor
from src.vector_store import get_document_vector_store
from src.summarizer import get_summarizer
from src.qa_engine import get_qa_engine
from src.exporter import get_exporter

# Page configuration
st.set_page_config(
    page_title="Document Intelligence",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6B7280;
        margin-bottom: 2rem;
    }
    .entity-card {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .confidence-high { color: #059669; font-weight: bold; }
    .confidence-medium { color: #D97706; }
    .confidence-low { color: #DC2626; }
    .key-point {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 0 4px 4px 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #DBEAFE;
        margin-left: 2rem;
    }
    .assistant-message {
        background-color: #F3F4F6;
        margin-right: 2rem;
    }
    .source-citation {
        font-size: 0.85rem;
        color: #6B7280;
        border-left: 2px solid #9CA3AF;
        padding-left: 0.5rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if "doc_id" not in st.session_state:
        st.session_state.doc_id = None
    if "processing" not in st.session_state:
        st.session_state.processing = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "document" not in st.session_state:
        st.session_state.document = None


def get_confidence_class(confidence: float) -> str:
    """Get CSS class based on confidence level."""
    if confidence >= 0.9:
        return "confidence-high"
    elif confidence >= 0.7:
        return "confidence-medium"
    else:
        return "confidence-low"


def format_confidence(confidence: float) -> str:
    """Format confidence as percentage with color."""
    css_class = get_confidence_class(confidence)
    return f'<span class="{css_class}">{confidence:.0%}</span>'


def process_document(file_content: bytes, filename: str) -> str:
    """Process uploaded document."""
    store = get_document_store()
    loader = get_document_loader()
    ocr_engine = get_ocr_engine()
    text_processor = get_text_processor()
    entity_extractor = get_entity_extractor()
    vector_store = get_document_vector_store()
    summarizer = get_summarizer()

    # Get file info
    ext = "." + filename.lower().split(".")[-1] if "." in filename else ""

    # Create document
    doc_id = store.create_document(
        filename=filename,
        file_type=ext,
        file_size_bytes=len(file_content)
    )

    progress_bar = st.progress(0, text="Loading document...")

    try:
        # Step 1: Load document
        store.set_status(doc_id, DocumentStatus.PROCESSING)
        load_result = loader.load(file_content, filename)

        if not load_result:
            store.set_error(doc_id, "Failed to load document")
            return doc_id

        progress_bar.progress(20, text="Extracting text...")

        # Step 2: Extract text
        from app.models import PageContent
        pages = []
        all_text = []
        image_idx = 0

        for page in load_result.pages:
            page_text = page.text or ""
            ocr_confidence = None
            is_scanned = page.is_scanned

            if is_scanned and image_idx < len(load_result.images):
                ocr_result = ocr_engine.process_image(load_result.images[image_idx])
                if ocr_result and ocr_result.text:
                    page_text = ocr_result.text
                    ocr_confidence = ocr_result.confidence
                image_idx += 1

            pages.append(PageContent(
                page_number=page.page_number,
                text=page_text,
                is_scanned=is_scanned,
                ocr_confidence=ocr_confidence
            ))
            all_text.append(page_text)

        progress_bar.progress(40, text="Processing text...")

        # Update document
        doc = store.get_document(doc_id)
        doc.pages = pages
        doc.raw_text = "\n\n".join(all_text)
        doc.metadata.page_count = load_result.page_count
        doc.metadata.is_scanned = load_result.is_scanned

        # Step 3: Process text
        processed = text_processor.process(doc.raw_text)
        doc.chunks = processed.chunks

        progress_bar.progress(60, text="Extracting entities...")

        # Step 4: Extract entities
        doc.entities = entity_extractor.extract(doc.raw_text)

        progress_bar.progress(75, text="Indexing document...")

        # Step 5: Index in vector store
        if doc.chunks:
            vector_store.index_document(doc_id, doc.chunks)

        progress_bar.progress(90, text="Generating summary...")

        # Step 6: Generate summary
        word_count = len(doc.raw_text.split())
        doc.summary = summarizer.summarize(
            doc.raw_text,
            word_count=word_count,
            page_count=doc.metadata.page_count
        )

        # Complete
        store.update_document(doc_id, doc)
        store.set_status(doc_id, DocumentStatus.COMPLETED)
        progress_bar.progress(100, text="Complete!")

        return doc_id

    except Exception as e:
        store.set_error(doc_id, str(e))
        st.error(f"Processing failed: {e}")
        return doc_id


def render_upload_tab():
    """Render the upload tab."""
    st.header("Upload Document")

    uploaded_file = st.file_uploader(
        "Choose a document",
        type=["pdf", "png", "jpg", "jpeg", "tiff"],
        help="Supported formats: PDF, PNG, JPG, JPEG, TIFF (max 25MB)"
    )

    if uploaded_file is not None:
        # Show file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("Size", f"{uploaded_file.size / 1024:.1f} KB")
        with col3:
            st.metric("Type", uploaded_file.type)

        if st.button("Process Document", type="primary", use_container_width=True):
            with st.spinner("Processing document..."):
                file_content = uploaded_file.read()
                doc_id = process_document(file_content, uploaded_file.name)
                st.session_state.doc_id = doc_id
                st.session_state.document = get_document_store().get_document(doc_id)
                st.session_state.chat_history = []
                st.success(f"Document processed! ID: {doc_id}")
                st.rerun()


def render_summary_tab():
    """Render the summary tab."""
    st.header("Document Summary")

    if not st.session_state.document:
        st.info("Please upload a document first.")
        return

    doc = st.session_state.document

    if doc.status != DocumentStatus.COMPLETED:
        st.warning(f"Document status: {doc.status.value}")
        return

    # Document metadata
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pages", doc.metadata.page_count)
    with col2:
        st.metric("Words", doc.summary.word_count if doc.summary else 0)
    with col3:
        st.metric("Scanned", "Yes" if doc.metadata.is_scanned else "No")
    with col4:
        doc_type = doc.summary.document_type.value if doc.summary else "unknown"
        st.metric("Type", doc_type.title())

    st.divider()

    if doc.summary:
        # Executive Summary
        st.subheader("Executive Summary")
        st.write(doc.summary.executive_summary)

        # Key Points
        st.subheader("Key Points")
        for i, point in enumerate(doc.summary.key_points, 1):
            st.markdown(f'<div class="key-point"><strong>{i}.</strong> {point}</div>',
                       unsafe_allow_html=True)
    else:
        st.warning("Summary not available.")


def render_entities_tab():
    """Render the entities tab."""
    st.header("Extracted Entities")

    if not st.session_state.document:
        st.info("Please upload a document first.")
        return

    doc = st.session_state.document

    if doc.status != DocumentStatus.COMPLETED:
        st.warning(f"Document status: {doc.status.value}")
        return

    entities = doc.entities

    # Entity type filter
    entity_types = ["All", "Dates", "Amounts", "Persons", "Organizations",
                   "Emails", "Phones", "Invoice Numbers", "GSTINs", "PANs"]
    selected_type = st.selectbox("Filter by type", entity_types)

    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Entities", entities.total_count)
    with col2:
        high_conf = sum(1 for e in entities.to_flat_list() if e.confidence >= 0.9)
        st.metric("High Confidence", high_conf)
    with col3:
        unique_types = len([t for t in [entities.dates, entities.amounts, entities.persons,
                                        entities.organizations, entities.emails, entities.phones,
                                        entities.invoice_numbers, entities.gstins, entities.pans]
                          if t])
        st.metric("Entity Types", unique_types)

    st.divider()

    # Render entities by type
    def render_entity_section(title: str, items: list, show_extra: str = None):
        if not items:
            return
        if selected_type != "All" and selected_type != title:
            return

        st.subheader(f"{title} ({len(items)})")
        for item in items:
            conf_html = format_confidence(item.confidence)
            extra_info = ""
            if show_extra == "parsed_date" and hasattr(item, 'parsed_date') and item.parsed_date:
                extra_info = f" (Parsed: {item.parsed_date.strftime('%Y-%m-%d')})"
            elif show_extra == "amount" and hasattr(item, 'numeric_value'):
                extra_info = f" ({item.currency} {item.numeric_value:,.2f})"

            page_info = f" [Page {item.page_number}]" if item.page_number else ""

            st.markdown(
                f'<div class="entity-card">'
                f'<strong>{item.value}</strong>{extra_info}{page_info}<br>'
                f'Confidence: {conf_html}'
                f'</div>',
                unsafe_allow_html=True
            )

    render_entity_section("Dates", entities.dates, "parsed_date")
    render_entity_section("Amounts", entities.amounts, "amount")
    render_entity_section("Persons", entities.persons)
    render_entity_section("Organizations", entities.organizations)
    render_entity_section("Emails", entities.emails)
    render_entity_section("Phones", entities.phones)
    render_entity_section("Invoice Numbers", entities.invoice_numbers)
    render_entity_section("GSTINs", entities.gstins)
    render_entity_section("PANs", entities.pans)


def render_qa_tab():
    """Render the Q&A tab."""
    st.header("Ask Questions")

    if not st.session_state.document:
        st.info("Please upload a document first.")
        return

    doc = st.session_state.document

    if doc.status != DocumentStatus.COMPLETED:
        st.warning(f"Document status: {doc.status.value}")
        return

    # Chat history display
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-message user-message">'
                f'<strong>You:</strong> {msg["content"]}'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            sources_html = ""
            if msg.get("sources"):
                sources_html = "<div class='source-citation'>Sources: "
                for src in msg["sources"]:
                    if src.page:
                        sources_html += f"Page {src.page}, "
                    if src.quote:
                        sources_html += f'"{src.quote[:50]}...", '
                sources_html = sources_html.rstrip(", ") + "</div>"

            st.markdown(
                f'<div class="chat-message assistant-message">'
                f'<strong>Assistant:</strong> {msg["content"]}'
                f'{sources_html}'
                f'</div>',
                unsafe_allow_html=True
            )

    # Suggested questions
    qa_engine = get_qa_engine()
    if not st.session_state.chat_history:
        st.write("**Suggested questions:**")
        questions = qa_engine.generate_suggested_questions(st.session_state.doc_id)
        cols = st.columns(min(len(questions), 3))
        for i, q in enumerate(questions[:3]):
            with cols[i]:
                if st.button(q, key=f"suggested_{i}"):
                    st.session_state.pending_question = q
                    st.rerun()

    # Question input
    question = st.chat_input("Ask a question about the document...")

    # Handle pending question from suggested
    if hasattr(st.session_state, 'pending_question') and st.session_state.pending_question:
        question = st.session_state.pending_question
        st.session_state.pending_question = None

    if question:
        # Add user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        # Get answer
        with st.spinner("Thinking..."):
            from app.models import QAMessage
            history = [
                QAMessage(role=msg["role"], content=msg["content"])
                for msg in st.session_state.chat_history[:-1]  # Exclude current question
            ]
            response = qa_engine.answer(
                doc_id=st.session_state.doc_id,
                question=question,
                conversation_history=history
            )

        # Add assistant response
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response.answer,
            "sources": response.sources,
            "confidence": response.confidence
        })

        st.rerun()


def render_export_tab():
    """Render the export tab."""
    st.header("Export Data")

    if not st.session_state.document:
        st.info("Please upload a document first.")
        return

    doc = st.session_state.document

    if doc.status != DocumentStatus.COMPLETED:
        st.warning(f"Document status: {doc.status.value}")
        return

    exporter = get_exporter()

    # Export options
    st.subheader("Export Options")

    col1, col2 = st.columns(2)
    with col1:
        include_summary = st.checkbox("Include Summary", value=True)
        include_entities = st.checkbox("Include Entities", value=True)
    with col2:
        include_raw_text = st.checkbox("Include Raw Text", value=False)

    st.divider()

    # Export buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("JSON Export")
        st.write("Structured data format")
        json_data = exporter.export(
            doc, ExportFormat.JSON,
            include_summary, include_entities, include_raw_text
        )
        st.download_button(
            "Download JSON",
            json_data,
            f"{st.session_state.doc_id}_export.json",
            "application/json",
            use_container_width=True
        )

    with col2:
        st.subheader("CSV Export")
        st.write("Flattened entities")
        csv_data = exporter.export(doc, ExportFormat.CSV)
        st.download_button(
            "Download CSV",
            csv_data,
            f"{st.session_state.doc_id}_entities.csv",
            "text/csv",
            use_container_width=True
        )

    with col3:
        st.subheader("Excel Export")
        st.write("Formatted workbook")
        excel_data = exporter.export(
            doc, ExportFormat.EXCEL,
            include_summary, include_entities, include_raw_text
        )
        st.download_button(
            "Download Excel",
            excel_data,
            f"{st.session_state.doc_id}_export.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    # Preview
    st.divider()
    st.subheader("Preview")

    preview_format = st.selectbox("Preview format", ["JSON", "CSV"])

    if preview_format == "JSON":
        st.json(json_data[:5000] + "..." if len(json_data) > 5000 else json_data)
    else:
        # Parse CSV and show as table
        csv_lines = csv_data.strip().split("\n")
        if len(csv_lines) > 1:
            import csv
            reader = csv.reader(io.StringIO(csv_data))
            rows = list(reader)
            if rows:
                df = pd.DataFrame(rows[1:], columns=rows[0])
                st.dataframe(df, use_container_width=True)


def render_sidebar():
    """Render sidebar with document info."""
    st.sidebar.markdown('<h2 class="main-header">Document Intelligence</h2>', unsafe_allow_html=True)
    st.sidebar.markdown('<p class="sub-header">AI-powered document analysis</p>', unsafe_allow_html=True)

    if st.session_state.document:
        doc = st.session_state.document
        st.sidebar.divider()
        st.sidebar.subheader("Current Document")
        st.sidebar.write(f"**File:** {doc.metadata.filename}")
        st.sidebar.write(f"**Status:** {doc.status.value}")
        st.sidebar.write(f"**Pages:** {doc.metadata.page_count}")

        if st.sidebar.button("Clear Document", use_container_width=True):
            # Clean up
            if st.session_state.doc_id:
                store = get_document_store()
                vector_store = get_document_vector_store()
                try:
                    vector_store.delete_store(st.session_state.doc_id)
                except:
                    pass
                store.delete_document(st.session_state.doc_id)

            st.session_state.doc_id = None
            st.session_state.document = None
            st.session_state.chat_history = []
            st.rerun()

    st.sidebar.divider()
    st.sidebar.info(
        "**Features:**\n"
        "- PDF and image processing\n"
        "- OCR for scanned documents\n"
        "- Entity extraction\n"
        "- AI-powered summarization\n"
        "- Q&A with citations\n"
        "- Export to JSON/CSV/Excel"
    )


def main():
    """Main application entry point."""
    initialize_session_state()

    # Render sidebar
    render_sidebar()

    # Main content with tabs
    if st.session_state.document and st.session_state.document.status == DocumentStatus.COMPLETED:
        tabs = st.tabs(["Summary", "Entities", "Q&A", "Export", "Upload New"])

        with tabs[0]:
            render_summary_tab()
        with tabs[1]:
            render_entities_tab()
        with tabs[2]:
            render_qa_tab()
        with tabs[3]:
            render_export_tab()
        with tabs[4]:
            render_upload_tab()
    else:
        # Show upload tab only
        render_upload_tab()


if __name__ == "__main__":
    main()
