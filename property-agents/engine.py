import os, re, hashlib, time, json
from datetime import datetime, timezone
import requests
from private_seller_agent import discover_private_sellers
from open_properties_agent import discover_open_properties, to_property_lead, last_scan_complete
from motivated_seller_agent import motivation_score, motivation_trend
from planning_opportunity_agent import analyse_planning_candidate, development_profit_scenario

BASE = "https://api.smartsheet.com/2.0"
TOKEN = os.getenv("SMARTSHEET_API_TOKEN", "").strip()
PROPERTY_SHEET = os.getenv("PROPERTY_LEADS_SHEET_ID", "").strip()
FINANCE_SHEET = os.getenv("FINANCE_OPPORTUNITIES_SHEET_ID", "").strip()
DRY_RUN = os.getenv("ATLAS_PROPERTY_AGENT_DRY_RUN", "").strip().lower() in ("1", "true", "yes")

missing = [k for k, v in {
    "SMARTSHEET_API_TOKEN": TOKEN,
    "PROPERTY_LEADS_SHEET_ID": PROPERTY_SHEET,
    "FINANCE_OPPORTUNITIES_SHEET_ID": FINANCE_SHEET,
}.items() if not v]
if missing and not DRY_RUN:
    raise RuntimeError("Missing GitHub Actions secrets: " + ", ".join(missing))
if DRY_RUN:
    print("ATLAS property agent is running in DRY_RUN because required Smartsheet secrets are not configured.")

H = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "smartsheet-integration-source": "SCRIPT,Inspiration Properties UK,Property Agent Engine",
}

def request(method, url, **kwargs):
    for attempt in range(3):
        try:
            r = requests.request(method, url, headers=H, timeout=30, **kwargs)
            if r.status_code in (429, 500, 502, 503, 504):
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
            r.raise_for_status()
            return r
        except requests.RequestException:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("Smartsheet request failed")

def get_sheet(sid):
    return request("GET", f"{BASE}/sheets/{sid}").json()

def put_rows(sid, rows):
    if not rows:
        return None
    return request("PUT", f"{BASE}/sheets/{sid}/rows", json=rows).json()

def cols(sheet):
    return {c["title"]: c["id"] for c in sheet.get("columns", [])}

def values(row, cmap):
    data = {c["columnId"]: c.get("value") for c in row.get("cells", [])}
    return {k: data.get(v) for k, v in cmap.items()}

def norm(x):
    return re.sub(r"\s+", " ", str(x or "")).strip().lower()

def _canonical_url(url):
    raw = str(url or "").strip()
    return raw.split("#", 1)[0].split("?", 1)[0].rstrip("/")

def _identity_key(v):
    explicit = str(v.get("Property Identity Key") or "").strip()
    if explicit:
        return explicit
    lead_id = str(v.get("Lead ID") or "").strip()
    source = str(v.get("Source") or "").strip().lower()
    if lead_id.startswith("OP-") and lead_id[3:]:
        return f"{source}:id:{lead_id[3:]}".lower()
    url = _canonical_url(v.get("Source URL"))
    return f"url:{url}".lower() if url else None

def bmv_discount_pct(estimated_market_value, asking_price):
    """Discount against evidence-backed estimated value; None when inputs are invalid."""
    market = _price(estimated_market_value)
    ask = _price(asking_price)
    if market is None or ask is None or market <= 0 or ask < 0:
        return None
    return round((market - ask) / market * 100, 2)


def bmv_tier(estimated_market_value, asking_price, evidence_count=0):
    """Fail closed: discount tier requires at least three comparable sold transactions."""
    discount = bmv_discount_pct(estimated_market_value, asking_price)
    try:
        count = int(evidence_count or 0)
    except (TypeError, ValueError):
        count = 0
    if discount is None or count < 3:
        return "Review - valuation evidence missing"
    if discount >= 30:
        return "Priority A - 30%+ BMV"
    if discount >= 25:
        return "Priority B - 25-29.9% BMV"
    return "Below BMV threshold"


