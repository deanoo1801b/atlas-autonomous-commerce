# Inspiration Properties UK — Scanner Integration Contract

## Current discovery output
The scheduled workflow runs `agents/property_opportunity_scanner.py` every six hours and saves:
- `property-agent-output/property-opportunities.csv`
- `property-agent-output/scan-summary.md`

The current source is Google News RSS. These records are research signals only; do not treat them as verified listings or seller leads.

## Target
Existing Smartsheet sheet: **Property Leads**
- Sheet ID: `3007077934124932`
- Existing sheet: https://app.smartsheet.com/sheets/95VHjPc74mJh2Q6485MHCqGjQP5p97wmW4x54Rg1

## Safe field mapping for a future connector
| CSV field | Smartsheet column | Rule |
|---|---|---|
| title | Opportunity Evidence | Preserve the source headline/snippet; label as unverified |
| publisher | Source | Publisher only, not seller identity |
| url | Source URL | Keep original source URL |
| query | Lead Type / Opportunity Type | Do not map automatically without classification review |
| published_at | First Seen / evidence history | Parse date; keep original publication text if parsing fails |
| verification_status | Status / Contact Notes | New records remain New / Qualifying until manually verified |
| lead_score | Lead Score | Leave Unscored until evidence-based scoring exists |
| contacted | Contact Status | Always Not Contacted on import |

## Required safeguards
1. Never infer seller names, emails, phone numbers, asking prices, ownership, distress, or motivation from a headline alone.
2. Never overwrite a row based only on title similarity. Deduplicate first by canonical source URL, then by a stable portal listing ID or a carefully reviewed identity key.
3. Do not add duplicate records; update a matching record only after checking its existing source URL and history.
4. Keep `Contact Permission` as `Unknown` unless a lawful, documented basis is established. Do not send outreach automatically.
5. Keep valuation, below-market status, motivation score, and finance calculations blank unless supported by evidence.
6. Store credentials only as GitHub Actions repository secrets; never commit tokens to source code or artifacts.
7. Fail closed if the Smartsheet secret is missing, the API fails, or required columns cannot be matched exactly.
8. Log counts of scanned, rejected, duplicate, imported, and failed records without logging secrets or unnecessary personal data.

## Proposed secret
- `SMARTSHEET_ACCESS_TOKEN`: Smartsheet API token stored as a GitHub Actions secret. Never place its value in code or logs.

## Next implementation gates
- [ ] Confirm at least one successful scheduled/manual GitHub Actions run.
- [ ] Inspect a real artifact and verify source URLs are usable.
- [ ] Add unit tests for CSV schema, URL normalization, deduplication, and empty/error responses.
- [ ] Add a dry-run importer that reports proposed Smartsheet changes without writing.
- [ ] Test against a small reviewed sample and compare it with the existing Property Leads sheet.
- [ ] Enable writes only after dry-run review; leave external contact disabled.

## Existing sheet quality note
The current Property Leads sheet includes some placeholder rows with `TBD` values and missing source evidence. Do not treat those rows as verified acquisition opportunities. The scanner integration should preserve them for review rather than silently replacing or promoting them.
