"""PDF report generation service."""

from __future__ import annotations

from io import BytesIO
from typing import Any

from quadra_diag.core.config import get_settings
from quadra_diag.core.logging import get_logger

logger = get_logger(__name__)

_reportlab_available_cache = None


def _reportlab_available() -> bool:
    global _reportlab_available_cache
    if _reportlab_available_cache is None:
        try:
            import reportlab  # type: ignore # noqa: F401
            _reportlab_available_cache = True
        except Exception:
            _reportlab_available_cache = False
    return _reportlab_available_cache


def generate_assessment_pdf(result: dict, spec: dict) -> bytes | None:
    """Generate a professional PDF report for an assessment."""
    settings = get_settings()
    if not settings.enable_pdf_export or not _reportlab_available():
        return None

    try:
        from reportlab.lib import colors  # type: ignore
        from reportlab.lib.pagesizes import letter  # type: ignore
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # type: ignore
        from reportlab.lib.units import inch  # type: ignore
        from reportlab.platypus import (  # type: ignore
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
        )

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "CustomTitle", parent=styles["Heading1"], fontSize=24,
            textColor=colors.HexColor("#0d6b52"), spaceAfter=30,
        )
        heading_style = ParagraphStyle(
            "CustomHeading", parent=styles["Heading2"], fontSize=14,
            textColor=colors.HexColor("#0f1f1c"), spaceAfter=12,
        )
        normal_style = styles["Normal"]
        normal_style.fontSize = 10
        normal_style.leading = 14

        story = []
        story.append(Paragraph("QuadraDiag Clinical Report", title_style))
        story.append(Paragraph(f"<b>{spec['title']}</b>", heading_style))
        story.append(Spacer(1, 0.2 * inch))

        risk_data = [
            ["Risk Band", result["risk_band"].upper()],
            ["Probability", f"{result['probability'] * 100:.1f}%"],
            ["Threshold", f"{result['threshold'] * 100:.0f}%"],
            ["Model ROC-AUC", str(result["metrics"]["roc_auc"])],
        ]
        risk_table = Table(risk_data, colWidths=[2.5 * inch, 2.5 * inch])
        risk_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0ebe1")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f1f1c")),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#e0ddd6")),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white]),
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 0.3 * inch))

        story.append(Paragraph("<b>Submitted Values</b>", heading_style))
        feature_data = [["Feature", "Value"]]
        for key, value in result["features"].items():
            feature_data.append([key, str(value)])

        feature_table = Table(feature_data, colWidths=[2.5 * inch, 2.5 * inch])
        feature_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6b52")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#e0ddd6")),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#faf8f3")]),
        ]))
        story.append(feature_table)
        story.append(Spacer(1, 0.3 * inch))

        if result.get("benchmarks"):
            story.append(Paragraph("<b>Benchmark Notes</b>", heading_style))
            for note in result["benchmarks"]:
                story.append(Paragraph(f"• {note}", normal_style))
            story.append(Spacer(1, 0.2 * inch))

        if result.get("shap_explanation"):
            story.append(Paragraph("<b>Feature Contributions (SHAP)</b>", heading_style))
            shap = result["shap_explanation"]
            story.append(Paragraph(f"Base value: {shap['base_value']}", normal_style))
            story.append(Paragraph(f"Prediction: {shap['prediction']}", normal_style))
            story.append(Spacer(1, 0.1 * inch))

            contrib_data = [["Feature", "Contribution"]]
            for feat, val in list(shap["feature_contributions"].items())[:8]:
                color = colors.HexColor("#1a7a58") if val > 0 else colors.HexColor("#8c2e24")
                contrib_data.append([feat, Paragraph(f'<font color="{color.hexval()}">{val:+.4f}</font>', normal_style)])

            contrib_table = Table(contrib_data, colWidths=[2.5 * inch, 2.5 * inch])
            contrib_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0ebe1")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f1f1c")),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#e0ddd6")),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#faf8f3")]),
            ]))
            story.append(contrib_table)

        story.append(Spacer(1, 0.4 * inch))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0ddd6")))
        story.append(Spacer(1, 0.1 * inch))
        disclaimer = Paragraph(
            "<i>This report is for educational and screening purposes only. Not a medical diagnosis.</i>",
            ParagraphStyle("Disclaimer", parent=normal_style, textColor=colors.HexColor("#566b64"), fontSize=9),
        )
        story.append(disclaimer)

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
    except Exception as exc:
        logger.error("PDF generation failed: %s", exc)
        return None

