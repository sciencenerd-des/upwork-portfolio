# Document Intelligence System

[![Live API](https://img.shields.io/badge/Live%20Demo-API-6366f1?logo=fastapi)](https://document-intelligence-api.onrender.com)
[![Live UI](https://img.shields.io/badge/Live%20Demo-UI-10b981?logo=streamlit)](https://document-intelligence-ui.streamlit.app)
[![License](https://img.shields.io/badge/License-MIT-8b5cf6.svg)](LICENSE)

**Instantly extract structured data from invoices, contracts, and documents—without templates.**

Transform PDFs and images into actionable intelligence using advanced OCR, NLP, and LLM workflows. No fixed layouts, no custom parsers per format, no brittle regex pipelines.

---

## 🎯 Who This Is For

### Finance Teams
- Automate invoice processing and payment verification
- Extract vendor details, line items, and totals from scanned documents
- Reconcile accounts payable with structured data exports

### Operations & Procurement
- Process purchase orders and contracts at scale
- Extract key terms, dates, and obligations automatically
- Eliminate manual data entry from document workflows

### Legal & Compliance
- Analyze contracts for key clauses and renewal dates
- Extract party information and agreement terms
- Generate summaries for due diligence reviews

### HR & Administration
- Process employee documents and verification forms
- Extract structured data from resumes and applications
- Automate onboarding document processing

---

## 📸 Screenshot Gallery

| Document Upload | Entity Extraction |
|---|---|
| ![Upload](docs/screenshots/upload-panel.png) | ![Entities](docs/screenshots/entity-extraction.png) |
| **Drag-and-drop PDF/Image upload** with OCR preprocessing | **Structured data extraction** with categorized entities |

| Summary View | Q&A Chat | Export Panel |
|---|---|---|
| ![Summary](docs/screenshots/summary-view.png) | ![QA](docs/screenshots/qa-chat.png) | ![Export](docs/screenshots/export-panel.png) |
| **AI-generated summaries** with key point extraction | **Natural language Q&A** with source citations | **One-click export** to JSON, CSV, and Excel |

---

## 📊 Before / After Examples

### Example 1: Invoice Processing

**Before (Scanned PDF)**
- Unstructured invoice with skewed text and vendor stamps
- Manual data entry required for each field
- Error-prone transcription of amounts and dates

**After (Structured JSON)**
```json
{
  "document_type": "invoice",
  "invoice_number": "INV-2026-0042",
  "invoice_date": "2026-01-14",
  "vendor": "Apex Industrial Supplies",
  "vendor_gst": "27AABCU9603R1ZX",
  "total_amount": 18450.75,
  "currency": "INR",
  "line_items_count": 12,
  "extracted_entities": {
    "dates": ["2026-01-14", "2026-02-14"],
    "amounts": [18450.75, 1537.56, 2890.00],
    "organizations": ["Apex Industrial Supplies"],
    "identifiers": ["INV-2026-0042", "27AABCU9603R1ZX"]
  }
}
```

### Example 2: Bank Statement Analysis

**Before (Mobile Photo)**
- Poor lighting and mixed quality
- Table columns difficult to parse
- Multiple pages to review manually

**After (Structured JSON)**
```json
{
  "document_type": "bank_statement",
  "account_holder": "Ravi Sharma",
  "account_number": "XXXX1234",
  "statement_period": "2025-12-01 to 2025-12-31",
  "opening_balance": 82250.00,
  "closing_balance": 100470.00,
  "detected_transactions": 46,
  "summary": "Net increase of ₹18,220 with 12 credits and 34 debits",
  "key_insights": [
    "Highest transaction: ₹25,000 (salary credit)",
    "Most frequent: Utility payments (₹3,400 total)",
    "Unusual activity: 2 international transactions"
  ]
}
```

---

## 🔐 Security & Compliance

### Data Handling
- **Session-scoped processing** — documents are processed in memory, not stored persistently
- **Automatic cleanup** — temporary files removed after processing completes
- **No training data retention** — document content never used to train models

### API Security
- Optional API key authentication (`DI_API_KEY`)
- CORS configuration for domain-restricted access
- Rate limiting support built-in

### Deployment Security
- Stateless architecture suitable for containerized deployments
- Environment variable configuration (no secrets in code)
- Health check endpoints for monitoring

### Compliance Notes
- GDPR-aligned: no persistent storage of personal data
- Processing logs available for audit trails
- Self-hostable for air-gapped environments

---

## 🚀 Core Capabilities

| Feature | Description |
|---------|-------------|
| **OCR Engine** | Extract text from scanned PDFs and images with 95%+ accuracy |
| **Entity Extraction** | Identify dates, amounts, names, organizations, IDs, addresses |
| **Document Summarization** | AI-generated executive summaries with key point extraction |
| **RAG-based Q&A** | Ask questions in natural language, get cited answers |
| **Multi-format Export** | Download results as JSON, CSV, or Excel |
| **Template-free** | Works with any document layout—no configuration needed |

---

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.10+
- `pip` package manager
- Tesseract OCR engine

**Install Tesseract:**
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y tesseract-ocr

# Windows
# Download installer from https://github.com/UB-Mannheim/tesseract/wiki
```

### 1. Install Project

```bash
git clone https://github.com/sciencenerd-des/document-intelligence.git
cd document-intelligence

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Optional but recommended for LLM features
export OPENROUTER_API_KEY=your_api_key_here

# Optional: enable API authentication
export DI_API_KEY=your_secure_api_key

# Optional: configure API endpoint for UI
export API_BASE_URL=https://your-api-domain.com
```

### 3. Run Locally

**Start the API server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
API Docs available at: `http://localhost:8000/docs`

**Start the UI (in another terminal):**
```bash
streamlit run app/streamlit_app.py
```
UI available at: `http://localhost:8501`

---

## 📦 Deployment

### Production Deployment (Recommended)

**API on Render + UI on Streamlit Cloud**

1. **Deploy API to Render:**
   - Connect GitHub repository
   - Use Dockerfile for build
   - Set environment variables: `OPENROUTER_API_KEY`, `DI_API_KEY`
   - Verify `/health` endpoint returns `200 OK`

2. **Deploy UI to Streamlit Cloud:**
   - Connect same repository
   - Set `API_BASE_URL` to your Render endpoint
   - Deploy and verify connection

**Live Instances:**
- 🌐 **API:** https://document-intelligence-api.onrender.com
- 🖥️ **UI:** https://document-intelligence-ui.streamlit.app

### Docker Deployment

```bash
# Build image
docker build -t document-intelligence .

# Run container
docker run -p 8000:8000 \
  -e OPENROUTER_API_KEY=your_key \
  -e DI_API_KEY=your_api_key \
  document-intelligence
```

---

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/process` | Upload and process document (OCR + extraction + summary) |
| `GET` | `/health` | Health check for monitoring |
| `POST` | `/qa/{doc_id}` | Ask questions about processed document |
| `GET` | `/export/{doc_id}/{format}` | Download results (json, csv, xlsx) |
| `DELETE` | `/document/{doc_id}` | Remove session data |

**Interactive API Documentation:**
- Swagger UI: `https://document-intelligence-api.onrender.com/docs`
- ReDoc: `https://document-intelligence-api.onrender.com/redoc`

---

## 🏗️ Architecture

```
┌─────────────────────────────┐
│ Input Layer                 │
│ - PDF / PNG / JPG           │
└──────────────┬──────────────┘
               v
┌─────────────────────────────┐
│ Document Loader             │
│ src/document_loader.py      │
└──────────────┬──────────────┘
               v
┌─────────────────────────────┐
│ OCR + Text Processing       │
│ src/ocr_engine.py           │
│ src/text_processor.py       │
└──────────────┬──────────────┘
               ├─────────────────────┐
               v                     v
┌─────────────────────────────┐  ┌─────────────────────────────┐
│ Entity Extractor            │  │ Vector Store + QA Engine    │
│ src/entity_extractor.py     │  │ src/vector_store.py         │
└──────────────┬──────────────┘  │ src/qa_engine.py            │
               │                 └──────────────┬──────────────┘
               └──────────────┬─────────────────┘
                              v
                   ┌──────────────────────────┐
                   │ Summarizer + Exporter    │
                   │ src/summarizer.py        │
                   │ src/exporter.py          │
                   └──────────────┬───────────┘
                                  v
                   ┌──────────────────────────┐
                   │ Delivery Layer           │
                   │ FastAPI + Streamlit UI   │
                   └──────────────────────────┘
```

---

## 📁 Project Structure

```
document-intelligence/
├── app/
│   ├── main.py              # FastAPI application
│   ├── streamlit_app.py     # Streamlit UI
│   ├── config.py            # Configuration
│   └── models.py            # Pydantic models
├── src/
│   ├── document_loader.py   # PDF/image loading
│   ├── ocr_engine.py        # Tesseract OCR wrapper
│   ├── text_processor.py    # Text normalization
│   ├── entity_extractor.py  # Named entity recognition
│   ├── summarizer.py        # LLM-based summarization
│   ├── qa_engine.py         # RAG question answering
│   ├── vector_store.py      # Document embeddings
│   └── exporter.py          # JSON/CSV/Excel export
├── prompts/                 # LLM prompt templates
├── tests/                   # Test suite
├── docs/                    # Documentation & screenshots
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container build
└── README.md               # This file
```

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 📞 Support

- 🐛 **Bug Reports:** [GitHub Issues](https://github.com/sciencenerd-des/document-intelligence/issues)
- 💼 **Professional Services:** Available for custom integrations and enterprise deployments

---

**Built with:** Python · FastAPI · Streamlit · Tesseract · Sentence Transformers · OpenRouter
