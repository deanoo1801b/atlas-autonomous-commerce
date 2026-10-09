"""Build an offline contract-route review queue from property candidates."""
from __future__ import annotations
import json, os
from datetime import datetime, timezone
from typing import Any
from contract_route_comparator import compare_routes

def candidate_to_route_input(candidate: dict[str, Any]) -> dict[str, Any]:
    """Map available fields only; do not invent valuation, comparable or legal evidence."""
    return {
        "deal_id": candidate.get("Lead ID") or candidate.get("Property Identity Key") or "UNASSIGNED",
        "source_evidence_url": candidate.get("Source URL"),
        "asking_price": candidate.get("Asking Price") or candidate.get("Current Asking Price"),
        "estimated_market_value": candidate.get("Estimated Market Value") or candidate.get("Estimated Completed Value") or candidate.get("Post-Works Market Value") or candidate.get("Estimated Market Value After Works"),
        "comparable_sales_count": candidate.get("Comparable Sales Count") or candidate.get("Comparable Sold Sales Count") or 0,
        "sourcing_fee": candidate.get("Proposed Sourcing Fee"),
        "assignment_fee": candidate.get("Proposed Assignment Fee"),
        "contract_purchase_price": candidate.get("Contract Purchase Price"),
        "deposit_at_risk": candidate.get("Deposit at Risk"),
        "assignment_permitted": candidate.get("Assignment Permitted"),
        "seller_consent_required": candidate.get("Seller Consent Required"),
        "seller_consent_obtained": candidate.get("Seller Consent Obtained"),
        "solicitor_reviewed": candidate.get("Solicitor Review Complete"),
        "title_checked": candidate.get("Title Checked"),
        "buyer_identified": candidate.get("Buyer Identified"),
        "buyer_funding_reviewed": candidate.get("Buyer Funding Reviewed"),
        "fee_disclosed": candidate.get("Fee Disclosure Complete"),
        "aml_status": candidate.get("AML Status"),
        "redress_status": candidate.get("Property Redress Status"),
        "marketing_authority_confirmed": candidate.get("Marketing Authority Confirmed"),
        "human_reviewed": candidate.get("Human Deal Review Complete"),
    }

def build_review_queue(candidates: list[dict[str, Any]], scan_id: str = "UNASSIGNED") -> dict[str, Any]:
    records = []
    for candidate in candidates:
        result = compare_routes(candidate_to_route_input(candidate))
        records.append({
            "deal_id": result["deal_id"],
            "area": candidate.get("Area") or candidate.get("Property Address") or candidate.get("Address"),
            "lead_type": candidate.get("Lead Type"),
            "opportunity_type": candidate.get("Opportunity Type"),
            "source_url": candidate.get("Source URL"),
            "asking_price": candidate.get("Asking Price"),
            "overall_status": result["overall_status"],
            "market_value_discount_pct": result["market_value_discount_pct"],
            "valuation_status": result["valuation_status"],
            "routes": result["routes"],
            "automatic_commitment": False, "automatic_contacting": False,
            "automatic_offer": False, "automatic_contracting": False,
            "automatic_payment": False,
        })
    return {
        "schema_version": 1, "scan_id": scan_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "offline_human_review_queue", "candidate_count": len(records),
        "records": records,
        "guardrails": {
            "writes_to_smartsheet": False, "automatic_contacting": False,
            "automatic_offers": False, "automatic_contracting": False,
            "automatic_payments": False, "automatic_referrals": False,
            "automatic_publishing": False,
            "approval": "Human review, compliance checks and independent solicitor review required.",
        },
    }

def write_review_queue(candidates: list[dict[str, Any]], scan_id: str, path: str | None = None) -> dict[str, Any]:
    report = build_review_queue(candidates, scan_id)
    destination = path or os.getenv("ATLAS_ROUTE_REVIEW_REPORT_PATH", "property-route-review-queue.json")
    with open(destination, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return report
