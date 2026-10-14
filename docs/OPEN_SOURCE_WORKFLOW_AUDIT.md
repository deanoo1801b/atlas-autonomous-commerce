# Open-source n8n workflow audit for ATLAS

Status: **in progress — not a complete audit of every workflow**  
Upstream: https://github.com/Zie619/n8n-workflows  
Audit rule: inspect the actual JSON, not only the workflow title or catalogue claim.

## Collection integrity findings

- The upstream README advertises 4,343 workflows and 365 integrations.
- The current Git tree returned 2,394 total tree entries, including directories and non-JSON files; this is not a count of workflow JSONs.
- A third-party audit reports 2,061 JSON files in the checked tree and warns that graph connections may be damaged. Treat this as a warning to validate the live upstream tree, not as an independently verified count for every revision.
- MIT license is shown in the upstream LICENSE file. Keep the notice when copying substantial portions and still inspect each file's own provenance and content.
- Do not import wholesale. The collection is a reference library, not a trusted production dependency.

## Previously inspected candidates

| Candidate | Finding | Decision |
|---|---|---|
| Real Estate Market Scanning | US/BatchData-specific fields, owner-contact assumptions and outbound email/Slack side effects | Reject direct import; adapt only generic source-normalisation and evidence patterns for UK property workflow |
| AI-Powered Information Monitoring | AI-labelled nodes include no-op placeholders in inspected JSON; external Sheets/Jina/Slack dependencies | Reuse monitoring/deduplication ideas only; rebuild and test |
| Google Sheets management/storage | Hard-coded sample data and empty connections map in inspected JSON | Reference only; do not import as executable |
| Web Server Monitor | Useful uptime/error-monitoring pattern but has notification/storage side effects | Candidate for a separate read-only health-check adaptation |
| On-Page SEO Audit / Search Console / keyword research / SERP research / Shopify SEO content factory | Candidate names previously surfaced; each exact JSON still needs graph, credential, side-effect, licence and test review | Not approved for import yet |
| Traffic-drop detection | Candidate pattern for store analytics monitoring | Rebuild around verified Atlas analytics data; test thresholds against sample data first |
| Deep research / niche research / product research | Candidate class only; search result is not proof of safe execution | Review exact JSON before adapting |

## ATLAS-specific review sequence

Review high-value workflows individually in batches. For every candidate, record:
1. Exact upstream path and commit SHA.
2. JSON parse result; nodes and node types; connections and unresolved endpoints.
3. Trigger, schedule, HTTP calls, code execution, shell commands and file operations.
4. Credentials required and least-privilege scopes.
5. Data sent to third parties, personal data, external contact, publishing, spending or destructive side effects.
6. Licensing/provenance notes and whether code can be reused.
7. UK/GB applicability, Shopify/Metricool compatibility and cost/rate-limit implications.
8. Adaptation made, automated test result and manual n8n import test result.
9. Final status: reject, reference only, adapt, or tested in disposable workspace.

## ATLAS safety defaults

- Start disabled and dry-run.
- No outbound customer/supplier/broker messages, social publishing, product edits, inventory changes, payments, ads spend or CRM writes without a separately approved action.
- Require source URL and timestamp for every research finding; deduplicate by canonical URL and stable entity key.
- Quarantine malformed, stale, unsupported or incomplete records.
- Never store tokens in workflow JSON, source control, logs or chat.
- Keep workflow-specific credentials outside the repo and use least privilege.
- A workflow is not "usable" until its graph validates, dependencies are mapped, sample tests pass and it imports in a disposable n8n instance.

## Priority batches

### Batch A — directly relevant to Atlas Goods Store
1. Shopify product/catalogue events and read-only product audit patterns.
2. Google Search Console, keyword/SERP research and SEO audits.
3. Google Analytics / traffic anomaly monitoring.
4. Social content preparation and Metricool scheduling patterns (publishing remains approval-gated).
5. Price/stock monitoring and product opportunity scoring.
6. Error monitoring, retry/backoff and deduplication primitives.

### Batch B — reusable platform primitives
7. Human approval / review queues.
8. Data normalisation, validation, deduplication and persistence.
9. PDF/image processing and creative asset pipelines.
10. Multi-agent orchestration only where executable nodes and real model calls are verified; reject no-op placeholders.

### Batch C — other Atlas-linked projects, only where explicitly in scope
11. UK property lead research, using UK sources and no unsolicited outreach.
12. KKAM Books production QA and digital-product opportunity research.
13. VANTE NOIRE / Gelato POD product and localisation research.