LONDON_SE_POSTCODE_PREFIXES = (
    "E", "EC", "N", "NW", "SE", "SW", "W", "WC", "AL", "BN", "BR", "CM", "CO", "CR", "CT", "DA", "EN", "GU",
    "HA", "HP", "IG", "KT", "ME", "MK", "OX", "RG", "RH", "RM", "SG", "SL", "SM", "SO", "SS", "TN", "TW", "UB", "WD",
)
DESIGNATED_AREA_TERMS = ("london", "croydon", "bromley", "lewisham", "greenwich", "bexley", "sutton", "kingston upon thames", "enfield", "harrow", "watford", "dartford", "erith", "romford", "grays", "gravesend", "swanley", "sevenoaks", "brighton", "crawley", "east grinstead", "redhill", "reigate", "guildford", "woking", "chatham", "rochester", "maidstone", "canterbury", "surrey", "kent", "sussex", "essex", "hertfordshire", "berkshire", "hampshire", "buckinghamshire", "oxfordshire")

def geography_status(candidate):
    """Conservative area gate; requires postcode or explicit place evidence."""
    postcode = re.sub(r"\s+", "", str(candidate.get("Postcode") or candidate.get("postcode") or "")).upper()
    match = re.match(r"([A-Z]{1,2})", postcode)
    if match:
        return "In designated area" if match.group(1) in LONDON_SE_POSTCODE_PREFIXES else "Outside designated area"
    text = norm(" ".join(str(candidate.get(k) or "") for k in ("Area", "Address", "Property Address", "Notes")))
    if any(term in text for term in DESIGNATED_AREA_TERMS):
        return "In designated area"
    return "Needs location verification"

def _stale_band(days):
    if days is None:
        return "Unknown"
    if days <= 60:
        return "Normal"
    if days <= 90:
        return "Watch"
    if days <= 120:
        return "Stale"
    if days <= 180:
        return "Strong"
    if days <= 270:
        return "Very Strong"
    return "Exceptional"

def route(v):
    opp, lt = norm(v.get("Opportunity Type")), norm(v.get("Lead Type"))
    if opp == "development": return "Development Finance"
    if opp == "buy-to-let": return "Buy-to-Let"
    if opp == "flip/refurb": return "Bridging"
    if opp == "land assembly": return "Land Finance"
    if opp == "jv partnership": return "JV/Equity"
    if "auction" in lt: return "Auction Finance"
    if lt in ("distressed sale", "probate", "repossession"): return "Bridging"
    return None

def score(v):
    s = 0
    if norm(v.get("Lead Type")) in ("distressed sale", "probate", "repossession", "auction", "price reduced"):
        s += 3
    if route(v): s += 2
    if v.get("Asking Price"): s += 1
    if v.get("Source URL") or v.get("Opportunity Evidence"): s += 1
    return "Hot" if s >= 5 else ("Warm" if s >= 3 else "Cold")

def compliance(v):
    if v.get("Do Not Contact") is True: return "Red"
    if norm(v.get("Contact Permission")) == "do not contact": return "Red"
    return "Amber"

def finance_ready(v):
    """Return True only when minimum evidence, listing availability, and compliance gates pass."""
    compliance_status = compliance(v)
    evidence_ready = bool(
        v.get("Source URL") or v.get("Opportunity Evidence")
    ) and _price(v.get("Asking Price")) is not None
    listing_available = str(v.get("Listing Status") or "Unknown") not in {"Removed"}
    return compliance_status != "Red" and evidence_ready and listing_available


def _today():
    return datetime.now(timezone.utc).date().isoformat()

def _scan_id():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def _miss_count(v):
    try:
        return max(0, int(float(str(v.get("Scan Miss Count") or 0))))
    except (TypeError, ValueError):
        return 0

def _price(v):
    try:
        return float(str(v).replace(",", "").replace("£", "").strip())
    except (TypeError, ValueError):
        return None

def _history(v):
    try:
        data = json.loads(str(v.get("Evidence History") or "[]"))
        return data if isinstance(data, list) else []
    except (TypeError, json.JSONDecodeError):
        return []

def _property_relisting_key(v):
    """Use exact street-address + postcode only; never postcode/area alone."""
    address = norm(v.get("Property Address") or v.get("Address") or v.get("Area") or "")
    postcode = norm(v.get("Postcode") or "")
    # Area is accepted only when it actually looks like a street address.
    if not address or not postcode or not re.search(r"\d", address):
        return None
    return f"{address}|{postcode}"


