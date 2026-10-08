"""Motivated-seller scoring from public, non-sensitive listing signals."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import re
from typing import Any

DISTRESS_TERMS = (
    "urgent sale", "must sell", "no chain", "cash buyers", "reduced",
    "price reduction", "motivated seller", "quick sale", "offers invited",
    "auction", "probate", "repossession", "needs refurbishment",
)

def _notes(lead: dict[str, Any]) -> dict[str, Any]:
    try:
        value = json.loads(str(lead.get("Notes") or "{}"))
        return value if isinstance(value, dict) else {}
    except (TypeError, json.JSONDecodeError):
        return {}

def motivation_score(lead: dict[str, Any]) -> int:
    score = 20  # baseline: a publicly marketed property is a weak acquisition signal.
    haystack = " ".join(str(lead.get(k) or "") for k in (
        "Lead Type", "Opportunity Type", "Opportunity Evidence", "Notes"
    )).lower()

    if any(term in haystack for term in DISTRESS_TERMS):
        score += 20
    if "private seller" in haystack:
        score += 10
    if "auction" in haystack:
        score += 15

    notes = _notes(lead)
    listing_date = str(notes.get("listing_date") or "").strip()
    if listing_date:
        try:
            dt = datetime.fromisoformat(listing_date.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            age = max(0, (datetime.now(timezone.utc) - dt).days)
            if age >= 180:
                score += 20
            elif age >= 90:
                score += 15
            elif age >= 45:
                score += 10
            elif age >= 21:
                score += 5
        except ValueError:
            pass

    # Keep this signal deliberately evidence-based: no inference of mortgage distress.
    if re.search(r"price[_ -]?reduction|previous[_ -]?price|old[_ -]?price", haystack):
        score += 15

    return max(0, min(100, score))
