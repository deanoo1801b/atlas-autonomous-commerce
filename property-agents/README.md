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
