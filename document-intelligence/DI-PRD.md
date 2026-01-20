# Product Requirements Document
## Document Intelligence System

**Version:** 1.0  
**Date:** January 20, 2026  
**Author:** Biswajit  
**Status:** Draft

---

## 1. Executive Summary

### 1.1 Product Vision
An AI-powered document processing tool that extracts, analyzes, and enables intelligent Q&A over uploaded documents (PDFs, images, scanned docs). Combines OCR, NLP, and LLM capabilities to transform unstructured documents into actionable data.

### 1.2 Business Objectives
- Showcase advanced AI/NLP integration skills for Upwork portfolio
- Demonstrate full-stack capabilities (backend processing + web interface)
- Target high-value document automation market ($3B+ globally)
- Build reusable components for custom client engagements
- Leverage audit background for compliance/financial document processing

### 1.3 Success Metrics
- Process documents up to 50 pages in under 60 seconds
- Entity extraction accuracy > 90% on standard document types
- Q&A relevance score > 85% on factual questions
- Support 5+ document types (invoices, contracts, reports, receipts, letters)
- Zero manual intervention from upload to insight delivery

---

## 2. Problem Statement

### 2.1 Current Pain Points
- Businesses manually extract data from invoices, contracts, and reports
- Searching through large documents is time-consuming
- Compliance teams spend hours reviewing documents for key clauses
- Scanned/image documents require manual transcription
- No easy way to query document contents with natural language

### 2.2 Target Users

| User Persona | Description | Primary Need |
|--------------|-------------|--------------|
| Accounts Payable Clerk | Processes 50+ invoices daily | Extract invoice data automatically |
| Legal Assistant | Reviews contracts for key terms | Find specific clauses quickly |
| Compliance Officer | Audits documents for regulatory compliance | Identify risks and missing items |
| Research Analyst | Reviews lengthy reports | Summarize and extract key findings |
| Small Business Owner | Manages receipts and business docs | Digitize and organize documents |

### 2.3 Market Opportunity
- Document AI market: $3.7B (2024) → $12.8B (2030)
- Key drivers: digital transformation, remote work, compliance requirements
- Upwork searches for "document processing" increased 45% YoY
- Average project value: $500-$5,000 for custom solutions

---

## 3. Product Scope

### 3.1 In Scope (MVP)
- PDF document upload (native and scanned)
- Image upload (JPG, PNG) with OCR
- Text extraction and preprocessing
- Entity extraction (dates, amounts, names, organizations)
- Document summarization
- Q&A chat interface over document content
- Export extracted data to JSON, CSV, Excel
- Web interface (Streamlit or FastAPI + React)

### 3.2 Out of Scope (v1.0)
- Batch processing multiple documents
- Document classification/categorization
- Workflow automation (triggers, actions)
- Integration with external systems (ERP, CRM)
- Multi-language support (English only for MVP)
- Document comparison
- Handwriting recognition

### 3.3 Future Considerations (v2.0+)
- Multi-document querying (ask questions across documents)
- Table extraction and structure preservation
- Custom entity training
- API endpoints for integration
- Document similarity and duplicate detection
- Audit trail and compliance reporting

---

## 4. Functional Requirements

### 4.1 Document Upload Module

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| F1.1 | Upload PDF files up to 50 pages / 25MB | P0 | Core functionality |
| F1.2 | Upload images (JPG, PNG, TIFF) up to 10MB | P0 | OCR source |
| F1.3 | Detect if PDF is native text or scanned | P0 | Route to OCR if needed |
| F1.4 | Multi-page document support | P0 | Process entire document |
| F1.5 | Drag-and-drop upload interface | P1 | UX enhancement |
| F1.6 | Upload progress indicator | P0 | User feedback |
| F1.7 | File validation (type, size, corruption) | P0 | Error prevention |

