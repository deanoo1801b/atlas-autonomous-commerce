#!/usr/bin/env python3
"""Scheduled public-source property opportunity discovery.

Searches Google News RSS for broad property acquisition signals and a separate,
explicit Rent to Buy housing requirement. Results are research signals only:
they are never represented as verified listings, available homes, seller intent,
or proof of scheme eligibility. No contact or CRM write is performed.
"""
import csv
import datetime as dt
import hashlib
import html
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

AREAS = ["Dartford", "Gravesend", "Grays Essex", "Croydon", "Lambeth"]
RENT_TO_BUY_AREAS = ["Dartford", "Grays Essex"]
RENT_TO_BUY_TERMS = [
    '"Rent to Buy" house',
    '"rent-to-buy" home',
    '"rent then buy" house',
    '"intermediate rent" "purchase"',
]
PROPERTY_TERMS = [
    '"property auction" house',
    '"price reduced" house property',
    '"property development site" land',
    '"landlord selling" property',
    '"house needs renovation" property',
    '"property portfolio for sale" landlord',
    '"vacant property" for sale',
    '"off-market" property',
]

def build_queries():
    queries = []
    # Property sourcing: pair each search intent with each target area.
    for area in AREAS:
        for term in PROPERTY_TERMS:
            queries.append(f'{term} "{area}"')
    # Separate housing requirement: genuine Rent to Buy, not shared ownership.
    for area in RENT_TO_BUY_AREAS:
        for term in RENT_TO_BUY_TERMS:
            queries.append(f'{term} "{area}" "2 bedroom" OR "3 bedroom"')
    # General provider pages and developments may not mention bedrooms in snippet.
    for area in RENT_TO_BUY_AREAS:
        queries.append(f'"Rent to Buy" "{area}" housing provider')
    return queries

QUERIES = build_queries()
OUT = Path("property-agent-output")
OUT.mkdir(exist_ok=True)
now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
seen = set()
rows = []
failures = []

for query in QUERIES:
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({
        "q": query, "hl": "en-GB", "gl": "GB", "ceid": "GB:en"
    })
    req = urllib.request.Request(url, headers={
        "User-Agent": "InspirationPropertiesResearchBot/1.0"
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            root = ET.fromstring(response.read())
        for item in root.findall("./channel/item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            published = (item.findtext("pubDate") or "").strip()
            source = item.find("source")
            publisher = (source.text or "").strip() if source is not None else ""
            description = html.unescape(item.findtext("description") or "")
            description = re.sub(r"<[^>]+>", " ", description)
            description = re.sub(r"\s+", " ", description).strip()
            if not title or not link:
                continue
            key = hashlib.sha256((title + link).encode()).hexdigest()
            if key in seen:
                continue
            seen.add(key)
            is_rtb = any(term.lower() in query.lower() for term in RENT_TO_BUY_TERMS)
            rows.append({
                "scanned_at_utc": now,
                "query": query,
                "lead_category": "HOUSING_REQUIREMENT_RENT_TO_BUY" if is_rtb else "PROPERTY_RESEARCH_SIGNAL",
                "title": title,
                "published_at": published,
                "publisher": publisher,
                "url": link,
                "snippet": description[:1000],
                "verification_status": "UNVERIFIED_NEEDS_HUMAN_REVIEW",
                "lead_score": "",
                "contacted": "NO",
                "requirement_note": (
                    "Seeking 2- or 3-bedroom house in Dartford or Grays; up to £2,000/month; "
                    "not shared ownership. Confirm genuine Rent to Buy and availability with provider."
                    if is_rtb else ""
                ),
            })
    except Exception as exc:
        message = f"WARNING: query failed ({query}): {exc}"
        print(message, file=sys.stderr)
        failures.append(message)

csv_path = OUT / "property-opportunities.csv"
fields = [
    "scanned_at_utc", "query", "lead_category", "title", "published_at",
    "publisher", "url", "snippet", "verification_status", "lead_score",
    "contacted", "requirement_note",
]
with csv_path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

rtb_count = sum(row["lead_category"] == "HOUSING_REQUIREMENT_RENT_TO_BUY" for row in rows)
summary = OUT / "scan-summary.md"
summary.write_text(
    "# Inspiration Properties UK — background research scan\n\n"
    f"- Scan time (UTC): {now}\n"
    f"- Queries attempted: {len(QUERIES)}\n"
    f"- Unique public research results: {len(rows)}\n"
    f"- Rent to Buy research signals (Dartford/Grays): {rtb_count}\n"
    f"- Query failures: {len(failures)}\n"
    "- Output: property-opportunities.csv\n\n"
    "## Important qualification\n"
    "Search results are not verified property listings, live availability, confirmed Rent to Buy "
    "offers, seller leads, or proof of eligibility. Search snippets can be stale or misleading. "
    "A human must open the source, verify the provider and scheme terms, bedroom count, rent, "
    "availability and location. Shared ownership is excluded from the intended housing requirement. "
    "No outreach or Smartsheet write is performed.\n\n"
    + ("## Query warnings\n" + "\n".join(f"- {failure}" for failure in failures) + "\n" if failures else ""),
    encoding="utf-8",
)
print(f"Scan completed: {len(rows)} unique research results ({rtb_count} Rent to Buy signals).")
print(f"CSV: {csv_path}")
