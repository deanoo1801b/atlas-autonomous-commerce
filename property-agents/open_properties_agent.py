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

_LAST_SCAN_COMPLETE = True

DEFAULT_LOCATIONS = (
    "London", "Birmingham", "Manchester", "Leeds", "Liverpool",
    "Bristol", "Nottingham", "Glasgow", "Edinburgh",
)

def _enabled() -> bool:
    return os.getenv("ATLAS_OPEN_PROPERTIES_ENABLED", "true").strip().lower() in {
        "1", "true", "yes", "on"
    }

def _locations() -> list[str]:
    raw = os.getenv("ATLAS_PROPERTY_LOCATIONS", "").strip()
    return [x.strip() for x in raw.split(",") if x.strip()] or list(DEFAULT_LOCATIONS)

def _run(location: str) -> tuple[list[dict[str, Any]], bool]:
    if not shutil.which("property"):
        return [], False
    with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
        cmd = [
            "property", "search", "--country", "GB", "--provider", "rightmove",
            "--location", location, "--transaction", "sale",
            "--max-pages", os.getenv("ATLAS_PROPERTY_MAX_PAGES", "1"),
            "--dedupe", "--output", tmp.name,
        ]
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=90, check=False)
        except (OSError, subprocess.SubprocessError):
            return [], False
        if p.returncode != 0:
            return [], False
        try:
            payload = json.load(tmp)
        except (OSError, json.JSONDecodeError):
            return [], False
    properties = payload.get("properties", [])
    return (properties, True) if isinstance(properties, list) else ([], False)

def discover_open_properties() -> list[dict[str, Any]]:
    global _LAST_SCAN_COMPLETE
    _LAST_SCAN_COMPLETE = True
    if not _enabled():
        _LAST_SCAN_COMPLETE = False
        return []
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for location in _locations():
        items, success = _run(location)
        if not success:
            _LAST_SCAN_COMPLETE = False
        for item in items:
            url = str(item.get("url") or "").strip()
            key = str(item.get("id") or url).strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            item["_search_location"] = location
            out.append(item)
    return out

def last_scan_complete() -> bool:
    return _LAST_SCAN_COMPLETE

def _property_identity_key(item: dict[str, Any]) -> str | None:
    """Stable physical-property key; requires exact source address and postcode."""
    address = " ".join(str(item.get("address") or "").split()).strip().lower()
    postcode = " ".join(str(item.get("postcode") or item.get("postal_code") or "").split()).strip().lower()
    if not address or not postcode:
        return None
    return f"address:{address}|postcode:{postcode}"

def to_property_lead(item: dict[str, Any]) -> dict[str, Any]:
    url = str(item.get("url") or "").strip()
    provider = str(item.get("portal") or "open-properties").strip()
    lead_id = str(item.get("id") or url).strip()
    evidence = (
        f"Normalized public listing from open-properties ({provider}); "
        "listing data is unverified until the agent's evidence checks pass."
    )
    identity_key = _property_identity_key(item)
    notes = {
        "address": item.get("address"),
        "schema_version": item.get("schema_version"),
        "beds": item.get("beds"),
        "baths": item.get("baths"),
        "property_type": item.get("property_type"),
        "listing_date": item.get("listing_date"),
        "fetched_at": item.get("fetched_at"),
    }
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
        "Property Identity Key": identity_key,
        "Notes": json.dumps(notes, separators=(",", ":")),
    }
