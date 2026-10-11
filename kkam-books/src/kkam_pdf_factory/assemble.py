from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, A5, LETTER, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

PAGE_SIZES = {
    "A4": A4,
    "A4-landscape": landscape(A4),
    "A5": A5,
    "A5-landscape": landscape(A5),
    "Letter": LETTER,
    "Letter-landscape": landscape(LETTER),
}


def _page_size(trim_size: str):
    try:
        return PAGE_SIZES[trim_size]
    except KeyError as exc:
        raise ValueError(f"Unsupported trim size {trim_size!r}; choose one of {', '.join(PAGE_SIZES)}") from exc


def _paragraph(text: Any, style: ParagraphStyle) -> Paragraph:
    # Escape arbitrary input as plain text; callers cannot inject raw ReportLab markup.
    from xml.sax.saxutils import escape
    return Paragraph(escape(str(text)).replace("\n", "<br/>"), style)


def _page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawCentredString(doc.pagesize[0] / 2, 9 * mm, str(doc.page))
    canvas.restoreState()


def build_business_pdf(spec: dict[str, Any], output_path: str | Path) -> Path:
    """Build a deterministic business workbook/guide PDF from structured content."""
    title = str(spec.get("title", "")).strip()
    if not title:
        raise ValueError("spec.title is required")
    sections = spec.get("sections")
    if not isinstance(sections, list) or not sections:
        raise ValueError("spec.sections must be a non-empty list")
    trim_size = str(spec.get("trim_size", "A4"))
    page_size = _page_size(trim_size)
    margin_mm = float(spec.get("margin_mm", 18))
    if margin_mm < 8 or margin_mm > 35:
        raise ValueError("margin_mm must be between 8 and 35")

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="KKAMTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=25, leading=31, alignment=TA_CENTER, spaceAfter=18))
    styles.add(ParagraphStyle(name="KKAMSubtitle", parent=styles["Normal"], fontName="Helvetica", fontSize=12, leading=17, alignment=TA_CENTER, textColor=colors.HexColor("#555555"), spaceAfter=18))
    styles.add(ParagraphStyle(name="KKAMSection", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=17, leading=21, spaceBefore=8, spaceAfter=10, keepWithNext=True))
    styles.add(ParagraphStyle(name="KKAMBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=10.5, leading=15, spaceAfter=8))
    styles.add(ParagraphStyle(name="KKAMBullet", parent=styles["BodyText"], fontName="Helvetica", fontSize=10, leading=14, leftIndent=14, firstLineIndent=-9, spaceAfter=4))

    story = [
        Spacer(1, 0.18 * page_size[1]),
        _paragraph(title, styles["KKAMTitle"]),
    ]
    if spec.get("subtitle"):
        story.append(_paragraph(spec["subtitle"], styles["KKAMSubtitle"]))
    if spec.get("author"):
        story.extend([Spacer(1, 10 * mm), _paragraph(spec["author"], styles["KKAMSubtitle"])])
    story.append(PageBreak())

    for section_index, section in enumerate(sections):
        if not isinstance(section, dict):
            raise ValueError(f"section {section_index + 1} must be an object")
        block = []
        heading = str(section.get("heading", "")).strip()
        if heading:
            block.append(_paragraph(heading, styles["KKAMSection"]))
        for paragraph in section.get("paragraphs", []):
            block.append(_paragraph(paragraph, styles["KKAMBody"]))
        for bullet in section.get("bullets", []):
            block.append(_paragraph("• " + str(bullet), styles["KKAMBullet"]))
        table_data = section.get("table")
        if table_data:
            if not isinstance(table_data, dict) or not isinstance(table_data.get("headers"), list) or not isinstance(table_data.get("rows"), list):
                raise ValueError(f"section {section_index + 1} table requires headers and rows")
            rows = [table_data["headers"], *table_data["rows"]]
            tbl = Table(rows, repeatRows=1, hAlign="LEFT")
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17243A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("LEADING", (0, 0), (-1, -1), 11),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B9C1CC")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            block.extend([Spacer(1, 4 * mm), tbl, Spacer(1, 5 * mm)])
        if not block:
            continue
        story.append(KeepTogether(block))
        if section.get("page_break_after") and section_index < len(sections) - 1:
            story.append(PageBreak())

    doc = SimpleDocTemplate(
        str(path), pagesize=page_size,
        rightMargin=margin_mm * mm, leftMargin=margin_mm * mm,
        topMargin=margin_mm * mm, bottomMargin=16 * mm,
        title=title, author=str(spec.get("author", "KKAM BOOKS")),
        subject=str(spec.get("subject", "KKAM BOOKS digital publication")),
        keywords=", ".join(spec.get("keywords", [])),
    )
    doc.build(story, onFirstPage=_page_number, onLaterPages=_page_number)
    return path


def build_colouring_book(
    title: str,
    image_paths: Iterable[str | Path],
    output_path: str | Path,
    *,
    cover_path: str | Path | None = None,
    trim_size: str = "A4",
    margin_mm: float = 12,
    age_range: str = "",
) -> Path:
    """Assemble one approved illustration per page, preserving image proportions."""
    if not title.strip():
        raise ValueError("title is required")
    images = [Path(p) for p in image_paths]
    if not images:
        raise ValueError("At least one interior illustration is required")
    missing = [str(p) for p in images if not p.is_file()]
    if cover_path is not None and not Path(cover_path).is_file():
        missing.append(str(cover_path))
    if missing:
        raise FileNotFoundError("Missing image assets: " + ", ".join(missing))
    if margin_mm < 5 or margin_mm > 30:
        raise ValueError("margin_mm must be between 5 and 30")

    from PIL import Image as PILImage
    for asset in images + ([Path(cover_path)] if cover_path is not None else []):
        try:
            with PILImage.open(asset) as image:
                image.verify()
        except Exception as exc:
            raise ValueError(f"Invalid image asset {asset}: {exc}") from exc

    page_size = _page_size(trim_size)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    usable_width = page_size[0] - 2 * margin_mm * mm
    usable_height = page_size[1] - 2 * margin_mm * mm - 8 * mm
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name="KKAMColouringTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=25, leading=31, alignment=TA_CENTER)
    subtitle_style = ParagraphStyle(name="KKAMColouringSubtitle", parent=styles["Normal"], fontName="Helvetica", fontSize=12, leading=16, alignment=TA_CENTER)

    story = [Spacer(1, page_size[1] * 0.25)]
    story.append(_paragraph(title, title_style))
    if age_range:
        story.extend([Spacer(1, 8 * mm), _paragraph(f"Ages {age_range}", subtitle_style)])
    story.append(PageBreak())

    if cover_path is not None:
        cover = Image(str(cover_path), width=usable_width, height=usable_height, kind="proportional")
        story.extend([cover, PageBreak()])

    for index, asset in enumerate(images):
        if index:
            story.append(PageBreak())
        story.append(Image(str(asset), width=usable_width, height=usable_height, kind="proportional", hAlign="CENTER"))

    doc = SimpleDocTemplate(
        str(path), pagesize=page_size,
        rightMargin=margin_mm * mm, leftMargin=margin_mm * mm,
        topMargin=margin_mm * mm, bottomMargin=margin_mm * mm,
        title=title, author="KKAM BOOKS",
        subject="Original colouring and activity book",
    )
    doc.build(story, onFirstPage=_page_number, onLaterPages=_page_number)
    return path


def build_from_spec(spec_path: str | Path, output_path: str | Path) -> Path:
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    if not isinstance(spec, dict):
        raise ValueError("Product spec must be a JSON object")
    return build_business_pdf(spec, output_path)
