"""Offline buyer verification and deal matching helpers."""
from datetime import date, datetime, timezone

VERIFICATION_MAX_AGE_DAYS = 90

def _norm(value):
    return " ".join(str(value or "").strip().lower().replace("-", " ").split())

def _number(value):
    try:
        return float(str(value).replace(",", "").replace("£", "").strip()) if value is not None and str(value).strip() else None
    except (TypeError, ValueError):
        return None

def _as_date(value):
    try:
        return date.fromisoformat(str(value)[:10]) if value else None
    except (TypeError, ValueError):
        return None

def buyer_verification_status(buyer, today=None, max_age_days=VERIFICATION_MAX_AGE_DAYS):
    today = today or datetime.now(timezone.utc).date()
    if buyer.get("do_not_contact") or _norm(buyer.get("consent_status")) == "withdrawn":
        return "Do not contact / withdrawn"
    if not buyer.get("identity_verified"):
        return "Unverified identity"
    if _norm(buyer.get("funding_evidence_status")) not in {"checked", "verified", "verified by reviewer"}:
        return "Purchasing capacity not verified"
    checked = _as_date(buyer.get("verification_date"))
    if checked is None:
        return "Verification date missing"
    age = (today - checked).days
    if age < 0:
        return "Verification date invalid"
    if age > max_age_days:
        return "Re-verification required"
    if _norm(buyer.get("consent_status")) not in {"recorded", "active", "yes"}:
        return "Buyer consent not recorded"
    return "Verified - human review recorded"

def match_buyer_to_deal(buyer, deal, today=None):
    status = buyer_verification_status(buyer, today=today)
    result = {"buyer_id": buyer.get("buyer_id"), "buyer_name": buyer.get("buyer_name"), "verification_status": status, "match_score": 0, "match_status": "Not qualified", "reasons": []}
    if status != "Verified - human review recorded":
        result["reasons"].append("Buyer verification gate not passed")
        return result
    asking = _number(deal.get("asking_price"))
    budget_max = _number(buyer.get("budget_max"))
    if asking is None or budget_max is None or asking > budget_max:
        result["reasons"].append("Asking price exceeds or cannot be checked against buyer budget")
        return result
    score = 25
    result["reasons"].append("Asking price fits buyer budget")
    areas = {_norm(x) for x in buyer.get("areas", []) if _norm(x)}
    area = _norm(deal.get("area"))
    if areas and area and any(a in area or area in a for a in areas):
        score += 25
        result["reasons"].append("Location fits buyer criteria")
    else:
        result["reasons"].append("Location not confirmed as a fit")
    strategies = {_norm(x) for x in buyer.get("strategies", []) if _norm(x)}
    strategy = _norm(deal.get("strategy"))
    if strategies and strategy and strategy in strategies:
        score += 20
        result["reasons"].append("Investment strategy fits")
    else:
        result["reasons"].append("Investment strategy not confirmed as a fit")
    profit = _number(deal.get("estimated_net_profit_before_tax"))
    minimum = _number(buyer.get("minimum_profit_before_tax"))
    if profit is not None and minimum is not None and profit >= minimum:
        score += 20
        result["reasons"].append("Estimated profit meets buyer threshold")
    else:
        result["reasons"].append("Profit threshold missing or not met")
    try:
        comps = int(deal.get("comparable_sales_count") or 0)
    except (TypeError, ValueError):
        comps = 0
    if comps >= 3 and deal.get("valuation_review_status") == "human_reviewed":
        score += 10
        result["reasons"].append("Valuation has at least three comparables and human review")
    else:
        result["reasons"].append("Valuation evidence needs human review")
    result["match_score"] = score
    result["match_status"] = "Strong candidate - human review required" if score >= 80 else ("Possible candidate - human review required" if score >= 50 else "Weak fit - do not present as recommended")
    return result

def rank_buyers_for_deal(buyers, deal, today=None):
    results = [match_buyer_to_deal(buyer, deal, today=today) for buyer in buyers]
    return sorted(results, key=lambda row: (row["verification_status"] == "Verified - human review recorded", row["match_score"]), reverse=True)
