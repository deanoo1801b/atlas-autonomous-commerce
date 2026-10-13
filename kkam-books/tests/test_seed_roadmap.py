from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from kkam_pdf_factory.catalogue import connect
from kkam_pdf_factory.seed_roadmap import seed


class ProductRoadmapSeedTests(unittest.TestCase):
    def test_seeds_all_seven_products_idempotently(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            roadmap = root / "roadmap.json"
            roadmap.write_text(json.dumps({"products": [
                {"product_id": f"KKAM-TEST-{i}", "title": f"Test Product {i}",
                 "category": "test", "keywords": ["test"], "acceptance_checks": ["check"]}
                for i in range(7)
            ]}), encoding="utf-8")
            db = root / "catalogue.sqlite3"
            first = seed(roadmap, db)
            second = seed(roadmap, db)
            self.assertEqual(first["count"], 7)
            self.assertEqual(second["count"], 7)
            with connect(db) as conn:
                rows = conn.execute("SELECT product_id, keywords_json FROM products").fetchall()
            self.assertEqual(len(rows), 7)
            self.assertTrue(all(json.loads(row["keywords_json"]) == ["test"] for row in rows))

    def test_rejects_duplicate_ids_before_overwriting(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            roadmap = root / "roadmap.json"
            roadmap.write_text(json.dumps({"products": [
                {"product_id": "DUP", "title": "One", "category": "test"},
                {"product_id": "DUP", "title": "Two", "category": "test"}
            ]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                seed(roadmap, root / "catalogue.sqlite3")


if __name__ == "__main__":
    unittest.main()
