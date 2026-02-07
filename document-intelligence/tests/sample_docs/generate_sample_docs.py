"""Generate realistic sample PDFs for demo/testing."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

OUTPUT_DIR = Path(__file__).resolve().parent


def build_invoice(path: Path) -> None:
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        "InvoiceTitle", parent=styles["Heading1"], fontSize=22, textColor=colors.HexColor("#0f172a")
    )

    story.append(Paragraph("ACME CONSULTING LLC", title_style))
    story.append(Paragraph("123 Market Street, San Francisco, CA 94105", styles["Normal"]))
    story.append(Spacer(1, 12))

    meta_table = Table(
        [
            ["Invoice Number", "INV-2026-0147"],
            ["Invoice Date", "January 20, 2026"],
            ["Due Date", "February 19, 2026"],
            ["Bill To", "NorthStar Retail Corporation"],
        ],
        colWidths=[5 * cm, 9 * cm],
    )
    meta_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(meta_table)
    story.append(Spacer(1, 16))

    line_items = Table(
        [
            ["Description", "Qty", "Unit Price", "Total"],
            ["Document AI workflow design", "12", "$150.00", "$1,800.00"],
            ["OCR pipeline implementation", "20", "$165.00", "$3,300.00"],
            ["QA and export module", "14", "$140.00", "$1,960.00"],
            ["Subtotal", "", "", "$7,060.00"],
            ["Tax (8.25%)", "", "", "$582.45"],
            ["Amount Due", "", "", "$7,642.45"],
        ],
        colWidths=[8.5 * cm, 2.0 * cm, 3.0 * cm, 3.0 * cm],
    )

    line_items.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e2e8f0")),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(line_items)
    story.append(Spacer(1, 14))
    story.append(Paragraph("Payment Terms: Net 30 days. Contact billing@acmeconsulting.com for inquiries.", styles["Normal"]))

    doc.build(story)


def build_contract(path: Path) -> None:
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("SERVICE AGREEMENT", styles["Title"]))
    story.append(Spacer(1, 10))

    intro = (
        "This Service Agreement (\"Agreement\") is entered into on January 15, 2026 between "
        "BlueWave Analytics Inc. (\"Provider\") and Meridian Logistics LLC (\"Client\")."
    )
    story.append(Paragraph(intro, styles["BodyText"]))
    story.append(Spacer(1, 12))

    clauses = [
        ("1. Services", "Provider will deliver document intelligence implementation and support services."),
        ("2. Term", "The term of this Agreement begins on February 1, 2026 and ends on July 31, 2026."),
        ("3. Fees", "Client shall pay a fixed fee of $24,000 in four monthly installments of $6,000."),
        ("4. Confidentiality", "Each party agrees to protect confidential information with reasonable care."),
        ("5. Termination", "Either party may terminate with 30 days written notice for material breach."),
        ("6. Governing Law", "This Agreement shall be governed by the laws of the State of California."),
    ]

    for title, body in clauses:
        story.append(Paragraph(f"<b>{title}</b>", styles["Heading4"]))
        story.append(Paragraph(body, styles["BodyText"]))
        story.append(Spacer(1, 8))

    story.append(Spacer(1, 12))
    signatures = Table(
        [
            ["Provider Signatory", "Client Signatory"],
            ["Anita Rao", "Michael Turner"],
            ["Chief Delivery Officer", "VP Operations"],
            [f"Date: {date(2026, 1, 15).isoformat()}", f"Date: {date(2026, 1, 15).isoformat()}"] ,
        ],
        colWidths=[7.5 * cm, 7.5 * cm],
    )

    signatures.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(signatures)

    doc.build(story)


def build_report(path: Path) -> None:
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Quarterly Operations Report - Q4 2025", styles["Title"]))
    story.append(Paragraph("Prepared for: Apex Manufacturing Company", styles["BodyText"]))
    story.append(Paragraph("Prepared by: InsightBridge Research Group", styles["BodyText"]))
    story.append(Spacer(1, 14))

    sections = [
        (
            "Executive Summary",
            "Q4 performance improved across production throughput, order fulfillment, and gross margin. "
            "Automation initiatives reduced manual processing time by 31% and improved SLA compliance to 97.4%.",
        ),
        (
            "Financial Highlights",
            "Revenue reached $4.82M, representing 12.6% quarter-over-quarter growth. Operating costs were $3.17M, "
            "while net operating profit closed at $1.65M.",
        ),
        (
            "Risk and Compliance",
            "Three moderate compliance findings were identified during the internal audit cycle. "
            "Corrective action plans are in progress with target closure by March 31, 2026.",
        ),
    ]

    for title, body in sections:
        story.append(Paragraph(title, styles["Heading3"]))
        story.append(Paragraph(body, styles["BodyText"]))
        story.append(Spacer(1, 10))

    kpi_table = Table(
        [
            ["Metric", "Q3 2025", "Q4 2025", "Change"],
            ["On-time Delivery", "91.2%", "97.4%", "+6.2 pp"],
            ["Production Throughput", "42,100 units", "50,900 units", "+20.9%"],
            ["Defect Rate", "2.8%", "1.9%", "-0.9 pp"],
            ["Customer Escalations", "34", "19", "-44.1%"],
        ],
        colWidths=[6.0 * cm, 3.0 * cm, 3.0 * cm, 3.0 * cm],
    )
    kpi_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(kpi_table)
    story.append(Spacer(1, 12))
    story.append(
        Paragraph(
            "Contact: reports@insightbridge.com | Phone: +1 415-555-0199",
            styles["BodyText"],
        )
    )

    doc.build(story)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    build_invoice(OUTPUT_DIR / "invoice_sample.pdf")
    build_contract(OUTPUT_DIR / "contract_sample.pdf")
    build_report(OUTPUT_DIR / "report_sample.pdf")


if __name__ == "__main__":
    main()
