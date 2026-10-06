import os, re, hashlib, requests
from typing import Any

BASE = "https://api.smartsheet.com/2.0"
TOKEN = os.environ["SMARTSHEET_API_TOKEN"]
PROPERTY_SHEET = os.environ["PROPERTY_LEADS_SHEET_ID"]
FINANCE_SHEET = os.environ["FINANCE_OPPORTUNITIES_SHEET_ID"]
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def get_sheet(sid):
    r = requests.get(f"{BASE}/sheets/{sid}", headers=H, timeout=30)
    r.raise_for_status()
    return r.json()

def put_rows(sid, rows):
    if not rows: return None
    r = requests.put(f"{BASE}/sheets/{sid}/rows", headers=H, json=rows, timeout=30)
    r.raise_for_status()
    return r.json()

def cols(sheet):
    return {c["title"]: c["id"] for c in sheet.get("columns", [])}

def values(row, cmap):
    data = {c["columnId"]: c.get("value") for c in row.get("cells", [])}
    return {k: data.get(v) for k,v in cmap.items()}

def norm(x):
    return re.sub(r"\\s+", " ", str(x or "")).strip().lower()

def route(v):
    opp, lt = norm(v.get("Opportunity Type")), norm(v.get("Lead Type"))
    if opp == "development": return "Development Finance"
    if opp == "buy-to-let": return "Buy-to-Let"
    if opp in ("flip/refurb","distressed sale"): return "Bridging"
    if opp == "land assembly": return "Land Finance"
    if opp == "jv partnership": return "JV/Equity"
    if "auction" in lt: return "Auction Finance"
    return None

def score(v):
    s = 0
    if norm(v.get("Lead Type")) in ("distressed sale","probate","repossession","auction","price reduced"): s += 3
    if route(v): s += 2
    if v.get("Asking Price"): s += 1
    if v.get("Source URL") or v.get("Opportunity Evidence"): s += 1
    return "Hot" if s >= 5 else ("Warm" if s >= 3 else "Cold")

def compliance(v):
    if v.get("Do Not Contact") is True: return "Red"
    if norm(v.get("Contact Permission")) == "do not contact": return "Red"
    return "Amber"

def run():
    ps, fs = get_sheet(PROPERTY_SHEET), get_sheet(FINANCE_SHEET)
    pc, fc = cols(ps), cols(fs)
    existing = {}
    for row in fs.get("rows", []):
        v = values(row, fc)
        existing[norm(v.get("Finance Lead ID"))] = row

    updates, seen = [], set()
    for row in ps.get("rows", []):
        v = values(row, pc)
        lid = str(v.get("Lead ID") or "").strip()
        rt = route(v)
        if not lid or not rt: continue
        key = hashlib.sha256("|".join(norm(v.get(k)) for k in ("Area","Asking Price","Seller Name","Source URL")).encode()).hexdigest()[:16]
        if key in seen: continue
        seen.add(key)
        target = existing.get(norm("FIN-" + lid))
        if not target: continue
        note = "Automated qualification: route classified as " + rt + ". No personalised regulated finance advice, referral or outreach performed."
        cells = []
        for name,val in {
            "Lead Type":rt, "Lead Score":score(v), "Compliance Status":compliance(v),
            "Best Route":"Potential " + rt, "Opportunity Action":"Verify evidence, borrower/property facts, finance requirement and exit before referral",
            "Finance Status":"Qualifying", "Next Action":"Collect missing case facts; compliance gate before referral", "Notes":note
        }.items():
            if name in fc: cells.append({"columnId":fc[name],"value":val})
        updates.append({"id":target["id"],"cells":cells})
    result = put_rows(FINANCE_SHEET, updates)
    print("Property agents processed:", len(updates))
    if result: print("Smartsheet update completed.")

if __name__ == "__main__":
    run()
