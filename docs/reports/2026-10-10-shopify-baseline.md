# Shopify Baseline Check — 10 October 2026

## Source and method
Read-only inspection through the connected Shopify integration. This report is an initial baseline, not a full catalogue audit. The standalone ATLAS repository runtime is not yet authenticated directly to Shopify.

## Store context
- Store name: Atlas goods store
- Store domain configured for the business: atlasgoodsstore.co.uk
- Currency: GBP
- Country: United Kingdom
- Plan: Shopify Basic

## Catalogue snapshot
- Total products reported by Shopify: 363
- A recent-products sample included both ACTIVE and DRAFT products.
- The sampled product records returned total inventory of 0 for the displayed items. This needs verification against supplier fulfilment/inventory tracking before taking action; zero Shopify inventory may be intentional for print-on-demand or externally fulfilled products.
- Do not automatically publish drafts or alter inventory based only on this snapshot.

## Sales snapshot
Shopify analytics query: sales orders, gross sales, net sales and total sales, daily timeseries, 10 September 2026 through 10 October 2026.

- Orders returned: 0 on each of the 31 daily rows.
- Gross sales: 0.00 in the returned analytics summary.
- Net sales and total sales: 0 on each returned daily row.

This is a serious signal to investigate, not proof of the cause. Possible explanations include genuinely no orders, analytics/reporting configuration, a new or recently reset reporting period, or a store/domain mismatch. Confirm in Shopify Admin and compare with order records before making strategic decisions.

## Prioritised next checks
1. Verify the connected Shopify store/domain matches the live public store.
2. Read order counts independently of the sales analytics report.
3. Audit active products for inventory tracking, fulfilment model, product status and sales-channel publication.
4. Check online-store sessions, add-to-cart, checkout and conversion data for the same period.
5. Calculate unit economics only after supplier cost, shipping, fees and fulfilment costs are available.
6. Build the first evidence-backed Opportunity Report after these checks.

## Safety
Read-only inspection only. No products, prices, inventory, orders, settings, marketing budgets or publications were changed.
