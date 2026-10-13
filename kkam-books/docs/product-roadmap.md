# KKAM BOOKS Product Roadmap

This is the machine-readable roadmap for the seven practical digital-product concepts inspired by the supplied market screenshot. The screenshot's prices and sales claims are unverified and are not used as forecasts.

## Product status

All seven records begin at `brief`, publication `draft`, licensing `not-reviewed`, and QA `not-run`. These are planning records, not claims that the products have been built or approved.

| ID | Product | Core customer job |
|---|---|---|
| KKAM-BIZ-001 | Freelancer Business Dashboard | Track clients, work and business money in one place |
| KKAM-LIFE-002 | 90-Day Life Organisation Planner | Turn goals into a 90-day action and review routine |
| KKAM-BIZ-003 | One-Person Business Operating System | Document recurring business operations |
| KKAM-PLAN-004 | Complete Printable Planner Bundle | Use a coherent, non-repetitive set of planning pages |
| KKAM-SOFT-005 | Software Quick-Start Toolkit | Start using one selected software tool with guided templates |
| KKAM-SCRIPT-006 | Ready-to-Use Message Scripts | Send suitable responses to common communication situations |
| KKAM-ART-007 | Original Character Design Toolkit | Develop and document original character concepts |

## Seed the SQLite catalogue

From the repository root:

```bash
PYTHONPATH=kkam-books/src python -m kkam_pdf_factory.seed_roadmap \
  --roadmap kkam-books/config/product-roadmap.json \
  --db output/catalogue/kkam-books.sqlite3
```

The seed is idempotent by product ID. Acceptance checks stay in the roadmap JSON so they are available to production planning without adding unreviewed schema fields to the catalogue.

## Release gates

Each product must have a confirmed target buyer, reviewed content, original/licensed assets, a successful technical QA report, human visual review, accurate metadata, and explicit approval before publication. Product price, sales demand and platform fit are not assumed from the screenshot.
