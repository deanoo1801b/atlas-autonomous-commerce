import tempfile
import unittest
from pathlib import Path

from kkam_pdf_factory.assemble import build_business_pdf, build_colouring_book
from kkam_pdf_factory.qa import inspect_pdf


class AssembleTests(unittest.TestCase):
    def test_build_business_pdf_and_qa(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "business.pdf"
            build_business_pdf({
                "title": "Small Business Finance",
                "subtitle": "Sample test document",
                "author": "KKAM BOOKS",
                "trim_size": "A4",
                "keywords": ["finance", "workbook"],
                "sections": [
                    {"heading": "Chapter 1", "paragraphs": ["Original sample content."], "bullets": ["Track income", "Track costs"]},
                    {"heading": "Example table", "table": {"headers": ["Item", "Amount"], "rows": [["Sales", "100"], ["Costs", "40"]]}},
                ],
            }, output)
            report = inspect_pdf(output, expected_pages=3, expected_trim="A4")
            self.assertEqual(report["technical_status"], "passed")
            self.assertEqual(report["page_count"], 3)
            self.assertTrue(report["metadata"].get("title"))

    def test_business_pdf_requires_title_and_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                build_business_pdf({"title": "", "sections": [{"heading": "A"}]}, Path(tmp) / "bad.pdf")
            with self.assertRaises(ValueError):
                build_business_pdf({"title": "No sections", "sections": []}, Path(tmp) / "bad.pdf")

    def test_colouring_book_missing_asset_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                build_colouring_book("Animals", [Path(tmp) / "missing.png"], Path(tmp) / "book.pdf")

    def test_colouring_book_assembles_original_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            from PIL import Image, ImageDraw
            tmp_path = Path(tmp)
            art = []
            for i in range(2):
                image = Image.new("RGB", (1200, 1600), "white")
                draw = ImageDraw.Draw(image)
                draw.ellipse((200, 200, 1000, 1000), outline="black", width=8)
                draw.line((300, 1200, 900, 1200), fill="black", width=8)
                p = tmp_path / f"art-{i}.png"
                image.save(p)
                art.append(p)
            output = tmp_path / "colouring.pdf"
            build_colouring_book("Animal Shapes", art, output, age_range="3–6")
            report = inspect_pdf(output, expected_pages=3, expected_trim="A4")
            self.assertEqual(report["technical_status"], "passed")
            self.assertEqual(report["page_count"], 3)


if __name__ == "__main__":
    unittest.main()
