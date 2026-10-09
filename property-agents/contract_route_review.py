"""Local, manual-review queue for property route comparisons.

Reads a user-supplied JSON file and writes a local JSON report. No network,
Smartsheet, seller contact, buyer contact, offers, signatures or payments.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from contract_route_comparator import compare_routes


def build_review_report(payload: Any) -> dict[str, Any]:
    if isinstance(payload, list):
        deals = payload
    elif isinstance(payload, dict) and isinstance(payload.get("deals"), list):
        deals = payload["deals"]
    else:
        raise ValueError("Input must be a JSON list of deals or an object with a 'deals' list.")
    if any(not isinstance(item, dict) for item in deals):
        raise ValueError("Every deal entry must be a JSON object.")
    comparisons = [compare_routes(deal) for deal in deals]
    return {
        "report_type": "manual_property_route_review",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "record_count": len(comparisons),
        "automatic_contacting": False,
        "automatic_offers": False,
        "automatic_contracting": False,
        "automatic_payments": False,
        "smartsheet_write": False,
        "review_items": comparisons,
        "notice": "Preliminary triage only. Human, regulatory and independent solicitor review remain required; this report does not authorise a transaction.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare sourcing vs contract assignment for manually supplied property deals.")
    parser.add_argument("input_json", help="Local JSON file containing a list of deal objects or {'deals': [...]}.")
    parser.add_argument("--output", default="property-route-review-report.json", help="Local output JSON path.")
    args = parser.parse_args()
    source = Path(args.input_json)
    destination = Path(args.output)
    payload = json.loads(source.read_text(encoding="utf-8"))
    report = build_review_report(payload)
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {report['record_count']} review item(s) to {destination}. No external systems were contacted or updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
