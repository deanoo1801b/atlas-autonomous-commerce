#!/usr/bin/env python3
"""Scheduled public-source property opportunity discovery prototype.

Uses Google News RSS search feeds (public headlines/snippets), not private data.
It does not bypass access controls, infer distress, or contact anyone.
"""
import csv
import datetime as dt
import hashlib
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

QUERIES = [
    '"off-market" property Croydon OR Lambeth',
    'property auction Croydon OR Lambeth house',
    'price reduced house Croydon OR Lambeth property',
    'property development site Croydon OR Lambeth',
    'landlord selling house Croydon OR Lambeth',
]
OUT = Path("property-agent-output")
OUT.mkdir(exist_ok=True)
now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
seen = set()
rows = []
for query in QUERIES:
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({
        "q": query, "hl": "en-GB", "gl": "GB", "ceid": "GB:en"
    })
    req = urllib.request.Request(url, headers={"User-Agent": "InspirationPropertiesResearchBot/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            root = ET.fromstring(response.read())
        for item in root.findall("./channel/item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            pub = (item.findtext("pubDate") or "").strip()
            source = item.find("source")
            publisher = (source.text or "").strip() if source is not None else ""
            desc = re.sub(r"<[^>]+>", " ", item.findtext("description") or "")
            desc = re.sub(r"\s+", " ", desc).strip()
            key = hashlib.sha256((title + link).encode()).hexdigest()
            if not title or not link or key in seen:
                continue
            seen.add(key)
            rows.append({
                "scanned_at_utc": now, "query": query, "title": title,
                "published_at": pub, "publisher": publisher, "url": link,
                "snippet": desc[:1000], "verification_status": "UNVERIFIED_NEEDS_HUMAN_REVIEW",
                "lead_score": "", "contacted": "NO"
            })
    except Exception as exc:
        print(f"WARNING: query failed ({query}): {exc}", file=sys.stderr)

path = OUT / "property-opportunities.csv"
with path.open("w", newline="", encoding="utf-8") as f:
    fields = ["scanned_at_utc","query","title","published_at","publisher","url","snippet","verification_status","lead_score","contacted"]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
summary = OUT / "scan-summary.md"
summary.write_text(
    "# Inspiration Properties UK — background research scan\n\n"
    f"- Scan time (UTC): {now}\n- Unique public news/search results: {len(rows)}\n"
    "- Output: property-opportunities.csv\n"
    "- IMPORTANT: These are research signals, not verified property listings or confirmed seller leads. "
    "Open each source, verify the opportunity, and check permissions before contacting anyone.\n",
    encoding="utf-8"
)
print(f"Scan completed: {len(rows)} unique results. CSV: {path}")
