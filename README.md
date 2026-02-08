# Upwork Portfolio Projects

This repository contains three portfolio-grade projects plus supporting Excel templates.

**Projects**
1. Automated Report Generator (`automated-report-generator/`)
Run: `streamlit run app.py`
Tests: `python -m pytest tests/ -v`

2. Document Intelligence System (`document-intelligence/`)
Run UI: `streamlit run app/streamlit_app.py`
Run API: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
Tests: `pytest tests/`

3. Task Manager (Next.js + Convex + WorkOS) (`task-manager/task-manager-frontend/`)
Install: `npm install`
Run: `npm run dev`
Backend: `npx convex dev`

**Excel Templates**
Location: `Excel_files/`

**License**
MIT
