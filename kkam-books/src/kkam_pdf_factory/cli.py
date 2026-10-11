from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from kkam_pdf_factory.assemble import build_business_pdf, build_colouring_book
from kkam_pdf_factory.catalogue import upsert_product
from kkam_pdf_factory.package_manifest import create_package_manifest
from kkam_pdf_factory.qa import inspect_pdf, write_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="KKAM Books PDF Factory")
    sub = parser.add_subparsers(dest="command", required=True)

    business = sub.add_parser("build-business", help="Build a business PDF from a JSON spec")
    business.add_argument("--spec", required=True)
    business.add_argument("--output", required=True)

    colouring = sub.add_parser("build-colouring", help="Assemble a colouring book from approved image assets")
    colouring.add_argument("--spec", required=True, help="JSON with title, image_paths and optional cover_path, trim_size, age_range")
    colouring.add_argument("--output", required=True)

    qa = sub.add_parser("qa", help="Run technical PDF QA and optionally render pages")
    qa.add_argument("--pdf", required=True)
    qa.add_argument("--expected-pages", type=int)
    qa.add_argument("--trim-size")
    qa.add_argument("--render-dir")
    qa.add_argument("--report", required=True)

    manifest = sub.add_parser("manifest", help="Create a SHA-256 package manifest")
    manifest.add_argument("--product-id", required=True)
    manifest.add_argument("--version", required=True)
    manifest.add_argument("--output", required=True)
    manifest.add_argument("--files", nargs="+", required=True)

    catalogue = sub.add_parser("catalogue-upsert", help="Insert/update a product from a JSON record")
    catalogue.add_argument("--db", required=True)
    catalogue.add_argument("--record", required=True)

    args = parser.parse_args(argv)
    try:
        if args.command == "build-business":
            spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
            path = build_business_pdf(spec, args.output)
            print(json.dumps({"status": "built", "path": str(path)}, indent=2))
            return 0
        if args.command == "build-colouring":
            spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
            path = build_colouring_book(
                spec["title"], spec["image_paths"], args.output,
                cover_path=spec.get("cover_path"),
                trim_size=spec.get("trim_size", "A4"),
                margin_mm=float(spec.get("margin_mm", 12)),
                age_range=spec.get("age_range", ""),
            )
            print(json.dumps({"status": "built", "path": str(path)}, indent=2))
            return 0
        if args.command == "qa":
            report = inspect_pdf(
                args.pdf,
                expected_pages=args.expected_pages,
                expected_trim=args.trim_size,
                render_dir=args.render_dir,
                render_pages=bool(args.render_dir),
            )
            write_report(report, args.report)
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return 0 if report["technical_status"] == "passed" else 2
        if args.command == "manifest":
            result = create_package_manifest(args.product_id, args.version, args.files, args.output)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0
        if args.command == "catalogue-upsert":
            record = json.loads(Path(args.record).read_text(encoding="utf-8"))
            upsert_product(args.db, record)
            print(json.dumps({"status": "saved", "product_id": record["product_id"]}, indent=2))
            return 0
    except Exception as exc:
        print(f"KKAM PDF Factory error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
