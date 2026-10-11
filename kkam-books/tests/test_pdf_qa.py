import tempfile
import unittest
from pathlib import Path

from kkam_pdf_factory.qa import analyse_colouring_pages, create_contact_sheet, inspect_pdf


def make_pdf(path: Path, pages, pagesize=None):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(str(path), pagesize=pagesize or A4)
    c.setTitle("KKAM QA Fixture")
    for text in pages:
        if text:
            c.drawString(60, 780, text)
        c.showPage()
    c.save()


class PdfQaTests(unittest.TestCase):
    def test_missing_pdf_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = inspect_pdf(Path(tmp) / "missing.pdf")
            self.assertEqual(report["technical_status"], "failed")
            self.assertIn("PDF file does not exist.", report["errors"])

    def test_malformed_pdf_fails_signature(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.pdf"
            path.write_bytes(b"not a pdf document")
            report = inspect_pdf(path)
            self.assertEqual(report["technical_status"], "failed")
            self.assertIn("File signature is not %PDF-.", report["errors"])

    def test_tiny_pdf_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tiny.pdf"
            path.write_bytes(b"%PDF-")
            report = inspect_pdf(path)
            self.assertEqual(report["technical_status"], "failed")
            self.assertIn("File is too small to be a valid PDF.", report["errors"])

    def test_expected_page_count_is_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "one-page.pdf"
            make_pdf(path, ["One page"])
            report = inspect_pdf(path, expected_pages=2)
            self.assertEqual(report["technical_status"], "failed")
            self.assertTrue(any("Expected 2 pages" in error for error in report["errors"]))

    def test_expected_a4_dimensions_are_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            from reportlab.lib.pagesizes import letter
            path = Path(tmp) / "letter.pdf"
            make_pdf(path, ["Wrong trim"], pagesize=letter)
            report = inspect_pdf(path, expected_trim="A4")
            self.assertEqual(report["technical_status"], "failed")
            self.assertTrue(any("not A4" in error for error in report["errors"]))

    def test_render_detects_duplicate_pages_and_blanks(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "duplicates.pdf"
            make_pdf(path, ["Same page", "Same page", ""])
            report = inspect_pdf(path, render_pages=True, render_dir=Path(tmp) / "rendered")
            self.assertEqual(report["technical_status"], "passed")
            self.assertEqual(len(report["rendered_pages"]), 3)
            self.assertTrue(report["duplicate_rendered_pages"])
            self.assertIn(3, report["blank_rendered_pages"])
            self.assertEqual(report["visual_status"], "rendered-needs-review")

    def test_missing_render_directory_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "one-page.pdf"
            make_pdf(path, ["Page"])
            report = inspect_pdf(path, render_pages=True)
            self.assertEqual(report["technical_status"], "failed")
            self.assertIn("render_dir is required when render_pages=True.", report["errors"])

    def test_contact_sheet_is_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            from PIL import Image, ImageDraw
            root = Path(tmp)
            page = root / "page-0001.png"
            image = Image.new("RGB", (200, 300), "white")
            ImageDraw.Draw(image).ellipse((40, 40, 160, 200), outline="black", width=3)
            image.save(page)
            output = create_contact_sheet([page], root / "contact.png", columns=1)
            self.assertTrue(output.is_file())

    def test_colouring_page_heuristics_flag_blank_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            from PIL import Image
            root = Path(tmp)
            blank = root / "blank.png"
            Image.new("RGB", (200, 300), "white").save(blank)
            report = analyse_colouring_pages([blank])
            self.assertEqual(report["overall_status"], "needs-review")
            self.assertIn("too-little-line-art-or-near-blank", report["pages"][0]["flags"])

    def test_colouring_page_heuristics_flag_grey_background(self):
        with tempfile.TemporaryDirectory() as tmp:
            from PIL import Image, ImageDraw
            root = Path(tmp)
            gray = root / "gray.png"
            image = Image.new("RGB", (200, 300), (220, 220, 220))
            ImageDraw.Draw(image).ellipse((40, 40, 160, 200), outline="black", width=3)
            image.save(gray)
            report = analyse_colouring_pages([gray])
            self.assertIn("background-not-clean-white", report["pages"][0]["flags"])

    def test_low_resolution_image_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            from PIL import Image
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            root = Path(tmp)
            image_path = root / "low-res.png"
            Image.new("RGB", (80, 80), "black").save(image_path)
            pdf_path = root / "low-res.pdf"
            c = canvas.Canvas(str(pdf_path), pagesize=A4)
            c.drawImage(str(image_path), 36, 36, width=520, height=750)
            c.save()
            report = inspect_pdf(pdf_path)
            self.assertTrue(report["images"])
            self.assertTrue(any("below 300 effective DPI" in warning for warning in report["warnings"]))


if __name__ == "__main__":
    unittest.main()
