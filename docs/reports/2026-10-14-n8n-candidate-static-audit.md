# ATLAS Workflow Candidate Audit — First Pass
Date: 14 October 2026
Repository: https://github.com/deanoo1801b/atlas-autonomous-commerce

## Scope
Inspected three representative JSON files from the public Zie619/n8n-workflows collection. This is a first-pass static review, not an exhaustive audit of the collection or an execution test. No workflow was imported into a live n8n instance and no production automation was activated.

## Findings

### 1. Low Stock & Sold Out Watcher for Shopify
Source: https://github.com/Zie619/n8n-workflows/blob/94007c1445d9258a7da116646b79473e7c7c3282/workflows/Code/0373_Code_Webhook_Automation_Webhook.json
Decision: **Do not import as-is; reuse the concept only.**

Issues found:
- Uses a public webhook trigger for inventory events; deployment would need authentication/verification and abuse protection.
- Contains placeholder credential references such as `YOUR_CREDENTIAL_HERE` and `{{ $env.API_BASE_URL }}`; not plug-and-play.
- Uses a GraphQL query pattern and fields that may be legacy or invalid for the current Shopify Admin API; must be rebuilt against the current schema/API version.
- References a credential identifier from the source author's instance; never reuse it.
- Posts inventory alerts to Discord, which would require an approved destination and configured credentials.
- Logic treats only exactly zero as out of stock and values 1–3 as low; it needs input validation, negative/null handling, duplicate alert suppression and per-supplier interpretation.
- Workflow notes suggest it is production-ready, but the JSON itself does not establish that it is safe or compatible with Atlas.

Safe reuse: event concept, low-stock/out-of-stock branching, alert-only intent. Rebuild using read-only current Shopify data, verified supplier mapping, audit events and a chosen alert channel.

### 2. Shopify order-created trigger sample
Source: https://github.com/Zie619/n8n-workflows/blob/94007c1445d9258a7da116646b79473e7c7c3282/workflows/Shopify/1015_Shopify_Automate_Triggered.json
Decision: **Do not import as-is.**

Issues found:
- The file has no connections between the trigger and error handler, so it does not demonstrate a functioning connected workflow.
- It references a source-instance credential alias `shopify_creds`; no credentials are included or portable.
- Its settings include retries but no clear idempotency key or duplicate-order protection.
- The node types/version and settings need compatibility checks against the target n8n release.
Safe reuse: a Shopify order event can be a trigger pattern, after wiring, permission scoping, deduplication and test-order validation.

### 3. Shopify-to-Odoo product sync
Source: https://github.com/Zie619/n8n-workflows/blob/94007c1445d9258a7da116646b79473e7c7c3282/workflows/Shopify/0961_Shopify_Filter_Create_Triggered.json
Decision: **Reject for Atlas's current needs; do not import.**

Issues found:
- Writes product data into Odoo; Atlas has not selected Odoo as a system of record.
- Contains a hard-coded external server address in credential metadata and source-instance credential references.
- Product mapping uses `variants[0].product_id` as a product code, which is likely an identifier mismatch and needs proof.
- Flow connections/logic should be reviewed; the existing-product filter and create/update behavior are not safe to assume correct.
- It performs external writes and is not relevant until an approved Odoo integration exists.
Safe reuse: only the general event-driven integration pattern, not the file.

## ATLAS starter created
File: [workflows/atlas-stock-availability-dry-run.json](../workflows/atlas-stock-availability-dry-run.json)

The new starter:
- Is inactive and uses a manual trigger.
- Uses synthetic example records only.
- Produces alert labels for tracked-zero stock and supplier-mapping review.
- Makes no Shopify requests and performs no external writes.
- Explicitly flags that it is a dry-run scaffold, not a live integration.

## Required before any production import
- Confirm the target n8n instance/version and whether n8n is already deployed.
- Create scoped credentials directly in n8n; never store tokens in GitHub or exported workflow JSON.
- Rebuild Shopify queries against the current Admin GraphQL schema/API version and test read-only.
- Confirm supplier app/SKU/location mapping for each product; do not infer Gelato linkage from app installation alone.
- Add idempotency/deduplication, timeouts, retry limits, structured audit logs and error notifications.
- Test valid, null, zero, negative, duplicate and unavailable supplier records.
- Verify alert recipients and avoid unnecessary customer data.
- Keep workflows inactive until the user-approved deployment and test plan is complete.

## Result
First-pass static review completed for three representative candidates. One safe synthetic dry-run scaffold has been added to the ATLAS repository. No live workflows were deployed or activated; no Shopify settings or inventory were changed.
