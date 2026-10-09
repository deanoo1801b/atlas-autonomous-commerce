"""Read-only public buyer prospect register helpers."""
import json
from pathlib import Path

DEFAULT_REGISTER = Path(__file__).with_name("data") / "buyer_prospects_seed.json"

def load_buyer_prospects(path=DEFAULT_REGISTER):
    """Load public prospect seeds; never promote them to verified buyers."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if any(data.get(k) is not False for k in ("contacting_enabled", "referral_enabled", "publishing_enabled")):
        raise ValueError("Prospect register must keep contact, referral and publishing disabled")
    seen = set()
    for record in data.get("records", []):
        pid = str(record.get("prospect_id") or "").strip()
        if not pid or pid in seen:
            raise ValueError("Every prospect needs a unique prospect_id")
        seen.add(pid)
        if str(record.get("verification_status", "")).startswith("Verified"):
            raise ValueError("Publicly discovered prospects must not be marked verified")
        if record.get("identity_verified") is not False:
            raise ValueError("Publicly discovered prospects must default to identity_verified=false")
        if not str(record.get("evidence_url") or "").startswith("https://"):
            raise ValueError("Every prospect needs an HTTPS evidence URL")
    return data

def buyer_candidates(records, geography=None, strategies=None):
    """Filter candidates by declared public criteria; this never implies verification."""
    geography = {str(x).strip().lower() for x in (geography or [])}
    strategies = {str(x).strip().lower() for x in (strategies or [])}
    output = []
    for record in records:
        if record.get("record_type", "").startswith("Investor-network"):
            continue
        areas = {str(x).strip().lower() for x in record.get("geography", [])}
        tags = {str(x).strip().lower() for x in record.get("property_strategies", [])}
        if geography and not any(g in a or a in g for g in geography for a in areas):
            continue
        if strategies and not any(s in t or t in s for s in strategies for t in tags):
            continue
        output.append(record)
    return output
