# Product Requirements Document
## Automated Report Generator

**Version:** 1.0  
**Date:** January 20, 2026  
**Author:** Biswajit  
**Status:** Draft

---

## 1. Executive Summary

### 1.1 Product Vision
A Python-based tool that transforms raw data (CSV/Excel) into professionally formatted PDF and Word reports with charts, tables, and AI-generated narrative insights. Target users: small business owners, analysts, and consultants who need to produce recurring reports quickly.

### 1.2 Business Objectives
- Demonstrate automation and data processing skills for Upwork portfolio
- Showcase ability to generate professional business documents programmatically
- Highlight AI integration capabilities through narrative generation
- Create a reusable tool that can be customized for client engagements

### 1.3 Success Metrics
- Generate complete report from raw data in under 30 seconds
- Support at least 3 report templates (Sales, Financial, Inventory)
- Produce pixel-perfect PDF output matching professional standards
- Achieve zero manual intervention from data upload to report download

---

## 2. Problem Statement

### 2.1 Current Pain Points
- Businesses spend 2-4 hours weekly creating recurring reports manually
- Copy-pasting data into templates is error-prone
- Maintaining consistent formatting across reports is tedious
- Non-technical users struggle with Excel charting and formatting
- AI insights require manual ChatGPT interactions and copy-pasting

### 2.2 Target Users

| User Persona | Description | Primary Need |
|--------------|-------------|--------------|
| Small Business Owner | Runs a retail/service business, needs monthly sales reports | Quick automated reports for stakeholders |
| Financial Analyst | Prepares weekly/monthly financial summaries | Consistent formatting, time savings |
| Operations Manager | Tracks inventory and fulfillment metrics | Automated KPI tracking and visualization |
| Consultant | Delivers client reports regularly | Professional output, customizable templates |

---

## 3. Product Scope

### 3.1 In Scope (MVP)
- CSV and Excel file upload
- Pre-built report templates (Sales, Financial, Inventory)
- Automatic chart generation (line, bar, pie)
- Summary statistics calculation
- AI-generated narrative insights (optional toggle)
- PDF export with professional formatting
- Word/DOCX export
- Web interface (Streamlit)

### 3.2 Out of Scope (v1.0)
- Database connections (future enhancement)
- Google Sheets integration (future enhancement)
- Scheduled/automated report generation
- Email delivery
- Multi-user authentication
- Template editor/builder

### 3.3 Future Considerations (v2.0+)
- Custom template designer
- API endpoints for integration
- Batch processing multiple files
- White-label branding options
- Cloud deployment with user accounts

---

## 4. Functional Requirements

### 4.1 Data Input Module

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| F1.1 | Upload CSV files up to 10MB | P0 | Core functionality |
| F1.2 | Upload Excel files (.xlsx, .xls) up to 10MB | P0 | Core functionality |
| F1.3 | Auto-detect column types (date, numeric, text) | P0 | Use pandas inference |
| F1.4 | Preview first 10 rows of uploaded data | P1 | User confirmation |
| F1.5 | Handle missing values gracefully | P0 | Fill or flag |
| F1.6 | Support multiple sheets from Excel (selectable) | P1 | Dropdown selection |
| F1.7 | Validate data against template requirements | P0 | Clear error messages |

### 4.2 Template Selection Module

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| F2.1 | Sales Report Template | P0 | Revenue, units, trends |
| F2.2 | Financial Summary Template | P0 | P&L style, margins |
| F2.3 | Inventory Report Template | P0 | Stock levels, turnover |
| F2.4 | Template preview before generation | P1 | Show sample output |
| F2.5 | Column mapping interface | P0 | Map data cols to template fields |

### 4.3 Report Templates Specification

#### Template 1: Sales Report
**Required Columns:** Date, Product/Category, Quantity, Revenue, Region (optional)

**Report Sections:**
1. **Executive Summary** - Total revenue, units sold, avg order value, period covered
2. **Revenue Trend** - Line chart of revenue over time (daily/weekly/monthly auto-detect)
3. **Product Performance** - Bar chart of top 10 products by revenue
4. **Regional Breakdown** - Pie chart of revenue by region (if region column present)
5. **Detailed Data Table** - Top 20 transactions by revenue
6. **AI Insights** - 3-5 bullet points analyzing trends and anomalies

#### Template 2: Financial Summary
**Required Columns:** Date, Category, Amount, Type (Income/Expense)

**Report Sections:**
1. **Financial Overview** - Total income, total expenses, net profit, profit margin
2. **Monthly Trend** - Line chart showing income vs expenses over time
3. **Expense Breakdown** - Pie chart of expenses by category
4. **Income Sources** - Bar chart of income by category
5. **Month-over-Month Comparison** - Table with MoM changes
6. **AI Insights** - Commentary on financial health and trends

#### Template 3: Inventory Report
**Required Columns:** Product, Category, Quantity, Reorder_Level, Unit_Cost

