# Automated Report Generator – Review & Critique

## Overview
The project cleanly separates responsibilities across `src/` modules and template classes, and the Streamlit UI in `app.py` guides users through upload → configuration → generation → download. Configuration-driven templates (`config/templates.yaml:1`) and styling (`config/styles.yaml:1`) make it easy to extend report types without touching the UI logic. Automated coverage is impressive (`pytest -q` runs 113 assertions in ~15s), giving confidence in the data-processing, charting, report-building, and template orchestration layers.

## Strengths
- Template orchestration clearly composes `DataProcessor`, `ChartGenerator`, `ReportBuilder`, and `AIInsights`, so each concern stays testable (`templates/sales_report.py:28`).
- Config files capture template metadata, chart palettes, and style tokens, which keeps presentation choices consistent and centralized (`config/templates.yaml:1`, `config/styles.yaml:1`).
- Tests span unit, integration, and end-to-end layers and all pass locally (`source venv/bin/activate && pytest -q`).
- The Streamlit wizard is thoughtfully staged with validation, preview tables, column mapping selectors, and download previews (`app.py:275`, `app.py:563`).

## Key Findings & Critique
1. **Temporary uploads are never cleaned up** – Every uploaded file is written to a `NamedTemporaryFile` with `delete=False`, loaded into pandas, and then simply left on disk (`app.py:295`). Nothing deletes those paths after `load_file/load_multiple_files` return, so repeated uploads will leak sensitive data and fill `/tmp`. Either delete the files after calling the processor or load straight from the in-memory `UploadedFile` buffer to avoid touching disk altogether.
2. **Excel multi-sheet selection still missing** – Requirement F1.6 (ARG-PRD.md:81) specifies that users must choose which sheet to ingest. There is a helper to enumerate sheet names (`src/data_processor.py:224`), but it’s never used anywhere else in the codebase (no references outside the definition). The UI always loads the default sheet in `load_file`, so workbooks with multiple sheets can’t be targeted without editing the file manually.
3. **Missing-value handling is not wired into the workflow** – Handling nulls gracefully is a P0 requirement (ARG-PRD.md:81). While `DataProcessor.fill_missing_values` exists (`src/data_processor.py:591`), nothing in the app or templates ever invokes it (confirmed by `rg`, it’s only exercised in tests). Users therefore have to pre-clean their data externally, and the app gives no guidance or option to impute/drop rows.
4. **AI failures are completely silent** – If the OpenRouter call errors, `AIInsights.generate_insights` catches the exception and simply falls back to deterministic bullet points without logging or surfacing the failure to the UI (`src/ai_insights.py:91`). Streamlit still shows “Generating AI insights…” (`app.py:548`), so users believe AI succeeded when it didn’t. At minimum, log the exception and bubble a warning so users know insights came from the fallback logic.

## Testing Summary
- `source venv/bin/activate && pytest -q`
  - Result: **113 passed**, 14 DeprecationWarnings from matplotlib font parsing. No regressions observed.

## Recommendations / Next Steps
1. Delete temporary upload files as soon as they are loaded, or switch to `UploadedFile` buffers directly to eliminate residual artifacts.
2. Wire up `get_excel_sheets` so users can pick the sheet prior to loading; store the selection in session state for repeatability.
3. Expose a missing-value strategy toggle (drop/zero/mean/forward) in Step 2 and call `fill_missing_values` before `process_data` so reports don’t silently drop metrics.
4. Add structured logging and user-facing warnings when AI calls fail, and include at least one integration test that mocks the OpenRouter client to assert the happy path is exercised.
