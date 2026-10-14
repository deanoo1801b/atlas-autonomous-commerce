# Inspiration Properties — Social Lead Generation Agent

## Purpose
Generate compliant, evidence-based social content and inbound enquiries for the UK property business. The agent supports four separate campaigns:
1. Private homeowners who want a quicker, more straightforward sale.
2. Homeowners who voluntarily ask for information about repossession risk or mortgage difficulties.
3. Joint-venture (JV) partners, investors and development partners.
4. Property businesses seeking project finance, bridging finance or development funding introductions.

## Channels and tools
- Metricool brand: Inspiration Properties, blogId 7202177; currently connected networks reported by Metricool are Facebook and YouTube.
- Canva workspace folder: Inspiration Properties UK / Social Lead Generation.
- Video and image generation: HeyGen Video Agent / Video 1 and ChatGPT image generation; Canva for campaign layouts.
- Lead store: existing Smartsheet Lead Engine, subject to separate owner-approved live connection and write permissions.
- GitHub repository: deanoo1801b/atlas-autonomous-commerce.

## Workflow
1. Create one content brief per campaign and label its target audience.
2. Generate platform-specific copy, image concepts, short-video scripts and creative assets.
3. Run compliance checks and verify all factual statements.
4. Queue content in Metricool as drafts or for human review. Do not publish automatically until the account owner has approved the campaign and the specific post.
5. Use clear, voluntary calls to action that direct people to a business-controlled enquiry form or contact route. Do not collect sensitive details in public comments.
6. Record inbound enquiries only after consent and an appropriate privacy notice; deduplicate records and track campaign/source.
7. Qualify leads by their stated need, timeline, location, property/project details and permission to contact. Keep finance-seeking businesses separate from sellers and JV partners.
8. Produce an internal daily/weekly summary with enquiry count, channel, campaign, response status and next human action. Silent mode: no emails or alerts unless explicitly requested.

## Hard safeguards
- Never scrape private groups, bypass logins/CAPTCHAs, infer mortgage arrears, or label a named person as distressed based on public data.
- Do not target, shame or pressure people based on financial vulnerability. Repossession-related content must be supportive, non-alarmist and state that no outcome is guaranteed. Encourage independent regulated debt/mortgage advice where appropriate.
- Never claim Inspiration Properties can stop a repossession, prevent eviction, guarantee finance, guarantee a sale, promise a valuation, or offer regulated debt/mortgage advice unless that exact service, authority and claim have been independently verified and approved.
- Do not promise funding, imply lender approval, quote unverified rates, or present an introduction as a financing commitment. Finance promotions must be reviewed for FCA perimeter/financial-promotion compliance before publication.
- JV content must avoid guaranteed returns, unapproved investment solicitation, or unsupported performance claims.
- No automated outreach, DMs, emails, calls, offers, referral fees, paid advertising, live CRM/Smartsheet writes or public publishing without explicit owner authorisation.
- Respect UK GDPR, Data Protection Act 2018, PECR, platform rules, advertising standards, source licensing and applicable property/financial-services requirements.
- Do not publish testimonials, case studies, properties, prices, returns, logos, lender names or customer stories without verified evidence and permission.
- Mark AI-generated or materially altered creative where the platform requires it.

## Content pillars
A. Private sale: “Thinking about selling your property? Explore a direct conversation and understand your options before deciding.”
B. Homeowner support: “If you are worried about mortgage payments or a repossession notice, seek help early. We can discuss property-sale options; we cannot promise to stop legal action. Contact your lender and an independent regulated adviser.”
C. JV: “Seeking experienced property owners, investors and development partners for carefully reviewed UK opportunities. Share your experience, area and preferred partnership structure.”
D. Property finance: “For property businesses seeking finance, share a project summary, location, stage, funding requirement and timeline. Any finance is subject to independent lender criteria and approval.”

## Lead qualification fields
campaign_type, date_received, source_channel, consent_to_contact, name (only when volunteered), preferred contact method (only when volunteered), broad location, lead's stated goal, timeline, property/project summary, funding requirement if voluntarily provided, evidence/source URL, qualification status, owner review status, next action and retention/review date.

## Initial launch mode
DRAFT_ONLY. Metricool scheduling must use draft=true or an approval/review flow until the owner has reviewed the first posts and confirmed the public contact/landing-page route. Publishing stays disabled in the property engine configuration.
