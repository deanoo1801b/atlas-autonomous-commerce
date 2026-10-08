import os, re, hashlib, time
import requests
from private_seller_agent import discover_private_sellers

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

def run():
    if DRY_RUN:
        print("Dry-run health check passed. No Smartsheet reads or writes performed.")
        return

    # Public private-seller discovery runs before qualification. It only creates
    # candidate rows; it never contacts sellers or collects private contact data.
    discovered = discover_private_sellers()
    ps, fs = get_sheet(PROPERTY_SHEET), get_sheet(FINANCE_SHEET)
    pc, fc = cols(ps), cols(fs)

    existing_property = {}
    for row in ps.get("rows", []):
        v = values(row, pc)
        for key in (norm(v.get("Lead ID")), norm(v.get("Source URL"))):
            if key:
                existing_property[key] = row

    new_property_rows = []
    for candidate in discovered:
        if norm(candidate.get("Lead ID")) in existing_property or norm(candidate.get("Source URL")) in existing_property:
            continue
        cells = []
        for name, value in candidate.items():
            if name in pc and value is not None:
                cells.append({"columnId": pc[name], "value": value})
        if cells:
            new_property_rows.append({"toBottom": True, "cells": cells})

    if new_property_rows:
        add_result = put_rows(PROPERTY_SHEET, new_property_rows)
        print(f"Private seller discovery found {len(discovered)} candidates; added {len(new_property_rows)} new Property Leads.")
        if add_result:
            print(f"Property Leads discovery resultCode={add_result.get('resultCode')} message={add_result.get('message')}")
    else:
        print(f"Private seller discovery found {len(discovered)} candidates; no new Property Leads required.")

    required_property = {"Lead ID", "Lead Type", "Opportunity Type", "Area", "Asking Price"}
    required_finance = {"Finance Lead ID", "Lead Type", "Lead Score", "Compliance Status", "Finance Status"}
    missing_property = required_property - set(pc)
    missing_finance = required_finance - set(fc)
    if missing_property:
        raise RuntimeError("Property Leads sheet is missing columns: " + ", ".join(sorted(missing_property)))
    if missing_finance:
        raise RuntimeError("Finance Opportunities sheet is missing columns: " + ", ".join(sorted(missing_finance)))

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
    print(f"Property agent engine processed {len(updates)} finance records.")
    if result:
        print(f"Smartsheet update resultCode={result.get('resultCode')} message={result.get('message')}")

if __name__ == "__main__":
    run()