**Report Sections:**
1. **Inventory Summary** - Total SKUs, total units, total value, items below reorder
2. **Stock Status** - Bar chart of quantity by category
3. **Reorder Alerts** - Table of items at or below reorder level
4. **Value Distribution** - Pie chart of inventory value by category
5. **Top Items by Value** - Table of highest-value inventory items
6. **AI Insights** - Recommendations on stock management

### 4.4 Chart Generation Module

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| F4.1 | Line charts with proper axis labels | P0 | For trends |
| F4.2 | Bar charts (horizontal and vertical) | P0 | For comparisons |
| F4.3 | Pie charts with labels and percentages | P0 | For distributions |
| F4.4 | Professional color palette | P0 | Consistent branding |
| F4.5 | Chart titles and legends | P0 | Self-documenting |
| F4.6 | Export charts as PNG for embedding | P0 | PDF compatibility |

### 4.5 AI Insights Module

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| F5.1 | Generate 3-5 bullet point insights | P1 | Use Claude/OpenAI API |
| F5.2 | Identify trends (up/down/stable) | P1 | Compare periods |
| F5.3 | Flag anomalies (outliers, sudden changes) | P1 | Statistical detection |
| F5.4 | Provide actionable recommendations | P2 | Business context |
| F5.5 | Toggle AI insights on/off | P0 | User preference |
| F5.6 | Handle API failures gracefully | P0 | Fallback to basic stats |

### 4.6 Report Generation Module

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| F6.1 | Generate PDF with embedded charts | P0 | ReportLab or WeasyPrint |
| F6.2 | Generate Word document (.docx) | P0 | python-docx |
| F6.3 | Professional header with report title and date | P0 | Branding |
| F6.4 | Page numbers and footer | P0 | Professional touch |
| F6.5 | Table of contents for multi-page reports | P2 | Optional |
| F6.6 | Consistent fonts and spacing | P0 | Typography standards |
| F6.7 | Download button for generated report | P0 | Core UX |

### 4.7 User Interface (Streamlit)

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| F7.1 | Clean, professional UI design | P0 | Not default Streamlit |
| F7.2 | Step-by-step wizard flow | P0 | Upload → Configure → Generate |
| F7.3 | Progress indicator during generation | P0 | User feedback |
| F7.4 | Error messages with clear guidance | P0 | Actionable errors |
| F7.5 | Report preview before download | P1 | In-browser preview |
| F7.6 | Mobile-responsive layout | P2 | Nice to have |

---

## 5. Non-Functional Requirements

### 5.1 Performance
- Report generation: < 30 seconds for files up to 10,000 rows
- File upload: < 5 seconds for 10MB file
- UI response: < 200ms for all interactions

### 5.2 Reliability
- Handle malformed CSV/Excel gracefully with clear error messages
- API timeout handling (LLM calls)
- No data loss on browser refresh (session state)

### 5.3 Scalability
- Single-user application (v1.0)
- Designed for easy migration to multi-user (session isolation)

### 5.4 Security
- No persistent storage of uploaded data
- Files processed in memory, deleted after session
- No authentication required (v1.0)

### 5.5 Maintainability
- Modular code architecture (separate modules for data, charts, reports, AI)
- Comprehensive docstrings
- Configuration file for templates (YAML/JSON)

---

## 6. Technical Architecture

### 6.1 Tech Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Language | Python 3.11+ | Core expertise, rich ecosystem |
| Web Framework | Streamlit | Rapid development, good UX |
| Data Processing | Pandas | Industry standard |
| Charts | Matplotlib + Seaborn | Publication quality |
| PDF Generation | ReportLab | Full control, professional output |
| Word Generation | python-docx | Native .docx support |
| AI Integration | Anthropic Claude API | Primary LLM |
| Fallback AI | OpenAI GPT-4 | Backup option |

### 6.2 Project Structure

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
│   └── utils.py              # Helper functions
├── templates/
│   ├── sales_report.py       # Sales template logic
│   ├── financial_report.py   # Financial template logic
│   └── inventory_report.py   # Inventory template logic
├── assets/
│   ├── fonts/                # Custom fonts
│   └── logos/                # Branding assets
├── sample_data/
│   ├── sales_sample.csv
│   ├── financial_sample.csv
│   └── inventory_sample.csv
└── tests/
    ├── test_data_processor.py
    ├── test_chart_generator.py
    └── test_report_builder.py
```

### 6.3 Data Flow

```
[User Upload] → [Data Validation] → [Column Mapping] → [Template Selection]
                                                              ↓
[Download Report] ← [PDF/DOCX Generation] ← [Chart Creation] ← [Data Analysis]
                                                              ↓
                                                    [AI Insights (optional)]
