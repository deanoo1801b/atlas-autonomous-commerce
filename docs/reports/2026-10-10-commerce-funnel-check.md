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

## Follow-up verification — 10 October 2026
- The Shopify Admin API confirms the connected shop is **Atlas goods store**, its `myshopify.com` domain is `gjb4b5-nz.myshopify.com`, and its primary domain is `https://atlasgoodsstore.co.uk`. The domain mismatch is therefore expected Shopify architecture, not evidence of the wrong store.
- The Admin API returned zero abandoned checkouts (exact count) and no checkout records in the latest 10. This differs from the session analytics' one session reaching checkout; these may measure different events/stages, so event tracking and checkout entry need validation.
- Product publication and saleability were checked for the 10 most recently updated active products. All 10 have an Online Store URL and publication timestamp. However, **5 of the 10 sampled active products had tracked inventory enabled, total inventory 0, and all sampled variants returned `availableForSale: false` with inventory policy `DENY`**. The other 5 sampled products had inventory tracking disabled and their sampled variants returned `availableForSale: true`.
- This is a confirmed availability problem for the affected sample, not just a generic zero-stock warning. It could prevent customers from buying those items. It is not yet established whether those products are supplier-stocked or print-on-demand, so inventory must not be fabricated or overselling enabled blindly.
- The store's configured shipping zones include the UK and several international markets including the US. This does not prove that the appropriate rate is available for each product/fulfilment location.


- Follow-up inventory-level queries for three unavailable examples (the children's vehicle mug, hot-pink graphic hoodie, and lion graphic T-shirt) showed every variant has available = 0, committed = 0, onHand = 0 at the single location `Atlas Goods Store - UK Online Fulfilment`. This confirms there is no stock currently recorded at that Shopify location for those examples. The supplier's real stock/production model remains unverified.

## Evidence-based fix path (no changes made)
1. For each tracked zero-inventory product, identify its supplier/fulfilment app and the location that fulfils online orders; sync the supplier's real available quantity and confirm that location has valid shipping rates.
2. For genuinely made-to-order/POD items, configure the supplier integration and Shopify inventory tracking according to the supplier's documented fulfilment model. Only allow sales with zero stock if the supplier can fulfil orders reliably; Shopify documents this as the "Continue selling when out of stock" setting, but it should not be enabled as a blanket fix.
3. Confirm each affected variant returns `availableForSale: true` after the correct supplier/inventory configuration and test adding it to cart.
4. Place a non-charged test order using Shopify's payment test mode only after the payment provider setup is understood. Test mode prevents live credit-card orders while active, so deactivate it after testing.
5. Investigate why session analytics records one checkout-start session while the Admin API has no abandoned checkout records. Do not treat this mismatch alone as proof of a broken checkout.
