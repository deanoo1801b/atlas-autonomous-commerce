# ATLAS Autonomous Runtime Plan

## Objective
Turn the documented agent architecture into a controlled execution system without bypassing approval gates.

## Runtime stages
1. Load verified configuration and permissions.
2. Run scheduled/triggered specialist scans.
3. Persist timestamped evidence and audit events.
4. Aggregate signals into the Opportunity Report.
5. Apply market, inventory, margin, compliance and confidence gates.
6. Produce recommended actions and experiments.
7. Require explicit approval for public publishing, spending, payment changes, orders, contracts, deletion and other protected actions.
8. Record outcomes and feed measured results back into the learning loop.

## Priority implementation order
- Audit-event persistence
- Agent health/status tracking
- Orchestration/task runner
- Shopify/Metricool data adapters
- Opportunity Report persistence
- Scheduled scanner execution
- Experiment/result tracking
- Approval queue

## Non-negotiable controls
- Default dry-run.
- No autonomous spending.
- No autonomous public publication.
- No payment/account-security changes.
- No financial trades or contracts.
- No destructive operations without approval.
- Every recommendation records evidence, timestamp, uncertainty and source.
- Product-market routing remains enforced: digital products generally worldwide subject to eligibility; GoDropship physical products UK-only; Gelato requires product/country fulfilment verification.
