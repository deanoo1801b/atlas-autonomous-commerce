# KKAM BOOKS Master Product Catalogue

Implementation: SQLite in `src/kkam_pdf_factory/catalogue.py`.

| Field | Purpose |
|---|---|
| product_id | Stable primary key, e.g. KKAM-0001 |
| title | Product display title |
| category | Colouring book, activity pack, workbook, guide, planner, template or bundle |
| audience | Age range or professional customer segment |
| product_brief | Approved scope, purpose and differentiators |
| page_count | Expected/actual PDF pages |
| trim_size | A4 default or explicit selected trim |
| source_files | JSON array of editable source paths |
| artwork_directory | Approved art asset location |
| final_pdf_path | Final versioned PDF path |
| cover_image_path | Approved cover path |
| version | Product version |
| production_status | Current pipeline stage/status |
| technical_qa_status | not-run / passed / failed / needs-review |
| visual_qa_status | not-run / passed / failed / needs-review |
| licensing_status | not-reviewed / passed / blocked / needs-review |
| keywords | JSON array of validated search keywords |
| product_description | Accurate listing description |
| suggested_price | Proposed price; not automatically published |
| actual_production_cost | Recorded per-product cost |
| publication_status | draft / approval-pending / published / withdrawn |
| last_updated | Automatically refreshed on catalogue upsert |
| qa_report_path | Technical and visual QA report location |
| approval_reference | Explicit approval reference for release |

The schema intentionally does not store credentials or customer personal data. It stores source paths and status metadata, not the product binaries themselves.

## Data integrity

- Product ID is unique.
- Required fields: product ID, title and category.
- Page count must be positive when supplied.
- Price and production cost cannot be negative.
- Unknown field names are rejected.
- Upsert updates an existing product rather than silently creating duplicates.
- Keep previous PDF/source versions rather than overwriting approved release artifacts.
