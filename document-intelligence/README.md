# Document Intelligence System

[![Live API](https://img.shields.io/badge/Live%20Demo-API-blue?logo=fastapi)](https://document-intelligence-api.onrender.com)
[![Live UI](https://img.shields.io/badge/Live%20Demo-UI-green?logo=streamlit)](https://document-intelligence-ui.streamlit.app)

Extract entities, summaries, and answers from PDFs and images using OCR + NLP + LLM workflows.

## Value Proposition

**Extract data from any document without templates.**

No fixed layouts, no custom parser per client format, no brittle regex-only pipeline.

## Screenshot Gallery

| Upload + OCR | Entity Extraction |
|---|---|
| ![Upload](https://placehold.co/1200x700/0f172a/ffffff?text=Upload+PDF%2FImage+%2B+OCR+Pipeline) | ![Entities](https://placehold.co/1200x700/1d4ed8/ffffff?text=Structured+Entity+Extraction+Dashboard) |

| Summary View | Q&A Chat | Export Panel |
|---|---|---|
| ![Summary](https://placehold.co/1200x700/047857/ffffff?text=Document+Summary+with+Key+Points) | ![QA](https://placehold.co/1200x700/7c2d12/ffffff?text=Ask+Questions+with+Cited+Answers) | ![Export](https://placehold.co/1200x700/7e22ce/ffffff?text=Export+JSON%2FCSV%2FXLSX) |

## Sample Documents (Before/After)

### Example 1: Invoice PDF

**Before**
- Unstructured scanned invoice with vendor stamp and skewed text

**After**
```json
{
  "document_type": "invoice",
  "invoice_number": "INV-2026-0042",
  "invoice_date": "2026-01-14",
  "vendor": "Apex Industrial Supplies",
  "total_amount": 18450.75,
  "currency": "INR",
  "line_items_count": 12
}
```

### Example 2: Bank Statement Image

**Before**
- Phone photo with mixed lighting and table columns

**After**
```json
{
  "account_holder": "Ravi Sharma",
  "statement_period": "2025-12-01 to 2025-12-31",
  "opening_balance": 82250.00,
  "closing_balance": 100470.00,
  "detected_transactions": 46
}
```

## Core Capabilities

- OCR for scanned PDFs/images
- Entity extraction (dates, amounts, names, orgs, IDs)
- LLM-powered summary generation
- RAG-style Q&A with source-aware retrieval
- Export to JSON, CSV, and Excel
- Session-scoped processing (no persistent document storage)

## Clear Setup Instructions

### 1. Prerequisites

- Python 3.10+
- `pip`
- Tesseract OCR

Install Tesseract:

```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y tesseract-ocr
```

### 2. Install Project

```bash
git clone https://github.com/sciencenerd-des/upwork-portfolio.git
cd upwork-portfolio/document-intelligence

python -m venv .venv
source .venv/bin/activate  # Windows (PowerShell): .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 3. Environment Variables

```bash
export OPENROUTER_API_KEY=your_api_key_here   # optional but recommended
export DI_API_KEY=your_internal_api_key        # optional
```

### 4. Run Locally

UI:
```bash
streamlit run app/streamlit_app.py
```

API:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open:
- UI: `http://localhost:8501`
- API Docs: `http://localhost:8000/docs`

## Deployment Instructions

### Option A: API on Render + UI on Streamlit Cloud

1. Deploy API service from `document-intelligence/` using Dockerfile
2. Set env vars on Render (`OPENROUTER_API_KEY`, optional `DI_API_KEY`)
3. Deploy Streamlit UI and set API base URL to your Render endpoint
4. Confirm `/health` and `/docs` are reachable

### Option B: Docker (Single Host)

```bash
docker build -t document-intelligence .
docker run -p 8000:8000 -e OPENROUTER_API_KEY=your_key document-intelligence
```

### Production Checklist

- `OPENROUTER_API_KEY` configured
- OCR dependencies installed in runtime
- API rate limit set
- CORS restricted to deployed UI domain
- Auth headers enabled for external API access

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/upload` | Upload and process document |
| GET | `/status/{doc_id}` | Processing status |
| GET | `/summary/{doc_id}` | Generated summary |
| GET | `/entities/{doc_id}` | Extracted entities |
| POST | `/qa/{doc_id}` | Ask questions on document |
| GET | `/export/{doc_id}/{format}` | Download JSON/CSV/Excel |
| DELETE | `/document/{doc_id}` | Remove session document |

## Architecture Diagram (Text-Based)

```text
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

## Project Structure

```text
document-intelligence/
├── app/
│   ├── main.py
│   ├── streamlit_app.py
│   ├── config.py
│   └── models.py
├── src/
│   ├── document_loader.py
│   ├── ocr_engine.py
│   ├── text_processor.py
│   ├── entity_extractor.py
│   ├── summarizer.py
│   ├── qa_engine.py
│   ├── vector_store.py
│   └── exporter.py
├── prompts/
├── tests/
├── requirements.txt
└── Dockerfile
```

## License

MIT
