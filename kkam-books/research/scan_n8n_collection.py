#!/usr/bin/env python3
"""Read-only indexer for the Zie619 n8n workflow collection.

Downloads workflow JSON files for static inspection only. It never imports,
executes or activates workflows. Run:
  python kkam-books/research/scan_n8n_collection.py --out kkam-books/research/generated
  python kkam-books/research/scan_n8n_collection.py --limit 50 --out /tmp/kkam-sample
"""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import quote

OWNER = "Zie619"
REPO = "n8n-workflows"
BRANCH = "main"
API_TREE = f"https://api.github.com/repos/{OWNER}/{REPO}/git/trees/{BRANCH}?recursive=1"
RAW_ROOT = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}/"
TERMS = re.compile(
    r"pdf|document|convert|markdown|docx|image|illustrat|resize|background|"
    r"google.?drive|sheets|airtable|shopify|openai|gemini|claude|report|content|"
    r"notion|email|schedule|error|approval|wait|readpdf|extractfromfile|"
    r"converttofile|editimage|writebinaryfile|readwritefile|compression",
    re.I,
)
SUSPICIOUS_TYPES = ("executeCommand", "ssh", "readWriteFile", "writeBinaryFile", "delete", "httpRequest")


def fetch_json(url: str, retries: int = 3) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": "KKAM-Books-Workflow-Audit/1.0"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            if attempt == retries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError("unreachable")


def count_edges(connections: dict[str, Any]) -> int:
    count = 0
    for outputs in connections.values():
        if not isinstance(outputs, dict):
            continue
        for groups in outputs.values():
            if not isinstance(groups, list):
                continue
            for group in groups:
                if isinstance(group, list):
                    count += len(group)
    return count


