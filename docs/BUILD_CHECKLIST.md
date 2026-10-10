# ATLAS Build Checklist

## Phase 1 — Foundation
- [x] Define the £1M business objective
- [x] Name the master AI: ATLAS
- [x] Define the agent hierarchy
- [x] Identify Atlas Goods Store as the primary store
- [x] Confirm Shopify connection
- [x] Confirm GitHub connection
- [x] Create GitHub repository (visibility currently public; private conversion requires owner approval)
- [x] Create ATLAS repository
- [x] Create initial project structure
- [x] Create master agent instructions
- [x] Create configuration/environment system
- [x] Create logging and audit system

## Phase 2 — Agent Team
- [ ] Market Research Agent
- [x] Product Opportunity & Evidence Agent
- [ ] Shopify Product Agent
- [ ] SEO & Copy Agent
- [ ] Creative/Content Agent
- [ ] Short-Form Video Agent
- [ ] Profit & Pricing Agent
- [ ] Analytics Agent
- [ ] Growth Agent
- [ ] Experiment/Testing Agent
- [ ] Supplier Agent
- [x] Agent Manager
- [x] Content Selection Gate — evidence required before video creation

## Phase 3 — Shopify
- [ ] Connect Shopify API
- [x] Define read-only Shopify adapter contract
- [x] Read product catalogue via connected Shopify integration (363 products reported; standalone runtime connection still pending)
- [ ] Read inventory
- [x] Read sales analytics via connected Shopify integration (initial 31-day snapshot; standalone runtime connection still pending)
- [ ] Read product performance
- [x] Test read-only retrieval through connected Shopify integration
- [ ] Test authenticated data retrieval from standalone ATLAS runtime
- [ ] Analyse catalogue (initial baseline recorded; full product/fulfilment audit pending)
- [x] Define Opportunity Report model
- [ ] Generate first live Profit Opportunity Report
- [ ] Enable controlled product creation
- [ ] Enable controlled product updates
- [ ] Enable controlled inventory updates

## Phase 4 — Product Factory
- [ ] Digital products
- [ ] PDF workbooks
- [ ] Templates
- [ ] Printables
- [ ] Business toolkits
- [ ] AI prompt packs
- [ ] Kids' activity products
- [ ] Physical-product opportunities
- [ ] Bundles
- [ ] Upsells
- [ ] Subscription/membership opportunities

## Phase 5 — Marketing Engine
- [ ] Google & YouTube
- [ ] Shop
- [ ] TikTok
- [ ] Facebook/Instagram
- [ ] Pinterest
- [ ] Organic content
- [ ] Paid advertising
- [ ] Retargeting
- [ ] Email capture
- [ ] Email marketing
- [ ] Affiliate/creator strategy

## Phase 6 — Profit Engine
- [ ] Calculate maximum allowable CAC
- [ ] Calculate break-even ROAS
- [ ] Identify consistently unprofitable products
- [ ] Improve borderline products
- [ ] Scale demonstrated winners
- [ ] Define controlled reinvestment rules

## Phase 7 — Autonomous Improvement
- [ ] Daily performance analysis
- [ ] Identify opportunities
- [ ] Generate experiments
- [ ] Measure results
- [ ] Learn from failures
- [ ] Update strategy
- [ ] Repeat

## Phase 8 — Controlled Agent Replication
- [ ] ATLAS can propose a new specialist
- [ ] Define specialist job
- [ ] Give limited budget
- [ ] Give limited permissions
- [ ] Measure revenue/cost
- [ ] Shut down failing agents
- [ ] Fund successful agents
- [ ] Allow successful agents to propose further specialists

## Phase 9 — £1M Revenue System
- [ ] Track £1,000
- [ ] Track £10,000
- [ ] Track £50,000
- [ ] Track £100,000
- [ ] Track £250,000
- [ ] Track £500,000
- [ ] Track £1,000,000
- [ ] Distinguish revenue vs profit at every stage

## Phase 5A — Social Media Management
- [ ] Social Media Manager Agent — daily monitoring of connected channels
- [ ] Daily content calendar health check
- [ ] Daily post/publishing status check
- [ ] Daily engagement and audience signal review
- [ ] Daily social traffic and conversion signal review
- [ ] Cross-channel issues/failed-post detection
- [ ] Link social performance to Shopify/commerce analytics
- [ ] Generate daily social media report for ATLAS


## Phase 1B — ATLAS Runtime Infrastructure
- [x] Create typed runtime configuration
- [x] Define safety defaults: dry-run and approval gates
- [x] Create structured audit event model
- [x] Create initial agent registry
- [x] Persist audit events
- [x] Build orchestration/task runner
- [x] Add agent health/status tracking


## Autonomous Commerce Specialist Layer

The specialist layer is now defined for competitor intelligence, customer demand mining, SEO opportunities, pricing/margin, fulfilment, revenue/profit, customer support/reviews, email retention, bundling/recommendations and product lifecycle management.

All specialist outputs feed the central Opportunity Report and ATLAS Decision Gate rather than operating as uncontrolled independent publishers.

## Phase 1C — Executable Runtime
- [x] Implement dry-run runtime entrypoint
- [x] Implement central agent registry
- [x] Implement JSONL audit-event persistence
- [x] Implement agent health/status checks
- [x] Enforce dry-run as the runtime default
- [x] Add read-only Shopify/Metricool adapter contracts
- [x] Add Opportunity Report persistence
- [x] Add controlled scanner execution
- [x] Add approval queue persistence
- [x] Define approval request model
- [x] Add experiment/result persistence


## Phase 1D — Social Intelligence Runtime
- [x] Instagram growth & monetisation intelligence layer
- [x] Social pipeline orchestration
- [x] Opportunity scanner persistence
- [x] Approval queue persistence
- [x] Experiment/result persistence
- [ ] Connect live Shopify data into scanner
- [ ] Connect live Metricool data into scanner
- [ ] Add authenticated scheduled execution


## Phase 1E — First Live Read-Only Baseline
- [x] Verify connected Shopify shop context
- [x] Retrieve recent product sample and total catalogue count
- [x] Query last 31 days of sales analytics
- [x] Save baseline report to docs/reports/2026-10-10-shopify-baseline.md
- [ ] Independently verify order count and analytics consistency
- [ ] Inspect sessions, cart, checkout and conversion data
- [ ] Audit inventory/fulfilment semantics before flagging zero-stock items
- [ ] Generate ranked Opportunity Report with verified evidence
