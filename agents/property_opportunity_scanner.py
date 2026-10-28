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

from property_query_classifier import is_rent_to_buy_query, is_london_living_rent_signal
from rent_to_buy_search_config import build_rent_to_buy_queries

AREAS = ["Dartford", "Gravesend", "Grays Essex", "Croydon", "Lambeth"]
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
    # Expanded housing search: London boroughs and surrounding commuter areas.
    # Includes London Living Rent and intermediate-rent terminology for London.
    queries.extend(build_rent_to_buy_queries())
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
            is_rtb = is_rent_to_buy_query(query)
            result_text = f"{title} {description}"
            is_llr = is_london_living_rent_signal(result_text)
            category = (
                "HOUSING_REQUIREMENT_LONDON_INTERMEDIATE_RENT"
                if is_rtb and is_llr else
                "HOUSING_REQUIREMENT_RENT_TO_BUY"
                if is_rtb else "PROPERTY_RESEARCH_SIGNAL"
            )
            rows.append({
                "scanned_at_utc": now,
                "query": query,
                "lead_category": category,
                "title": title,
                "published_at": published,
                "publisher": publisher,
                "url": link,
                "snippet": description[:1000],
                "verification_status": "UNVERIFIED_NEEDS_HUMAN_REVIEW",
                "lead_score": "",
                "contacted": "NO",
                "requirement_note": (
                    "Seeking a 2- or 3-bedroom house across London and surrounding areas; up to £2,000/month; "
                    "exclude shared ownership. Confirm scheme, property type and availability with provider. "
                    + ("London Living Rent can lead toward shared ownership; do not treat as a match unless that route is acceptable." if is_llr else "")
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
llr_count = sum(row["lead_category"] == "HOUSING_REQUIREMENT_LONDON_INTERMEDIATE_RENT" for row in rows)
summary = OUT / "scan-summary.md"
summary.write_text(
    "# Inspiration Properties UK — background research scan\n\n"
    f"- Scan time (UTC): {now}\n"
    f"- Queries attempted: {len(QUERIES)}\n"
    f"- Unique public research results: {len(rows)}\n"
    f"- Rent to Buy / London Living Rent research signals (London and surrounding region): {rtb_count}\n"
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
