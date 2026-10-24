# ATLAS SEO Autopilot — Strategy and Safe Implementation

Status: design specification; not yet a live publishing automation.

## Purpose
Improve Atlas Goods Store's organic visibility in traditional search and AI-assisted discovery through useful content, technical SEO, product/collection optimization, and legitimate digital PR. This adapts the ideas in the Visibly AI advertisement as a strategy, not as a promise that ATLAS can deliver 30 articles or 100 backlinks every month immediately.

## Operating principles
- Start with measurement and read-only audits. Do not publish, edit live pages, send outreach, or purchase links without an explicit approval gate.
- Never promise rankings, traffic, sales, AI citations, a specific Domain Authority score, or a fixed backlink count.
- Do not buy links, use private blog networks, automate spam comments, mass-submit directories, or generate pages solely to manipulate rankings.
- Prefer original, useful, product-relevant content and genuine editorial links. Third-party Domain Authority metrics are estimates, not Google ranking factors.
- Do not invent product attributes, certifications, delivery promises, discounts, reviews, or supplier claims.
- Respect UK consumer law, platform rules, copyright, privacy, and email marketing requirements.
- Keep audit results, sources, approvals, publication URLs, and rollback notes in an auditable log.

## Agent modules
1. **SEO Master / Overlord** — ranks work by expected impact, effort, confidence, and risk; deduplicates issues; prevents agents from editing the same URL at once; requires approval for live changes.
2. **Technical SEO Auditor** — checks status codes, redirects, canonical tags, robots/noindex, sitemap, indexability, broken internal links, metadata, structured data, mobile usability signals, and Core Web Vitals where data is available.
3. **Keyword and Intent Researcher** — maps queries to search intent and relevant existing product, collection, or guide URLs; identifies cannibalization and content gaps.
4. **Shopify On-page Agent** — proposes title, meta description, headings, internal links, image alt text, and product/collection copy improvements. All claims must be grounded in current Shopify product data.
5. **Editorial Content Agent** — creates evidence-based briefs and drafts (buying guides, comparisons, FAQs, care/use guides, and category guides). Each piece must have a clear user need, unique value, sources for factual claims, a target URL, internal links, and a human-readable author/review policy.
6. **Digital PR and Backlink Researcher** — finds relevant publications, resource pages, supplier/brand partnerships, journalists, and legitimate outreach opportunities. It proposes prospects and personalized drafts only; it must not send messages automatically without approval.
7. **SEO QA Agent** — checks factual accuracy, duplication, search intent, links, metadata, schema validity, readability, accessibility, and policy risks before publication.
8. **Analytics Agent** — compares Search Console and analytics performance over consistent periods; distinguishes impressions, clicks, CTR, average position, sessions, conversions, and revenue; flags anomalies without claiming causation.
9. **Monthly Report Agent** — reports completed work, pending approvals, technical issues, published URLs, earned links, results, confidence, and next priorities.

## Content production cadence
- Begin with a baseline audit and a small pilot: up to 2–4 high-quality pieces per month, depending on research capacity and available evidence.
- Increase only after QA demonstrates quality and the team can sustain useful, non-duplicative content.
- Treat 30 articles/month as an optional future capacity target, not a quota. Never pad output to meet a number.
- Prioritize improvements to existing high-intent product and collection pages before creating large numbers of new URLs.

## Backlink / authority policy
- Target relevance, editorial independence, real audience, and referral value—not a promised third-party authority score.
- Build opportunities through useful resources, original data, expert commentary, supplier/brand relationships, local/business citations where appropriate, and genuine partnerships.
- Record the source domain, contact rationale, outreach approval, link URL, link type, relevance, and status.
- Reject paid link schemes, guaranteed-DA packages, bulk link drops, irrelevant placements, and any service unwilling to disclose its methods.
- A target of 100 links per month must never be treated as a required KPI. Count earned, relevant placements only, and report quality before quantity.

## Approval gates
- **Read-only:** audits and recommendations may run automatically.
- **Draft:** content and outreach drafts may be generated and saved for review.
- **Publish:** requires human approval of the exact URL, copy, metadata, media, and claims.
- **Outreach:** requires human approval of recipients and message before sending.
- **High-risk changes:** robots.txt, canonical changes, redirects, theme code, structured data affecting many URLs, bulk product edits, and removal/noindex actions require explicit review and a rollback plan.

## Initial implementation checklist
- [ ] Record current organic baseline and export available Search Console data.
- [ ] Crawl public storefront and inventory the important product, collection, and informational URLs.
- [ ] Map keywords to existing URLs and identify cannibalization before proposing new pages.
- [ ] Prioritize fixes by impact, confidence, effort, and risk.
- [ ] Generate a limited pilot content brief and draft for human review.
- [ ] Build a reviewed digital-PR prospect list; do not send outreach automatically.
- [ ] Validate each draft with QA and record approval before publication.
- [ ] Measure results after publication using comparable date ranges.

## Dependencies and current limitations
This specification does not itself connect Search Console, install an n8n server, provide Metricool API access, or publish to Shopify. These integrations must be configured and tested separately. Any automated job must fail safely if credentials, source data, or approval state are missing.

## Success measures
Use qualified organic clicks, relevant impressions, CTR, indexed eligible pages, conversion rate, revenue attributable where measurable, helpful content quality, relevant earned editorial links, and resolved technical issues. Domain Authority/Domain Rating can be tracked as third-party diagnostic metrics only—not as a guaranteed outcome or primary success measure.
