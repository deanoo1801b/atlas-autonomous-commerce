# Atlas Activepieces Automation Rollout

## Decision

Use Activepieces as the preferred self-hosted workflow engine for Atlas Goods Store. Its core is MIT-licensed and its Shopify integration is available in self-hosted deployments. Official references:
- https://github.com/activepieces/activepieces
- https://www.activepieces.com/pieces/shopify
- https://www.activepieces.com/docs/about/license
- https://github.com/activepieces/activepieces/blob/main/docs/install/options/docker-compose.mdx

## Current state

This file records the selected platform and safe rollout plan. Activepieces is **not yet deployed**: this repository does not provide a running Docker host, persistent database/Redis service, or a configured public HTTPS endpoint. GitHub Actions is not a persistent host for the Activepieces web application.

## First workflows (read-only / no external side effects)

1. **Public Store Health** — monitor HTTPS status, title, meta description, and noindex state for atlasgoodsstore.co.uk.
2. **Shopify Read-only Audit** — read active products and essential listing fields; report missing/weak titles, descriptions, images/alt text, and availability. Do not edit listings or inventory.
3. **Analytics Summary** — compare supplied analytics periods and report sessions, add-to-carts, checkouts, orders and revenue without sending alerts by default.
4. **Metricool Connection Check** — use the existing authorised Metricool connection where supported. Do not purchase API access or scrape private endpoints.
5. **Approval Queue** — prepare suggested changes for human review; never publish, message customers, change prices, or alter stock automatically.

## Security requirements

- Store credentials only in Activepieces encrypted connections or the hosting provider's secret manager; never commit credentials or put them in chat.
- Shopify access must be limited to the minimum required read scopes for initial testing.
- Keep public workflows read-only until their output has been checked.
- Require explicit human approval for writes, public posts, customer contact, pricing, stock changes, and order actions.
- Use HTTPS and a persistent database; back up the Activepieces configuration and database separately.
- Pin reviewed workflow versions and audit imported JSON before enabling.

## Deployment gate

Before deployment, choose/confirm a persistent host with Docker Compose v2, secure HTTPS/domain, and persistent storage. Then follow the upstream official Docker Compose instructions to generate environment secrets and launch Activepieces. Do not expose an unauthenticated instance to the public internet.

## Acceptance checks

- Health endpoint and UI respond over HTTPS.
- Database and Redis remain healthy after restart.
- Shopify connection can read the shop and active-product count.
- First flows produce reports only and do not modify Shopify.
- Failed runs show actionable logs without logging credentials.
