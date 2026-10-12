# UK Property Workflow Adaptation — Implementation Record

Date: 2026-10-12
Repository: `deanoo1801b/atlas-autonomous-commerce`
Status: **design and validation foundation only**. This change does not deploy n8n, connect credentials, crawl listing portals, or enable outreach.

## Decision

Do not import the shortlisted templates directly into production. Reuse their patterns only after inspection and rebuild the workflow connections and UK data adapters. The first release should be a scheduled, read-only evidence queue with manual review.

## Candidate ranking and source links

These are reference templates, not verified production-ready UK workflows:

1. **Real Estate Market Scanning** — [JSON](https://github.com/Zie619/n8n-workflows/blob/main/workflows/Splitout/1748_Splitout_Code_Automation_Webhook.json). Reuse schedule/change-detection/alert pattern; replace US BatchData assumptions, US location fields and equity filters.
2. **Lead Qualification with BatchData** — [JSON](https://github.com/Zie619/n8n-workflows/blob/main/workflows/Code/1910_Code_Webhook_Automation_Webhook.json). Reuse stage separation only; replace BatchData and US scoring logic with UK evidence-based scoring.
3. **Property Lead Contact Enrichment from CRM** — [JSON](https://github.com/Zie619/n8n-workflows/blob/main/workflows/Emailsend/1628_Emailsend_Code_Automation_Webhook.json). Reference only; do not enable personal-data enrichment until source, lawful basis, retention and marketing controls are reviewed.
4. **AI-Powered Information Monitoring** — [JSON](https://github.com/Zie619/n8n-workflows/blob/main/workflows/Code/1278_Code_Schedule_Monitor_Webhook.json). Reuse RSS/source registry, URL deduplication and digest concept; verify node types, connections, credentials and current service terms before use.
5. **Google Sheets append/lookup/update/read** — [JSON](https://github.com/Zie619/n8n-workflows/blob/main/workflows/Manual/1062_Manual_GoogleSheets_Update_Triggered.json). Rebuild for idempotent upsert and a stable Lead ID; not a property scout by itself.
6. **Amazon Product Price Tracker** — [JSON](https://github.com/Zie619/n8n-workflows/blob/main/workflows/Schedule/1697_Schedule_HTTP_Monitor_Scheduled.json). Reuse threshold/history pattern only, not its source adapter.
7. **Googlesheetstrigger Workflow** — [JSON](https://github.com/Zie619/n8n-workflows/blob/main/workflows/Http/0470_HTTP_GoogleSheets_Update_Webhook.json). Reference for conditional updates; inspect wiring and idempotency.
8. **Insert and update data in Airtable** — [JSON](https://github.com/Zie619/n8n-workflows/blob/main/workflows/Manual/0218_Manual_Airtable_Update_Triggered.json). Optional storage pattern only; avoid adding Airtable if Smartsheet is already available.
9. **Web Server Monitor** — [JSON](https://github.com/Zie619/n8n-workflows/blob/main/workflows/Schedule/1952_Schedule_HTTP_Monitor_Webhook.json). Reuse health-check/error-report pattern.
10. **Email Summary Agent** — [JSON](https://github.com/Zie619/n8n-workflows/blob/main/workflows/Aggregate/1430_Aggregate_Schedule_Send_Scheduled.json). Reuse digest pattern only; validate AI nodes and disable sending during tests.

The previously inspected collection files showed configuration placeholders and structural/connection concerns. These links should not be treated as passed import tests. Re-inspect the live JSON and licensing before importing any file.

## UK adaptation rules

- Use England/Wales/Scotland/Northern Ireland as explicit jurisdiction fields where relevant; do not treat UK property law as uniform.
- Store UK postcode as supplied and a normalized comparison key. Do not use postcode alone as a property identity.
- Replace US fields (state, ZIP, equity percentage, absentee owner, BatchData-specific statuses) with UK-relevant fields: address, postcode, tenure if sourced, property type, asking price, listing/observed dates, documented price changes, source and source terms.
- Prioritise permitted official feeds/APIs, auction catalogues whose terms allow the intended use, open datasets and direct public project announcements. Maintain an allowlist of sources and rate limits.
- Never infer arrears, repossession, vulnerability, financial hardship or willingness to sell from listing age, price reductions, vacancy or neighbourhood.
- A source URL proves provenance only. It does not prove ownership, factual accuracy, consent or permission to contact.
- Keep contact data separate from property/project data. Do not enrich private individuals automatically.
- Human approval is required before external contact, broker referral, offers, or any CRM action that discloses personal data.
- Store credentials in n8n credential storage/secrets, not in JSON, prompts, Git or logs.
- Keep schedule disabled until the import, source terms, credentials, error paths and synthetic-data tests have passed.

## Recommended smallest combination

A single orchestrator with small stages is preferable to eight separate AI agents initially:

1. Daily schedule (disabled until approved).
2. Read approved source registry.
3. Fetch only permitted RSS/API sources.
4. Normalize and validate evidence.
5. Deduplicate by source URL plus normalized address/postcode where available.
6. Persist a review record with source URL, observed date and evidence summary.
7. Produce an internal digest and error report.
8. Keep all outbound contact and broker referral disabled.

Use Smartsheet if API access and column mapping are confirmed. Otherwise use a temporary local/staging store; do not silently switch to a paid provider.

## Lead record minimum

`leadId`, `discoveredAt`, `category`, `propertyOrProjectLocation`, `postcode`, `sourceName`, `sourceUrl`, `sourcePublishedAt`, `lastObservedAt`, `askingPriceGbp`, `priceHistoryEvidence`, `verifiedFacts[]`, `unverifiedClaims[]`, `evidenceConfidence`, `duplicateKey`, `complianceStatus`, `outreachStatus`, `reviewReason`, `nextAction`.

Prices and margins must not be invented. A valuation requires comparable-sale evidence with source URLs, dates, property type and methodology; estimates remain estimates until reviewed.

## Safe acceptance tests

- Valid HTTPS source URL with hostname: accepted as provenance, not as proof of ownership.
- Missing/malformed URL, unsupported scheme, whitespace or malformed port: quarantine.
- Missing address or source date: retain with an explicit missing-data flag; do not mark verified.
- Repeated listing: update last-observed/history rather than create a duplicate.
- Price change: preserve old and new price with observed timestamps and source evidence.
- Long-listed or price-reduced listing: do not label distressed or infer mortgage problems.
- Source error/rate limit/empty response: log failure and report it; never treat it as zero opportunities.
- All email, Slack, CRM write and broker referral actions disabled during tests.

## Current blockers before live application

- Confirm the running n8n instance and test workspace.
- Approve a source allowlist and its terms/rate limits.
- Confirm Smartsheet API access and destination columns.
- Choose internal alert destination.
- Review UK GDPR, Data Protection Act 2018, PECR, call suppression, data licensing and property-sector regulatory requirements with a qualified adviser where needed.
- Run import tests against the exact candidate JSON files. Do not claim deployment or passing tests until execution evidence exists.
