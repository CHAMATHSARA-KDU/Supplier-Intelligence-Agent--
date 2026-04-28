"""
PDF Report Generator
Automatically generates a professional supplier intelligence report as PDF.
Uses reportlab — no external dependencies beyond pip install reportlab.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# ── Color palette ─────────────────────────────────────────────
DARK_BLUE  = colors.HexColor("#1a2744")
RED        = colors.HexColor("#e74c3c")
ORANGE     = colors.HexColor("#f39c12")
GREEN      = colors.HexColor("#27ae60")
DARK_RED   = colors.HexColor("#8e1010")
LIGHT_GRAY = colors.HexColor("#f5f5f5")
MID_GRAY   = colors.HexColor("#cccccc")

RISK_COLORS = {
    "LOW RISK":      GREEN,
    "MODERATE RISK": ORANGE,
    "HIGH RISK":     RED,
    "CRITICAL RISK": DARK_RED,
}

REPORTS_FOLDER = "reports"


def _get_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        fontSize=22,
        fontName="Helvetica-Bold",
        textColor=colors.white,
        alignment=TA_CENTER,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="ReportSubtitle",
        fontSize=11,
        fontName="Helvetica",
        textColor=colors.HexColor("#d0d8e8"),
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontSize=13,
        fontName="Helvetica-Bold",
        textColor=DARK_BLUE,
        spaceBefore=14,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="BodyText2",
        fontSize=10,
        fontName="Helvetica",
        textColor=colors.HexColor("#333333"),
        spaceAfter=6,
        leading=14,
    ))
    styles.add(ParagraphStyle(
        name="SmallText",
        fontSize=8,
        fontName="Helvetica",
        textColor=colors.HexColor("#888888"),
        alignment=TA_CENTER,
    ))
    return styles


def generate_pdf_report(
    supplier_name: str,
    score: float,
    risk_level: str,
    summary: str,
    output_path: str = None,
) -> str:
    """
    Generates a professional PDF supplier intelligence report.

    Args:
        supplier_name: Name of the supplier
        score: Risk score 0-10
        risk_level: e.g. HIGH RISK
        summary: Full agent report text
        output_path: Optional custom path. Defaults to reports/supplier_name_date.pdf

    Returns:
        Path to the generated PDF file
    """
    # Create reports folder
    os.makedirs(REPORTS_FOLDER, exist_ok=True)

    if output_path is None:
        safe_name = "".join(c if c.isalnum() or c in (' ', '-') else '_' for c in supplier_name)
        safe_name = safe_name.replace(' ', '_')[:40]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(REPORTS_FOLDER, f"{safe_name}_{timestamp}.pdf")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    styles = _get_styles()
    story = []
    risk_color = RISK_COLORS.get(risk_level, RED)

    # ── Header banner ─────────────────────────────────────────
    header_data = [[
        Paragraph("SUPPLIER INTELLIGENCE REPORT", styles["ReportTitle"]),
    ]]
    header_table = Table(header_data, colWidths=[17*cm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), DARK_BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.4*cm))

    # ── Subtitle ──────────────────────────────────────────────
    story.append(Paragraph(
        f"Generated autonomously on {datetime.now().strftime('%B %d, %Y at %H:%M')}",
        styles["SmallText"]
    ))
    story.append(Spacer(1, 0.5*cm))

    # ── Supplier name ─────────────────────────────────────────
    story.append(Paragraph("Supplier Name", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", thickness=1, color=MID_GRAY))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(supplier_name, ParagraphStyle(
        name="SupplierName",
        fontSize=16,
        fontName="Helvetica-Bold",
        textColor=DARK_BLUE,
    )))
    story.append(Spacer(1, 0.5*cm))

    # ── Score card ────────────────────────────────────────────
    story.append(Paragraph("Risk Assessment", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", thickness=1, color=MID_GRAY))
    story.append(Spacer(1, 0.2*cm))

    score_data = [
        ["Overall Risk Score", "Trust Level", "Assessment Date"],
        [
            f"{score} / 10",
            risk_level,
            datetime.now().strftime("%Y-%m-%d"),
        ]
    ]
    score_table = Table(score_data, colWidths=[5.5*cm, 6.5*cm, 5*cm])
    score_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), DARK_BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 10),
        ("BACKGROUND",    (0, 1), (-1, 1), LIGHT_GRAY),
        ("FONTNAME",      (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 1), (0, 1),  16),
        ("TEXTCOLOR",     (0, 1), (0, 1),  risk_color),
        ("TEXTCOLOR",     (1, 1), (1, 1),  risk_color),
        ("FONTSIZE",      (1, 1), (1, 1),  12),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("GRID",          (0, 0), (-1, -1), 0.5, MID_GRAY),
        ("ROUNDEDCORNERS", [4]),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Recommendation box ────────────────────────────────────
    recommendations = {
        "LOW RISK":      "Safe to proceed with full contract. Continue standard monitoring.",
        "MODERATE RISK": "Request a trial order before full commitment. Verify claims directly.",
        "HIGH RISK":     "Seek alternative suppliers. Activate contingency plan immediately.",
        "CRITICAL RISK": "Do NOT proceed. Escalate to procurement leadership immediately.",
    }
    recommendation = recommendations.get(risk_level, "Seek additional verification.")

    rec_data = [[
        Paragraph(f"Recommendation: {recommendation}", ParagraphStyle(
            name="Rec",
            fontSize=10,
            fontName="Helvetica-Bold",
            textColor=colors.white,
        ))
    ]]
    rec_table = Table(rec_data, colWidths=[17*cm])
    rec_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), risk_color),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS", [4]),
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Findings summary ──────────────────────────────────────
    story.append(Paragraph("Intelligence Findings", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", thickness=1, color=MID_GRAY))
    story.append(Spacer(1, 0.2*cm))

    # Clean and split summary into paragraphs
    clean_summary = summary.replace("##", "").replace("**", "").strip()
    paragraphs = [p.strip() for p in clean_summary.split("\n") if p.strip()]

    for para in paragraphs[:20]:  # max 20 lines
        if para.startswith("#"):
            story.append(Paragraph(para.replace("#", "").strip(), styles["SectionHeader"]))
        elif para.startswith("-") or para.startswith("•"):
            story.append(Paragraph(f"• {para.lstrip('-•').strip()}", styles["BodyText2"]))
        else:
            story.append(Paragraph(para, styles["BodyText2"]))

    story.append(Spacer(1, 0.8*cm))

    # ── Footer ────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "This report was generated autonomously by the Supplier Intelligence Agent. "
        "No human intervention was required. For procurement decisions, consult your team.",
        styles["SmallText"]
    ))

    doc.build(story)
    print(f"[PDF] Report saved: {output_path}")
    return output_path
