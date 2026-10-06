# CBS Agent Architecture

1. CBS Orchestrator — owns pipeline state, evidence, approvals and audit trail.
2. Amazon Trend & Demand Agent — finds current Amazon/KDP category signals, bestseller movement, search-intent clues, reviews and recurring customer requests.
3. Competitor Gap Agent — analyses positioning, audience, format, page count, visual promise, pricing, reviews and unmet needs without reproducing protected content.
4. Concept & Differentiation Agent — turns validated opportunities into original concepts, titles, audiences, art direction and value propositions.
5. Interior Production Agent — creates structured page specifications for original coloring pages with consistent line-art style and variety.
6. Interior QA Agent — checks page count, duplicates, margins, bleed, line quality, resolution, readability and export requirements.
7. Cover & Metadata Agent — creates cover briefs and KDP metadata, keywords, categories, audience and pricing tests.
8. KDP Compliance Gate — checks the package against current KDP requirements and blocks release when evidence is missing.
9. Shopify Listing Agent — converts approved books into Shopify digital products for Atlas Goods Store.
10. Performance & Learning Agent — reads approved Amazon/Shopify performance data and feeds lessons back into opportunity scoring.
11. Rights & Originality Agent — flags obvious IP-risk patterns and blocks concepts dependent on copying.
12. Portfolio & Series Agent — expands validated winners into coherent series and bundles without near-duplicate books.
13. Asset/Export Agent — maintains production manifests and final interior/cover packages.
14. Agent Manager — ATLAS-level manager controlling budgets, permissions, health, retries and shutdown rules.

All agents emit structured evidence and never silently publish or spend money.
