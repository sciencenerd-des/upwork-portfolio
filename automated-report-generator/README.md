# Automated Report Generator

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-green?logo=streamlit)](https://automated-report-generator.streamlit.app)

Transform raw CSV/Excel files into polished PDF and Word reports with charts, summaries, and optional AI commentary.

## The Business Problem

**Manual reporting is expensive.**

Business analysts spend 4+ hours per report cleaning data, building charts, formatting documents, and writing executive summaries. This repetitive work delays decisions, introduces errors, and pulls talent away from strategic analysis.

**Our solution:** Upload your data and generate executive-ready reports in 30 seconds.

## Who Uses This

- **Sales Operations** — Weekly pipeline reports, territory performance summaries
- **Financial Analysts** — P&L statements, expense tracking, budget variance reports
- **Inventory Managers** — Stock level analysis, reorder alerts, cost summaries
- **Consultants** — Client-ready deliverables without the manual formatting

## Try the Demo

Experience the report generator instantly—no signup required.

**Live Demo:** https://automated-report-generator.streamlit.app

### Quick Start with Sample Data

1. Visit the demo link above
2. Download a sample file:
   - [Sales Sample](sample_data/sales_sample.csv) — Revenue trends by product
   - [Financial Sample](sample_data/financial_sample.csv) — Expense tracking
   - [Inventory Sample](sample_data/inventory_sample.csv) — Stock levels and costs
3. Upload to the app
4. Select matching report template
5. Click **Generate Report**
6. Download your PDF and Word documents

*No data is stored. Files are processed in memory and deleted immediately after report generation.*

## Screenshot Gallery

| Upload & Validation | Column Mapping | Report Generation |
|---|---|---|
| ![Upload Step](assets/screenshots/01-data-upload.png) | ![Template and Mapping](assets/screenshots/02-column-mapping.png) | ![Generate Report](assets/screenshots/03-report-generation.png) |

## What It Does

- **Multi-format support** — CSV and Excel uploads (`.csv`, `.xlsx`, `.xls`)
- **Intelligent mapping** — Auto-detects and maps columns to template fields
- **Professional visualizations** — Line, bar, and pie charts with consistent styling
- **Executive deliverables** — PDF and Word reports ready for client presentation
- **Smart insights** — Optional AI-powered commentary on your data
- **Batch processing** — Combine multiple files into unified reports

## Crystal-Clear Setup

### 1. Prerequisites

- Python 3.9+
- `pip`

### 2. Install

```bash
git clone https://github.com/sciencenerd-des/upwork-portfolio.git
cd upwork-portfolio/automated-report-generator

python -m venv .venv
source .venv/bin/activate  # Windows (PowerShell): .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 3. (Optional) Enable AI Insights

```bash
export OPENROUTER_API_KEY=your_api_key_here
# Windows (PowerShell): $env:OPENROUTER_API_KEY="your_api_key_here"
```

Get a key from [OpenRouter](https://openrouter.ai/).

### 4. Run

```bash
streamlit run app.py
```

Open `http://localhost:8501`.

### 5. First Run Checklist

1. Upload `sample_data/sales_sample.csv`
2. Pick `Sales Report`
3. Keep auto-mapped columns
4. Click `Generate Report`
5. Download PDF and DOCX

## Usage Flow

1. Upload one or more files
2. Select report type (Sales, Financial, Inventory)
3. Review auto-mapped columns
4. Toggle AI insights/output formats
5. Generate and download reports

## Report Templates

### Sales Report
**Best for:** Revenue tracking, product performance, sales team metrics

**Required columns:** `Date`, `Product`, `Revenue`

### Financial Report
**Best for:** Expense management, budget tracking, financial summaries

**Required columns:** `Date`, `Category`, `Amount`, `Transaction Type`

### Inventory Report
**Best for:** Stock management, reorder planning, cost analysis

**Required columns:** `Product`, `Quantity`, `Reorder Level`, `Unit Cost`

## Trust & Security

- **No data persistence** — Files are processed in memory only
- **No external storage** — Your data never leaves the session
- **No tracking** — No analytics, cookies, or user identification
- **Self-hostable** — Run entirely on your infrastructure
- **Optional AI** — AI features only activate with your API key

## Architecture Diagram

```text
┌──────────────────────────────┐
│ Streamlit UI (app.py)        │
│ - Upload                     │
│ - Mapping                    │
│ - Options                    │
└──────────────┬───────────────┘
               │
               v
┌──────────────────────────────┐
│ Data Processor               │
│ src/data_processor.py        │
│ - load/merge/validate        │
│ - infer column types         │
└──────────────┬───────────────┘
               │
               ├─────────────┐
               v             v
┌─────────────────────┐   ┌─────────────────────┐
│ Chart Generator     │   │ AI Insights         │
│ src/chart_generator │   │ src/ai_insights.py  │
│ - line/bar/pie      │   │ - OpenRouter (opt.) │
└──────────┬──────────┘   └──────────┬──────────┘
           └──────────────┬──────────┘
                          v
               ┌──────────────────────────┐
               │ Report Builder           │
               │ src/report_builder.py    │
               │ - PDF (ReportLab)        │
               │ - DOCX (python-docx)     │
               └──────────┬───────────────┘
                          v
               ┌──────────────────────────┐
               │ Download Artifacts       │
               │ - *.pdf                  │
               │ - *.docx                 │
               └──────────────────────────┘
```

## Project Structure

```text
automated-report-generator/
├── app.py
├── requirements.txt
├── config/
│   ├── templates.yaml
│   └── styles.yaml
├── sample_data/
├── src/
│   ├── data_processor.py
│   ├── chart_generator.py
│   ├── ai_insights.py
│   └── report_builder.py
├── templates/
└── tests/
```

## Tests

```bash
python -m pytest tests/ -v
```

## Tech Stack

- Streamlit
- Pandas
- Matplotlib + Seaborn
- ReportLab
- python-docx
- OpenRouter API (optional)

## License

MIT