## Current progress

- UK property adaptation was drafted in PR #2 as a disabled, safe n8n skeleton with no credentials or network calls; not yet described as deployed or production-tested.
- This document establishes a repeatable audit register. It does **not** claim all 4,343 catalogue entries have been inspected.
- Next unit of work: retrieve the exact JSON for each Batch A candidate, run static graph/credential/side-effect checks, and adapt only the strongest candidates with tests.


## Individually inspected in this pass (2026-10-14)

### 1. On-Page SEO Audit
- Upstream file: `workflows/Form/1886_Form_Markdown_Automation_Webhook.json`
- Upstream blob SHA: `3864f3bff0e75dd0cac8aed36164b209ef5946f2`
- Findings: the named OpenAI/chat and audit nodes are represented as `n8n-nodes-base.noOp`, so the promised AI analysis is not executable as labelled. The HTTP node targets `$env.BASE_URL` rather than clearly using the submitted landing-page URL. It includes a Gmail send node addressed to `hello@youremail.com`, plus external credentials references.
- Decision: **reject direct import**. Rebuild the SEO audit with an allowlisted URL, safe fetch limits, explicit content extraction, actual model node if chosen, structured output, and report preview. No automatic email or Shopify edits.

### 2. Google Analytics reporting template
- Upstream file: `workflows/Googleanalytics/1480_Googleanalytics_Code_Automation_Webhook.json`
- Upstream blob SHA: `a1968a949fed393b6e49c14656a3d8b4b9ef3ab3`
- Findings: hard-coded GA4 property ID `460520224`, credential IDs tied to another instance, workflow description proposes Baserow storage, and code logs full input data. The prior-period query in this file uses a fixed historical end date (`2024-10-23`). These are unsafe/stale defaults for Atlas.
- Decision: **reuse only the reporting idea**. Build a clean Atlas-specific read-only report using Atlas-authorised analytics connection, rolling date windows, no full-data debug logs, and synthetic comparison tests. Do not import credentials or the hard-coded property.

### 3. Scheduled Google Analytics report
- Upstream file: `workflows/Googleanalytics/0475_Googleanalytics_Code_Automate_Scheduled.json`
- Upstream blob SHA: `fc3d61ee911b6ba1ec52dd32d6dd03c2c84fdd3f`
- Findings: hard-coded property ID `420633845`, third-party credential IDs and labels, an email-reporting side effect, and analytics fields that may not be supported as configured. The workflow uses a third party's property (Kenetic Brand Builders) and is not Atlas-ready.
- Decision: **reject direct import**. Rebuild a report without email side effects and validate each GA4 metric/dimension against the authorised Atlas property.

### 4. Shopify order trigger
- Upstream file: `workflows/Shopify/1015_Shopify_Automate_Triggered.json`
- Upstream blob SHA: `22b01c33d4e1d53bd1d1fecbd88e1c39bd9310f9`
- Findings: contains an `orders/create` trigger with a credential alias but the `connections` object is empty. The workflow therefore has no connected path from the trigger to the error handler or any business logic.
- Decision: **reject as a functioning workflow**. If an order event workflow is needed later, build a new minimal trigger with verified signature/authentication, idempotency, least-privilege scopes and a dry-run sink.

### Validation status for this pass
- Four exact upstream JSON files retrieved and inspected individually.
- All four have a documented decision; none is approved for direct production import.
- No n8n instance is connected in this task, so no import/runtime execution test is claimed.
- The strongest immediate reusable patterns are the SEO audit checklist and week-over-week analytics comparison; both should be rebuilt natively with Atlas data access rather than copying the upstream JSON.


### Adaptation committed to ATLAS
- Added `src/seo/audit.ts`, a deterministic read-only SEO page audit inspired by the useful checklist concept from the upstream audit workflow.
- It accepts an already-supplied HTML snapshot; it does not fetch URLs, call an AI provider, email anyone, or modify Shopify.
- It restricts the supplied URL to HTTPS pages on `atlasgoodsstore.co.uk` and checks title, meta description, H1 count, canonical URL, noindex directives, and image alt attributes.
- It returns structured findings and always marks the report for human review.
- Commit: `c2b342a5f869e41a01903026f7e27c08af0f195f`.
- Validation caveat: the file is committed, but a TypeScript build, automated test run, and n8n import/runtime test have not been verified in this session. It must not yet be described as production-tested.
