# Inspiration Properties UK — Agent System

Controlled-autonomy layer for the property and finance lead engine.

Pipeline:
Discover -> Verify -> Deduplicate -> Classify -> Score -> Qualify -> Compliance -> Human Approval -> Refer -> Track

Agents:
Private Seller Finder, Motivated Seller Detector, Lead Finder, Verification, Deduplication, Lead Scorer, Finance Classifier, Deal Strategist, Finance Qualifier, Compliance Guard, Buyer Matcher, Pipeline Manager, Social Content, Orchestrator.

Safety:
No autonomous calls, WhatsApp messages, emails, finance applications, property purchases, regulated mortgage arranging, or financial-promotion publishing. Newly discovered finance cases default to Amber until verified and reviewed.

Runtime secrets:
SMARTSHEET_API_TOKEN
PROPERTY_LEADS_SHEET_ID
FINANCE_OPPORTUNITIES_SHEET_ID

Sheet configuration:
The engine reads both Smartsheet IDs from GitHub Actions secrets at runtime; IDs are intentionally not hard-coded in the engine.
- PROPERTY_LEADS_SHEET_ID: current live Property Leads sheet ID is 3007077934124932
- FINANCE_OPPORTUNITIES_SHEET_ID: current live Finance Opportunities sheet ID is 890673877438340


## Planning & Development Opportunity Detector

The planning adapter queries the Planning Data API for England using the candidate postcode. It looks for planning records that mention bedroom creation, loft/dormer work, extensions, conversions, subdivisions, annexes and additional dwellings. Same-road and nearby-postcode signals are distinguished where the returned record supports that comparison. Evidence is saved to the candidate Notes and visible summary fields when the existing sheet has those optional columns.

Important limits:
- National planning-application data is incomplete and the dataset/specification is still evolving. A no-result response is not proof that no application exists.
- A neighbouring approval is precedent only, not permission for the target property. Check the local planning authority portal and seek a qualified planning professional's view before relying on it.
- Net profit is calculated only when the completed-value estimate and every required cost input are available. Results are illustrative and before tax; no costs are silently assumed.
- The engine does not contact sellers, councils, agents or advisers.
- Optional runtime settings: `ATLAS_PLANNING_ENABLED=false` disables lookups; `ATLAS_PLANNING_MAX_PROPERTIES=25` limits candidate lookups per run; `ATLAS_PLANNING_REQUEST_DELAY=0.25` sets a polite delay between API calls.


## Verified Buyer & Investor Intelligence

The offline `buyer_intelligence.py` module adds a verification gate and criteria-based deal matching. It does not discover buyers automatically, scrape personal data, contact anyone, or store proof-of-funds documents. Buyer profiles must be sourced lawfully and reviewed by a person.

Verification requires recorded identity verification, a checked funding-evidence status, a verification date no more than 90 days old, and recorded consent. This status means human review is recorded; it does not guarantee available funds or completion. Store verification metadata only, not bank statements or identity documents in ordinary spreadsheets.

Matching considers budget, location, strategy, stated minimum profit, and valuation evidence. Scores are triage aids, not investment recommendations. Human review remains required before any deal pack or introduction.

The commercial sourcing workflow remains disabled pending regulatory review. HMRC guidance says property sourcing/deal packaging and introducing buyers or investors to property deals can constitute estate agency work; check supervision and redress requirements before trading. No outreach, referral, or financial-promotion publishing is enabled by this module.


## Public Buyer Prospecting Register

`data/buyer_prospects_seed.json` contains an initial source-linked register of public acquisition businesses and investor-network channels relevant to London and South East England. All businesses are labelled as prospects only; networking organisations are not classified as purchasers.

`buyer_prospecting.py` loads and validates this register, fails closed if a public prospect is accidentally labelled verified, and filters prospects by stated geography and strategy. Published profiles are starting points, not endorsements. Current mandates, legal identities, available funds, and willingness to consider sourced deals have not been independently confirmed.

Do not store identity documents or bank statements in this register. Contacting, referrals, and publishing remain disabled; do not outreach or make introductions until applicable regulatory and data-protection requirements are reviewed.


## Contract Assignment vs Property Sourcing Comparator

The offline `contract_route_comparator.py` compares two possible routes for an individual property: paid property sourcing and contract assignment. It reports known fee inputs, a provisional BMV discount calculation, missing evidence, regulatory blockers and route-specific legal risks.

The comparator is deliberately fail-closed. It does not establish that a fee is legally payable, that a contract can be assigned, that seller consent is unnecessary, that an activity is outside estate agency rules, or that a buyer can complete. Assignment rights, consent, title, AML/redress status, marketing authority, fee disclosure, funding evidence and independent solicitor review must be confirmed by a human.

Even a route marked `ELIGIBLE_FOR_SOLICITOR/COMPLIANCE_REVIEW` is **not approved to transact**. It only means the recorded fields passed this module's preliminary checks. The overall status always remains `HUMAN_AND_SOLICITOR_REVIEW_REQUIRED`. No contact, offer, contract, payment, referral or publication is triggered. The module does not write to Smartsheet.


## Manual Contract Route Review Queue

Use `contract_route_review.py` to compare manually entered opportunities without connecting to live systems. Copy `data/contract_route_review_template.json`, replace the illustrative record with evidence-backed fields, then run from the `property-agents` directory:

```bash
python contract_route_review.py data/contract_route_review_template.json --output property-route-review-report.json
```

The report compares sourcing and assignment route gates for each record. It writes only the local output JSON file; it does not call the internet, contact any person, create an offer, sign or amend a contract, pay money, or read/write Smartsheet. The template URL and figures are examples only and must not be treated as a real property lead. Never put identity documents, bank statements or sensitive personal data in this JSON file.


## Contract Assignment vs Property Sourcing Review Queue

`contract_route_comparator.py` compares property sourcing and contract-assignment routes. `property_route_review.py` maps available candidate data to that comparator and writes a JSON review-queue artifact for human review. Missing data stays missing; the module does not infer market value, sold comparables, contract rights, consent, buyer funding or legal compliance.

The review queue is an audit artifact only. It does not write to Smartsheet, contact sellers or buyers, make offers, sign contracts, pay fees, refer parties or publish opportunities. Even a route passing preliminary checks remains subject to human, compliance and independent solicitor review.

The workflow also uploads a self-contained HTML review page alongside the JSON queue. It escapes property/source text before rendering and clearly labels all results as review-only, never transaction approval.
