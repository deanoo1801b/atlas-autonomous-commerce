# KKAM BOOKS PDF Product Factory

This project builds a reliable, approval-gated pipeline for colouring books, children's activity packs and professional business PDFs.

## Core rule

Research examples are references, not trusted executable software. Workflow JSONs are statically audited before import. No candidate from the initial n8n sample is approved for direct production import.

## Production pipeline

1. Research opportunity and record evidence.
2. Create and approve product brief.
3. Generate original content and illustrations.
4. Validate each asset and its licence/source.
5. Assemble PDF from approved assets.
6. Render pages for inspection.
7. Run technical PDF checks.
8. Run visual QA and content QA.
9. Correct defects and rebuild.
10. Complete originality/licensing review.
11. Prepare product metadata and listing copy.
12. Record catalogue entry and version.
13. Request final human approval.
14. Publish only after explicit approval.

## Zero-cost-first implementation

- SQLite catalogue (Python standard library).
- PDF technical validation with optional `pypdf`.
- Page rendering with optional `PyMuPDF`.
- Image checks with optional `Pillow`.
- PDF generation with optional `reportlab`.
- Unit tests using Python's standard `unittest`.
- n8n remains an optional orchestration layer; the product pipeline can run as a scheduled script or background worker once hosted.

## Naming convention

`NUMBER-KKAM-Short-Product-Name.pdf`

Use a stable product ID and version metadata. Never overwrite an approved final without retaining the previous version.

## Current records

- [Collection inventory](research/collection-inventory.md)
- [Initial candidate audit](research/candidate-audit.md)

## Status

Research is ongoing. The current source repository tree has 2,061 workflow JSON files, despite the README advertising 4,343. The recursive tree was complete and non-truncated. Only a targeted sample of JSON bodies has been audited so far; do not describe the whole collection as fully inspected.
