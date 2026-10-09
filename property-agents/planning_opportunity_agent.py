"""Planning precedent and development-opportunity screening.

Uses the public Planning Data API for England. Coverage is incomplete; results are
signals for human investigation, not confirmation of planning permission or feasibility.
Never contacts owners or planning authorities.
"""
from __future__ import annotations

import os
import re
import time
from typing import Any
from urllib.parse import urlencode

import requests

API_URL = "https://www.planning.data.gov.uk/entity.json"
ENABLED = os.getenv("ATLAS_PLANNING_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}
MAX_PER_RUN = max(1, int(os.getenv("ATLAS_PLANNING_MAX_PROPERTIES", "25")))
REQUEST_DELAY = max(0.0, float(os.getenv("ATLAS_PLANNING_REQUEST_DELAY", "0.25")))

DEVELOPMENT_TERMS = (
    "additional bedroom", "bedroom", "loft conversion", "dormer", "hip to gable",
    "rear extension", "side extension", "two storey extension", "single storey extension",
    "roof extension", "roof alteration", "basement", "conversion", "convert",
    "subdivision", "sub-divide", "change of use", "annexe", "annex", "additional dwelling",
    "new dwelling", "flat conversion", "householder", "erection of dwelling",
)
POSITIVE_DECISIONS = ("approved", "granted", "permitted", "consent")
NEGATIVE_DECISIONS = ("refused", "rejected", "withdrawn", "invalid", "declined")


def _norm(value: Any) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", str(value or "").lower()).strip()


def _postcode(value: Any) -> str:
    return re.sub(r"\s+", "", str(value or "")).upper()


def _description(item: dict[str, Any]) -> str:
    parts = []
    for key in ("name", "description", "proposal", "application-type", "application_type", "address"):
        value = item.get(key)
        if value:
            parts.append(str(value))
    return " | ".join(parts)


def _road_name(address: Any) -> str:
    """Conservative road extraction from a public address string."""
    first = str(address or "").split(",")[0].strip().lower()
    first = re.sub(r"^\s*\d+[a-z]?\s+", "", first)
    first = re.sub(r"\b(flat|apartment|unit)\s+\w+\b", "", first)
    return _norm(first)


def _same_road(candidate_address: Any, application_address: Any) -> bool:
    road = _road_name(candidate_address)
    other = _road_name(application_address)
    if not road or not other:
        return False
    # Require a meaningful phrase match; do not match on generic words alone.
    if len(road) >= 5 and (road in other or other in road):
        return True
    a = {t for t in road.split() if len(t) > 2 and t not in {"road", "street", "avenue", "lane", "close", "drive"}}
    b = {t for t in other.split() if len(t) > 2 and t not in {"road", "street", "avenue", "lane", "close", "drive"}}
    return bool(a and b and len(a & b) >= min(2, len(a)))


def _application_url(item: dict[str, Any]) -> str | None:
    for key in ("documentation-url", "documentation_url", "url", "source-url", "source_url"):
        value = item.get(key)
        if isinstance(value, str) and value.startswith("http"):
            return value
    entity = item.get("entity")
    if entity:
        return f"https://www.planning.data.gov.uk/entity/{entity}"
    return None


def _get_applications(postcode: str) -> list[dict[str, Any]]:
    response = requests.get(
        API_URL,
        params={"q": postcode, "dataset": "planning-application", "limit": 100},
        timeout=15,
        headers={"Accept": "application/json", "User-Agent": "InspirationPropertiesUK/1.0 (public planning data)"},
    )
    response.raise_for_status()
    if REQUEST_DELAY:
        time.sleep(REQUEST_DELAY)
    payload = response.json()
    entities = payload.get("entities", [])
    return entities if isinstance(entities, list) else []


def analyse_planning_candidate(candidate: dict[str, Any], applications: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Return planning signals for a candidate. Pass applications to test without network."""
    postcode = _postcode(candidate.get("Postcode") or candidate.get("postcode"))
    address = candidate.get("Property Address") or candidate.get("Address") or candidate.get("Area")
    if not ENABLED:
        return {"Planning Review Status": "Disabled", "Planning Opportunity Summary": "Planning scan disabled by configuration."}
    if not postcode:
        return {
            "Planning Review Status": "Needs postcode",
            "Planning Opportunity Summary": "Planning precedent scan not run: no property postcode available.",
        }
    if applications is None:
        applications = _get_applications(postcode)
    relevant = []
    for item in applications:
        desc = _description(item)
        lower = desc.lower()
        if not any(term in lower for term in DEVELOPMENT_TERMS):
            continue
        app_address = item.get("address") or item.get("site-address") or item.get("site_address") or item.get("name")
        same_road = _same_road(address, app_address)
        app_postcode = _postcode(item.get("postcode") or item.get("post-code") or item.get("postal-code"))
        same_postcode = bool(app_postcode and app_postcode == postcode)
        # The API query is postcode-scoped. Retain records with matching road or
        # explicit same postcode, but label the latter as area precedent only.
        if not same_road and not same_postcode:
            continue
        decision = str(item.get("decision") or item.get("decision-outcome") or item.get("decision_outcome") or "").strip()
        decision_lower = decision.lower()
        if any(word in decision_lower for word in NEGATIVE_DECISIONS):
            outcome = "Refused/unsuccessful (verify official record)"
        elif any(word in decision_lower for word in POSITIVE_DECISIONS):
            outcome = "Potentially approved (verify official record)"
        else:
            outcome = "Outcome unknown"
        relevant.append({
            "address": app_address,
            "description": desc[:600],
            "decision": decision or "Unknown",
            "outcome_label": outcome,
            "reference": item.get("reference") or item.get("planning-application-reference"),
            "date": item.get("start-date") or item.get("validated-date") or item.get("decision-date"),
            "same_road": same_road,
            "url": _application_url(item),
        })
    same_road_apps = [x for x in relevant if x["same_road"]]
    positive_same_road = [x for x in same_road_apps if x["outcome_label"].startswith("Potentially approved")]
    positive_nearby = [x for x in relevant if x["outcome_label"].startswith("Potentially approved")]
    if positive_same_road:
        status = "Same-road precedent found - verify"
        summary = f"Found {len(positive_same_road)} potentially approved development-related application(s) on the same road; these are precedent clues, not permission for this property."
    elif positive_nearby:
        status = "Nearby precedent found - verify"
        summary = f"Found {len(positive_nearby)} potentially approved development-related application(s) in the postcode area; same-road match not established."
    elif relevant:
        status = "Applications found - outcome needs review"
        summary = f"Found {len(relevant)} development-related planning record(s), but no confirmed positive same-road decision."
    else:
        status = "No matching records returned"
        summary = "No matching development applications were returned for this postcode by the national dataset. Coverage is incomplete; check the relevant council planning portal."
    return {
        "Planning Review Status": status,
        "Planning Opportunity Summary": summary,
        "Planning Precedent Count": len(relevant),
        "Planning Same-Road Count": len(same_road_apps),
        "Planning Potentially Approved Count": len(positive_nearby),
        "Planning Evidence": relevant[:10],
        "Planning Search URL": "https://www.planning.data.gov.uk/entity.json?" + urlencode({
            "q": postcode, "dataset": "planning-application", "limit": 100
        }),
    }


def development_profit_scenario(asking_price: Any, estimated_completed_value: Any,
                                works_cost: Any = None, professional_fees: Any = None,
                                finance_and_holding: Any = None, purchase_costs: Any = None,
                                selling_costs: Any = None, contingency_pct: float = 15.0) -> dict[str, Any]:
    """Calculate a transparent scenario only when every required cost input is supplied."""
    def number(v):
        try:
            result = float(str(v).replace(",", "").replace("£", "").strip())
            return result if result >= 0 else None
        except (TypeError, ValueError):
            return None
    purchase, end_value = number(asking_price), number(estimated_completed_value)
    costs = [number(x) for x in (works_cost, professional_fees, finance_and_holding, purchase_costs, selling_costs)]
    if purchase is None or end_value is None or any(x is None for x in costs):
        return {"status": "Incomplete inputs - no profit estimate published", "estimated_net_profit": None}
    works, fees, finance, acquisition, selling = costs
    contingency = works * max(0.0, float(contingency_pct)) / 100
    total_cost = purchase + works + fees + finance + acquisition + selling + contingency
    return {
        "status": "Illustrative only - planning, valuation and all costs require verification",
        "estimated_completed_value": round(end_value, 2),
        "purchase_price": round(purchase, 2),
        "works_cost": round(works, 2),
        "contingency": round(contingency, 2),
        "professional_fees": round(fees, 2),
        "finance_and_holding": round(finance, 2),
        "purchase_costs": round(acquisition, 2),
        "selling_costs": round(selling, 2),
        "estimated_total_cost": round(total_cost, 2),
        "estimated_net_profit_before_tax": round(end_value - total_cost, 2),
        "estimated_margin_on_end_value_pct": round((end_value - total_cost) / end_value * 100, 2) if end_value else None,
    }