```

---

## 7. User Experience Flow

### 7.1 Happy Path

1. **Upload Data**
   - User lands on home page
   - Clicks "Upload File" button
   - Selects CSV or Excel file
   - System validates and shows preview

2. **Select Template**
   - System suggests template based on columns detected
   - User confirms or selects different template
   - Preview of sample report shown

3. **Configure Mapping**
   - System auto-maps columns where possible
   - User adjusts mappings via dropdowns
   - Validation shows green checkmarks

4. **Generate Options**
   - User toggles AI insights on/off
   - Selects output format (PDF, Word, or both)
   - Clicks "Generate Report"

5. **Download**
   - Progress bar shows generation status
   - Preview displayed in browser
   - Download buttons appear for each format

### 7.2 Error Handling

| Error Scenario | User Message | System Action |
|----------------|--------------|---------------|
| Invalid file format | "Please upload a CSV or Excel file (.csv, .xlsx, .xls)" | Reject upload |
| File too large | "File exceeds 10MB limit. Please reduce file size." | Reject upload |
| Missing required columns | "Template requires [Date, Amount]. Please check your data." | Show mapping screen |
| Data type mismatch | "Column 'Revenue' contains non-numeric values. Please review." | Highlight issues |
| AI API failure | "AI insights unavailable. Report generated with standard analysis." | Continue without AI |

---

## 8. Deliverables

### 8.1 MVP Deliverables
- [ ] Working Streamlit application
- [ ] 3 report templates (Sales, Financial, Inventory)
- [ ] PDF export with charts
- [ ] Word export with charts
- [ ] AI insights integration
- [ ] Sample data files for demo
- [ ] README with setup instructions
- [ ] Requirements.txt

### 8.2 Documentation Deliverables
- [ ] User Guide (how to use the tool)
- [ ] Template Customization Guide
- [ ] API Documentation (for AI module)
- [ ] Portfolio Client Pack (PDF)

### 8.3 Demo Assets
- [ ] Screen recording of full workflow
- [ ] Sample generated reports (all 3 templates)
- [ ] Before/after comparison (raw data → report)

---

## 9. Timeline

| Phase | Tasks | Duration | Target Date |
|-------|-------|----------|-------------|
| Setup | Project structure, dependencies, config | 1 day | Day 1 |
| Data Module | Upload, validation, processing | 1 day | Day 2 |
| Charts Module | All chart types, styling | 1 day | Day 3 |
| PDF Generation | ReportLab integration, layouts | 2 days | Day 5 |
| Word Generation | python-docx integration | 1 day | Day 6 |
| Templates | Sales, Financial, Inventory templates | 2 days | Day 8 |
| AI Integration | Claude API, insights generation | 1 day | Day 9 |
| UI Polish | Streamlit styling, UX improvements | 1 day | Day 10 |
| Testing | End-to-end testing, bug fixes | 1 day | Day 11 |
| Documentation | README, guides, portfolio assets | 1 day | Day 12 |
| **Total** | | **12 days** | |

---

## 10. Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| ReportLab complexity | High | Medium | Use WeasyPrint as fallback, simpler HTML→PDF |
| AI API costs | Medium | Low | Implement caching, limit token usage |
| Chart quality in PDF | Medium | Medium | Pre-render as PNG, test extensively |
| Streamlit limitations | Low | Low | Custom CSS, consider Gradio alternative |

---

## 11. Success Criteria

### 11.1 Functional
- [ ] All 3 templates produce complete, error-free reports
- [ ] PDF and Word outputs open correctly in standard viewers
- [ ] Charts are clear, properly labeled, and visually appealing
- [ ] AI insights are relevant and grammatically correct

### 11.2 Portfolio
- [ ] Demo video shows complete workflow in under 3 minutes
- [ ] Sample reports are client-presentation quality
- [ ] Code is clean, documented, and ready for GitHub
- [ ] README clearly explains value proposition

---

## 12. Appendix

### A. Sample Column Mappings

**Sales Template:**
```yaml
required:
  - date: [Date, Transaction_Date, Order_Date, date, DATE]
  - product: [Product, Item, SKU, product_name, Product_Name]
  - quantity: [Quantity, Qty, Units, quantity, QTY]
  - revenue: [Revenue, Amount, Sales, Total, revenue, REVENUE]
optional:
  - region: [Region, Area, Territory, Location, region]
  - category: [Category, Type, Group, category]
```

### B. AI Prompt Template

```
Analyze the following business data summary and provide 3-5 concise, actionable insights:

Data Summary:
- Total Revenue: {total_revenue}
- Number of Transactions: {transaction_count}
- Date Range: {start_date} to {end_date}
- Top Category: {top_category} ({top_category_pct}%)
- Trend: {trend_direction} ({trend_pct}% change)

Provide insights in bullet point format. Focus on:
1. Key performance highlights
2. Concerning trends or anomalies
3. Actionable recommendations

Keep each insight to 1-2 sentences. Use business language appropriate for executive review.
```

### C. Color Palette

```python
COLORS = {
    'primary': '#2563EB',      # Blue
    'secondary': '#10B981',    # Green
    'accent': '#F59E0B',       # Amber
    'danger': '#EF4444',       # Red
    'neutral': '#6B7280',      # Gray
    'background': '#F9FAFB',   # Light gray
    'text': '#111827',         # Dark gray
}

CHART_PALETTE = ['#2563EB', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']
```

---

*Document Version History*

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-20 | Biswajit | Initial draft |
