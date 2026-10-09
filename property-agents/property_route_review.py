"""Build an offline contract-route review queue from property candidates."""
from __future__ import annotations
import html, json, os
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

def _prioritise_record(record: dict[str, Any]) -> dict[str, Any]:
    """Rank only evidence completeness and arithmetic signals, not investment quality."""
    sourcing = record.get("routes", {}).get("property_sourcing", {})
    assignment = record.get("routes", {}).get("contract_assignment", {})
    risks = sourcing.get("risks", []) + assignment.get("risks", [])
    blockers = sourcing.get("blockers", []) + assignment.get("blockers", [])
    discount = record.get("market_value_discount_pct")
    comps_status = record.get("valuation_status")
    score = 0
    reasons = []
    if record.get("source_url", "").startswith("https://"):
        score += 10
    else:
        reasons.append("No valid HTTPS source link")
    if isinstance(discount, (int, float)) and comps_status == "supported_by_minimum_count_only_not_valued_by_this_module":
        score += 20
        reasons.append("Entered price/value and minimum comparable count present; verify source comparables independently")
    else:
        reasons.append("Market value/comparable evidence incomplete")
    if sourcing.get("gross_fee_estimate") is not None:
        score += 5
    else:
        reasons.append("Sourcing fee not entered")
    if assignment.get("gross_fee_estimate") is not None and assignment.get("blockers"):
        reasons.append("Assignment route still has legal/compliance blockers")
    if blockers:
        reasons.append(f"{len(blockers)} recorded route blocker(s)")
    if risks:
        reasons.append(f"{len(risks)} recorded route risk(s)")
    # Priority is explicitly evidence-work order, never a buy/offer recommendation.
    band = "Review evidence first" if score >= 25 else ("Needs evidence" if score >= 10 else "Incomplete record")
    return {"review_priority_score": score, "review_priority_band": band, "priority_reasons": reasons}


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
        records[-1].update(_prioritise_record(records[-1]))
    return {
        "schema_version": 1, "scan_id": scan_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "offline_human_review_queue", "candidate_count": len(records),
        "priority_meaning": "Evidence-review order only; not investment advice, a valuation, or approval to transact.",
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
    write_review_html(report)
    return report


def render_review_html(report: dict[str, Any]) -> str:
    """Render a self-contained, escaped HTML summary for human review."""
    def esc(value: Any) -> str:
        return html.escape("" if value is None else str(value), quote=True)

    rows = []
    for record in report.get("records", []):
        route_cells = []
        for key, label in (("property_sourcing", "Sourcing"), ("contract_assignment", "Assignment")):
            route = record.get("routes", {}).get(key, {})
            blockers = route.get("blockers", [])
            risks = route.get("risks", [])
            items = "".join(f"<li>{esc(item)}</li>" for item in blockers + risks)
            fee = route.get("gross_fee_estimate")
            fee_text = f"£{fee:,.2f}" if isinstance(fee, (int, float)) else "Not provided"
            route_cells.append(
                f"<td><strong>{esc(label)}: {esc(route.get('status'))}</strong>"
                f"<p>Gross fee input: {esc(fee_text)}</p>"
                f"<details><summary>{len(blockers)} blockers / {len(risks)} risks</summary>"
                f"<ul>{items or '<li>No recorded risks; independent review still required.</li>'}</ul></details></td>"
            )
        source = record.get("source_url")
        source_link = f'<a href="{esc(source)}" rel="noreferrer">{esc(source)}</a>' if isinstance(source, str) and source.startswith("https://") else "Missing/invalid source URL"
        discount = record.get("market_value_discount_pct")
        discount_text = f"{discount:.2f}%" if isinstance(discount, (int, float)) else "Not calculated"
        rows.append(
            "<tr>"
            f"<td>{esc(record.get('deal_id'))}<br>{esc(record.get('area'))}</td>"
            f"<td>{esc(record.get('lead_type'))}<br>{esc(record.get('opportunity_type'))}</td>"
            f"<td>{esc(record.get('asking_price'))}<br>Discount: {esc(discount_text)}<br>{esc(record.get('valuation_status'))}</td>"
            f"<td>{source_link}</td>{''.join(route_cells)}"
            "</tr>"
        )
    body = "".join(rows) or '<tr><td colspan="6">No candidates in this run. An empty queue is not evidence that no opportunities exist.</td></tr>'
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Inspiration Properties — Contract Route Review</title>
<style>
body{{font:16px/1.5 system-ui,sans-serif;margin:1rem;color:#172033}}h1{{font-size:1.5rem}}
.notice{{padding:1rem;border:2px solid #9b2c2c;border-radius:.5rem;background:#fff7f7}}
.wrap{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;min-width:1100px}}th,td{{border:1px solid #ccd2dc;padding:.65rem;vertical-align:top;text-align:left}}th{{background:#eef2f7}}td p{{margin:.25rem 0}}small,.muted{{color:#475569}}details{{max-width:30rem}}li{{margin:.35rem 0}}
</style></head><body>
<h1>Inspiration Properties UK — Contract Route Review</h1>
<p>Scan: <strong>{esc(report.get('scan_id'))}</strong> · Generated UTC: {esc(report.get('generated_at_utc'))} · Candidates: {len(report.get('records', []))}</p>
<div class="notice"><strong>REVIEW ONLY — NOT APPROVED TO TRANSACT.</strong>
No seller/buyer contact, offer, contract, payment, referral, publishing or Smartsheet write is performed by this report.
All route outcomes require human review, applicable compliance checks and independent solicitor review. Missing information is not assumed safe.</div>
<p class="muted">Discount is only a preliminary calculation from entered asking price and estimated market value. It is not a valuation; comparables and source evidence require independent verification.</p>
<div class="wrap"><table><thead><tr><th>Deal</th><th>Type</th><th>Price / discount</th><th>Source evidence</th><th>Property sourcing</th><th>Contract assignment</th></tr></thead><tbody>{body}</tbody></table></div>
</body></html>"""


def write_review_html(report: dict[str, Any], path: str | None = None) -> str:
    destination = path or os.getenv("ATLAS_ROUTE_REVIEW_HTML_PATH", "property-route-review-queue.html")
    with open(destination, "w", encoding="utf-8") as fh:
        fh.write(render_review_html(report))
    return destination
