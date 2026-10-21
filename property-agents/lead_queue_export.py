"""Export local property candidates into spreadsheet-safe, separated review queues.

This is a local, read-only export. It never contacts people or writes to business systems.
"""
from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Any

FIELDS = (
    "Lead ID", "Lead Type", "Opportunity Type", "Area", "Postcode",
    "Asking Price", "Current Asking Price", "Estimated Market Value",
    "Source", "Source URL", "Opportunity Evidence", "Comparable Sales Count",
    "Comparable Evidence Status", "Planning Review Status", "Contact Permission",
    "Compliance Status", "Notes",
)

def _bmv_review_candidate(row: dict[str, Any]) -> bool:
    """Flag for review only when supplied values imply 25%+ discount and 3+ comp records."""
    try:
        asking = float(str(row.get("Asking Price") or row.get("Current Asking Price") or "").replace(",", "").replace("£", "").strip())
        market = float(str(row.get("Estimated Market Value") or "").replace(",", "").replace("£", "").strip())
        comps = int(float(str(row.get("Comparable Sales Count") or "0").strip()))
    except (TypeError, ValueError, OverflowError):
        return False
    if asking <= 0 or market <= 0 or comps < 3:
        return False
    return (market - asking) / market * 100 >= 25


QUEUE_RULES = {
    "private_seller_review.csv": lambda row: (
        "private" in _text(row, "Lead Type") or "private" in _text(row, "Source")
        or "direct owner" in _text(row, "Lead Type") or "owner direct" in _text(row, "Source")
    ),
    "open_market_review.csv": lambda row: (
        "open market" in _text(row, "Lead Type")
        or _text(row, "Source").startswith("open-properties/")
    ),
    "development_review.csv": lambda row: (
        any(word in _text(row, "Opportunity Type") for word in ("development", "land assembly"))
        or "developer site" in _text(row, "Lead Type")
    ),
    "finance_review.csv": lambda row: (
        "finance" in _text(row, "Lead Type")
        or "mortgage" in _text(row, "Opportunity Type")
        or "bridging" in _text(row, "Opportunity Type")
    ),
    "bmv_review.csv": _bmv_review_candidate,
}


def _text(row: dict[str, Any], field: str) -> str:
    return str(row.get(field) or "").strip().lower()


def _spreadsheet_safe(value: Any) -> Any:
    """Neutralize CSV formula injection in text cells while preserving numeric values."""
    if value is None or isinstance(value, (int, float, bool)):
        return value
    text = str(value)
    if text.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + text
    return text


def export_review_queues(
    candidates: list[dict[str, Any]],
    directory: str | os.PathLike[str] | None = None,
) -> dict[str, Any]:
    """Write separated CSV review queues; unmatched rows remain in the general acquisition queue."""
    destination = Path(directory or os.getenv("ATLAS_LEAD_QUEUE_EXPORT_DIR", "."))
    destination.mkdir(parents=True, exist_ok=True)
    queues: dict[str, list[dict[str, Any]]] = {name: [] for name in QUEUE_RULES}
    queues["property_acquisition_review.csv"] = []
    for candidate in candidates:
        matched = False
        for name, predicate in QUEUE_RULES.items():
            if predicate(candidate):
                row = dict(candidate)
                if name == "bmv_review.csv":
                    row["Comparable Evidence Status"] = (str(row.get("Comparable Evidence Status") or "") + " | PRELIMINARY BMV REVIEW FLAG — discount arithmetic only; human valuation review required").strip(" |")
                queues[name].append(row)
                matched = True
        if not matched:
            queues["property_acquisition_review.csv"].append(candidate)

    written = {}
    for filename, rows in queues.items():
        path = destination / filename
        with path.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow({field: _spreadsheet_safe(row.get(field)) for field in FIELDS})
        written[filename] = {"path": str(path), "count": len(rows)}
    return {
        "directory": str(destination),
        "candidate_count": len(candidates),
        "queues": written,
        "safety": "Local review only; no contact, offers, referrals, publishing, or production writes.",
    }
