from __future__ import annotations

import argparse
import json
from pathlib import Path

from kkam_pdf_factory.catalogue import upsert_product


def seed(roadmap_path: str | Path, db_path: str | Path) -> dict[str, object]:
    roadmap = json.loads(Path(roadmap_path).read_text(encoding="utf-8"))
    products = roadmap.get("products")
    if not isinstance(products, list) or not products:
        raise ValueError("Roadmap must contain a non-empty products list")
    ids: set[str] = set()
    for product in products:
        product_id = str(product.get("product_id", "")).strip()
        if not product_id or product_id in ids:
            raise ValueError(f"Missing or duplicate product_id: {product_id!r}")
        ids.add(product_id)
        record = {k: v for k, v in product.items() if k != "acceptance_checks"}
        upsert_product(db_path, record)
    return {"status": "seeded", "count": len(products), "product_ids": sorted(ids), "database": str(db_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed the KKAM BOOKS catalogue from the product roadmap")
    parser.add_argument("--roadmap", default="kkam-books/config/product-roadmap.json")
    parser.add_argument("--db", default="output/catalogue/kkam-books.sqlite3")
    args = parser.parse_args()
    print(json.dumps(seed(args.roadmap, args.db), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
