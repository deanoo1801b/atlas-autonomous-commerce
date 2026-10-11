from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    audience TEXT NOT NULL DEFAULT '',
    product_brief TEXT NOT NULL DEFAULT '',
    page_count INTEGER,
    trim_size TEXT NOT NULL DEFAULT 'A4',
    source_files_json TEXT NOT NULL DEFAULT '[]',
    artwork_directory TEXT NOT NULL DEFAULT '',
    final_pdf_path TEXT NOT NULL DEFAULT '',
    cover_image_path TEXT NOT NULL DEFAULT '',
    version TEXT NOT NULL DEFAULT '0.1.0',
    production_status TEXT NOT NULL DEFAULT 'brief',
    technical_qa_status TEXT NOT NULL DEFAULT 'not-run',
    visual_qa_status TEXT NOT NULL DEFAULT 'not-run',
    licensing_status TEXT NOT NULL DEFAULT 'not-reviewed',
    keywords_json TEXT NOT NULL DEFAULT '[]',
    product_description TEXT NOT NULL DEFAULT '',
    suggested_price REAL,
    actual_production_cost REAL,
    publication_status TEXT NOT NULL DEFAULT 'draft',
    last_updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    qa_report_path TEXT NOT NULL DEFAULT '',
    approval_reference TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(production_status);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
"""

FIELDS = (
    "product_id", "title", "category", "audience", "product_brief",
    "page_count", "trim_size", "source_files_json", "artwork_directory",
    "final_pdf_path", "cover_image_path", "version", "production_status",
    "technical_qa_status", "visual_qa_status", "licensing_status",
    "keywords_json", "product_description", "suggested_price",
    "actual_production_cost", "publication_status", "qa_report_path",
    "approval_reference",
)

JSON_FIELDS = {"source_files": "source_files_json", "keywords": "keywords_json"}


def connect(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def _prepare(record: dict[str, Any]) -> dict[str, Any]:
    data = dict(record)
    for source, target in JSON_FIELDS.items():
        if source in data:
            data[target] = json.dumps(data.pop(source), ensure_ascii=False)
    unknown = set(data) - set(FIELDS)
    if unknown:
        raise ValueError("Unknown catalogue fields: " + ", ".join(sorted(unknown)))
    for required in ("product_id", "title", "category"):
        if not str(data.get(required, "")).strip():
            raise ValueError(f"{required} is required")
    if data.get("page_count") is not None and int(data["page_count"]) < 1:
        raise ValueError("page_count must be a positive integer")
    for key in ("suggested_price", "actual_production_cost"):
        if data.get(key) is not None and float(data[key]) < 0:
            raise ValueError(f"{key} cannot be negative")
    return data


def upsert_product(db_path: str | Path, record: dict[str, Any]) -> None:
    data = _prepare(record)
    with connect(db_path) as conn:
        cols = ["product_id", "title", "category", *[k for k in FIELDS if k not in {"product_id", "title", "category"} and k in data]]
        values = [data.get(col) for col in cols]
        updates = [col for col in cols if col != "product_id"]
        sql = (
            f"INSERT INTO products ({', '.join(cols)}) VALUES ({', '.join('?' for _ in cols)}) "
            f"ON CONFLICT(product_id) DO UPDATE SET "
            + ", ".join(f"{col}=excluded.{col}" for col in updates)
            + ", last_updated=CURRENT_TIMESTAMP"
        )
        conn.execute(sql, values)


def get_product(db_path: str | Path, product_id: str) -> dict[str, Any] | None:
    with connect(db_path) as conn:
        row = conn.execute("SELECT * FROM products WHERE product_id=?", (product_id,)).fetchone()
    if row is None:
        return None
    result = dict(row)
    result["source_files"] = json.loads(result.pop("source_files_json"))
    result["keywords"] = json.loads(result.pop("keywords_json"))
    return result


def list_products(db_path: str | Path, production_status: str | None = None) -> list[dict[str, Any]]:
    with connect(db_path) as conn:
        if production_status:
            rows = conn.execute(
                "SELECT product_id,title,category,production_status,technical_qa_status,visual_qa_status,publication_status,last_updated FROM products WHERE production_status=? ORDER BY last_updated DESC",
                (production_status,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT product_id,title,category,production_status,technical_qa_status,visual_qa_status,publication_status,last_updated FROM products ORDER BY last_updated DESC"
            ).fetchall()
    return [dict(row) for row in rows]


def suggested_filename(number: int, short_product_name: str) -> str:
    if number < 1:
        raise ValueError("number must be positive")
    slug = "-".join(
        part for part in "".join(c if c.isalnum() else " " for c in short_product_name).split()
    )
    if not slug:
        raise ValueError("short_product_name must contain letters or numbers")
    return f"{number:02d}-KKAM-{slug}.pdf"
