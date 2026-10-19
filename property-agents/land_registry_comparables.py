"""Evidence-first sold-comparable lookup using HM Land Registry open linked data.

This module is opt-in and only reads official Price Paid Data. It does not infer
current ownership, bedrooms, condition, current value, or seller motivation.
"""
from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Any
from urllib.parse import urlsplit

import requests

ENDPOINT = "https://landregistry.data.gov.uk/landregistry/query"
ATTRIBUTION = (
    "Contains HM Land Registry data © Crown copyright and database right 2021. "
    "Licensed under the Open Government Licence v3.0."
)
POSTCODE_RE = re.compile(
    r"^\s*([A-PR-UWYZ]{1,2}\d[A-Z\d]?)(?:\s*\d[ABD-HJLNP-UW-Z]{2})?\s*$",
    re.IGNORECASE,
)
PROPERTY_TYPE_TERMS = {
    "detached": ("detached",),
    "semi-detached": ("semi", "semi-detached", "semi detached"),
    "terraced": ("terraced",),
    "flat": ("flat", "maisonette"),
    "other": ("other",),
}


def postcode_outcode(postcode: str) -> str | None:
    """Extract a UK postcode outcode; reject free-text that contains no postcode."""
    match = POSTCODE_RE.search(str(postcode or "").upper())
    return re.sub(r"\s+", "", match.group(1)).upper() if match else None


def _local_type(value: str) -> str:
    token = str(value or "").lower().replace("_", "-").split("/")[-1].split("#")[-1]
    if "semi" in token:
        return "semi-detached"
    if "detached" in token:
        return "detached"
    if "terraced" in token or token in {"terrace", "t"}:
        return "terraced"
    if "flat" in token or "maisonette" in token or token in {"f"}:
        return "flat"
    if "other" in token or token in {"o"}:
        return "other"
    return token


def build_query(outcode: str, since: date, limit: int = 100) -> str:
    """Build a bounded query; outcode is validated before interpolation."""
    normalized = postcode_outcode(outcode)
    if normalized != re.sub(r"\s+", "", str(outcode or "")).upper():
        raise ValueError("A valid postcode outcode is required")
    if not 1 <= int(limit) <= 250:
        raise ValueError("limit must be between 1 and 250")
    safe_outcode = normalized.replace('"', "")
    return f'''PREFIX ppi: <http://landregistry.data.gov.uk/def/ppi/>
PREFIX common: <http://landregistry.data.gov.uk/def/common/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?transaction ?price ?date ?propertyType ?postcode ?paon ?street ?town
WHERE {{
  ?transaction a ppi:Transaction ;
      ppi:pricePaid ?price ;
      ppi:transactionDate ?date ;
      ppi:propertyType ?propertyType ;
      ppi:propertyAddress ?address .
  ?address common:postcode ?postcode .
  OPTIONAL {{ ?address common:paon ?paon . }}
  OPTIONAL {{ ?address common:street ?street . }}
  OPTIONAL {{ ?address common:town ?town . }}
  FILTER(STRSTARTS(UCASE(STR(?postcode)), "{safe_outcode} "))
  FILTER(?date >= "{since.isoformat()}"^^xsd:date)
}}
ORDER BY DESC(?date)
LIMIT {int(limit)}'''


