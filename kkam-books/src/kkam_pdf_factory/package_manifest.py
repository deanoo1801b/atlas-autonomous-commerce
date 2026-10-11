from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_package_manifest(
    product_id: str,
    version: str,
    files: Iterable[str | Path],
    output_path: str | Path,
) -> dict:
    if not product_id.strip() or not version.strip():
        raise ValueError("product_id and version are required")
    paths = [Path(p) for p in files]
    if not paths:
        raise ValueError("At least one package file is required")
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        raise FileNotFoundError("Missing package files: " + ", ".join(missing))
    names = [p.name for p in paths]
    if len(names) != len(set(names)):
        raise ValueError("Package contains duplicate basenames; use unique asset names")
    records = [
        {
            "file_name": p.name,
            "path": str(p),
            "size_bytes": p.stat().st_size,
            "sha256": sha256_file(p),
        }
        for p in sorted(paths, key=lambda item: item.name.lower())
    ]
    manifest = {
        "product_id": product_id,
        "version": version,
        "file_count": len(records),
        "files": records,
    }
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest
