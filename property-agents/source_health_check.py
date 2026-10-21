"""Read-only health checks for official UK property data sources.

This tool checks API reachability and whether the test queries return records.
It does not collect property leads, scrape listing portals, contact anyone, or
write to business systems. An empty response is a coverage warning, not proof
that no relevant property or planning application exists.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

import requests

from land_registry_comparables import fetch_sold_comparables
from planning_opportunity_agent import API_URL as PLANNING_API_URL

PLANNING_DATASET_URL = "https://www.planning.data.gov.uk/dataset/planning-application"
USER_AGENT = "InspirationPropertiesUK/1.0 (read-only official-source health check)"


def check_land_registry(fetcher: Any = fetch_sold_comparables) -> dict[str, Any]:
    """Check the official sold-price endpoint with a bounded historic sample."""
    try:
        result = fetcher("CR0", "terraced", days=3650, limit=5)
        count = int(result.get("result_count", len(result.get("comparables", []))))
        return {
            "source": "HM Land Registry Price Paid Data",
            "status": "reachable_with_records" if count else "reachable_no_records_for_test_query",
            "endpoint": "https://landregistry.data.gov.uk/landregistry/query",
            "test_area": "CR0",
            "test_property_type": "terraced",
            "lookback_days": 3650,
            "sample_records_returned": count,
            "attribution": result.get("attribution"),
            "limitations": result.get("limitations", []),
        }
    except Exception as exc:
        return {
            "source": "HM Land Registry Price Paid Data",
            "status": "unavailable_or_query_failed",
            "endpoint": "https://landregistry.data.gov.uk/landregistry/query",
            "error_type": type(exc).__name__,
            "error": str(exc)[:500],
        }


def check_planning_data(session: Any = requests) -> dict[str, Any]:
    """Check the public national planning-application dataset, without a lead search."""
    try:
        response = session.get(
            PLANNING_API_URL,
            params={"dataset": "planning-application", "limit": 1},
            timeout=15,
            headers={"Accept": "application/json", "User-Agent": USER_AGENT},
        )
        response.raise_for_status()
        payload = response.json()
        entities = payload.get("entities", []) if isinstance(payload, dict) else []
        if not isinstance(entities, list):
            raise ValueError("Planning API response did not contain an entities list")
        return {
            "source": "Planning Data API — planning-application dataset",
            "status": "reachable_with_records" if entities else "reachable_but_empty",
            "endpoint": PLANNING_API_URL,
            "dataset_status_page": PLANNING_DATASET_URL,
            "sample_records_returned": len(entities),
            "warning": (
                None if entities else
                "The dataset query returned no records. Do not treat this as evidence that no planning applications exist; check the relevant local council register."
            ),
        }
    except Exception as exc:
        return {
            "source": "Planning Data API — planning-application dataset",
            "status": "unavailable_or_query_failed",
            "endpoint": PLANNING_API_URL,
            "dataset_status_page": PLANNING_DATASET_URL,
            "error_type": type(exc).__name__,
            "error": str(exc)[:500],
        }


def build_report(
    land_registry_check: dict[str, Any] | None = None,
    planning_check: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a transparent report; API reachability never means lead validation."""
    checks = [
        land_registry_check if land_registry_check is not None else check_land_registry(),
        planning_check if planning_check is not None else check_planning_data(),
    ]
    statuses = {item["status"] for item in checks}
    if any(status == "unavailable_or_query_failed" for status in statuses):
        overall = "ACTION_REQUIRED"
    elif any(status == "reachable_but_empty" for status in statuses):
        overall = "PARTIAL_DATA_COVERAGE"
    else:
        overall = "CHECKS_COMPLETED_REVIEW_REQUIRED"
    return {
        "report_type": "read_only_official_source_health_check",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "overall_status": overall,
        "checks": checks,
        "explicit_non_actions": {
            "property_candidates_created": 0,
            "seller_contacts_sent": 0,
            "offers_made": 0,
            "finance_referrals_made": 0,
            "production_writes": 0,
        },
        "interpretation": (
            "This report verifies only bounded API reachability and sample-query responses. "
            "It does not validate listing-source access, identify live deals, establish market value, "
            "or prove that a search with no results means no opportunity exists."
        ),
    }


def main() -> int:
    report = build_report()
    path = os.getenv("ATLAS_SOURCE_HEALTH_REPORT_PATH", "source-health-report.json")
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if report["overall_status"] == "ACTION_REQUIRED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
