# ATLAS Commerce Funnel Check — 10 October 2026

## Scope
Read-only Shopify integration queries for 10 September–10 October 2026. No store changes were made.

## Verified findings
- Shopify order lookup returned totalCount = 0.
- Sales analytics returned 0 orders and 0 sales across the 31-day period.
- Sessions analytics returned 201 sessions in the period.
- Funnel analytics returned one session with an add-to-cart event, one session reaching checkout, and zero completed checkouts.
- Device breakdown: desktop 142 sessions, mobile 57, other 2.
- Country breakdown: United States 138 sessions; Rwanda 14; Canada 6; Brazil 5; India 5; France 5; Ireland 4; Tanzania 4; United Kingdom 4; other countries 19.
- Social referrer report attributed only 2 sessions: one Facebook and one Instagram.
- Product catalogue query reported 363 products total: 353 active and 10 draft. These are Shopify product statuses, not confirmation that every active product is published to the Online Store sales channel.
- Recent sampled products show inventory quantity 0. This may be normal for print-on-demand or supplier-fulfilled products; do not mark them unavailable until tracking and fulfilment configuration is checked.
- Session and funnel analytics identify the underlying shop domain as `gjb4b5-nz.myshopify.com`; the Shopify shop-info call returns `atlasgoodsstore.co.uk`. Confirm these identify the intended live store before treating the analytics as definitive business-wide reporting.

## Interpretation
Traffic exists, but the observed funnel has not produced completed orders. The sample is small (201 sessions over 31 days). Most sessions are reported from the United States while the store is configured for the United Kingdom and GBP; this could reflect genuine international interest, low-intent traffic, VPNs, or analytics noise. Only four sessions were attributed to the UK, and only two were attributed to social referrers. Validate geography and tracking before changing marketing strategy.

## Priority actions (recommendations only)
1. Confirm the connected Shopify Admin and analytics shop are the intended live store/domain.
2. Test the storefront as a customer: open a product, select variants, add to cart, proceed to checkout, and verify shipping/payment options. Do not submit a real payment during a test.
3. Check active product publication to Online Store and product/variant availability, including supplier fulfilment and inventory-tracking settings for zero-inventory listings.
4. Inspect shipping rates, payment-provider status, checkout settings, delivery expectations and trust/policy pages.
5. Verify analytics tracking is recording cart and checkout events correctly, and inspect traffic geography/referrers for bot, VPN, or low-intent traffic patterns without assuming any one cause.
6. Review mobile usability: mobile accounts for 57/201 sessions (28.4%), so test mobile product pages and cart as well as desktop.
7. Once the purchase path and measurement are verified, test a small number of high-intent product pages and monitor add-to-cart and checkout progression.

## Controls
No products, prices, inventory, orders, settings, marketing budgets, or publishing status were changed. This is a diagnostic report, not proof of a specific checkout fault.
