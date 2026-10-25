#!/usr/bin/env python3
"""Validate scanner CSV and prepare a non-writing Smartsheet import report."""
import csv
import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

INPUT = Path(os.environ.get("PROPERTY_SCAN_CSV", "property-agent-output/property-opportunities.csv"))
OUTPUT = Path("property-agent-output/smartsheet-dry-run.json")
REQUIRED = {"title", "published_at", "publisher", "url", "verification_status", "lead_score", "contacted"}

def canonical_url(raw):
    parts = urlsplit((raw or "").strip())
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        return ""
    # Preserve path; remove fragment and common tracking query parameters.
    kept = []
    for pair in parts.query.split("&") if parts.query else []:
        key = pair.split("=", 1)[0].lower()
        if key.startswith("utm_") or key in {"gclid", "fbclid"}:
            continue
        kept.append(pair)
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), "&".join(kept), ""))

def main():
    if not INPUT.exists():
        raise SystemExit(f"Input CSV not found: {INPUT}")
    with INPUT.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            raise SystemExit("CSV schema missing required columns: " + ", ".join(sorted(missing)))
        rows = list(reader)

    by_url = {}
    invalid = []
    for row in rows:
        url = canonical_url(row.get("url", ""))
        if not url:
            invalid.append({"title": row.get("title", ""), "reason": "invalid_or_missing_http_url"})
            continue
        key = hashlib.sha256(url.encode()).hexdigest()
        if key not in by_url:
            by_url[key] = {
                "source_url": url,
                "title": (row.get("title") or "").strip(),
                "source": (row.get("publisher") or "").strip(),
                "evidence": (row.get("snippet") or "").strip()[:1000],
                "verification_status": "UNVERIFIED_NEEDS_HUMAN_REVIEW",
                "lead_score": "Unscored",
                "contact_status": "Not Contacted",
                "contact_permission": "Unknown",
                "asking_price": "",
                "seller_name": "",
                "seller_email": "",
                "seller_phone": "",
                "identity_key_sha256": key,
                "proposed_action": "REVIEW_ONLY_NO_WRITE"
            }

    report = {
        "mode": "DRY_RUN_ONLY",
        "target_sheet": "Property Leads",
        "input_file": str(INPUT),
        "input_rows": len(rows),
        "unique_valid_source_urls": len(by_url),
        "duplicate_source_urls_collapsed": max(0, len(rows) - len(invalid) - len(by_url)),
        "invalid_rows": invalid,
        "proposed_records": list(by_url.values()),
        "safety_note": "No Smartsheet API calls are made. All records remain unverified; no outreach is performed."
    }
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("mode", "input_rows", "unique_valid_source_urls", "duplicate_source_urls_collapsed")}))
    print(f"Dry-run report: {OUTPUT}")

if __name__ == "__main__":
    main()