def audit_workflow(path: str) -> dict[str, Any]:
    row: dict[str, Any] = {
        "path": path,
        "source_url": RAW_ROOT + path,
        "json_valid": False,
        "name": "",
        "node_count": 0,
        "edge_count": 0,
        "dangling_connection_count": 0,
        "dangling_connection_sources": "",
        "dangling_connection_targets": "",
        "connection_source_format": "",
        "no_op_count": 0,
        "code_nodes": 0,
        "shell_nodes": 0,
        "http_nodes": 0,
        "file_nodes": 0,
        "credential_types": "",
        "node_types": "",
        "external_urls": "",
        "hard_coded_ids": "",
        "has_error_handler": False,
        "has_manual_approval_signal": False,
        "has_write_side_effects": False,
        "license_metadata": "",
        "error": "",
    }
    try:
        data = fetch_json(RAW_ROOT + quote(path, safe="/"))
        if not isinstance(data, dict):
            raise ValueError("workflow root is not an object")
        nodes = data.get("nodes", [])
        connections = data.get("connections", {})
        if not isinstance(nodes, list) or not isinstance(connections, dict):
            raise ValueError("nodes or connections has invalid shape")
        node_objects = [n for n in nodes if isinstance(n, dict)]
        types = [str(n.get("type", "")) for n in node_objects]
        node_names = {str(n.get("name", "")) for n in node_objects}
        node_ids = {str(n.get("id", "")) for n in node_objects if n.get("id")}
        dangling_sources = sorted(source for source in connections if source not in node_names and source not in node_ids)
        dangling_targets = set()
        for outputs in connections.values():
            if not isinstance(outputs, dict):
                continue
            for groups in outputs.values():
                if not isinstance(groups, list):
                    continue
                for group in groups:
                    if not isinstance(group, list):
                        continue
                    for edge in group:
                        if isinstance(edge, dict):
                            target = str(edge.get("node", ""))
                            if target and target not in node_names and target not in node_ids:
                                dangling_targets.add(target)
        dangling_count = len(dangling_sources) + len(dangling_targets)
        creds = sorted({key for n in node_objects for key in (n.get("credentials") or {}).keys()})
        urls, hard_ids = set(), set()
        for node in nodes:
            if not isinstance(node, dict):
                continue
            params = node.get("parameters") or {}
            serialized = json.dumps(params, ensure_ascii=False)
            urls.update(re.findall(r"https?://[^\s\"'<>]+", serialized))
            hard_ids.update(re.findall(r"(?<![A-Za-z0-9])(?:[A-Za-z0-9_-]{18,}|[A-Z0-9]{20,})(?![A-Za-z0-9])", serialized))
        row.update({
            "json_valid": True,
            "name": str(data.get("name") or ""),
            "node_count": len(nodes),
            "edge_count": count_edges(connections),
            "dangling_connection_count": dangling_count,
            "dangling_connection_sources": ";".join(dangling_sources),
            "dangling_connection_targets": ";".join(sorted(dangling_targets)),
            "connection_source_format": "node-names" if all(source in node_names for source in connections) else ("node-ids" if all(source in node_ids for source in connections) else "mixed-or-unmatched"),
            "no_op_count": sum("noOp" in t.lower() or t.endswith(".noOp") for t in types),
            "code_nodes": sum(any(x in t.lower() for x in ("n8n-nodes-base.code", "n8n-nodes-base.function")) for t in types),
            "shell_nodes": sum(any(x in t.lower() for x in ("executecommand", "ssh")) for t in types),
            "http_nodes": sum(t.endswith(".httpRequest") for t in types),
            "file_nodes": sum(any(x in t.lower() for x in ("readbinaryfile", "writebinaryfile", "readwritefile", "readpdf", "extractfromfile", "converttofile", "editimage", "compression")) for t in types),
            "credential_types": ";".join(creds),
            "node_types": ";".join(sorted(set(types))),
            "external_urls": ";".join(sorted(urls)),
            "hard_coded_ids": ";".join(sorted(hard_ids)),
            "has_error_handler": any(t.endswith(".stopAndError") or t.endswith(".errorTrigger") for t in types),
            "has_manual_approval_signal": any(re.search(r"approval|approve|human|review", str(n.get("name", "")), re.I) for n in nodes if isinstance(n, dict)),
            "has_write_side_effects": any(
                any(word in (str(n.get("name", "")) + " " + json.dumps(n.get("parameters") or {})).lower()
                    for word in ("upload", "publish", "delete", "append", "update", "send email", "create product"))
                for n in nodes if isinstance(n, dict)
            ),
            "license_metadata": str((data.get("meta") or {}).get("license") or ""),
        })
        return row
    except Exception as exc:
        row["error"] = f"{type(exc).__name__}: {exc}"
        return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="kkam-books/research/generated")
    parser.add_argument("--limit", type=int, default=0, help="0 means all workflow JSON files")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    tree = fetch_json(API_TREE)
    if tree.get("truncated"):
        print("ERROR: GitHub returned a truncated tree; refusing to claim complete path coverage.", file=sys.stderr)
        return 2
    paths = sorted(
        item["path"] for item in tree.get("tree", [])
        if item.get("type") == "blob" and item.get("path", "").startswith("workflows/")
        and item.get("path", "").endswith(".json")
    )
    selected = paths[:args.limit] if args.limit > 0 else paths
    print(f"Tree SHA: {tree.get('sha')}; workflow JSON paths: {len(paths)}; scanning: {len(selected)}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        rows = list(pool.map(audit_workflow, selected))
    output = Path(args.out)
    output.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys()) if rows else ["path"]
    with (output / "workflow-audit.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    (output / "workflow-audit.json").write_text(json.dumps({
        "source_repository": f"https://github.com/{OWNER}/{REPO}",
        "branch": BRANCH,
        "tree_sha": tree.get("sha"),
        "tree_truncated": tree.get("truncated"),
        "workflow_json_paths": len(paths),
        "scanned": len(rows),
        "valid_json": sum(r["json_valid"] for r in rows),
        "failed_download_or_parse": sum(not r["json_valid"] for r in rows),
        "files_with_noop": sum(r["no_op_count"] > 0 for r in rows),
        "files_with_dangling_connections": sum(r["dangling_connection_count"] > 0 for r in rows),
        "total_dangling_connection_references": sum(r["dangling_connection_count"] for r in rows),
        "files_with_shell_nodes": sum(r["shell_nodes"] > 0 for r in rows),
        "files_with_http_nodes": sum(r["http_nodes"] > 0 for r in rows),
        "files_with_error_handler": sum(r["has_error_handler"] for r in rows),
        "files_with_write_side_effects": sum(r["has_write_side_effects"] for r in rows),
        "rows": rows,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Scanned {len(rows)}; valid JSON {sum(r['json_valid'] for r in rows)}; failures {sum(not r['json_valid'] for r in rows)}")
    print(f"Wrote {output / 'workflow-audit.csv'} and {output / 'workflow-audit.json'}")
    return 0 if all(r["json_valid"] for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
