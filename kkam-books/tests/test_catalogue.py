import tempfile
import unittest
from pathlib import Path

from kkam_pdf_factory.catalogue import get_product, list_products, suggested_filename, upsert_product


class CatalogueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "catalogue.sqlite3"

    def tearDown(self):
        self.tmp.cleanup()

    def test_insert_and_read_product(self):
        upsert_product(self.db, {
            "product_id": "KKAM-0001",
            "title": "Animal Colouring Book",
            "category": "colouring-book",
            "page_count": 32,
            "source_files": ["brief.md", "cover.png"],
            "keywords": ["animals", "preschool"],
        })
        item = get_product(self.db, "KKAM-0001")
        self.assertEqual(item["title"], "Animal Colouring Book")
        self.assertEqual(item["source_files"], ["brief.md", "cover.png"])
        self.assertEqual(item["keywords"], ["animals", "preschool"])
        self.assertEqual(item["publication_status"], "draft")

    def test_upsert_does_not_duplicate_product(self):
        base = {"product_id": "KKAM-0002", "title": "Book A", "category": "workbook"}
        upsert_product(self.db, base)
        upsert_product(self.db, {**base, "title": "Book A Revised"})
        self.assertEqual(len(list_products(self.db)), 1)
        self.assertEqual(get_product(self.db, "KKAM-0002")["title"], "Book A Revised")

    def test_required_fields(self):
        with self.assertRaises(ValueError):
            upsert_product(self.db, {"product_id": "", "title": "Missing ID", "category": "workbook"})

    def test_reject_negative_price(self):
        with self.assertRaises(ValueError):
            upsert_product(self.db, {
                "product_id": "KKAM-0003", "title": "Book", "category": "workbook", "suggested_price": -1
            })

    def test_filename_convention(self):
        self.assertEqual(suggested_filename(7, "Small Business Finance"), "07-KKAM-Small-Business-Finance.pdf")
        with self.assertRaises(ValueError):
            suggested_filename(0, "Book")


if __name__ == "__main__":
    unittest.main()
