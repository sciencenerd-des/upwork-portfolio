# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains portfolio projects for Upwork freelancing, showcasing skills in Excel, Python automation, AI/NLP, and full-stack development. The projects are designed to demonstrate professional-grade work for potential clients.

## Repository Structure

```
├── automated-report-generator/   # Project 1: Streamlit report generator
│   ├── ARG-PRD.md               # Product requirements document
│   ├── src/                     # Core modules
│   ├── templates/               # Report templates
│   └── sample_data/             # Demo CSV files
│
├── document-intelligence/        # Project 2: Document processing system
│   ├── DI-PRD.md                # Product requirements document
│   ├── app/                     # FastAPI + Streamlit apps
│   ├── src/                     # OCR, NER, RAG modules
│   └── prompts/                 # LLM prompt templates
│
└── task-manager/                 # Project 3: Full-stack task management
    ├── TM-PRD.md                # Product requirements document
    ├── task-manager-frontend/   # Next.js 14 app
    └── task-manager-backend/    # FastAPI backend
```

## Projects

### 1. Automated Report Generator
- **PRD:** `automated-report-generator/ARG-PRD.md`
- **Stack:** Python 3.11+, Streamlit, Pandas, Matplotlib, ReportLab, python-docx, Anthropic SDK
- **Purpose:** Generate PDF/Word reports from CSV/Excel data with AI-powered insights

### 2. Document Intelligence System
- **PRD:** `document-intelligence/DI-PRD.md`
- **Stack:** Python 3.11+, FastAPI, Streamlit, PyMuPDF, Tesseract OCR, spaCy, ChromaDB, Anthropic SDK
- **Purpose:** Document processing with OCR, entity extraction, summarization, and RAG-based Q&A

### 3. Task & Project Management Tool
- **PRD:** `task-manager/TM-PRD.md`
- **Stack:** Next.js 14, Tailwind CSS, shadcn/ui, @dnd-kit/core (frontend); FastAPI, PostgreSQL, SQLAlchemy, python-jose (backend)
- **Purpose:** Full-stack task management with Kanban board, list view, and JWT authentication
- **Deployment:** Vercel (frontend) + Railway (backend + PostgreSQL)

## Build Order

1. Automated Report Generator (P0)
2. Document Intelligence System (P0)
3. Task Management Tool (P0)

## Code Standards

- Use type hints (Python) and TypeScript
- Configuration via files, no hardcoded values
- Modular architecture with separation of concerns
- Include sample data for all demos
- Generate comprehensive README with setup instructions

## Performance Requirements

- Report Generator: < 30s for 10,000 rows
- Document Intelligence: < 30s for 10 pages, < 90s for 50 pages
- Task Manager API: < 200ms response time (p95)

## Reference

- `Project-overview.md` - High-level portfolio overview
- Each project's PRD file contains detailed specifications, database schemas, and API endpoints
