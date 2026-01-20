# Upwork Portfolio Project Setup Prompt

## Context

I am Biswajit, an Auditor in the Indian Audit and Accounts Department with an engineering background (IIEST Shibpur, 2016). I'm building a portfolio for Upwork freelancing to showcase skills in Excel, Python automation, AI/NLP, and full-stack development.

## Completed Work

### Excel Templates (✅ Complete)
Location: `/home/claude/01-excel-templates/`

| Template | File | Formulas |
|----------|------|----------|
| Expense Tracker | `expense-tracker/expense_tracker_budget_vs_actual.xlsx` | 958 |
| Invoice Tracker | `invoice-tracker/invoice_tracker_aging.xlsx` | 794 |
| Financial Dashboard | `financial-dashboard/financial_dashboard.xlsx` | 586 |
| Loan Calculator | `loan-amortization/loan_amortization_calculator.xlsx` | 6,789 |
| Data Analysis | `data-analysis/sales_data_analysis.xlsx` | 2,730 |

**Total:** 11,857 formulas, all with documentation and Client Pack PDFs.

---

## Projects to Build

### Project 1: Automated Report Generator

**PRD:** `/home/claude/01-excel-templates/PRDs/01-automated-report-generator-prd.md`

**What to Build:**
- Streamlit web app for generating PDF/Word reports from CSV/Excel data
- 3 report templates: Sales Report, Financial Summary, Inventory Report
- Auto-generated charts (line, bar, pie) using Matplotlib
- AI-powered narrative insights using Claude API
- Professional PDF output with ReportLab
- Word output with python-docx

**Tech Stack:**
```
Python 3.11+, Streamlit, Pandas, Matplotlib, Seaborn, 
ReportLab, python-docx, Anthropic SDK
```

**Project Structure:**
```
automated-report-generator/
├── app.py                    # Streamlit main app
├── requirements.txt
├── README.md
├── config/
│   ├── templates.yaml        # Template definitions
│   └── styles.yaml           # Chart and report styles
├── src/
│   ├── __init__.py
│   ├── data_processor.py     # Data loading, validation, cleaning
│   ├── chart_generator.py    # Chart creation functions
│   ├── report_builder.py     # PDF and DOCX generation
│   ├── ai_insights.py        # LLM integration
│   └── utils.py
├── templates/
│   ├── sales_report.py
│   ├── financial_report.py
│   └── inventory_report.py
├── sample_data/
│   ├── sales_sample.csv
│   ├── financial_sample.csv
│   └── inventory_sample.csv
└── outputs/                  # Generated reports
```

**Key Requirements:**
- Data validation with clear error messages
- Column auto-mapping with manual override
- Charts: Professional styling, consistent color palette
- PDF: Header, footer, page numbers, embedded charts
- AI: 3-5 bullet insights, toggle on/off, graceful API failure handling
- Processing time < 30 seconds for 10,000 rows

**Deliverables:**
- [ ] Working Streamlit app
- [ ] 3 report templates with sample data
- [ ] PDF and Word export
- [ ] AI insights integration
- [ ] README with setup instructions
- [ ] Demo video/screenshots

---

### Project 2: Document Intelligence System

**PRD:** `/home/claude/01-excel-templates/PRDs/02-document-intelligence-prd.md`

**What to Build:**
- FastAPI + Streamlit app for document processing
- PDF upload (native + scanned) with OCR
- Image upload (JPG, PNG) with OCR
- Entity extraction: dates, amounts, names, organizations
- Document summarization using Claude API
- Q&A chat interface (RAG) over document content
- Export extracted data to JSON, CSV, Excel

**Tech Stack:**
```
Python 3.11+, FastAPI, Streamlit, PyMuPDF, Tesseract OCR,
spaCy, ChromaDB, OpenAI Embeddings, Anthropic SDK
```

**Project Structure:**
```
document-intelligence/
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI app
│   ├── streamlit_app.py      # Streamlit interface
│   ├── config.py
│   └── models.py             # Pydantic models
├── src/
│   ├── __init__.py
│   ├── document_loader.py    # PDF and image loading
│   ├── ocr_engine.py         # OCR processing
│   ├── text_processor.py     # Text cleaning, chunking
│   ├── entity_extractor.py   # NER and regex extraction
│   ├── summarizer.py         # LLM summarization
│   ├── qa_engine.py          # RAG Q&A system
│   ├── vector_store.py       # Embedding and retrieval
│   └── exporter.py           # Export functions
├── prompts/
│   ├── summarization.txt
│   ├── qa_system.txt
│   └── entity_extraction.txt
├── tests/
│   └── sample_docs/          # Test documents
├── requirements.txt
├── README.md
└── Dockerfile
```

**Key Requirements:**
- OCR: Tesseract primary, Cloud OCR fallback for difficult docs
- Entities: Dates, amounts (₹, $), names, organizations, GSTIN, PAN
- Q&A: Vector search with ChromaDB, cite source (page, section)
- Summarization: Document type detection, executive summary, key points
- Processing: < 30s for 10 pages, < 90s for 50 pages
- No persistent storage (process in memory, delete after session)

