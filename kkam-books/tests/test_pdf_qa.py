import tempfile
import unittest
from pathlib import Path

from kkam_pdf_factory.qa import inspect_pdf


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


if __name__ == "__main__":
    unittest.main()
