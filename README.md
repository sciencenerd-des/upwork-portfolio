# Upwork Portfolio Projects

Three production-ready portfolio projects demonstrating full-stack development, AI integration, and data automation expertise.

---

## 🚀 Live Demos

| Project | Platform | Status | Live URL |
|---------|----------|--------|----------|
| **Automated Report Generator** | Streamlit Cloud | ✅ **LIVE** | https://sciencenerd-des-upwork-por-automated-report-generatorapp-vuwedn.streamlit.app |
| **Document Intelligence** | Render | ✅ **LIVE** | https://upwork-portfolio-gx4d.onrender.com |
| **Task Manager** | Vercel | ✅ **LIVE** | [https://task-manager-frontend-lvabx3u4j.vercel.app](https://task-manager-frontend-lvabx3u4j.vercel.app) |

---

## 📊 Project 1: Automated Report Generator

Transform CSV/Excel data into professional PDF/Word reports with charts and AI insights.

[![Deploy to Streamlit Cloud](https://img.shields.io/badge/Deploy-Streamlit%20Cloud-FF4B4B?logo=streamlit)](https://share.streamlit.io/deploy?repository=sciencenerd-des/upwork-portfolio&branch=main&mainModule=automated-report-generator/app.py)

**Tech:** Python, Streamlit, Pandas, ReportLab, OpenRouter API  
**Folder:** `automated-report-generator/`  
**Local Run:** `cd automated-report-generator && streamlit run app.py`

### Quick Deploy Steps
1. Click deploy button above
2. Select repository: `sciencenerd-des/upwork-portfolio`
3. Set Main file path: `automated-report-generator/app.py`
4. (Optional) Add `OPENROUTER_API_KEY` for AI insights
5. Click Deploy

---

## 📄 Project 2: Document Intelligence System

AI-powered document processing with OCR, entity extraction, and RAG-based Q&A.

[![Deploy to Render](https://img.shields.io/badge/Deploy-Render-46E3B7?logo=render)](https://render.com/deploy?repo=https://github.com/sciencenerd-des/upwork-portfolio)

**Tech:** FastAPI, Streamlit, Tesseract OCR, ChromaDB, LangChain  
**Folder:** `document-intelligence/`  
**Local Run:** 
```bash
cd document-intelligence
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Quick Deploy Steps
1. Click deploy button above or go to [Render Dashboard](https://dashboard.render.com)
2. Create New Web Service
3. Connect GitHub repo
4. Set Root Directory: `document-intelligence`
5. Runtime: Docker
6. Add env vars: `OPENROUTER_API_KEY`, `DI_API_KEY`
7. Deploy

---

## 🎯 Project 3: Task Management System (Northstar PM)

Enterprise-grade project management with Notion-level polish.

**✅ LIVE DEMO:** [https://task-manager-frontend-lvabx3u4j.vercel.app](https://task-manager-frontend-lvabx3u4j.vercel.app)

**Tech:** Next.js 14, TypeScript, Convex, WorkOS Auth, Tailwind CSS  
**Folder:** `task-manager/task-manager-frontend/`  
**Local Run:** `cd task-manager/task-manager-frontend && npm install && npm run dev`

---

## 🛠️ Development Setup

```bash
# Clone repository
git clone https://github.com/sciencenerd-des/upwork-portfolio.git
cd upwork-portfolio

# Project 1: Automated Report Generator
cd automated-report-generator
pip install -r requirements.txt
streamlit run app.py

# Project 2: Document Intelligence  
cd document-intelligence
pip install -r requirements.txt
uvicorn app.main:app --reload

# Project 3: Task Manager
cd task-manager/task-manager-frontend
npm install
npm run dev
```

---

## 📋 Deployment Status

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed deployment instructions and troubleshooting.

---

**License:** MIT  
**Portfolio:** https://www.upwork.com/freelancers/~01228b6c590d97c3cc
