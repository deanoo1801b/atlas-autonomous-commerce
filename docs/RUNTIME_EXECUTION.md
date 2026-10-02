# ATLAS Runtime Execution

The first executable runtime is intentionally **DRY_RUN only**.

## Current capabilities
- Loads a central agent registry.
- Performs an agent health/status check.
- Writes timestamped JSONL audit events.
- Uses the approval policy as the execution boundary.
- Produces no public posts, paid spend, orders, account changes, trades or destructive operations.

## Run locally

```bash
npm install
npm run check
npx tsx src/runtime/index.ts
```

The audit log defaults to `runtime-data/audit-events.jsonl`. Set `ATLAS_AUDIT_LOG` to override it.

## Next runtime layer

1. Add persistent Opportunity Report storage.
2. Add read-only Shopify/Metricool adapters.
3. Add scheduled scanner definitions.
4. Add approval-queue records.
5. Add experiment/result persistence.
6. Only then consider controlled write adapters, each behind explicit approval and least-privilege credentials.

The runtime must not silently upgrade from DRY_RUN to execution.
