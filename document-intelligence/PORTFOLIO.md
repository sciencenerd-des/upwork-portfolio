# Document Intelligence System

> **Enterprise-grade document processing with OCR, NLP, and LLM capabilities.**

[![Live API](https://img.shields.io/badge/API-Production-6366f1?logo=fastapi)](https://document-intelligence-api.onrender.com)
[![Live UI](https://img.shields.io/badge/UI-Live-10b981?logo=streamlit)](https://document-intelligence-ui.streamlit.app)

---

## 🎯 Project Overview

**Document Intelligence System** is a production-ready application that transforms unstructured documents (PDFs, images, scans) into structured, actionable data. Built for enterprise use cases including invoice processing, contract analysis, and document automation.

### Key Differentiators
- **Template-free processing** — Works with any document layout
- **95%+ OCR accuracy** — Advanced preprocessing and Tesseract integration
- **AI-powered insights** — LLM summaries and natural language Q&A
- **Enterprise security** — Session-scoped processing, no persistent storage

---

## 🌐 Live Demos

| Component | URL | Description |
|-----------|-----|-------------|
| **API** | https://document-intelligence-api.onrender.com | FastAPI backend with interactive docs |
| **UI** | https://document-intelligence-ui.streamlit.app | Streamlit frontend for document processing |
| **API Docs** | https://document-intelligence-api.onrender.com/docs | Swagger/OpenAPI documentation |

---

## 🚀 Core Features

### Document Processing Pipeline
1. **Upload** — Accepts PDF, PNG, JPG, TIFF formats
2. **OCR** — Extracts text with skew correction and preprocessing
3. **Extraction** — Identifies dates, amounts, names, IDs, addresses
4. **Summarization** — AI-generated executive summaries
5. **Q&A** — RAG-based question answering with source citations
6. **Export** — JSON, CSV, Excel downloads

### Supported Document Types
- Invoices & purchase orders
- Bank statements & financial reports
- Contracts & legal agreements
- ID documents & verification forms
- General business correspondence

---

## 🏗️ Technical Architecture

### Backend Stack
- **FastAPI** — High-performance async API framework
- **Tesseract OCR** — Open-source text recognition engine
- **Sentence Transformers** — Document embeddings for semantic search
- **LangChain** — LLM orchestration and RAG pipelines
- **OpenRouter** — Unified LLM API access

### Frontend Stack
- **Streamlit** — Rapid data app development
- **Custom CSS** — Enterprise-grade styling (navy/indigo theme)
- **Responsive layout** — Optimized for desktop and tablet

### Infrastructure
- **Docker** — Containerized deployment
- **Render** — Cloud API hosting
- **Streamlit Cloud** — UI hosting
- **GitHub Actions** — CI/CD pipeline

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| **OCR Accuracy** | 95%+ on clean documents, 85%+ on scans |
| **Processing Speed** | ~2-5 seconds per page |
| **API Response Time** | <200ms (health check), <30s (full processing) |
| **Supported Languages** | English + 100+ via Tesseract |
| **Max File Size** | 50MB per document |

---

## 💼 Use Cases

### Finance & Accounting
```
Input: Scanned vendor invoice (PDF)
Output: {
  "invoice_number": "INV-2026-0042",
  "vendor": "Apex Industrial Supplies",
  "total_amount": 18450.75,
  "line_items": [...],
  "payment_terms": "Net 30"
}
```

### Operations
```
Input: Mobile photo of purchase order
Output: {
  "po_number": "PO-78432",
  "buyer": "Acme Corp",
  "items_count": 15,
  "delivery_date": "2026-03-15",
  "total_value": 45200.00
}
```

### Legal & Compliance
```
Input: Multi-page service agreement
Output: {
  "contract_type": "Service Agreement",
  "parties": ["Company A", "Vendor B"],
  "effective_date": "2026-01-01",
  "renewal_date": "2027-01-01",
  "key_clauses": ["Termination", "SLA", "Liability"]
}
```

---

## 🛡️ Security & Compliance

- ✅ **Session-scoped processing** — No persistent document storage
- ✅ **Environment-based secrets** — API keys via env vars
- ✅ **Optional authentication** — API key middleware
- ✅ **CORS configuration** — Domain-restricted access
- ✅ **Self-hostable** — Deploy on your own infrastructure

---

## 🛠️ Local Development

```bash
# Clone repository
git clone https://github.com/sciencenerd-des/document-intelligence.git
cd document-intelligence

# Setup environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run API
uvicorn app.main:app --reload --port 8000

# Run UI (separate terminal)
streamlit run app/streamlit_app.py
```

---

## 📈 Project Stats

| Metric | Count |
|--------|-------|
| **Lines of Code** | 3,500+ |
| **Test Coverage** | 85%+ |
| **API Endpoints** | 8 |
| **Source Modules** | 12 |
| **Dependencies** | 25 (production) |

---

## 🔗 Repository

**GitHub:** https://github.com/sciencenerd-des/document-intelligence

---

## 📞 Contact

For custom integrations, enterprise deployments, or professional services:
- 📧 Email: hello@biswajit.dev
- 💼 Upwork: [Hire on Upwork](https://www.upwork.com/freelancers/~016c7a9e9e0e8d5c2c)

---

*Built with Python, FastAPI, Streamlit, and modern AI/ML tooling.*
