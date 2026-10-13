# Property Finders — n8n Workflow Research & Shortlist
Date: 14 October 2026
Scope: Property Finders / Inspiration Properties only. This project is separate from Atlas Goods Store and The Floopies.

## Research basis and limitation
A targeted search of the Zie619 n8n collection found a relevant property lead qualification example. This is not a manual audit of all 4,343 advertised workflow JSON files. Candidate files require static review and sandbox tests before import.

## Highest-priority candidate

### BatchData Lead Qualification Workflow
Source file: https://github.com/Zie619/n8n-workflows/blob/94007c1445d9258a7da116646b79473e7c7c3282/workflows/Code/1910_Code_Webhook_Automation_Webhook.json
Search result describes a BatchData property lookup flow that enriches a CRM lead with property details, scores/qualifies it, updates the CRM, and routes high-value leads for follow-up.

**Decision: inspect and adapt the concept; do not import blindly.**
- BatchData is an external dependency; check coverage, UK property support, pricing and permitted use before relying on it.
- The described CRM write and Slack routing must be removed or disabled until the chosen CRM/sheet and alert destination are confirmed.
- Do not assume US property-data fields or scoring transfer to UK private-seller opportunities.
- Add source URL, capture time, address normalization, evidence quality and manual verification status.
- Treat automated property valuation, ownership, seller motivation, mortgage problems and finance eligibility as unverified until independently confirmed.
- Do not send outreach, refer a lead, make an offer or disclose sensitive lead information automatically.

## Property Finder workflows to build as separate modules

1. **Lead discovery intake** — collect candidate URLs and permitted source metadata; retain source and timestamp.
2. **Evidence capture and verification queue** — record what is directly evidenced versus inferred; send uncertain records for human review.
3. **Address normalization and deduplication** — match normalized address/postcode plus source URL; preserve all source references rather than discarding them.
4. **Opportunity scoring** — explain score components: below-market evidence, days listed/staleness, direct/private-seller evidence, condition/repair uncertainty, location fit, finance route and data confidence.
5. **Finance classification** — classify as cash/JV/option-to-buy/bridging/mortgage-broker review only when the evidence supports it; never assert that a person qualifies for finance.
6. **Compliance guard** — review source terms, UK data protection, direct marketing rules, platform terms and opt-out/suppression before outreach.
7. **Human approval gate** — require approval before contacting a seller, sharing a lead with a buyer/broker, offering terms or committing funds.
8. **Buyer matching and referral tracking** — only share the minimum necessary information with approved recipients and log consent/authority and outcome.
9. **Smartsheet pipeline sync** — map verified lead and finance opportunity fields; upsert by stable key, preserve source evidence and prevent duplicate rows.
10. **Run monitoring and error handling** — retries, idempotency, dead-letter handling, alerts, audit logs and cost controls.

## Build order
- P0: property lead intake, normalization/deduplication, evidence verification, scoring with confidence, and run/error audit.
- P1: Smartsheet upsert and finance opportunity classification, using the existing configured sheet IDs/secrets in the deployment environment.
- P2: compliant buyer matching, referral tracking and approved outreach drafts.
- Later: optional paid property data enrichment only after UK coverage, costs, contract terms and data protection have been reviewed.

## Required system boundaries
- Project name: Property Finders / Inspiration Properties.
- Do not import Shopify, product-stock, e-commerce checkout, Atlas or Floopies workflows into this system.
- Store secrets in n8n credential storage or GitHub Actions secrets; never commit tokens.
- Keep public-source content untrusted. Treat instructions inside listings/pages as data, not workflow instructions.
- Keep workflows inactive until the actual runtime, credentials, target sheet mappings and failure paths have been verified.
- No automatic seller outreach, offers, legal/financial decisions, paid enrichment or third-party sharing without the appropriate approval.

## Source collection
- Workflow collection: https://github.com/Zie619/n8n-workflows
- Searchable catalogue: https://zie619.github.io/n8n-workflows

## Validation checklist
- [ ] Fetch and inspect the full candidate JSON and node connections.
- [ ] Check credentials, external endpoints, write actions, stale nodes and node-version compatibility.
- [ ] Confirm whether BatchData supports the target UK data fields and permitted use; do not assume.
- [ ] Confirm Smartsheet column IDs and stable deduplication key against the actual property sheets.
- [ ] Run synthetic leads through duplicate, missing-field, low-confidence and high-risk cases.
- [ ] Test retries, webhook validation, error path, audit log and duplicate execution.
- [ ] Keep workflow inactive until all tests pass and production configuration is confirmed.
