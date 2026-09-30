# ATLAS Commerce Execution Layer

## Flow

QC passed
→ SEO package
→ Media generation jobs
→ Shopify draft
→ Human approval
→ Publish
→ Analytics
→ Optimisation

## Shopify

The software exposes a Shopify adapter boundary for draft creation. Live publishing remains outside the adapter until the connected Shopify workflow is explicitly authorised.

## Creative

Image and video requests are represented as structured jobs so Canva/OpenArt/HeyGen-style integrations can be connected without changing the product workflow.

## Safety

- Draft creation is separated from publication.
- Commercial publication requires QC plus explicit human approval.
- Paid promotion and irreversible changes remain approval-gated.
- Every execution stage should emit an auditable event.
