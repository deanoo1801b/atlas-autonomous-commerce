"""Compare UK property contract assignment and sourcing routes without commitments.

This module performs offline triage only. It is not legal advice and never
authorises outreach, offers, signing, payments, referrals or publishing.
"""
from __future__ import annotations

from typing import Any


def _money(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        number = float(str(value).replace(",", "").replace("£", "").strip())
    except (TypeError, ValueError):
        return None
    return number if number >= 0 else None


def _yes(value: Any) -> bool:
    return value is True or str(value).strip().lower() in {"yes", "true", "verified", "confirmed"}


def compare_routes(deal: dict[str, Any]) -> dict[str, Any]:
    """Return route economics and risk gates for a single deal.

    Expected optional fields:
      asking_price, estimated_market_value, comparable_sales_count,
      sourcing_fee, assignment_fee, contract_purchase_price, deposit_at_risk,
      assignment_permitted, seller_consent_required, seller_consent_obtained,
      solicitor_reviewed, title_checked, buyer_identified, buyer_funding_reviewed,
      fee_disclosed, aml_status, redress_status, marketing_authority_confirmed,
      completion_date, source_evidence_url, human_reviewed.
    Missing information is flagged; it is never silently assumed to be safe.
    """
    risks: list[str] = []
    blockers: list[str] = []
    evidence_url = str(deal.get("source_evidence_url") or "").strip()
    if not evidence_url.startswith("https://"):
        risks.append("Missing HTTPS source evidence; independently verify the property and source.")
    try:
        comparable_count = int(deal.get("comparable_sales_count") or 0)
    except (TypeError, ValueError):
        comparable_count = 0
    if comparable_count < 3:
        risks.append("Fewer than three comparable sold transactions: valuation/discount remains unsubstantiated.")

    ask = _money(deal.get("asking_price"))
    market = _money(deal.get("estimated_market_value"))
    discount = round((market - ask) / market * 100, 2) if market and market > 0 and ask is not None else None
    if discount is None:
        risks.append("Asking price or evidence-backed market value is missing; BMV discount not calculated.")

    # Common commercial/regulatory checks apply to any paid sourcing activity.
    if str(deal.get("aml_status") or "").strip().lower() not in {"confirmed_not_required", "registered", "reviewed_as_compliant"}:
        blockers.append("AML supervision/status has not been confirmed for this proposed activity.")
    if str(deal.get("redress_status") or "").strip().lower() not in {"member", "confirmed_not_required", "reviewed_as_compliant"}:
        blockers.append("Property redress-scheme applicability/membership has not been confirmed.")
    if not _yes(deal.get("fee_disclosed")):
        blockers.append("Fee and remuneration disclosure is not confirmed.")
    if not _yes(deal.get("marketing_authority_confirmed")):
        blockers.append("Authority and lawful basis to market/share this specific opportunity are not confirmed.")

    sourcing_fee = _money(deal.get("sourcing_fee"))
    sourcing = {
        "route": "property_sourcing",
        "gross_fee_estimate": sourcing_fee,
        "net_profit_estimate": None,
        "status": "REVIEW",
        "risks": [],
        "blockers": list(blockers),
    }
    if sourcing_fee is None:
        sourcing["risks"].append("Sourcing fee not specified; no fee economics calculated.")
    if not _yes(deal.get("buyer_identified")):
        sourcing["risks"].append("No buyer match recorded; this is not proof of buyer demand.")
    if not _yes(deal.get("buyer_funding_reviewed")):
        sourcing["risks"].append("Buyer purchasing capacity has not been human-reviewed.")
    if not _yes(deal.get("human_reviewed")):
        sourcing["risks"].append("Human deal review is outstanding.")
    sourcing["risks"].extend(risks)
    if not sourcing["blockers"] and _yes(deal.get("human_reviewed")) and _yes(deal.get("buyer_identified")) and _yes(deal.get("buyer_funding_reviewed")) and sourcing_fee is not None:
        sourcing["status"] = "ELIGIBLE_FOR_SOLICITOR/COMPLIANCE_REVIEW"
    else:
        sourcing["status"] = "HOLD_FOR_REVIEW"

    assignment_fee = _money(deal.get("assignment_fee"))
    contract_price = _money(deal.get("contract_purchase_price"))
    deposit = _money(deal.get("deposit_at_risk"))
    assignment = {
        "route": "contract_assignment",
        "gross_fee_estimate": assignment_fee,
        "net_profit_estimate": None,
        "status": "HOLD_FOR_LEGAL_REVIEW",
        "risks": [],
        "blockers": list(blockers),
    }
    if assignment_fee is None:
        assignment["risks"].append("Assignment fee not specified; no fee economics calculated.")
    if contract_price is None:
        assignment["risks"].append("Contract purchase price is missing.")
    if deposit is None:
        assignment["risks"].append("Deposit/commitment exposure is unknown.")
    else:
        assignment["risks"].append(f"Potential deposit/commitment exposure entered: £{deposit:,.2f}; confirm actual liability with solicitor.")
    if not _yes(deal.get("assignment_permitted")):
        assignment["blockers"].append("Contract assignment rights have not been confirmed by a solicitor.")
    if _yes(deal.get("seller_consent_required")) and not _yes(deal.get("seller_consent_obtained")):
        assignment["blockers"].append("Required seller consent is not recorded.")
    if not _yes(deal.get("solicitor_reviewed")):
        assignment["blockers"].append("Independent solicitor has not reviewed the contract and proposed assignment.")
    if not _yes(deal.get("title_checked")):
        assignment["risks"].append("Title, ownership, restrictions and existing charges have not been verified.")
    if not _yes(deal.get("buyer_identified")):
        assignment["risks"].append("No end buyer recorded; contract completion risk remains.")
    if not _yes(deal.get("buyer_funding_reviewed")):
        assignment["risks"].append("End-buyer funding has not been human-reviewed.")
    if not _yes(deal.get("human_reviewed")):
        assignment["risks"].append("Human deal review is outstanding.")
    assignment["risks"].extend(risks)
    if not assignment["blockers"] and _yes(deal.get("human_reviewed")) and _yes(deal.get("buyer_identified")) and _yes(deal.get("buyer_funding_reviewed")) and _yes(deal.get("title_checked")) and assignment_fee is not None and contract_price is not None:
        assignment["status"] = "ELIGIBLE_FOR_SOLICITOR/COMPLIANCE_REVIEW"
    else:
        assignment["status"] = "HOLD_FOR_LEGAL_REVIEW"

    # Neither route is ever auto-approved, even when all recorded checks are green.
    return {
        "comparison_version": 1,
        "deal_id": str(deal.get("deal_id") or "UNASSIGNED"),
        "market_value_discount_pct": discount,
        "valuation_status": "supported_by_minimum_count_only_not_valued_by_this_module" if comparable_count >= 3 and discount is not None else "review_required",
        "routes": {"property_sourcing": sourcing, "contract_assignment": assignment},
        "overall_status": "HUMAN_AND_SOLICITOR_REVIEW_REQUIRED",
        "automatic_commitment": False,
        "automatic_contacting": False,
        "automatic_offer": False,
        "automatic_contracting": False,
        "automatic_payment": False,
        "legal_advice": False,
    }