def _binding_value(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    return str(value.get("value") or "").strip() if isinstance(value, dict) else ""


def normalize_results(payload: dict[str, Any], outcode: str, property_type: str,
                      since: date | None = None, limit: int = 100) -> list[dict[str, Any]]:
    """Normalize results and retain only recent, same-outcode, same-type sales."""
    normalized_outcode = postcode_outcode(outcode)
    if not normalized_outcode:
        raise ValueError("A valid UK postcode/outcode is required")
    target_type = _local_type(property_type)
    allowed = PROPERTY_TYPE_TERMS.get(target_type, (target_type,))
    since = since or (date.today() - timedelta(days=365))
    bindings = payload.get("results", {}).get("bindings", [])
    if not isinstance(bindings, list):
        return []
    output = []
    seen = set()
    for row in bindings:
        if not isinstance(row, dict):
            continue
        postcode = " ".join(_binding_value(row, "postcode").upper().split())
        if postcode_outcode(postcode) != normalized_outcode:
            continue
        try:
            sold_date = date.fromisoformat(_binding_value(row, "date")[:10])
            price = float(_binding_value(row, "price"))
        except (ValueError, TypeError):
            continue
        if sold_date < since or sold_date > date.today() or price <= 0:
            continue
        raw_type = _binding_value(row, "propertyType")
        normalized_type = _local_type(raw_type)
        if not any(term in normalized_type for term in allowed):
            continue
        transaction = _binding_value(row, "transaction")
        parts = urlsplit(transaction)
        if parts.scheme not in {"http", "https"} or not parts.hostname:
            continue
        source_url = "https://" + parts.netloc + parts.path
        if source_url in seen:
            continue
        seen.add(source_url)
        address = " ".join(filter(None, (
            _binding_value(row, "paon"), _binding_value(row, "street"),
            _binding_value(row, "town"),
        )))
        output.append({
            "sold_price": round(price, 2),
            "sale_date": sold_date.isoformat(),
            "source_url": source_url,
            "postcode": postcode,
            "property_type": target_type,
            "address_label": address or None,
            "evidence_source": "HM Land Registry Price Paid Data",
            "evidence_status": "OFFICIAL_TRANSACTION_RECORD_REQUIRES_HUMAN_COMPARABILITY_REVIEW",
        })
    output.sort(key=lambda item: item["sale_date"], reverse=True)
    return output[:limit]


def enrich_candidates_with_sold_comparables(candidates: list[dict[str, Any]], *,
                                            enabled: bool | None = None,
                                            max_lookups: int = 10,
                                            fetcher: Any = fetch_sold_comparables) -> dict[str, Any]:
    """Optionally enrich candidate records with official sold evidence, never a valuation.

    Disabled by default. Caches each outcode/property-type lookup during this run.
    """
    import json
    import os

    if enabled is None:
        enabled = os.getenv("ATLAS_HMLR_COMPARABLES_ENABLED", "").strip().lower() in {
            "1", "true", "yes", "on"
        }
    if not enabled:
        return {"enabled": False, "lookups": 0, "enriched": 0, "errors": 0}
    if not 1 <= int(max_lookups) <= 25:
        raise ValueError("max_lookups must be between 1 and 25")

    cache: dict[tuple[str, str], dict[str, Any]] = {}
    enriched = errors = 0
    for candidate in candidates:
        postcode = str(candidate.get("Postcode") or candidate.get("postcode") or "").strip()
        property_type = str(candidate.get("Property Type") or candidate.get("property_type") or "").strip()
        notes = candidate.get("Notes")
        if not property_type and isinstance(notes, str):
            try:
                parsed_notes = json.loads(notes)
                if isinstance(parsed_notes, dict):
                    property_type = str(parsed_notes.get("property_type") or "").strip()
            except (TypeError, json.JSONDecodeError):
                pass
        outcode = postcode_outcode(postcode)
        if not outcode or not property_type:
            candidate.setdefault("Comparable Evidence Status", "Not run: postcode or property type missing")
            continue
        key = (outcode, _local_type(property_type))
        if key not in cache:
            if len(cache) >= int(max_lookups):
                candidate.setdefault("Comparable Evidence Status", "Deferred: per-run lookup limit reached")
                continue
            try:
                cache[key] = fetcher(postcode, property_type, days=365, limit=100)
            except Exception as exc:
                errors += 1
                candidate["Comparable Evidence Status"] = (
                    f"Lookup failed ({type(exc).__name__}); no valuation inferred"
                )
                continue
        result = cache[key]
        records = result.get("comparables", [])
        candidate["Comparable Sales Evidence"] = json.dumps(records, separators=(",", ":"))
        candidate["Comparable Sales Count"] = len(records)
        candidate["Comparable Evidence Status"] = (
            "Candidate evidence available; human comparability review required"
            if len(records) >= 3 else
            "Insufficient recent same-type sales; do not classify as BMV"
        )
        if isinstance(notes, str):
            try:
                notes_obj = json.loads(notes)
                if not isinstance(notes_obj, dict):
                    notes_obj = {}
            except (TypeError, json.JSONDecodeError):
                notes_obj = {}
        else:
            notes_obj = {}
        notes_obj["hm_land_registry_comparable_attribution"] = result.get("attribution", ATTRIBUTION)
        notes_obj["hm_land_registry_comparable_limitations"] = result.get("limitations", [])
        candidate["Notes"] = json.dumps(notes_obj, separators=(",", ":"))[:4000]
        enriched += 1
    return {"enabled": True, "lookups": len(cache), "enriched": enriched, "errors": errors}


def fetch_sold_comparables(postcode: str, property_type: str, *,
                           days: int = 365, limit: int = 100,
                           session: Any = requests) -> dict[str, Any]:
    """Fetch official sold-price records for manual review; never estimates market value."""
    outcode = postcode_outcode(postcode)
    if not outcode:
        raise ValueError("A valid UK postcode is required")
    if not 1 <= int(days) <= 3650:
        raise ValueError("days must be between 1 and 3650")
    since = date.today() - timedelta(days=int(days))
    query = build_query(outcode, since, limit)
    response = session.post(
        ENDPOINT,
        data={"query": query},
        headers={"Accept": "application/sparql-results+json"},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    records = normalize_results(payload, outcode, property_type, since, limit)
    return {
        "query_area": outcode,
        "property_type_filter": _local_type(property_type),
        "date_from": since.isoformat(),
        "date_to": date.today().isoformat(),
        "result_count": len(records),
        "comparables": records,
        "attribution": ATTRIBUTION,
        "limitations": [
            "Sold-price records do not establish current market value or current ownership.",
            "Outcode and property type are broad filters; check exact location, size, tenure, condition, and sale circumstances.",
            "Do not label a property BMV from this dataset alone; human valuation review and at least three genuinely comparable sales are required.",
        ],
    }
