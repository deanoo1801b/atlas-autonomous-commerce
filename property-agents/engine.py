import os, re, hashlib, time, json
from datetime import datetime, timezone
import requests
from private_seller_agent import discover_private_sellers
from open_properties_agent import discover_open_properties, to_property_lead, last_scan_complete
from motivated_seller_agent import motivation_score

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

def _write_scan_report(scan_id, discovered_count, open_market_count, open_market_scan_complete, status, error=None):\n    payload = {\n        "scan_id": scan_id,\n        "timestamp_utc": datetime.now(timezone.utc).isoformat(),\n        "discovered_candidates": discovered_count,\n        "open_market_candidates": open_market_count,\n        "open_market_scan_complete": bool(open_market_scan_complete),\n        "status": status,\n        "error": error,\n    }\n    path = os.getenv("ATLAS_SCAN_REPORT_PATH", "property-agent-scan-report.json")\n    try:\n        with open(path, "w", encoding="utf-8") as fh:\n            json.dump(payload, fh, indent=2)\n    except OSError as exc:\n        print(f"Warning: unable to write scan report: {exc}")\n\ndef run():
    if DRY_RUN:
        print("Dry-run health check passed. No Smartsheet reads or writes performed.")
        return

    # Public private-seller discovery runs before qualification. It only creates
    # candidate rows; it never contacts sellers or collects private contact data.
    discovered = discover_private_sellers()
    open_market = discover_open_properties()
    open_market_scan_complete = last_scan_complete()
    scan_id = _scan_id()
    discovered.extend(to_property_lead(item) for item in open_market)
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
    for candidate in discovered:
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
        previous_identity = _identity_key(previous) if previous else None
        candidate_identity = _identity_key(candidate)
        same_identity = bool(existing_row and candidate_identity and previous_identity and candidate_identity == previous_identity)
        url_changed = bool(existing_row and norm(candidate.get("Source URL")) != norm((previous or {}).get("Source URL")))
        previously_removed = str((previous or {}).get("Listing Status") or "") == "Removed"
        genuine_relist = bool(same_identity and previously_removed)
        relist_confidence = "High" if (genuine_relist and url_changed) else ("Medium" if genuine_relist else "Unknown")
        historical = _listing_fields(candidate, previous, genuine_relist, relist_confidence)
        candidate.update(historical)
        if existing_row:
            discovery_fields = {
                "Lead Type", "Opportunity Type", "Area", "Asking Price", "Lead Score",
                "Source", "Source URL", "Opportunity Evidence", "Notes", "Motivation Score",
                "Listing Status", "Relisting Flag", "Relisting Confidence", "Stale Band",
                "Property Identity Key", "First Seen", "Last Seen", "Days on Market",
                "Scan Miss Count", "Last Scan ID", "Removal Evidence", "Portal Listing ID", "Postcode",
                "Original Asking Price", "Current Asking Price", "Reduction Amount",
                "Reduction %", "Reduction Count", "Motivation Trend", "Evidence History",
                "Previous Source URL",
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
    miss_updates = []
    for row in ps.get("rows", []):
        v = values(row, pc)
        if not norm(v.get("Source")).startswith("open-properties/"):
            continue
        if str(v.get("Listing Status") or "Unknown") not in {"Active", "Relisted", "Unknown"}:
            continue
        identity = _identity_key(v)
        if identity and identity in seen_identities:
            continue
        misses = _miss_count(v) + 1
        cells = []
        if "Scan Miss Count" in pc:
            cells.append({"columnId": pc["Scan Miss Count"], "value": misses})
        if "Last Scan ID" in pc:
            cells.append({"columnId": pc["Last Scan ID"], "value": scan_id})
        if misses >= 2:
            if "Listing Status" in pc:
                cells.append({"columnId": pc["Listing Status"], "value": "Removed"})
            if "Removal Evidence" in pc:
                cells.append({"columnId": pc["Removal Evidence"], "value":
                    "Not observed in two consecutive normalized open-market discovery scans; provisional removal only, not evidence of seller financial distress."})
        if cells:
            miss_updates.append({"id": row["id"], "cells": cells})
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

        note = (
            "Automated qualification: route classified as " + rt +
            ". Evidence/borrower facts remain subject to verification. "
            "No personalised regulated finance advice, referral or outreach performed."
        )
        mapped = {
            "Lead Type": rt,
            "Lead Score": score(v),
            "Compliance Status": compliance(v),
            "Best Route": "Potential " + rt,
            "Opportunity Action": "Verify evidence, borrower/property facts, finance requirement and exit before referral",
            "Finance Status": "Qualifying",
            "Next Action": "Collect missing case facts; compliance gate before referral",
            "Notes": note,
        }
        cells = [{"columnId": fc[name], "value": val} for name, val in mapped.items() if name in fc]
        updates.append({"id": target["id"], "cells": cells})

    result = put_rows(FINANCE_SHEET, updates)
    _write_scan_report(scan_id, len(discovered), len(open_market), open_market_scan_complete, "SUCCESS")\n    print(f"Property agent engine processed {len(updates)} finance records.")
    if result:
        print(f"Smartsheet update resultCode={result.get('resultCode')} message={result.get('message')}")

if __name__ == "__main__":
    run()
