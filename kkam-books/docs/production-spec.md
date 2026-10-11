# KKAM BOOKS PDF Production Specification

## Product classes

### Colouring and activity books
- Original line art; clean dark outlines on a white background.
- No unlicensed characters, copied pages, traced commercial art or unlicensed fonts.
- Usable enclosed colouring areas; age-appropriate complexity.
- Consistent line weight and visual style across a book.
- Page content kept inside trim-safe margins.
- A4 default; trim size is a required field in the brief, not hard-coded globally.
- Print-ready and digital-download exports may have different bleed/margin requirements.

### Professional business PDFs
- Original practical content with clear sections and actionable worksheets.
- Calculations, examples and factual claims flagged for validation.
- Consistent typography, tables, headings, page numbers and page hierarchy.
- Source/editable assets retained with each release.

## Standard product package

- `NUMBER-KKAM-Short-Product-Name.pdf`
- `cover.png`
- `source/` — editable Markdown/HTML/SVG/JSON or document sources
- `artwork/` — approved original illustration assets
- `renders/page-0001.png...`
- `qa/technical-report.json`
- `qa/visual-review.json`
- `metadata/product.json`
- `listing/listing-copy.md`
- `licensing/provenance.json`
- `manifest.sha256`

## Required technical checks

1. PDF signature and strict parser open.
2. Non-zero page count and expected page count.
3. Every page has valid dimensions; dimensions match the selected trim/orientation.
4. Metadata title is present; author/subject/keywords are populated when required.
5. Fonts are inspected; missing/unembedded fonts are flagged for review, not automatically treated as a failure when the font is standard.
6. Render every page to PNG at a defined QA resolution.
7. Detect exact duplicate rendered pages and blank/near-blank pages.
8. Check image resolution and image placement for print.
9. Verify page order and required cover/title/copyright pages against the product brief.
10. Store machine report and rendered page manifest.

## Required visual checks

- Every page inspected; no file-existence-only approval.
- No clipping, overlapping elements, broken glyphs, unexpected shading or unwanted backgrounds.
- No repeated/omitted pages unless explicitly intended and recorded.
- Colouring interiors: white page background, clean black outlines, adequate enclosed areas, no accidental grey fills or gradients.
- Business PDFs: spelling, table alignment, readable text, sufficient contrast and correct page numbers.
- QA failures are recorded, corrected, rebuilt and rechecked.

## Human gates

Human approval is required for:
- Concept approval before bulk production.
- Copyright/licensing exceptions.
- Final product release.
- Any public marketplace publication or paid service activation.

The system may draft listings but must not publish without an explicit approval reference.

## Production state

The pipeline implementation uses explicit stages and acceptance criteria. A stage cannot be skipped; missing criteria block the task and append a failure record. Publishing requires a recorded approval reference.
