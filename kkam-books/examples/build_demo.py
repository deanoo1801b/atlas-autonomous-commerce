from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

from kkam_pdf_factory.assemble import build_business_pdf, build_colouring_book
from kkam_pdf_factory.package_manifest import create_package_manifest
from kkam_pdf_factory.qa import (
    analyse_colouring_pages, create_contact_sheet, inspect_pdf, write_report,
)


def make_demo_art(path: Path, subject: str) -> None:
    image = Image.new("RGB", (1800, 2400), "white")
    draw = ImageDraw.Draw(image)
    draw.ellipse((360, 300, 1440, 1380), outline="black", width=12)
    draw.ellipse((620, 650, 760, 790), outline="black", width=10)
    draw.ellipse((1040, 650, 1180, 790), outline="black", width=10)
    draw.arc((650, 720, 1150, 1150), start=10, end=170, fill="black", width=12)
    draw.line((900, 1380, 900, 1760), fill="black", width=12)
    draw.line((900, 1520, 650, 1660), fill="black", width=12)
    draw.line((900, 1520, 1150, 1660), fill="black", width=12)
    draw.line((900, 1760, 700, 2020), fill="black", width=12)
    draw.line((900, 1760, 1100, 2020), fill="black", width=12)
    image.save(path, format="PNG", dpi=(300, 300))


def main() -> int:
    out = Path("kkam-books/demo-output")
    art_dir = out / "artwork"
    render_dir = out / "renders"
    qa_dir = out / "qa"
    for folder in (out, art_dir, render_dir, qa_dir):
        folder.mkdir(parents=True, exist_ok=True)

    art_paths = []
    for i, subject in enumerate(("animal-a", "animal-b", "animal-c"), start=1):
        path = art_dir / f"page-{i:03d}-{subject}.png"
        make_demo_art(path, subject)
        art_paths.append(path)

    business_pdf = out / "01-KKAM-Demo-Business-Workbook.pdf"
    build_business_pdf({
        "title": "Small Business Finance Workbook",
        "subtitle": "KKAM BOOKS PDF Factory — sample output",
        "author": "KKAM BOOKS",
        "subject": "Demonstration PDF; not a commercial release",
        "keywords": ["small business", "finance", "workbook"],
        "trim_size": "A4",
        "sections": [
            {"heading": "1. Monthly Money Snapshot", "paragraphs": [
                "Use this page to record your opening balance, money received, money paid and closing balance.",
                "This sample is illustrative and contains no financial advice."
            ], "bullets": ["Record every transaction", "Keep source evidence", "Reconcile totals monthly"]},
            {"heading": "2. Simple Cash Summary", "paragraphs": ["Example figures are for layout testing only."],
             "table": {"headers": ["Category", "Example amount"], "rows": [["Income", "£1,000"], ["Costs", "£350"], ["Balance before tax", "£650"]]}},
        ],
    }, business_pdf)

    colouring_pdf = out / "02-KKAM-Demo-Animal-Colouring.pdf"
    build_colouring_book(
        "Friendly Animal Shapes",
        art_paths,
        colouring_pdf,
        trim_size="A4",
        age_range="3–6",
    )

    business_report = inspect_pdf(business_pdf, expected_trim="A4")
    colouring_report = inspect_pdf(
        colouring_pdf, expected_pages=4, expected_trim="A4",
        render_dir=render_dir, render_pages=True,
    )
    write_report(business_report, qa_dir / "business-technical-qa.json")
    write_report(colouring_report, qa_dir / "colouring-technical-qa.json")
    visual = analyse_colouring_pages(colouring_report["rendered_pages"])
    (qa_dir / "colouring-pixel-review.json").write_text(json.dumps(visual, indent=2), encoding="utf-8")
    contact_sheet = create_contact_sheet(
        [Path(p) for p in colouring_report["rendered_pages"]],
        qa_dir / "colouring-contact-sheet.png",
        columns=2,
    )
    files = [business_pdf, colouring_pdf, *art_paths,
             qa_dir / "business-technical-qa.json",
             qa_dir / "colouring-technical-qa.json",
             qa_dir / "colouring-pixel-review.json", contact_sheet]
    manifest = create_package_manifest("KKAM-DEMO-0001", "0.1.0", files, out / "manifest.json")
    summary = {
        "status": "demo-built",
        "commercial_release": False,
        "business_pdf": str(business_pdf),
        "colouring_pdf": str(colouring_pdf),
        "business_technical_status": business_report["technical_status"],
        "colouring_technical_status": colouring_report["technical_status"],
        "colouring_visual_status": colouring_report["visual_status"],
        "colouring_pixel_review_status": visual["overall_status"],
        "manifest_file_count": manifest["file_count"],
        "note": "Synthetic sample artwork and content for pipeline testing only; not approved for sale.",
    }
    (out / "demo-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if business_report["technical_status"] == "passed" and colouring_report["technical_status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
