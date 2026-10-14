# Live Shopify + Metricool Runtime Connection

This check uses read-only calls and never publishes, schedules, edits products, or changes account settings.

## GitHub Actions secrets required

Open repository Settings -> Secrets and variables -> Actions and add:

- `SHOPIFY_STORE_DOMAIN`: the store's `.myshopify.com` domain (currently recorded as `gjb4b5-nz.myshopify.com`)
- `SHOPIFY_ADMIN_ACCESS_TOKEN`: Shopify Admin API token from a custom app with the minimum read scopes needed for shop and product-count queries (at least `read_products`)
- `METRICOOL_API_TOKEN`: Metricool API token from Account Settings -> API (Metricool API access is plan-dependent)
- `METRICOOL_USER_ID`: numeric Metricool user ID

Never put tokens in source files, commit messages, issue comments, or chat.

## Metricool brand requirement

The token must belong to the intended Metricool account, and that account must include a brand named Atlas Goods / AtlasGoodsStore. The health check deliberately blocks if no Atlas brand is found; it does not use another brand as a substitute.

## Run and verify

After adding secrets, open Actions -> ATLAS Live Connector Health Check -> Run workflow. The workflow also checks every six hours. A successful run means both read-only connectors authenticated. A failed run will show which connector is blocked without printing credentials.

## Current limitation

The ChatGPT Shopify connector can already read Atlas Goods Store, but that connection does not automatically transfer its credentials into GitHub Actions. GitHub Actions needs its own secret. The current Metricool account visible to this integration has not exposed Atlas Goods, so reconnect/add Atlas Goods in Metricool before the check can pass.

## Safety

This workflow is read-only, does not publish posts, does not edit Shopify, and does not write data to the store. Live publishing remains a separate approval-gated step.
