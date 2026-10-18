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

def _extract_uk_postcode(text: str) -> str | None:
    """Return a normalized UK postcode only when it appears in the public listing text."""
    pattern = r"\\b(GIR\\s*0AA|(?:[A-PR-UWYZ]\\d{1,2}|[A-PR-UWYZ][A-HK-Y]\\d{1,2}|[A-PR-UWYZ]\\d[A-HJKSTUW]|[A-PR-UWYZ][A-HK-Y]\\d[ABEHMNPRV-Y])\\s*\\d[ABD-HJLNP-UW-Z]{2})\\b"
    match = re.search(pattern, text or "", re.IGNORECASE)
    if not match:
        return None
    value = re.sub(r"\\s+", " ", match.group(1).upper()).strip()
    if value == "GIR 0AA":
        return value
    return re.sub(r"^(.*?)(\\d[A-Z]{2})$", r"\\1 \\2", value.replace(" ", ""))


def _is_sample_listing(text: str, url: str = "", label: str = "") -> bool:
    """Reject obvious demo/test/sample pages before treating them as real property leads."""
    combined = re.sub(r"\s+", " ", f"{label} {url} {text}").lower()
    patterns = (
        r"\bsample listing\b",
        r"\bnot a real (?:home|property|listing)\b",
        r"\bdemo (?:listing|property|home)\b",
        r"\btest (?:listing|property|home)\b",
        r"\bexample (?:listing|property|home)\b",
        r"\bplaceholder (?:listing|property|home)\b",
    )
    return any(re.search(pattern, combined) for pattern in patterns)

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
            # Exclude platform demo data; a sample page must never become a seller lead.
            if _is_sample_listing(text, url, label):
                continue
            # Require listing-level evidence, even on owner-focused platforms:
            # platform positioning alone does not prove that this individual listing
            # is genuinely being offered directly by its owner.
            private_signal = any(k in low for k in (
                "private seller", "owner listed", "owner-listed", "sell privately",
                "directly by the owner", "private vendor", "homeowner",
                "owner-to-buyer", "no estate agent", "without an estate agent",
                "listed by the owner", "listed directly by owners",
                "for sale by owner", "sold directly by owner", "owner is selling",
                "selling my home", "selling our home"
            ))
            if not private_signal:
                continue
            price = _price(text)
            postcode = _extract_uk_postcode(text)
            digest = hashlib.sha256(url.encode()).hexdigest()[:16]
            candidates.append({
                "Lead ID": f"PS-{digest}",
                "Lead Type": "Private Seller",
                "Opportunity Type": "Private Sale",
                "Seller Type": "Direct Owner",
                "Contact Route": "Platform only; human approval required",

                "Area": postcode,
                "Postcode": postcode,
                "Location Evidence": f"UK postcode extracted from public listing text: {postcode}" if postcode else None,
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
