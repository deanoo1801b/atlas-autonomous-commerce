"""Optional adapter for the MIT-licensed open-properties data layer.

The adapter keeps the acquisition/compliance logic in our repository. It only consumes
normalized public listing records from the external CLI and never contacts sellers.
Provider access rules remain those of the upstream project and each portal.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from typing import Any

DEFAULT_LOCATIONS = (
    "London",
    "Birmingham",
    "Manchester",
    "Leeds",
    "Liverpool",
    "Bristol",
    "Nottingham",
    "Glasgow",
    "Edinburgh",
)

def _enabled() -> bool:
    return os.getenv("ATLAS_OPEN_PROPERTIES_ENABLED", "true").strip().lower() in {
        "1", "true", "yes", "on"
    }

def _locations() -> list[str]:
    raw = os.getenv("ATLAS_PROPERTY_LOCATIONS", "").strip()
    return [x.strip() for x in raw.split(",") if x.strip()] or list(DEFAULT_LOCATIONS)

def _run(location: str) -> list[dict[str, Any]]:
    if not shutil.which("property"):
        return []
    with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
        cmd = [
            "property", "search",
            "--country", "GB",
            "--provider", "rightmove",
            "--location", location,
            "--transaction", "sale",
            "--max-pages", os.getenv("ATLAS_PROPERTY_MAX_PAGES", "1"),
            "--dedupe",
            "--output", tmp.name,
        ]
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=90, check=False)
        except (OSError, subprocess.SubprocessError):
            return []
        if p.returncode != 0:
            return []
        try:
            payload = json.load(tmp)
        except (OSError, json.JSONDecodeError):
            return []
    properties = payload.get("properties", [])
    return properties if isinstance(properties, list) else []

def discover_open_properties() -> list[dict[str, Any]]:
    if not _enabled():
        return []
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for location in _locations():
        for item in _run(location):
            url = str(item.get("url") or "").strip()
            key = str(item.get("id") or url).strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            item["_search_location"] = location
            out.append(item)
    return out

def to_property_lead(item: dict[str, Any]) -> dict[str, Any]:
    url = str(item.get("url") or "").strip()
    provider = str(item.get("portal") or "open-properties").strip()
    lead_id = str(item.get("id") or url).strip()
    evidence = (
        f"Normalized public listing from open-properties ({provider}); "
        "listing data is unverified until the agent's evidence checks pass."
    )
    return {
        "Lead ID": "OP-" + lead_id[:80],
        "Lead Type": "Open Market Listing",
        "Opportunity Type": "Property Acquisition",
        "Area": item.get("address") or item.get("_search_location"),
        "Portal Listing ID": item.get("id"),
        "Postcode": item.get("postcode") or item.get("postal_code"),
        "Asking Price": item.get("price"),
        "Seller Name": None,
        "Source": f"open-properties/{provider}",
        "Source URL": url or None,
        "Opportunity Evidence": evidence,
        "Contact Permission": "Unknown",
        "Do Not Contact": False,
        "Finance Candidate": "Review",
        "Notes": json.dumps({
            "schema_version": item.get("schema_version"),
            "beds": item.get("beds"),
            "baths": item.get("baths"),
            "property_type": item.get("property_type"),
            "listing_date": item.get("listing_date"),
            "fetched_at": item.get("fetched_at"),
        }, separators=(",", ":")),
    }
