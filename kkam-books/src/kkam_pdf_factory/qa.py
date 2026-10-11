from __future__ import annotations

import json
import hashlib
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
        "blank_rendered_pages": [],
        "duplicate_rendered_pages": [],
        "fonts": [],
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

        try:
            import fitz
            font_doc = fitz.open(str(path))
            seen_fonts = set()
            for page_index, page in enumerate(font_doc, start=1):
                for font in page.get_fonts(full=True):
                    xref = int(font[0])
                    basefont = str(font[3])
                    key = (xref, basefont)
                    if key in seen_fonts:
                        continue
                    seen_fonts.add(key)
                    embedded = False
                    if xref > 0:
                        try:
                            embedded = bool(font_doc.extract_font(xref)[3])
                        except Exception:
                            embedded = False
                    report["fonts"].append({"page": page_index, "name": basefont, "xref": xref, "embedded": embedded})
                    if not embedded:
                        report["warnings"].append(f"Font {basefont} could not be confirmed as embedded; review before print production.")
            font_doc.close()
        except ImportError:
            report["warnings"].append("PyMuPDF not installed; embedded-font inspection skipped.")
        except Exception as exc:
            report["warnings"].append(f"Font inspection could not complete: {type(exc).__name__}: {exc}")

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
                    rendered_hashes: dict[str, int] = {}
                    for index, page in enumerate(doc, start=1):
                        image_path = output / f"page-{index:04d}.png"
                        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
                        pix.save(str(image_path))
                        report["rendered_pages"].append(str(image_path))
                        digest = hashlib.sha256(pix.samples).hexdigest()
                        if digest in rendered_hashes:
                            report["duplicate_rendered_pages"].append({"page": index, "matches_page": rendered_hashes[digest]})
                        else:
                            rendered_hashes[digest] = index
                        if pix.samples and all(value >= 250 for value in pix.samples):
                            report["blank_rendered_pages"].append(index)
                    doc.close()
                    if report["duplicate_rendered_pages"]:
                        report["warnings"].append("Exact duplicate rendered pages detected; review before approval.")
                    if report["blank_rendered_pages"]:
                        report["warnings"].append("Blank or near-blank rendered pages detected; review before approval.")
                    report["visual_status"] = "rendered-needs-review"
                    report["warnings"].append("Pages were rendered; clipping, spelling, illustration quality and colouring-area suitability still require visual review.")
        report["technical_status"] = "passed" if not report["errors"] else "failed"
        return report
    except Exception as exc:
        report["errors"].append(f"PDF parser failure: {type(exc).__name__}: {exc}")
        return report


def write_report(report: dict[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")



def create_contact_sheet(
    rendered_pages: list[str | Path],
    output_path: str | Path,
    *,
    columns: int = 4,
    thumbnail_width: int = 240,
) -> Path:
    """Create a human-review contact sheet from rendered PDF pages."""
    if not rendered_pages:
        raise ValueError("rendered_pages must not be empty")
    if columns < 1 or thumbnail_width < 80:
        raise ValueError("columns must be >= 1 and thumbnail_width >= 80")
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise RuntimeError("Pillow is required to create a contact sheet.") from exc

    thumbs = []
    for item in rendered_pages:
        path = Path(item)
        if not path.is_file():
            raise FileNotFoundError(f"Missing rendered page: {path}")
        with Image.open(path) as source:
            thumb = source.convert("RGB")
            height = max(1, round(thumb.height * thumbnail_width / thumb.width))
            thumb = thumb.resize((thumbnail_width, height))
            thumbs.append((path.name, thumb))
    cell_h = max(image.height for _, image in thumbs) + 34
    rows = (len(thumbs) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * thumbnail_width, rows * cell_h), "white")
    draw = ImageDraw.Draw(sheet)
    for index, (name, image) in enumerate(thumbs):
        x = (index % columns) * thumbnail_width
        y = (index // columns) * cell_h
        sheet.paste(image, (x, y + 24))
        draw.text((x + 4, y + 5), name, fill="black")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, format="PNG")
    return output


def analyse_colouring_pages(
    rendered_pages: list[str | Path],
    *,
    minimum_white_ratio: float = 0.90,
    minimum_ink_ratio: float = 0.001,
    maximum_ink_ratio: float = 0.25,
    maximum_midtone_ratio: float = 0.02,
) -> dict[str, Any]:
    """Heuristic pre-screen for colouring interiors; never replaces visual review."""
    if not rendered_pages:
        raise ValueError("rendered_pages must not be empty")
    try:
        from PIL import Image, ImageStat
    except ImportError as exc:
        raise RuntimeError("Pillow is required for colouring-page analysis.") from exc

    pages = []
    for item in rendered_pages:
        path = Path(item)
        if not path.is_file():
            raise FileNotFoundError(f"Missing rendered page: {path}")
        with Image.open(path) as source:
            gray = source.convert("L")
            histogram = gray.histogram()
            total = max(1, sum(histogram))
            dark = sum(histogram[:200]) / total
            midtone = sum(histogram[200:246]) / total
            white = sum(histogram[246:]) / total
            flags = []
            if white < minimum_white_ratio:
                flags.append("background-not-clean-white")
            if dark < minimum_ink_ratio:
                flags.append("too-little-line-art-or-near-blank")
            if dark > maximum_ink_ratio:
                flags.append("very-dense-artwork")
            if midtone > maximum_midtone_ratio:
                flags.append("possible-shading-or-grey-background")
            pages.append({
                "path": str(path),
                "width_px": gray.width,
                "height_px": gray.height,
                "white_ratio": round(white, 5),
                "dark_ink_ratio": round(dark, 5),
                "midtone_ratio": round(midtone, 5),
                "flags": flags,
                "status": "needs-review" if flags else "heuristics-passed-needs-visual-review",
            })
    return {
        "page_count": len(pages),
        "pages": pages,
        "overall_status": "needs-review" if any(p["flags"] for p in pages) else "heuristics-passed-needs-visual-review",
        "note": "Pixel ratios are heuristics only. A human/vision reviewer must inspect every page for clipping, line quality, age appropriateness and unintended content.",
    }
