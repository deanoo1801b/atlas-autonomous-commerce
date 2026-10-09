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


def motivation_trend(history: list[dict[str, Any]], current_score: int | None = None) -> int:
    """Return a conservative -100..100 direction-of-travel score from observed history."""
    if not history:
        return 0
    scores = []
    prices = []
    for event in history[-20:]:
        try:
            if event.get("motivation") is not None:
                scores.append(float(event["motivation"]))
        except (TypeError, ValueError):
            pass
        try:
            if event.get("price") is not None:
                prices.append(float(event["price"]))
        except (TypeError, ValueError):
            pass
    if current_score is not None:
        scores.append(float(current_score))
    trend = 0.0
    if len(scores) >= 2:
        trend += max(-50.0, min(50.0, (scores[-1] - scores[0]) * 2.0))
    if len(prices) >= 2 and prices[0] > 0:
        reduction_pct = max(0.0, (prices[0] - prices[-1]) / prices[0] * 100.0)
        trend += min(30.0, reduction_pct * 3.0)
    return int(max(-100, min(100, round(trend))))
