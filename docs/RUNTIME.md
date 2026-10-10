# ATLAS Runtime

## Safety defaults

- The default mode is `observe`.
- `ATLAS_DRY_RUN` defaults to `true`.
- Writes require approval by default.
- Spending requires approval by default.
- The runtime does not perform external actions unless an explicit action handler is implemented and permitted.

## Local smoke test

Requires Node.js 20 or newer and installed project dependencies.

```bash
npm install
npm run check
npm run runtime
```

The runtime writes JSON Lines audit records to `data/audit.jsonl` by default. Set `ATLAS_AUDIT_PATH` to choose another path. Keep runtime data and credentials out of version control; never commit Shopify access tokens.

## Shopify integration status

The Shopify adapter is currently an interface/stub. Live Shopify reads are available through the connected ChatGPT Shopify integration for manual analysis, but the standalone repository runtime is not yet authenticated to Shopify. A read-only Shopify Admin API credential and an approved secure secret store are required before direct runtime integration.