### 4.2 OCR Module

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| F2.1 | Extract text from scanned PDFs | P0 | Tesseract / Cloud OCR |
| F2.2 | Extract text from images | P0 | JPG, PNG support |
| F2.3 | Handle rotated/skewed documents | P1 | Pre-processing |
| F2.4 | Multi-column layout detection | P1 | Preserve reading order |
| F2.5 | Confidence scores for OCR output | P2 | Quality indicator |
| F2.6 | Fallback to cloud OCR for difficult docs | P1 | Google Vision / AWS Textract |

### 4.3 Text Processing Module

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| F3.1 | Clean and normalize extracted text | P0 | Remove artifacts, fix spacing |
| F3.2 | Detect document structure (headers, paragraphs, lists) | P1 | Semantic chunking |
| F3.3 | Handle special characters and encodings | P0 | UTF-8 normalization |
| F3.4 | Sentence boundary detection | P0 | For chunking |
| F3.5 | Create searchable text index | P0 | For Q&A retrieval |

### 4.4 Entity Extraction Module

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| F4.1 | Extract dates (multiple formats) | P0 | Invoice dates, due dates |
| F4.2 | Extract monetary amounts (₹, $, €) | P0 | Totals, line items |
| F4.3 | Extract person names | P0 | Signatories, contacts |
| F4.4 | Extract organization names | P0 | Vendors, clients |
| F4.5 | Extract addresses | P1 | Billing, shipping |
| F4.6 | Extract email addresses and phone numbers | P1 | Contact info |
| F4.7 | Extract invoice/PO numbers | P1 | Document identifiers |
| F4.8 | Display extracted entities with confidence | P0 | User verification |

**Entity Extraction Schema:**
```json
{
  "entities": {
    "dates": [
      {"value": "2026-01-15", "label": "Invoice Date", "confidence": 0.95},
      {"value": "2026-02-14", "label": "Due Date", "confidence": 0.92}
    ],
    "amounts": [
      {"value": 15000.00, "currency": "INR", "label": "Total", "confidence": 0.98},
      {"value": 2700.00, "currency": "INR", "label": "Tax", "confidence": 0.94}
    ],
    "organizations": [
      {"value": "Acme Corp", "type": "vendor", "confidence": 0.89}
    ],
    "persons": [
      {"value": "Rahul Sharma", "type": "signatory", "confidence": 0.87}
    ]
  }
}
```

### 4.5 Summarization Module

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| F5.1 | Generate executive summary (100-200 words) | P0 | LLM-powered |
| F5.2 | Extract key points (5-10 bullets) | P0 | Structured summary |
| F5.3 | Identify document type | P1 | Invoice, contract, report |
| F5.4 | Highlight important sections | P1 | Draw attention to key info |
| F5.5 | Adjustable summary length | P2 | User preference |

### 4.6 Q&A Module (RAG)

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| F6.1 | Natural language question input | P0 | Chat interface |
| F6.2 | Semantic search over document | P0 | Vector embeddings |
| F6.3 | Retrieve relevant passages | P0 | Context for LLM |
| F6.4 | Generate accurate answers | P0 | Grounded in document |
| F6.5 | Cite source location (page, paragraph) | P0 | Verifiability |
| F6.6 | Handle "not found" gracefully | P0 | Don't hallucinate |
| F6.7 | Conversation history (multi-turn) | P1 | Follow-up questions |
| F6.8 | Suggested questions based on content | P2 | User guidance |

### 4.7 Export Module

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| F7.1 | Export extracted entities to JSON | P0 | Machine-readable |
| F7.2 | Export to CSV | P0 | Spreadsheet import |
| F7.3 | Export to Excel with formatting | P1 | Professional output |
| F7.4 | Export full text with annotations | P2 | Research use case |
| F7.5 | Export summary as PDF | P2 | Sharing |

### 4.8 User Interface

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| F8.1 | Clean, professional landing page | P0 | First impression |
| F8.2 | Document viewer (PDF preview) | P0 | See original |
| F8.3 | Entity highlighting in document | P1 | Visual feedback |
| F8.4 | Tabbed interface (Summary, Entities, Q&A, Export) | P0 | Organization |
| F8.5 | Real-time processing status | P0 | User feedback |
| F8.6 | Error messages with guidance | P0 | Actionable errors |
| F8.7 | Dark mode support | P2 | Nice to have |

