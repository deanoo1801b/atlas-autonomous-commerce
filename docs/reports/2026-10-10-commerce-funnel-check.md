# ATLAS Commerce Funnel Check — 10 October 2026

## Scope
Read-only Shopify integration queries for 10 September–10 October 2026. No store changes were made.

## Verified findings
- Shopify order lookup returned totalCount = 0.
- Sales analytics returned 0 orders and 0 sales across the 31-day period.
- Sessions analytics returned 201 sessions in the period.
- Funnel analytics returned one session with an add-to-cart event, one session reaching checkout, and zero completed checkouts.
- Session source is the connected Shopify analytics integration for shop domain `gjb4b5-nz.myshopify.com`. Confirm that this is the intended Atlas Goods Store before treating the figures as final business-wide reporting.
- Product-grouped sales query returned no rows.

## Interpretation
There is some measured store traffic, but the observed funnel has not produced completed orders. The sample is small (201 sessions over 31 days), so avoid overinterpreting day-to-day variation. The immediate priorities are verifying the connected store/domain, checking the customer purchase journey and checkout readiness, and improving qualified traffic only after the purchase path has been tested.

## Priority actions (recommendations only)
1. Confirm the Shopify Admin store behind the connected domain is the intended live store.
2. Test the storefront as a customer: open a product, select variants, add to cart, proceed to checkout, and verify shipping/payment options. Do not submit a real payment during a test.
3. Check active product publication to Online Store and product/variant availability, including the supplier fulfilment method for zero-inventory listings.
4. Inspect shipping rates, payment-provider status, checkout settings, delivery expectations and trust/policy pages.
5. Verify analytics tracking is recording cart and checkout events correctly.
6. After the above checks, test a small number of high-intent product pages and monitor add-to-cart and checkout progression.

## Controls
No products, prices, inventory, orders, settings, marketing budgets, or publishing status were changed. This is a diagnostic report, not proof of a specific checkout fault.
