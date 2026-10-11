# KKAM BOOKS PDF Factory — Roadmap

## Milestone 1 — Foundation (partially implemented)

- [x] Collection inventory and targeted candidate audit.
- [x] Repeatable static n8n collection scanner.
- [x] SQLite product catalogue and naming convention.
- [x] PDF technical QA: signature, parser, page count, dimensions, metadata, font review.
- [x] Optional page rendering with PyMuPDF.
- [x] Exact duplicate-render and blank-page warnings.
- [x] Fail-closed production stage state machine.
- [x] Approval references required for concept approval, final approval and publishing.
- [x] Unit tests and GitHub Actions CI workflow.
- [ ] Verify current CI result after latest dependency and QA updates.
- [ ] Complete whole-collection static audit and retain its output as a versioned report.

## Milestone 2 — PDF build engine

- Add deterministic HTML/Markdown-to-PDF templates using ReportLab or HTML/CSS renderer after choosing the layout path.
- Add page-order manifest and asset provenance manifest.
- Add cover/interior assembly and trim-size presets.
- Add print DPI checks for raster assets and margin checks.
- Add valid sample PDFs and golden-file regression tests.

## Milestone 3 — Visual QA

- Render every page and produce a contact sheet.
- Detect blank/near-blank pages, exact duplicates, low-contrast pages and content outside safe margins.
- Add optional computer-vision review for colouring-page line-art quality.
- Keep visual QA as needs-review until all pages have a review record; a render alone is not approval.

## Milestone 4 — Content and illustration agents

- Structured briefs and age-specific content schemas.
- Original illustration prompts and asset provenance.
- Batch naming, dimension and file-type validation.
- Spelling, calculation and factual-claim review.
- Rights review for fonts, source images, model output and external assets.

## Milestone 5 — Catalogue and packaging

- Generate package manifest and checksums.
- Versioned folders and deterministic file names.
- Duplicate detection by content hash.
- QA reports stored beside each release.

## Milestone 6 — Distribution integrations

- Draft listing title, description, keywords, FAQs and image plan.
- Shopify/marketplace connectors remain disabled until separately configured and approved.
- Add notification and background scheduler after a deployment target is selected.

## Current dependencies and estimated costs

| Component | Status | Cost posture |
|---|---|---|
| Python + SQLite | Implemented | No licence fee |
| ReportLab | Optional dependency | Open source; no per-document fee |
| pypdf | Optional dependency | Open source; no per-document fee |
| PyMuPDF | Optional dependency | Open source; check licence and distribution terms for intended commercial deployment |
| Pillow | Optional dependency | Open source |
| n8n | Not connected/imported | Self-hosting may have infrastructure/maintenance costs; hosted plans may cost money |
| Google Drive/Sheets | Not configured for KKAM | Account/API terms and quotas apply |
| Image-generation model | Not connected in this package | May incur usage costs; requires explicit approval |
| Vision QA model | Not connected | May incur usage costs; requires explicit approval |
| Shopify/marketplace publishing | Not connected to this factory | Approval-gated; platform fees may apply |

No paid service is activated by this code. Cost estimates for hosting, printing, APIs and marketplace fees require actual volume, provider and region details.

## First working milestone definition

The first milestone is complete when CI passes and a sample product can be:
1. registered in SQLite,
2. assembled into a PDF,
3. rendered page-by-page,
4. technically checked,
5. given a QA report and manifest,
6. blocked from publication until explicit approval.
