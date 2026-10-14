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
