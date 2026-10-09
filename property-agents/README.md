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
