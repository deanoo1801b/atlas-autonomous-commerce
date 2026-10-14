# Live Shopify + Metricool Runtime Connection

Last reviewed: 2026-10-14.

## What is verified directly in ChatGPT

- Shopify connector: authenticated and returning the Atlas Goods Store shop record.
- Metricool connector: authenticated and returning the Atlas goods store brand, brand ID/blog ID 7424343.
- Atlas brand networks returned by Metricool: Facebook, Instagram (@atlasgoodsstoreuk), Pinterest (AtlasGoodsStore), and TikTok (@atlasgoodsstore).
- Metricool scheduled-post check for 2026-10-14 through 2026-10-21 returned no scheduled posts.

These checks prove that the connected ChatGPT tools can read the shop and Metricool brand. They do not prove that GitHub Actions has separate credentials or that social publishing has been tested end-to-end.

## GitHub Actions secrets required for the separate runtime

Open repository Settings -> Secrets and variables -> Actions and add:

- `SHOPIFY_STORE_DOMAIN`: `gjb4b5-nz.myshopify.com`
- `SHOPIFY_ADMIN_ACCESS_TOKEN`: Shopify Admin API token from a custom app with the minimum read scopes required by the health check (shop data and product count; typically `read_products`).
- `METRICOOL_API_TOKEN`: Metricool API token from Account Settings -> API. Metricool's external API requires an Advanced or Custom plan.
- `METRICOOL_USER_ID`: numeric Metricool user ID.

Never put tokens in source files, commit messages, issue comments, or chat.

## Run and verify

After adding secrets, open Actions -> ATLAS Live Connector Health Check -> Run workflow. The workflow also checks every six hours. A successful run means both read-only connectors authenticated and the health check found the Atlas brand. A failed run will report which connector is blocked without printing credentials.

## Current limitation

ChatGPT's Shopify and Metricool connections do not automatically transfer their credentials into GitHub Actions. The GitHub workflow cannot pass until the four required secrets are configured in the repository. The health-check script defaults to Shopify Admin GraphQL API version 2026-10 (the latest stable version at the time of review), and applies a 15-second timeout to both external requests.

## Safety

This workflow is read-only: it does not publish posts, edit Shopify products, or change account settings. Live publishing remains a separate approval-gated step. Do not enable autonomous public posting until product availability, URL, market, claims, platform disclosure, and final review gates are implemented and tested.