def classify_relisting(previous, current):
    """Classify a reappearance without resetting the listing's historical identity."""
    previous = previous or {}
    current = current or {}
    previous_status = str(previous.get("Listing Status") or "Unknown")
    previous_identity = _identity_key(previous)
    current_identity = _identity_key(current)
    same_listing = bool(previous_identity and current_identity and previous_identity == current_identity)
    same_property = bool(
        _property_relisting_key(previous)
        and _property_relisting_key(current)
        and _property_relisting_key(previous) == _property_relisting_key(current)
    )
    if not (previous_status == "Removed" and (same_listing or same_property)):
        return False, "Unknown"
    previous_url = _canonical_url(previous.get("Source URL"))
    current_url = _canonical_url(current.get("Source URL"))
    if previous_url and current_url and previous_url != current_url:
        return True, "High"
    return True, "Medium"


def _listing_fields(v, previous=None, relisting=False, relisting_confidence="Unknown"):
    previous = previous or {}
    today = _today()
    current = _price(v.get("Asking Price"))
    original = _price(previous.get("Original Asking Price")) or current
    previous_current = _price(previous.get("Current Asking Price"))
    reductions = int(previous.get("Reduction Count") or 0)
    if current is not None and previous_current is not None and current < previous_current:
        reductions += 1
    amount = max(0, original - current) if current is not None and original is not None else None
    pct = round(amount / original * 100, 2) if amount is not None and original else None
    first = previous.get("First Seen") or today
    try:
        days = max(0, (datetime.fromisoformat(today) - datetime.fromisoformat(str(first)[:10])).days)
    except ValueError:
        days = 0
    previous_status = str(previous.get("Listing Status") or "Unknown")
    status = "Relisted" if relisting else ("Active" if previous_status not in {"Removed", "Relisted"} else previous_status)
    previous_url = previous.get("Source URL")
    current_url = v.get("Source URL")
    event = {
        "date": today, "price": current, "url": current_url,
        "source": v.get("Source"), "motivation": v.get("Motivation Score"),
        "status": status, "url_changed": bool(previous_url and current_url and _canonical_url(previous_url) != _canonical_url(current_url)),
    }
    return {
        "First Seen": first, "Last Seen": today, "Days on Market": days,
        "Original Asking Price": original, "Current Asking Price": current,
        "Reduction Amount": amount, "Reduction %": pct, "Reduction Count": reductions,
        "Listing Status": status, "Relisting Flag": bool(relisting),
        "Relisting Confidence": relisting_confidence, "Stale Band": _stale_band(days),
        "Property Identity Key": _identity_key(v),
        "Last Scan ID": _scan_id(),
        "Motivation Trend": int(v.get("Motivation Score") or 0) - int(previous.get("Motivation Score") or 0),
        "Evidence History": json.dumps((_history(previous) + [event])[-20:], separators=(",", ":")),
        "Previous Source URL": previous_url,
    }

def removal_updates(rows, cmap, seen_identities, scan_complete, scan_id):
    """Return provisional removal row updates only after a complete scan."""
    if not scan_complete:
        return []
    updates = []
    for row in rows:
        v = values(row, cmap)
        if not norm(v.get("Source")).startswith("open-properties/"):
            continue
        if str(v.get("Listing Status") or "Unknown") not in {"Active", "Relisted", "Unknown"}:
            continue
        identity = _identity_key(v)
        if identity and identity in seen_identities:
            continue
        misses = _miss_count(v) + 1
        cells = []
        if "Scan Miss Count" in cmap:
            cells.append({"columnId": cmap["Scan Miss Count"], "value": misses})
        if "Last Scan ID" in cmap:
            cells.append({"columnId": cmap["Last Scan ID"], "value": scan_id})
        if misses >= 2:
            if "Listing Status" in cmap:
                cells.append({"columnId": cmap["Listing Status"], "value": "Removed"})
            if "Removal Evidence" in cmap:
                cells.append({"columnId": cmap["Removal Evidence"], "value":
                    "Not observed in two consecutive normalized open-market discovery scans; provisional removal only, not evidence of seller financial distress."})
        if cells:
            updates.append({"id": row["id"], "cells": cells})
    return updates

def _write_scan_report(scan_id, discovered_count, open_market_count, open_market_scan_complete, status, error=None):
    payload = {
        "scan_id": scan_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "discovered_candidates": discovered_count,
        "open_market_candidates": open_market_count,
        "open_market_scan_complete": bool(open_market_scan_complete),
        "status": status,
        "error": error,
    }
    path = os.getenv("ATLAS_SCAN_REPORT_PATH", "property-agent-scan-report.json")
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
    except OSError as exc:
        print(f"Warning: unable to write scan report: {exc}")