---

## 5. Non-Functional Requirements

### 5.1 Performance

| Metric | Requirement |
|--------|-------------|
| Document processing (10 pages) | < 30 seconds |
| Document processing (50 pages) | < 90 seconds |
| Q&A response time | < 5 seconds |
| OCR processing (per page) | < 3 seconds |
| UI response | < 200ms |

### 5.2 Accuracy

| Metric | Requirement |
|--------|-------------|
| OCR accuracy (clean docs) | > 98% |
| OCR accuracy (scanned docs) | > 92% |
| Date extraction accuracy | > 95% |
| Amount extraction accuracy | > 95% |
| Name extraction accuracy | > 85% |
| Q&A relevance | > 85% |

### 5.3 Reliability
- Graceful degradation if OCR fails (show error, allow retry)
- LLM API fallback (Claude → OpenAI → local model)
- Session persistence (don't lose work on refresh)
- Rate limiting awareness for API calls

### 5.4 Security
- No persistent storage of documents (process in memory)
- Files deleted after session ends
- HTTPS for all API calls
- No PII logging
- Clear privacy policy displayed

### 5.5 Scalability
- Single-user application (v1.0)
- Stateless design for future multi-user support
- Configurable model providers

---

## 6. Technical Architecture

### 6.1 Tech Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Language | Python 3.11+ | Core expertise, ML ecosystem |
| Web Framework | FastAPI + Streamlit | API + quick UI |
| OCR | Tesseract (primary) | Free, local, good quality |
| OCR Fallback | Google Cloud Vision | High accuracy, paid |
| PDF Processing | PyMuPDF (fitz) | Fast, feature-rich |
| Embeddings | OpenAI text-embedding-3-small | High quality, affordable |
| Vector Store | ChromaDB | Simple, local, efficient |
| LLM | Claude API (claude-sonnet-4-20250514) | Primary reasoning |
| LLM Fallback | OpenAI GPT-4 | Backup |
| NER | spaCy (en_core_web_lg) | Entity extraction |
| Image Processing | Pillow, OpenCV | Pre-processing |

### 6.2 Project Structure

```
document-intelligence/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── streamlit_app.py        # Streamlit interface
│   ├── config.py               # Configuration
│   └── models.py               # Pydantic models
├── src/
│   ├── __init__.py
│   ├── document_loader.py      # PDF and image loading
│   ├── ocr_engine.py           # OCR processing
│   ├── text_processor.py       # Text cleaning, chunking
│   ├── entity_extractor.py     # NER and regex extraction
│   ├── summarizer.py           # LLM summarization
│   ├── qa_engine.py            # RAG Q&A system
│   ├── vector_store.py         # Embedding and retrieval
│   └── exporter.py             # Export to various formats
├── prompts/
│   ├── summarization.txt       # Summary prompt template
│   ├── qa_system.txt           # Q&A system prompt
│   └── entity_extraction.txt   # Entity extraction prompt
├── tests/
│   ├── test_ocr.py
│   ├── test_entities.py
│   ├── test_qa.py
│   └── sample_docs/            # Test documents
├── assets/
│   ├── logo.png
│   └── styles.css
├── requirements.txt
├── README.md
├── Dockerfile
└── docker-compose.yml
```

### 6.3 Processing Pipeline

```
[Document Upload]
       ↓
[File Type Detection] → [PDF Native] → [Text Extraction]
       ↓                                      ↓
[Scanned/Image] → [OCR Engine] → [Text Cleaning]
                                      ↓
                            [Text Chunking]
                                  ↓
              ┌───────────────────┼───────────────────┐
              ↓                   ↓                   ↓
      [Entity Extraction]  [Embedding Generation]  [Summarization]
              ↓                   ↓                   ↓
      [Structured Data]    [Vector Store]       [Summary Text]
              ↓                   ↓                   ↓
              └───────────────────┼───────────────────┘
                                  ↓
                         [Q&A Interface]
                                  ↓
                         [Export Options]
```

### 6.4 RAG Architecture

```
User Question
      ↓
[Query Embedding] → [Vector Search] → [Top-K Chunks]
                                            ↓
                                    [Reranking (optional)]
                                            ↓
                    [LLM Prompt: System + Context + Question]
                                            ↓
                                    [Answer + Citations]
```

---

## 7. User Experience Flow

### 7.1 Main Flow

1. **Landing Page**
   - Hero section with value proposition
   - "Upload Document" CTA button
   - Sample document demo option

2. **Upload**
   - Drag-and-drop or click to upload
   - Progress bar during upload
   - File validation feedback

3. **Processing**
   - "Analyzing your document..." message
   - Step-by-step progress (OCR → Extraction → Indexing)
   - Estimated time remaining

4. **Results Dashboard**
   - **Tab 1: Summary**
     - Document type badge
     - Executive summary paragraph
     - Key points as bullets
   - **Tab 2: Extracted Data**
     - Dates, amounts, names, organizations
     - Edit/correct option
     - Confidence indicators
   - **Tab 3: Q&A**
     - Chat interface
     - Suggested questions
     - Source citations
   - **Tab 4: Export**
     - Download buttons (JSON, CSV, Excel)
     - Full text download

5. **New Document**
   - Clear current document
   - Upload new file

### 7.2 Q&A Interaction

```
User: What is the total invoice amount?
System: The total invoice amount is ₹15,000.00, which includes a base amount 
        of ₹12,711.86 and GST of ₹2,288.14 (18%).
        
        📍 Source: Page 1, Section "Invoice Details"

User: When is the payment due?
System: The payment is due on February 14, 2026. This is 30 days from the 
        invoice date of January 15, 2026.
        
        📍 Source: Page 1, "Payment Terms"

User: Who signed this invoice?
System: The invoice was signed by Rahul Sharma, Finance Manager at Acme Corp.
        
        📍 Source: Page 2, Signature block
```

---

## 8. API Specification

### 8.1 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /upload | Upload document |
| GET | /status/{doc_id} | Get processing status |
| GET | /summary/{doc_id} | Get document summary |
| GET | /entities/{doc_id} | Get extracted entities |
| POST | /qa/{doc_id} | Ask question |
| GET | /export/{doc_id}/{format} | Export data |
| DELETE | /document/{doc_id} | Delete document |

### 8.2 Request/Response Examples

**Upload Document:**
```http
POST /upload
Content-Type: multipart/form-data

file: [binary]
```

**Response:**
```json
{
  "doc_id": "abc123",
  "filename": "invoice_2026.pdf",
  "pages": 2,
  "status": "processing",
  "estimated_time": 15
}
```

**Ask Question:**
```http
POST /qa/abc123
Content-Type: application/json

{
  "question": "What is the total amount?",
  "include_sources": true
}
```

**Response:**
```json
{
  "answer": "The total amount is ₹15,000.00, including GST.",
  "confidence": 0.95,
  "sources": [
    {
      "page": 1,
      "section": "Invoice Details",
      "text": "Total Amount: ₹15,000.00 (Incl. GST)"
    }
  ]
}
```

---

## 9. Deliverables

### 9.1 MVP Deliverables
- [ ] Working web application (Streamlit)
- [ ] PDF processing (native + OCR)
- [ ] Entity extraction (dates, amounts, names, orgs)
- [ ] Document summarization
- [ ] Q&A chat interface with citations
- [ ] Export to JSON, CSV, Excel
- [ ] Sample documents for demo
- [ ] README with setup instructions
- [ ] Requirements.txt
- [ ] Dockerfile

### 9.2 Documentation
- [ ] User Guide
- [ ] API Documentation
- [ ] Architecture Overview
- [ ] Portfolio Client Pack (PDF)

### 9.3 Demo Assets
- [ ] Screen recording of full workflow
- [ ] Sample processed documents
- [ ] Q&A session examples
- [ ] Before/after comparison

---

## 10. Timeline

| Phase | Tasks | Duration | Target |
|-------|-------|----------|--------|
| Setup | Project structure, dependencies, Docker | 1 day | Day 1 |
| Document Loading | PDF/image upload, native extraction | 1 day | Day 2 |
| OCR Integration | Tesseract setup, image processing | 2 days | Day 4 |
| Text Processing | Cleaning, chunking, indexing | 1 day | Day 5 |
| Entity Extraction | spaCy + regex patterns | 2 days | Day 7 |
| Vector Store | ChromaDB, embedding generation | 1 day | Day 8 |
| Q&A Engine | RAG implementation, prompts | 2 days | Day 10 |
| Summarization | LLM integration, prompt tuning | 1 day | Day 11 |
| Export Module | JSON, CSV, Excel output | 1 day | Day 12 |
| UI Development | Streamlit interface, styling | 2 days | Day 14 |
| Testing | End-to-end, edge cases | 1 day | Day 15 |
| Documentation | README, guides, portfolio | 1 day | Day 16 |
| **Total** | | **16-18 days** | |

---

## 11. Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| OCR accuracy on poor scans | High | Medium | Cloud OCR fallback, pre-processing |
| LLM hallucination in Q&A | High | Medium | Strict grounding, confidence thresholds |
| Processing time for large docs | Medium | Medium | Async processing, progress feedback |
| API costs during development | Low | High | Use smaller models, caching |
| Complex document layouts | Medium | Medium | Focus on standard formats first |

---

## 12. Success Criteria

### 12.1 Functional
- [ ] Process invoice PDF and extract all key fields correctly
- [ ] Process scanned document with > 90% OCR accuracy
- [ ] Answer 5 factual questions correctly from a test document
- [ ] Generate relevant summary that captures main points
- [ ] Export to all formats without errors

### 12.2 Portfolio
- [ ] Demo video under 4 minutes showing full capability
- [ ] Clean, impressive UI that non-technical users can appreciate
- [ ] Code is modular, documented, and ready for GitHub
- [ ] README clearly explains business value

---

## 13. Appendix

### A. Sample Entity Patterns

```python
PATTERNS = {
    "invoice_number": [
        r"Invoice\s*#?\s*:?\s*([A-Z0-9-]+)",
        r"Inv\s*No\.?\s*:?\s*([A-Z0-9-]+)",
    ],
    "date": [
        r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
        r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})",
    ],
    "amount_inr": [
        r"₹\s*([\d,]+\.?\d*)",
        r"Rs\.?\s*([\d,]+\.?\d*)",
        r"INR\s*([\d,]+\.?\d*)",
    ],
    "gstin": [
        r"\b(\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1})\b",
    ],
    "pan": [
        r"\b([A-Z]{5}\d{4}[A-Z]{1})\b",
    ],
}
```

### B. System Prompts

**Summarization Prompt:**
```
You are a document analyst. Analyze the following document and provide:

1. DOCUMENT TYPE: Identify what type of document this is (invoice, contract, report, letter, etc.)

2. EXECUTIVE SUMMARY: Write a 2-3 sentence summary of the document's purpose and key content.

3. KEY POINTS: List 5-7 most important facts or takeaways from the document.

Document Text:
{document_text}

Respond in JSON format:
{
  "document_type": "...",
  "summary": "...",
  "key_points": ["...", "..."]
}
```

**Q&A System Prompt:**
```
You are a document assistant. Answer questions based ONLY on the provided document context. 

Rules:
- Only use information from the context provided
- If the answer is not in the context, say "I cannot find this information in the document"
- Always cite the source (page number, section) when possible
- Be concise and direct
- For numerical questions, provide exact figures from the document

Context:
{context}

Question: {question}

Answer:
```

### C. Document Type Patterns

| Document Type | Key Indicators |
|---------------|----------------|
| Invoice | Invoice #, Total, Due Date, Bill To |
| Contract | Agreement, Party, Terms, Signature |
| Receipt | Receipt #, Amount Paid, Thank You |
| Report | Executive Summary, Findings, Recommendations |
| Letter | Dear, Sincerely, Date |
| Resume | Experience, Education, Skills |

---

*Document Version History*

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-20 | Biswajit | Initial draft |
