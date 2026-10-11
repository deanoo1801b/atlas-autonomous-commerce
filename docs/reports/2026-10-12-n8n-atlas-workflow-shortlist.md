# ATLAS n8n Workflow Research — Shortlist
Date: 12 October 2026
Target: Atlas Goods Store (atlasgoodsstore.co.uk)
Research source: Zie619 n8n workflow collection, advertised as 4,343 workflow JSONs across 15 categories, plus current public n8n workflow templates.

## Important scope note
This is a targeted, relevance-first shortlist from searches across the collection and current n8n template library, not a manual audit of all 4,343 JSON files. Candidate templates must be inspected, adapted, security-reviewed and tested in a sandbox before import. Public templates can contain stale API versions, hard-coded examples, incorrect assumptions or risky live actions.

## Priority shortlist

| Priority | Workflow / source | Best use for ATLAS | Decision |
|---|---|---|---|
| P0 | [Low Stock & Sold Out Watcher for Shopify](https://github.com/Zie619/n8n-workflows/blob/94007c1445d9258a7da116646b79473e7c7c3282/workflows/Code/0373_Code_Webhook_Automation_Webhook.json) | Alert on low/zero stock and flag products that are unavailable | Adapt after verifying supplier/location mapping; alert-only, no automatic inventory edits |
| P0 | [AI-powered product research & SEO content automation #5195](https://n8n.io/workflows/5195-ai-powered-product-research-and-seo-content-automation/) | Competitor-informed product SEO title, description and keyword research | Good candidate; require source links, claims checks and draft output |
| P0 | [Shopify multi-module automation #4455](https://n8n.io/workflows/4455-shopify-multi-module-automation-with-gpt-4o-langchain-agents-and-integrations/) | Reference architecture for support, recommendations, cart recovery, low-stock alerts, review monitoring and marketing | Study as a modular pattern; do not import as one uncontrolled mega-workflow |
| P1 | [AI-powered competitor research with Exa, Notion and agents #2354](https://n8n.io/workflows/2354-automate-competitor-research-with-exaai-notion-and-ai-agents) | Competitor products, reviews and positioning summaries | Adapt; preserve source URLs and date every finding |
| P1 | [Shopify product posting to Instagram/Facebook/X #14969](https://n8n.io/workflows/14969-post-new-shopify-products-to-instagram-facebook-and-x-with-openai-and-airtable/) | Turn products into platform-specific social posts and log duplicates | Draft-first; publishing requires an approved content gate and connected publishing accounts |
| P1 | [Shopify product-to-SEO-blog #12286](https://n8n.io/workflows/12286-turn-new-shopify-products-into-seo-blogs-with-perplexity-gemini-and-sheets/) | Turn selected products into researched blog drafts | Draft-only initially; add originality, factual, SEO and product-link QA before publishing |
| P1 | [Abandoned Shopify checkout recovery #17053](https://n8n.io/workflows/17053-recover-abandoned-shopify-carts-with-gmail-whatsapp-and-slack-alerts/) | Recheck checkout conversion and prepare recovery message; includes error alerting | Keep disabled until checkout data is available, consent/legal basis and sender setup are verified; never message if already converted |
| P1 | [Evidence-first audience insights from YouTube comments #20206](https://n8n.io/workflows/20206-turn-youtube-comments-into-audience-insights-with-youtube-api-and-google-gemini/) | Mine repeated questions, objections and product/content ideas | Useful for content intelligence; only relevant channels/topics, store evidence IDs and source links |
| P1 | [Error Trigger alert workflow #10755](https://n8n.io/workflows/10755-simple-error-workflow/) | Notify ATLAS operator when a scheduled workflow fails | Implement early; include workflow name, execution URL, severity and deduplication |
| P2 | [Shopify ↔ Airtable product/inventory sync #7468](https://n8n.io/workflows/7468-sync-products-between-airtable-and-shopify-with-inventory-management/) | Pattern for product data reconciliation | Do not use to write stock until Airtable is formally chosen as source of truth; current store has supplier/location uncertainty |
| P2 | [Buyer objections mining #19404](https://n8n.io/workflows/19404-mine-youtube-buyer-objections-with-bright-data-openai-google-sheets-and-slack/) | Extract price, trust, usability and feature objections from competitor review comments | Good research input; verify Bright Data costs/terms and avoid treating comments as representative statistics |

## Recommended build order
1. **Operational safety and alerts:** error handler, run logs, retry limits, idempotency keys, credential separation and alert deduplication.
2. **Availability/fulfilment monitor:** read-only inventory and supplier-location reconciliation; alert when an active product cannot be bought. Do not auto-enable overselling or invent stock.
3. **Commerce analytics digest:** orders, revenue, sessions, cart/checkout, product availability and traffic source in one daily report; distinguish zero data from tracking failure.
4. **Product/competitor research:** evidence-backed demand score with source URLs, freshness, confidence, UK availability/fulfilment, margin and risk.
5. **SEO and content drafts:** product copy, FAQ, blog/social drafts; duplicate checks and human approval before publishing.
6. **Social distribution:** queue approved content; publish only when connected account permissions, brand calendar and platform constraints are verified.
7. **Cart recovery:** only after real checkout events are confirmed; recheck order status and stock before each message, deduplicate, respect consent and suppression lists.
8. **Controlled experiments:** propose tests and measure results; no ad spend, discounts or price changes without approval.

## ATLAS integration rules
- Use Shopify as the authoritative source for orders and storefront product records; use the actual supplier/POD app as authority for supplier availability until mapping is verified.
- The current Shopify audit found some active variants with tracked zero inventory and policy DENY. The correct fix depends on actual supplier linkage; do not blindly set quantities or enable “continue selling when out of stock.”
- All workflows start in manual test/dry-run mode. Use synthetic/test data first, then read-only production observation.
- Keep credentials in n8n credentials/environment secrets; never export secrets into workflow JSON or GitHub.
- Every workflow needs owner, purpose, trigger, inputs/outputs, permissions, cost estimate, failure path, audit log, duplicate protection and rollback/disable instructions.
- Add an approval gate before product creation/update, publishing, customer outreach, discounts, inventory changes or any paid API/media/ad action.
- Avoid duplicate agents: make these modular n8n workflows invoked by ATLAS rather than creating a separate autonomous agent for every task.

## Collection and search entry points
- Collection repository: https://github.com/Zie619/n8n-workflows
- Searchable catalogue: https://zie619.github.io/n8n-workflows
- Repository advertises 4,343 workflows, 365 integrations and 15 categories. These are maintainer-reported collection statistics, not independent quality or security guarantees.

## Next validation tasks
- [ ] Download and inspect candidate workflow JSONs for credentials, stale API versions, destructive nodes, external endpoints, prompt injection exposure and node compatibility.
- [ ] Score candidates for Atlas fit, maintenance burden, security, operating cost and measurable value.
- [ ] Import only the P0 candidates into a non-production n8n workspace for dry-run tests.
- [ ] Record selected workflow IDs, adapted versions, required credentials and test evidence.
- [ ] Do not mark a workflow production-ready until a successful test and failure-path test are documented.