def run():
    scan_id = _scan_id()
    try:
        if DRY_RUN:
            print("Dry-run health check passed. No Smartsheet reads or writes performed.")
            _write_scan_report(_scan_id(), 0, 0, False, "DRY_RUN")
            return
    
        # Public private-seller discovery runs before qualification. It only creates
        # candidate rows; it never contacts sellers or collects private contact data.
        discovered = discover_private_sellers()
        open_market = discover_open_properties()
        open_market_scan_complete = last_scan_complete()
        scan_id = _scan_id()
        discovered.extend(to_property_lead(item) for item in open_market)
        # Planning precedent is an enrichment signal only. Failures are recorded on
        # the candidate and do not imply that no applications exist.
        planning_processed = 0
        for candidate in discovered:
            if planning_processed >= int(os.getenv("ATLAS_PLANNING_MAX_PROPERTIES", "25")):
                candidate.setdefault("Planning Review Status", "Deferred by per-run planning scan limit")
                continue
            try:
                planning = analyse_planning_candidate(candidate)
                candidate.update({k: v for k, v in planning.items() if k != "Planning Evidence"})
                notes = candidate.get("Notes")
                try:
                    notes_obj = json.loads(notes) if isinstance(notes, str) else {}
                    if not isinstance(notes_obj, dict): notes_obj = {}
                except (TypeError, json.JSONDecodeError):
                    notes_obj = {"previous_notes": str(notes)[:1000]} if notes else {}
                if planning.get("Planning Evidence"):
                    notes_obj["planning_evidence"] = planning["Planning Evidence"]
                profit = development_profit_scenario(
                    candidate.get("Asking Price"),
                    candidate.get("Estimated Completed Value") or candidate.get("Post-Works Market Value") or candidate.get("Estimated Market Value After Works"),
                    candidate.get("Estimated Works Cost") or candidate.get("Works Cost"),
                    candidate.get("Professional Fees"),
                    candidate.get("Finance and Holding Costs"),
                    candidate.get("Purchase Costs"),
                    candidate.get("Selling Costs"),
                )
                notes_obj["development_profit_scenario"] = profit
                candidate["Profit Estimate Status"] = profit.get("status")
                candidate["Estimated Net Profit Before Tax"] = profit.get("estimated_net_profit_before_tax")
                candidate["Estimated Completed Value"] = profit.get("estimated_completed_value")
                candidate["Estimated Total Project Cost"] = profit.get("estimated_total_cost")
                candidate["Notes"] = json.dumps(notes_obj, separators=(",", ":"))[:4000]
                if planning.get("Planning Opportunity Summary"):
                    existing_evidence = str(candidate.get("Opportunity Evidence") or "").strip()
                    profit_text = (
                        f" Illustrative estimated net profit before tax: £{profit['estimated_net_profit_before_tax']:,.0f}."
                        if profit.get("estimated_net_profit_before_tax") is not None
                        else " Profit not estimated: completed value and all project cost inputs must be evidenced first."
                    )
                    candidate["Opportunity Evidence"] = (existing_evidence + " Planning scan: " + planning["Planning Opportunity Summary"] + profit_text).strip()[:4000]
                planning_processed += 1
            except Exception as planning_exc:
                candidate["Planning Review Status"] = "Planning API error - council portal review required"
                candidate["Planning Opportunity Summary"] = f"Planning scan failed ({type(planning_exc).__name__}); this is not evidence that no applications exist."
                planning_processed += 1
        ps, fs = get_sheet(PROPERTY_SHEET), get_sheet(FINANCE_SHEET)
        pc, fc = cols(ps), cols(fs)
    
        # Fail closed on schema drift. Motivation Score is numeric; Lead Score is
        # a controlled Hot/Warm/Cold picklist and must never receive 0-100.
        required_property = {
            "Lead ID", "Lead Type", "Opportunity Type", "Area", "Asking Price",
            "Lead Score", "Motivation Score", "Source URL", "Opportunity Evidence",
        }
        required_finance = {"Finance Lead ID", "Lead Type", "Lead Score", "Compliance Status", "Finance Status"}
        missing_property = required_property - set(pc)
        missing_finance = required_finance - set(fc)
        if missing_property:
            raise RuntimeError("Property Leads sheet is missing columns: " + ", ".join(sorted(missing_property)))
        if missing_finance:
            raise RuntimeError("Finance Opportunities sheet is missing columns: " + ", ".join(sorted(missing_finance)))
    
        valid_lead_types = {
            "Off-Market", "Private Seller", "Distressed Sale", "Probate", "Auction",
            "Developer Site", "Price Reduced", "Repossession", "Open Market Listing",
        }
        valid_opportunity_types = {
            "Buy-to-Let", "Development", "JV Partnership", "Flip/Refurb",
            "Portfolio Acquisition", "Land Assembly", "Private Sale", "Property Acquisition",
        }
        for candidate in discovered:
            if candidate.get("Lead Type") not in valid_lead_types:
                candidate["Lead Type"] = "Open Market Listing"
            if candidate.get("Opportunity Type") not in valid_opportunity_types:
                candidate["Opportunity Type"] = "Property Acquisition"
    
        existing_property = {}
        existing_property_identity = {}
        for row in ps.get("rows", []):
            v = values(row, pc)
            for key in (norm(v.get("Lead ID")), norm(v.get("Source URL"))):
                if key:
                    existing_property[key] = row
            identity = _identity_key(v)
            if identity:
                existing_property_identity[identity] = row
    
        new_property_rows = []
        property_updates = []
        discovered = [candidate for candidate in discovered if geography_status(candidate) != "Outside designated area"]
        for candidate in discovered:
            candidate["Geography Review Status"] = geography_status(candidate)
            if candidate["Geography Review Status"] == "Needs location verification":
                candidate["Lead Score"] = "Cold"
                candidate["Opportunity Evidence"] = (str(candidate.get("Opportunity Evidence") or "") + " Geography not verified; do not shortlist until location is confirmed.").strip()
            m = motivation_score(candidate)
            candidate["Motivation Score"] = m
            candidate["Lead Score"] = "Hot" if m >= 70 else ("Warm" if m >= 45 else "Cold")
            candidate["Last Scan ID"] = scan_id
            candidate["Scan Miss Count"] = 0
            existing_row = (
                existing_property.get(norm(candidate.get("Lead ID")))
                or existing_property.get(norm(candidate.get("Source URL")))
                or existing_property_identity.get(_identity_key(candidate))
            )
            previous = values(existing_row, pc) if existing_row else None
            genuine_relist, relist_confidence = classify_relisting(previous, candidate) if existing_row else (False, "Unknown")
            if not existing_row and candidate.get("Source", "").startswith("open-properties/"):
                removed_matches = [
                    values(row, pc) for row in ps.get("rows", [])
                    if str(values(row, pc).get("Listing Status") or "") == "Removed"
                    and _property_relisting_key(values(row, pc))
                    and _property_relisting_key(values(row, pc)) == _property_relisting_key(candidate)
                ]
                if len(removed_matches) == 1:
                    previous = removed_matches[0]
                    genuine_relist, relist_confidence = classify_relisting(previous, candidate)
                    existing_row = next(
                        row for row in ps.get("rows", [])
                        if values(row, pc) == previous
                    )
                    candidate["Property Identity Key"] = previous.get("Property Identity Key") or _identity_key(previous)
            historical = _listing_fields(candidate, previous, genuine_relist, relist_confidence)
            candidate.update(historical)
            candidate["Motivation Trend"] = motivation_trend(_history(previous), m)
            if existing_row:
                discovery_fields = {
                    "Lead Type", "Opportunity Type", "Area", "Asking Price", "Lead Score",
                    "Source", "Source URL", "Opportunity Evidence", "Notes", "Motivation Score",
                    "Listing Status", "Relisting Flag", "Relisting Confidence", "Stale Band",
                    "Property Identity Key", "First Seen", "Last Seen", "Days on Market",
                    "Scan Miss Count", "Last Scan ID", "Removal Evidence", "Portal Listing ID", "Postcode",
                    "Original Asking Price", "Current Asking Price", "Reduction Amount",
                    "Reduction %", "Reduction Count", "Motivation Trend", "Evidence History",
                    "Previous Source URL", "Planning Review Status", "Planning Opportunity Summary",
                    "Planning Precedent Count", "Planning Same-Road Count", "Planning Potentially Approved Count", "Planning Search URL",
                    "Profit Estimate Status", "Estimated Net Profit Before Tax", "Estimated Completed Value", "Estimated Total Project Cost", "Geography Review Status",
                }
                cells = [{"columnId": pc[name], "value": value} for name, value in candidate.items()
                         if name in pc and name in discovery_fields and value is not None]
                if cells:
                    property_updates.append({"id": existing_row["id"], "cells": cells})
                continue
            cells = []
            for name, value in candidate.items():
                if name in pc and value is not None:
                    cells.append({"columnId": pc[name], "value": value})
            if cells:
                new_property_rows.append({"toBottom": True, "cells": cells})
    
        # Conservative removal gate: only normalized open-market rows qualify,
        # and two consecutive misses are required before a provisional Removed status.
        seen_identities = {_identity_key(x) for x in discovered if _identity_key(x)}
        miss_updates = removal_updates(ps.get("rows", []), pc, seen_identities, open_market_scan_complete, scan_id)
        if open_market_scan_complete and miss_updates:
            property_updates.extend(miss_updates)
    
        if new_property_rows:
            add_result = put_rows(PROPERTY_SHEET, new_property_rows)
            print(f"Property discovery found {len(discovered)} candidates ({len(open_market)} normalized open-market listings); added {len(new_property_rows)} new Property Leads.")
            if property_updates:
                update_result = put_rows(PROPERTY_SHEET, property_updates)
                print(f"Historical property updates applied: {len(property_updates)} rows; resultCode={update_result.get('resultCode')}")
    
            if add_result:
                print(f"Property Leads discovery resultCode={add_result.get('resultCode')} message={add_result.get('message')}")
        else:
            if property_updates:
                update_result = put_rows(PROPERTY_SHEET, property_updates)
                print(f"Historical property updates applied: {len(property_updates)} rows; resultCode={update_result.get('resultCode')}")
            print(f"Property discovery found {len(discovered)} candidates ({len(open_market)} normalized open-market listings); no new Property Leads required.")
    
        existing = {}
        for row in fs.get("rows", []):
            v = values(row, fc)
            fid = norm(v.get("Finance Lead ID"))
            if fid:
                existing[fid] = row
    
        updates, seen = [], set()
        for row in ps.get("rows", []):
            v = values(row, pc)
            lid = str(v.get("Lead ID") or "").strip()
            rt = route(v)
            if not lid or not rt:
                continue
    
            key = hashlib.sha256("|".join(
                norm(v.get(k)) for k in ("Area", "Asking Price", "Seller Name", "Source URL")
            ).encode()).hexdigest()[:16]
            if key in seen:
                continue
            seen.add(key)
    
            target = existing.get(norm("FIN-" + lid))
            if not target:
                continue
    
            compliance_status = compliance(v)
            finance_gate = finance_ready(v)
            note = (
                "Automated route classification: " + rt + ". "
                + ("Minimum evidence gate passed; case remains subject to human verification."
                   if finance_gate else
                   "Minimum finance evidence gate NOT passed; case remains for evidence review.")
                + " No personalised regulated finance advice, referral or outreach performed."
            )
            mapped = {
                "Lead Type": rt,
                "Lead Score": score(v) if finance_gate else "Cold",
                "Compliance Status": compliance_status,
                "Best Route": "Potential " + rt if finance_gate else "Evidence Review Required",
                "Opportunity Action": (
                    "Verify borrower/property facts, finance requirement and exit before referral"
                    if finance_gate else
                    "Obtain and verify minimum evidence before finance qualification"
                ),
                "Finance Status": "Qualifying" if finance_gate else "Review",
                "Next Action": (
                    "Collect missing case facts; compliance gate before referral"
                    if finance_gate else
                    "Verify source evidence, asking price and listing status"
                ),
                "Notes": note,
            }
            cells = [{"columnId": fc[name], "value": val} for name, val in mapped.items() if name in fc]
            updates.append({"id": target["id"], "cells": cells})
    
        result = put_rows(FINANCE_SHEET, updates)
        _write_scan_report(scan_id, len(discovered), len(open_market), open_market_scan_complete, "SUCCESS")
        print(f"Property agent engine processed {len(updates)} finance records.")
        if result:
            print(f"Smartsheet update resultCode={result.get('resultCode')} message={result.get('message')}")
    
    except Exception as exc:
        _write_scan_report(
            scan_id,
            0,
            0,
            False,
            "FAILED",
            error=f"{type(exc).__name__}: {exc}",
        )
        raise

if __name__ == "__main__":
    run()
