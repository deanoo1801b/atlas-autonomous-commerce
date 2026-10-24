# ATLAS Always-On Agent Runtime

## Objective
Run ATLAS independently of any ChatGPT conversation or browser session. GitHub is the source-code repository, not the runtime. A successful GitHub Actions run proves only that that individual job ran; it does not prove the full agent is continuously running.

## Current verified baseline
- The credential-free public storefront monitor exists at `.github/workflows/atlas-public-store-monitor.yml`.
- It has passed a manual run and checks the public homepage response, title, meta description, and a basic noindex directive.
- It is scheduled by GitHub Actions every six hours. It is a lightweight monitor, not the full SEO agent and not a social publisher.
- Metricool brand discovery shows the Atlas Goods Store brand and connected social profiles. A recent schedule lookup returned no scheduled posts.
- The repository has previously been observed as public. Make it private before adding secrets or sensitive business logic.

## Recommended runtime
Use a self-hosted open-source n8n deployment on an always-on VPS or existing always-on server, using Docker Compose with persistent volumes and a restart policy. The user explicitly prefers open-source/self-hosted rather than n8n Cloud. GitHub Actions remains suitable for short, credential-free checks, but not as a substitute for a persistent orchestration service.

## Runtime services
1. **n8n** — schedules, workflow orchestration, retries, alerts, and approvals.
2. **Persistent database** — PostgreSQL for n8n state and workflow metadata.
3. **Secret storage** — environment secrets or deployment secret manager; never commit credentials to Git.
4. **Workflow backup** — encrypted/off-site backups and versioned workflow exports without secrets.
5. **Health checks and alerts** — monitor the runtime and each workflow; alert on failures, stale data, or missing credentials.
6. **Audit trail** — record each run, input source, result, approval, external action, and error.

## First workflows to deploy
### A. Daily SEO Monitor (read-only)
- Check storefront HTTP status, redirects, title, meta description, canonical, robots/noindex, sitemap, and key page availability.
- When Search Console access is configured, compare clicks, impressions, CTR, and position using equivalent date ranges.
- Produce a concise report and prioritised issues. No live site edits.

### B. SEO Research and Content Drafts
- Build a keyword-to-existing-URL map; detect duplicates and likely cannibalization.
- Produce briefs and draft content based on verified product data and cited sources.
- Store drafts for review. Do not auto-publish in the first release.

### C. Social Publishing
- Check publishing API availability and permissions before relying on it.
- Generate platform-specific post drafts and media requirements.
- Initially schedule a single approved test post through a supported integration and verify its published state.
- Never mark a post as published based only on a successful scheduling response.
- If API credentials or platform permissions are missing, stop and report the blocker; do not loop or incur unexpected subscription charges.

### D. Master report and safety controls
- Deduplicate issues and prevent two workflows from editing the same URL.
- Require approval for live edits, publishing, outreach, spending, bulk changes, redirects, robots/canonical changes, or theme code.
- Add idempotency/deduplication keys, rate limits, retry caps, and failure notifications.
- Start with observe/draft mode; enable narrowly scoped actions only after tests pass.

## Deployment checklist
- [ ] Change repository visibility to private before adding sensitive configuration.
- [ ] Select/provision an always-on server and confirm SSH or supported deployment access.
- [ ] Deploy Docker Compose for n8n and PostgreSQL with persistent storage and restart policies.
- [ ] Configure HTTPS, strong authentication, firewall, and regular updates.
- [ ] Store credentials securely; do not commit `.env` or tokens.
- [ ] Import the read-only SEO monitor and run a successful test.
- [ ] Connect Shopify read-only credentials and Google Search Console access if available.
- [ ] Connect social publishing only through a verified supported credential path.
- [ ] Run an approved test post and verify the actual published URL/status.
- [ ] Enable schedules, alerts, backups, and audit logs.
- [ ] Confirm the runtime still runs after closing ChatGPT and after a server restart.

## What remains blocked / unverified
No always-on server has yet been confirmed or provisioned in this repository workflow. No full n8n deployment has been verified. The available context does not establish that a Metricool API token is available. Do not claim the full agent is live until deployment, credentials, test runs, and post-publication verification succeed.
