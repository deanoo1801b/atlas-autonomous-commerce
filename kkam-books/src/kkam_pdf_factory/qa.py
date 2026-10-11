from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def inspect_pdf(
    pdf_path: str | Path,
    *,
    expected_pages: int | None = None,
    expected_trim: str | None = None,
    render_dir: str | Path | None = None,
    render_pages: bool = False,
) -> dict[str, Any]:
    """Inspect PDF structure and optionally render every page to PNG.

    Requires pypdf for technical inspection. Rendering requires PyMuPDF.
    This function never marks visual QA as passed based on file existence alone.
    """
    path = Path(pdf_path)
    report: dict[str, Any] = {
        "path": str(path),
        "exists": path.is_file(),
        "technical_status": "failed",
        "visual_status": "not-run",
        "errors": [],
        "warnings": [],
        "page_count": None,
        "page_sizes_points": [],
        "metadata": {},
        "rendered_pages": [],
    }
    if not path.is_file():
        report["errors"].append("PDF file does not exist.")
        return report
    if path.stat().st_size < 8:
        report["errors"].append("File is too small to be a valid PDF.")
        return report
    with path.open("rb") as handle:
        signature = handle.read(5)
    if signature != b"%PDF-":
        report["errors"].append("File signature is not %PDF-.")
        return report

    try:
        from pypdf import PdfReader
    except ImportError:
        report["errors"].append("pypdf is not installed; install kkam-books/requirements-optional.txt.")
        return report

    try:
        reader = PdfReader(str(path), strict=True)
        if reader.is_encrypted:
            report["errors"].append("Encrypted PDF requires an explicit password policy.")
            return report
        pages = list(reader.pages)
        report["page_count"] = len(pages)
        if not pages:
            report["errors"].append("PDF has no pages.")
        if expected_pages is not None and len(pages) != expected_pages:
            report["errors"].append(f"Expected {expected_pages} pages but found {len(pages)}.")
        for index, page in enumerate(pages, start=1):
            box = page.mediabox
            width, height = float(box.width), float(box.height)
            report["page_sizes_points"].append({"page": index, "width": round(width, 2), "height": round(height, 2)})
            if width <= 0 or height <= 0:
                report["errors"].append(f"Page {index} has invalid dimensions.")
            if expected_trim and expected_trim.upper() == "A4":
                if abs(width - 595.28) > 3 or abs(height - 841.89) > 3:
                    if abs(width - 841.89) <= 3 and abs(height - 595.28) <= 3:
                        continue
                    report["errors"].append(f"Page {index} is not A4 portrait or landscape.")
        meta = reader.metadata
        if meta:
            report["metadata"] = {
                "title": meta.title,
                "author": meta.author,
                "subject": meta.subject,
                "creator": meta.creator,
                "producer": meta.producer,
            }
        if not meta or not meta.title:
            report["warnings"].append("PDF title metadata is missing.")

        if render_pages:
            if render_dir is None:
                report["errors"].append("render_dir is required when render_pages=True.")
            else:
                try:
                    import fitz
                except ImportError:
                    report["errors"].append("PyMuPDF is not installed; rendering was not performed.")
                else:
                    output = Path(render_dir)
                    output.mkdir(parents=True, exist_ok=True)
                    doc = fitz.open(str(path))
                    for index, page in enumerate(doc, start=1):
                        image_path = output / f"page-{index:04d}.png"
                        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
                        pix.save(str(image_path))
                        report["rendered_pages"].append(str(image_path))
                    doc.close()
                    report["visual_status"] = "rendered-needs-review"
                    report["warnings"].append("Pages were rendered; human or vision-based visual review is still required.")
        report["technical_status"] = "passed" if not report["errors"] else "failed"
        return report
    except Exception as exc:
        report["errors"].append(f"PDF parser failure: {type(exc).__name__}: {exc}")
        return report


def write_report(report: dict[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