**Deliverables:**
- [ ] Working web application
- [ ] PDF + image processing with OCR
- [ ] Entity extraction with confidence scores
- [ ] Q&A chat interface with citations
- [ ] Export to JSON, CSV, Excel
- [ ] Sample documents for demo
- [ ] README and Dockerfile

---

### Project 3: Task & Project Management Tool

**PRD:** `/home/claude/01-excel-templates/PRDs/03-task-management-tool-prd.md`

**What to Build:**
- Full-stack web app with Next.js frontend and FastAPI backend
- User authentication (JWT with access + refresh tokens)
- Project CRUD with color coding
- Task CRUD with status, priority, due dates
- Kanban board with drag-and-drop
- List view with sorting and filtering
- Dashboard with task summary
- Responsive design (mobile, tablet, desktop)
- Production deployment (Vercel + Railway)

**Tech Stack:**
```
Frontend: Next.js 14, Tailwind CSS, shadcn/ui, @dnd-kit/core
Backend: FastAPI, PostgreSQL, SQLAlchemy, Alembic, python-jose
Deployment: Vercel (FE), Railway (BE + DB)
```

**Frontend Structure:**
```
task-manager-frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── (dashboard)/
│   │   ├── dashboard/page.tsx
│   │   ├── project/[id]/page.tsx
│   │   └── settings/page.tsx
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/
│   ├── ui/                   # shadcn components
│   ├── layout/
│   ├── projects/
│   ├── tasks/
│   └── dashboard/
├── lib/
│   ├── api.ts
│   ├── auth.ts
│   └── utils.ts
├── hooks/
├── types/
└── package.json
```

**Backend Structure:**
```
task-manager-backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── services/
│   └── utils/
├── alembic/
├── tests/
├── requirements.txt
└── Dockerfile
```

**Database Schema:**
```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projects
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    color VARCHAR(7) DEFAULT '#2563EB',
    status VARCHAR(20) DEFAULT 'active',
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'todo',      -- todo, in_progress, done
    priority VARCHAR(20) DEFAULT 'medium',  -- low, medium, high, urgent
    due_date DATE,
    position INTEGER DEFAULT 0,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Requirements:**
- Auth: JWT tokens, bcrypt password hashing, protected routes
- Kanban: 3 columns (To Do, In Progress, Done), smooth drag-drop
- UI: Clean, modern design comparable to commercial tools
- API: < 200ms response time, proper error handling
- Deploy: Live demo URL accessible without registration

**Deliverables:**
- [ ] Frontend application (Next.js)
- [ ] Backend API (FastAPI)
- [ ] Database with migrations
- [ ] User authentication
- [ ] Kanban + List views
- [ ] Dashboard
- [ ] Production deployment
- [ ] README and documentation

---

## Build Order & Timeline

| Week | Project | Days | Priority |
|------|---------|------|----------|
| Week 3-4 | Automated Report Generator | 12 | P0 |
| Week 5-6 | Document Intelligence System | 16-18 | P0 |
| Week 7-9 | Task Management Tool | 19-21 | P0 |

## Quality Standards

### Code Quality
- Modular architecture with separation of concerns
- Type hints (Python) / TypeScript
- Comprehensive error handling
- No hardcoded values (use config files)
- Clear docstrings and comments

### Documentation
- README with: Overview, Features, Setup, Usage, Screenshots
- Environment variables documented
- API documentation (auto-generated for FastAPI)

### Testing
- Sample data for all demos
- End-to-end testing of main flows
- Edge case handling

### Portfolio Assets
- Demo video (3-5 minutes per project)
- Screenshots for Upwork profile
- Client Pack PDF with value proposition

---

## Instructions for Building

When I ask to build any of these projects:

1. **Read the full PRD** from the specified path
2. **Create project structure** with all directories and files
3. **Build incrementally** - core functionality first, then enhancements
4. **Test each component** before moving to next
5. **Generate sample data** for demos
6. **Create README** with professional documentation
7. **Provide deliverable checklist** showing completion status

Start with: "Which project would you like to build? I recommend starting with the Automated Report Generator."

---

## File Locations

```
/home/claude/01-excel-templates/
├── expense-tracker/          # ✅ Complete
├── invoice-tracker/          # ✅ Complete
├── financial-dashboard/      # ✅ Complete
├── loan-amortization/        # ✅ Complete
├── data-analysis/            # ✅ Complete
└── PRDs/
    ├── PORTFOLIO_OVERVIEW.md           # This file
    ├── 01-automated-report-generator-prd.md
    ├── 02-document-intelligence-prd.md
    └── 03-task-management-tool-prd.md

/mnt/user-data/outputs/       # All deliverables copied here
```

---

*Last Updated: January 20, 2026*
