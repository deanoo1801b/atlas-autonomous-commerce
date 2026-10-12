# UK Property Source Adapter Specification

Status: implementation specification; not connected to a live n8n instance.

## Initial approved-source candidates

### 1. Planning Data API (England)
- Official documentation: https://www.planning.data.gov.uk/docs
- Purpose: planning applications and site constraints; useful for development/JV opportunity research.
- Access: documented JSON API, polite rate limiting, pagination, explicit dataset selection.
- Suggested query: `/entity.json?dataset=planning-application&limit=100&offset=0`
- Important limitation: planning data is not complete and the platform remains in development. Treat records as leads for review, not proof of planning status or ownership.

### 2. HM Land Registry Price Paid Data (England and Wales)
- Official current data: https://www.gov.uk/government/statistical-data-sets/price-paid-data-single-file
- Purpose: comparable-sale research and observed market history.
- Access: official monthly/yearly CSV/TXT downloads or report builder. Do not fetch the 5GB single file on every daily run; use incremental monthly data or curated extracts.
- Required attribution: "Contains HM Land Registry data © Crown copyright and database right 2021. This data is licensed under the Open Government Licence v3.0."
- Licence caveat: the OGL permits commercial/non-commercial reuse of Price Paid Data, but some address components are subject to separate third-party rights and restrictions. Review intended address use before publishing or redistributing.

### 3. Local authority planning portals and auction catalogues
- Add only after a per-source terms, robots/access, rate-limit, and permitted-use review.
- Prefer official RSS/API/bulk feeds where available.
- Do not scrape login-only pages, bypass access controls, or treat portal listings as permission to contact private individuals.

## Normalized record
```json
{
  "leadId": "stable-hash",
  "jurisdiction": "England | Wales | Scotland | Northern Ireland",
  "category": "planning_or_development | auction | listing | comparable_sale",
  "propertyOrProjectLocation": "",
  "postcode": "",
  "sourceName": "",
  "sourceUrl": "",
  "sourcePublishedAt": null,
  "discoveredAt": "",
  "lastObservedAt": "",
  "askingPriceGbp": null,
  "transactionPriceGbp": null,
  "verifiedFacts": [],
  "unverifiedClaims": [],
  "evidenceConfidence": "low | medium | high",
  "duplicateKey": "",
  "complianceStatus": "review_required",
  "outreachStatus": "not_authorized",
  "reviewReason": "",
  "nextAction": "human_review"
}
```

## Stable identity and deduplication
1. Prefer a source's own persistent record/application/reference ID.
2. Otherwise hash normalized source hostname + source record URL.
3. Use normalized postcode/address as a secondary matching signal only; never treat postcode alone as property identity.
4. Preserve old and new observed values with timestamps. Do not overwrite price history.
5. A failed/empty API response is an error state, never evidence of zero opportunities.

## Evidence and compliance gates
- A valid URL establishes provenance only.
- Never infer arrears, repossession, vulnerability, financial hardship, ownership, willingness to sell, or permission to contact from a listing or price change.
- Price Paid Data Category B does not uniquely identify repossession transactions; do not label it as a repossession lead.
- Keep contact data separate from property/project records.
- No email, calls, marketing, broker referral, CRM disclosure, or external write until human approval and relevant UK GDPR/PECR and source licensing checks are completed.
- For Scotland and Northern Ireland, use separate official data adapters; England/Wales sources are not UK-wide.

## Acceptance tests before activation
- Valid official API response produces normalized records with provenance.
- Duplicate source record updates last-observed/history instead of creating a duplicate.
- Missing source URL/location is quarantined.
- API 429/5xx/timeout produces logged source error and does not report zero leads.
- Pagination is followed within documented limits and with polite rate limiting.
- Invalid/missing prices remain null; never fabricate valuation or asking price.
- Outbound nodes remain absent/disabled in the initial release.
