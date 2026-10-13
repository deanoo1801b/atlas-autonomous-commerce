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

- [Seven-product roadmap and acceptance criteria](docs/product-roadmap.md)
- [Machine-readable product roadmap](config/product-roadmap.json)
- [Collection inventory and full-scan results](research/collection-inventory.md)
- [Initial candidate audit](research/candidate-audit.md)
- [Ranked 20-workflow shortlist](research/ranked-shortlist.md)
- [Production specification](docs/production-spec.md)
- [Catalogue schema](docs/catalogue-schema.md)
- [Compatibility/risk matrix](docs/workflow-compatibility-matrix.md)
- [Implementation roadmap](docs/implementation-roadmap.md)

## Implemented components

- `src/kkam_pdf_factory/catalogue.py` — SQLite product catalogue and filename convention.
- `src/kkam_pdf_factory/assemble.py` — deterministic business-PDF and colouring-book assembly.
- `src/kkam_pdf_factory/qa.py` — technical PDF validation, optional page rendering, duplicate/blank checks, contact sheets and colouring-page pixel heuristics.
- `src/kkam_pdf_factory/pipeline.py` — fail-closed stage state machine with acceptance criteria and approval references.
- `src/kkam_pdf_factory/package_manifest.py` — versioned SHA-256 asset manifest.
- `research/scan_n8n_collection.py` — repeatable read-only static scanner for the complete workflow tree.
- GitHub Actions workflows run the unit tests and full collection scan.

## Status

Research and implementation are ongoing. The current source repository tree has 2,061 workflow JSON files, despite the README advertising 4,343. All 2,061 JSON bodies have now been fetched and parsed by the static scanner; targeted candidates have been inspected in detail. This does not mean every workflow was imported or executed. The collection has significant graph-integrity warnings; see the inventory and ranked shortlist.


## Run the factory locally

From the repository root, install the open-source PDF tools and set the package path:

```bash
pip install -r kkam-books/requirements-optional.txt
export PYTHONPATH=kkam-books/src
python -m kkam_pdf_factory.cli --help
```

Build a professional business PDF:

```bash
python -m kkam_pdf_factory.cli build-business --spec product-spec.json --output output/01-KKAM-Sample.pdf
```

Assemble a colouring book from approved local PNG/JPEG assets:

```bash
python -m kkam_pdf_factory.cli build-colouring --spec colouring-spec.json --output output/02-KKAM-Animals.pdf
```

Run technical QA and render every page:

```bash
python -m kkam_pdf_factory.cli qa --pdf output/01-KKAM-Sample.pdf --trim-size A4 --render-dir output/renders --report output/qa/technical-report.json
```

Create a checksummed package manifest:

```bash
python -m kkam_pdf_factory.cli manifest --product-id KKAM-0001 --version 1.0.0 --files output/01-KKAM-Sample.pdf output/qa/technical-report.json --output output/manifest.json
```

The CLI returns a non-zero exit code for failed technical QA. Rendering creates evidence for review; it does not automatically approve the visual quality of the product.


## Verified first milestone

- Latest GitHub Actions test run: [30 tests passed; sample PDFs built and QA checked](https://github.com/deanoo1801b/atlas-autonomous-commerce/actions/runs/38180138371).
- Full collection static scan: [audit run](https://github.com/deanoo1801b/atlas-autonomous-commerce/actions/runs/38179913018).
- Demo package artifact: [download from the test run](https://github.com/deanoo1801b/atlas-autonomous-commerce/actions/runs/38180138371/artifacts/11716643866). It contains a sample business workbook, sample colouring PDF, rendered pages, contact sheet, QA JSON and SHA-256 manifest. Demo content/artwork is synthetic and **not approved for commercial sale**.
