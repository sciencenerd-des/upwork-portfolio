# Automated Report Generator

Transform raw CSV/Excel data into professionally formatted PDF and Word reports with AI-powered insights.

## Features

- **Multiple Report Templates**: Sales, Financial, and Inventory reports
- **Smart Column Mapping**: Auto-detects and maps data columns to template fields
- **Professional Charts**: Line trends, bar charts, and pie charts with consistent styling
- **AI-Generated Insights**: Claude AI analyzes your data and provides actionable insights
- **Multiple Export Formats**: Generate PDF and/or Word documents
- **User-Friendly Interface**: Step-by-step wizard with progress indicators

## Quick Start

### Prerequisites

- Python 3.9+
- pip (Python package manager)

### Installation

1. Clone the repository and navigate to the project directory:

```bash
cd automated-report-generator
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. (Optional) Set up OpenRouter API for AI insights:

```bash
export OPENROUTER_API_KEY=your_api_key_here
```

Get your API key from [OpenRouter](https://openrouter.ai/).

### Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

## Usage

### Step 1: Upload Data

Upload one or more CSV/Excel files. The application supports:
- CSV files (.csv)
- Excel files (.xlsx, .xls)
- **Multiple files** - automatically combined into a single dataset
- Files up to 10MB each, 500,000 total rows

### Step 2: Configure Report

1. **Select Template**: Choose from Sales, Financial, or Inventory templates
2. **Map Columns**: The system auto-maps columns; adjust if needed
3. **Generation Options**: Toggle AI insights and select output formats

### Step 3: Generate Report

Click "Generate Report" and wait for the progress bar to complete.

### Step 4: Download

Download your reports in PDF and/or Word format. Preview PDFs directly in the browser.

## Report Templates

### Sales Report

Required columns: Date, Product, Revenue

Includes:
- Executive Summary (Total Revenue, Units Sold, Avg Order Value)
- Revenue Trend Chart
- Product Performance Chart
- Regional Breakdown (if region data available)
- Top Transactions Table
- AI Insights

### Financial Report

Required columns: Date, Category, Amount, Transaction Type (Income/Expense)

Includes:
- Financial Overview (Income, Expenses, Net Profit, Margin)
- Monthly Income vs Expenses Trend
- Expense Breakdown Pie Chart
- Income Sources Bar Chart
- Month-over-Month Comparison Table
- AI Insights

### Inventory Report

Required columns: Product, Quantity, Reorder Level, Unit Cost

Includes:
- Inventory Summary (Total SKUs, Units, Value, Items Below Reorder)
- Stock Status by Category
- Reorder Alerts Table
- Value Distribution Chart
- Top Items by Value Table
- AI Insights

## Sample Data

Try the application with included sample data files:

- `sample_data/sales_sample.csv` - 75 sales transactions
- `sample_data/financial_sample.csv` - 75 financial records
- `sample_data/inventory_sample.csv` - 60 inventory items

## Project Structure

```
automated-report-generator/
├── app.py                    # Streamlit web application
├── requirements.txt          # Python dependencies
├── config/
│   ├── templates.yaml        # Template definitions
│   └── styles.yaml           # Chart and report styles
├── src/
│   ├── __init__.py
│   ├── data_processor.py     # Data loading and validation
│   ├── chart_generator.py    # Chart creation
│   ├── report_builder.py     # PDF and Word generation
│   ├── ai_insights.py        # Claude AI integration
│   └── utils.py              # Helper functions
├── templates/
│   ├── __init__.py           # Template registry
│   ├── sales_report.py       # Sales report template
│   ├── financial_report.py   # Financial report template
│   └── inventory_report.py   # Inventory report template
├── sample_data/
│   ├── sales_sample.csv
│   ├── financial_sample.csv
│   └── inventory_sample.csv
└── tests/
    ├── test_data_processor.py
    ├── test_chart_generator.py
    ├── test_ai_insights.py
    ├── test_report_builder.py
    └── test_e2e.py
```

## Running Tests

Run all tests:

```bash
python -m pytest tests/ -v
```

Run specific test module:

```bash
python -m pytest tests/test_e2e.py -v
```

## Configuration

### Templates (config/templates.yaml)

Define report templates with required/optional columns, aliases for auto-mapping, and section specifications.

### Styles (config/styles.yaml)

Customize colors, fonts, and styling for charts, PDFs, and Word documents.

## Performance

- Report generation: < 30 seconds for files up to 10,000 rows
- File upload: < 5 seconds for 10MB files
- Supports files up to 500,000 rows

## Technologies Used

- **Streamlit** - Web interface
- **Pandas** - Data processing
- **Matplotlib/Seaborn** - Chart generation
- **ReportLab** - PDF generation
- **python-docx** - Word document generation
- **OpenRouter API** - AI insights (optional)

## License

MIT License

## Author

Biswajit Mondal

---

Built for Upwork Portfolio - Demonstrating Python automation, data processing, and AI integration capabilities.
