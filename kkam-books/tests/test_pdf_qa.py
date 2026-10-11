import tempfile
import unittest
from pathlib import Path

from kkam_pdf_factory.qa import inspect_pdf


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


if __name__ == "__main__":
    unittest.main()
