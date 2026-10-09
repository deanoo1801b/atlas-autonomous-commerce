"""Public-source private seller discovery.

This module only reads publicly accessible listing/index pages. It never logs in,
bypasses controls, collects private contact details, or contacts sellers.
Sources are intentionally limited to platforms that advertise owner/private listings.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser

SOURCES = [
    {"name": "Keyzee", "base": "https://keyzee.co.uk/", "index": "https://keyzee.co.uk/", "owner_only": True},
    {"name": "FYSH", "base": "https://www.fysh.uk/", "index": "https://www.fysh.uk/", "owner_only": True},
    {"name": "OffAgent", "base": "https://www.offagent.co.uk/", "index": "https://www.offagent.co.uk/properties", "owner_only": True},
    {"name": "Hauski", "base": "https://www.hauski.com/", "index": "https://www.hauski.com/", "owner_only": True},
    {"name": "OwnerBridge", "base": "https://www.ownerbridge.co.uk/", "index": "https://www.ownerbridge.co.uk/", "owner_only": True},
    {"name": "FMDirect", "base": "https://fairmovedirect.co.uk/", "index": "https://fairmovedirect.co.uk/", "owner_only": True},
    {"name": "Bybricks", "base": "https://www.bybricks.co.uk/", "index": "https://www.bybricks.co.uk/", "owner_only": False},
    {"name": "OpenMoov", "base": "https://openmoov.co.uk/", "index": "https://openmoov.co.uk/", "owner_only": False},
]

UA = "InspirationPropertiesPublicListingAgent/1.0 (+public-listing-discovery)"

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.text = []
        self._href = None

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            self._href = dict(attrs).get("href")

    def handle_data(self, data):
        if data.strip():
            self.text.append(data.strip())

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self._href:
            self.links.append((" ".join(self.text[-4:]), self._href))
            self._href = None

def _robots_ok(url: str) -> bool:
    p = urlparse(url)
    robots_url = f"{p.scheme}://{p.netloc}/robots.txt"
    rp = RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(UA, url)
    except Exception:
        # Fail closed if robots.txt cannot be read.
        return False

def _fetch(url: str) -> str | None:
    if not _robots_ok(url):
        return None
    try:
        req = Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"})
        with urlopen(req, timeout=15) as r:
            if "text/html" not in (r.headers.get("Content-Type") or ""):
                return None
            data = r.read(1_500_000)
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return None

def _price(text: str):
    m = re.search(r"£\s*([0-9][0-9,]*(?:\.[0-9]+)?)", text)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except ValueError:
        return None

def _candidate_links(source, html):
    parser = LinkParser()
    parser.feed(html)
    host = urlparse(source["base"]).netloc
    out = []
    for label, href in parser.links:
        if not href:
            continue
        url = urljoin(source["index"], href)
        if urlparse(url).netloc != host:
            continue
        path = urlparse(url).path.lower()
        if any(k in path for k in ("/property", "/properties", "/listing", "/listings", "/home", "/homes", "/sale")):
            out.append((label, url))
    # preserve order and cap per source
    seen = set()
    result = []
    for item in out:
        if item[1] in seen:
            continue
        seen.add(item[1])
        result.append(item)
        if len(result) >= 25:
            break
    return result

def discover_private_sellers():
    candidates = []
    for source in SOURCES:
        index_html = _fetch(source["index"])
        if not index_html:
            continue
        for label, url in _candidate_links(source, index_html):
            html = _fetch(url)
            if not html:
                continue
            text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()
            if len(text) < 40:
                continue
            low = text.lower()
            # Strong private-owner signal from the source itself.
            private_signal = any(k in low for k in (
                "private seller", "owner listed", "owner-listed", "sell privately",
                "directly by the owner", "private vendor", "homeowner",
                "owner-to-buyer", "no estate agent", "without an estate agent",
                "listed by the owner", "listed directly by owners"
            ))
            if not source.get("owner_only") and not private_signal:
                continue
            price = _price(text)
            digest = hashlib.sha256(url.encode()).hexdigest()[:16]
            candidates.append({
                "Lead ID": f"PS-{digest}",
                "Lead Type": "Private Seller",
                "Opportunity Type": "Private Sale",
                "Seller Type": "Direct Owner",
                "Contact Route": "Platform only; human approval required",

                "Area": None,
                "Asking Price": price,
                "Seller Name": None,
                "Source": source["name"],
                "Source URL": url,
                "Opportunity Evidence": "Public owner/private-seller listing detected; seller contact details intentionally not collected.",
                "Contact Permission": "Unknown",
                "Do Not Contact": False,
                "Finance Candidate": "Review",
            })
            time.sleep(0.5)
    return candidates

if __name__ == "__main__":
    print(json.dumps(discover_private_sellers(), indent=2))
