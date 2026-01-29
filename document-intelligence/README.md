# Document Intelligence System

AI-powered document processing system with OCR, entity extraction, summarization, and RAG-based Q&A.

## Features

- **Document Processing**: Support for PDF and image files (PNG, JPG, TIFF)
- **OCR Engine**: Tesseract-based OCR with image preprocessing for scanned documents
- **Entity Extraction**: Extract dates, amounts, names, organizations, emails, phones, GSTIN, PAN, invoice numbers
- **AI Summarization**: LLM-powered summaries with fallback to extractive methods
- **RAG Q&A**: Ask questions about documents with source citations
- **Export**: Export to JSON, CSV, and Excel formats
- **Privacy-First**: No persistent document storage - all processing is session-based

## Quick Start

### Prerequisites

- Python 3.9+
- Tesseract OCR (optional, for scanned documents)

### Installation

#### macOS

```bash
# Install Tesseract OCR via Homebrew
brew install tesseract tesseract-lang

# Clone the repository
cd document-intelligence

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (includes urllib3<2.0 for LibreSSL compatibility)
pip install -r requirements.txt

# Download spaCy model (optional, improves NER)
python -m spacy download en_core_web_sm
```

#### Linux

```bash
# Install Tesseract OCR
sudo apt-get install tesseract-ocr tesseract-ocr-eng

# Clone the repository
cd document-intelligence

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model (optional, improves NER)
python -m spacy download en_core_web_sm
```

#### Windows

1. Install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
2. Add Tesseract to system PATH
3. Install Python dependencies as shown above

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
# OPENROUTER_API_KEY=your_key_here
```

### Running the Application

**Option 1: Streamlit UI (Recommended)**
```bash
streamlit run app/streamlit_app.py
```
Open http://localhost:8501 in your browser.

**Option 2: FastAPI Backend**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
API docs at http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload document for processing |
| GET | `/status/{doc_id}` | Get processing status |
| GET | `/summary/{doc_id}` | Get document summary |
| GET | `/entities/{doc_id}` | Get extracted entities |
| POST | `/qa/{doc_id}` | Ask a question about the document |
| GET | `/export/{doc_id}/{format}` | Export data (json/csv/excel) |
| DELETE | `/document/{doc_id}` | Delete document |

## Project Structure

```
document-intelligence/
├── app/
│   ├── config.py          # Settings and configuration
│   ├── models.py          # Pydantic data models
│   ├── main.py            # FastAPI application
│   └── streamlit_app.py   # Streamlit UI
├── src/
│   ├── document_loader.py # PDF/image loading
│   ├── document_store.py  # In-memory session storage
│   ├── ocr_engine.py      # Tesseract OCR processing
│   ├── text_processor.py  # Text cleaning and chunking
│   ├── entity_extractor.py# NER and pattern extraction
│   ├── vector_store.py    # ChromaDB embeddings
│   ├── summarizer.py      # LLM summarization
│   ├── qa_engine.py       # RAG Q&A engine
│   └── exporter.py        # Export functionality
├── config/
│   ├── settings.yaml      # Application settings
│   └── prompts.yaml       # LLM prompt templates
├── tests/                 # Test files
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## Configuration Options

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | API key for LLM services | Optional |

### Settings (config/settings.yaml)

```yaml
document:
  max_file_size_mb: 25
  max_pages: 50
  supported_formats: [".pdf", ".png", ".jpg", ".jpeg", ".tiff"]

ocr:
  timeout_seconds: 60
  dpi: 300
  preprocessing: true

entity_extraction:
  confidence_threshold: 0.7
  deduplicate: true

summarization:
  min_key_points: 3
  max_key_points: 7

qa:
  max_context_chunks: 5
  max_conversation_history: 10
```

## Graceful Degradation

The system is designed to work even without external API keys:

| Component | With API Key | Without API Key |
|-----------|--------------|-----------------|
| Summarization | LLM-powered | Extractive fallback |
| Embeddings | OpenRouter API | Zero vectors / local model |
| Q&A | RAG with LLM | Keyword matching |
| OCR | Tesseract | Skip (use native text) |

## Performance

- Document processing: < 30 seconds for 10 pages
- Q&A response: < 5 seconds
- API response time: < 200ms (p95)

## Entity Types Extracted

| Entity Type | Examples | Confidence |
|-------------|----------|------------|
| Dates | 15/01/2024, January 15, 2024 | 90%+ |
| Amounts | Rs. 15,000, $1,200.50, €500 | 95%+ |
| Persons | John Smith, Raj Kumar | 85%+ |
| Organizations | ABC Corp, Google Inc | 88%+ |
| Emails | user@example.com | 98%+ |
| Phones | +91 98765 43210 | 85%+ |
| Invoice Numbers | INV-2024-001 | 90%+ |
| GSTIN | 27AABCU9603R1ZM | 98%+ |
| PAN | ABCDE1234F | 95%+ |

## Docker Deployment

### Quick Start with Docker

```bash
# Build and run the API
docker build -t document-intelligence .
docker run -p 8000:8000 -e OPENROUTER_API_KEY=your_key document-intelligence

# Access the API at http://localhost:8000
```

### Docker Compose (Recommended)

```bash
# Set environment variables
export OPENROUTER_API_KEY=your_api_key
export DI_API_KEY=your_secret_api_key  # Optional: for API authentication

# Start both API and Streamlit UI
docker-compose up --build

# API available at http://localhost:8000
# UI available at http://localhost:8501
```

### Production Deployment

#### Railway

1. Connect your repository to Railway
2. Set environment variables:
   - `OPENROUTER_API_KEY`: Your OpenRouter API key
   - `DI_API_KEY`: Secret key for API authentication (optional)
3. Railway will auto-detect the Dockerfile

#### Render

1. Create a new Web Service
2. Connect to your repository
3. Set the Dockerfile path
4. Add environment variables in the dashboard

#### Environment Variables for Production

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | API key for LLM services | Optional |
| `DI_API_KEY` | API key for authentication | Optional |

### API Authentication

When `DI_API_KEY` is set and `require_auth: true` in config, endpoints require the `X-API-Key` header:

```bash
curl -X POST http://localhost:8000/upload \
  -H "X-API-Key: your_secret_key" \
  -F "file=@document.pdf"
```

### Rate Limiting

The API includes built-in rate limiting (default: 60 requests/minute per client).
Configure in `config/settings.yaml`:

```yaml
api:
  rate_limit_requests_per_minute: 60
```

## Development

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_phase1.py -v

# Run enhancement tests (security, validation, etc.)
pytest tests/test_enhancements.py -v

# Check code style
flake8 app/ src/
```

### Test Coverage

Tests are organized by functionality:
- `test_phase1.py`: Configuration, models, document store
- `test_phase2.py`: OCR and text processing
- `test_phase3.py`: Entity extraction
- `test_phase4.py`: Summarization and Q&A
- `test_enhancements.py`: Security and reliability features

## License

MIT License - see LICENSE file for details.

## Support

For issues or questions, please create an issue in the repository.
