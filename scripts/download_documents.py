#!/usr/bin/env python3
"""Download documents listed in data/document_inventory.csv.

Raw PDFs are intentionally ignored by git. This script makes the local
collection reproducible from the tracked document inventory.
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import sys
import urllib.request


def default_path(row: dict[str, str]) -> pathlib.Path:
    return pathlib.Path("data/raw") / row["case_id"] / f"{row['document_id']}.pdf"


def pending_case_ids(path: str) -> set[str]:
    if not path:
        return set()
    with open(path, newline="", encoding="utf-8") as handle:
        return {
            row["source_row_id"]
            for row in csv.DictReader(handle)
            if row.get("llm_label_status") == "pending"
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", default="data/document_inventory.csv")
    parser.add_argument("--case-id", default="")
    parser.add_argument("--pending-seed", default="")
    parser.add_argument("--key-docs-only", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    with open(args.inventory, newline="") as f:
        rows = list(csv.DictReader(f))

    pending = pending_case_ids(args.pending_seed)
    key_types = {
        "prospectus",
        "legal_opinion",
        "rating_report",
        "issuance_disclosure_document",
    }
    count = 0
    for row in rows:
        if args.case_id and row["case_id"] != args.case_id:
            continue
        if pending and row["case_id"] not in pending:
            continue
        if args.key_docs_only and row.get("document_type", "") not in key_types:
            continue
        url = row.get("download_url", "")
        if not url:
            continue
        out = pathlib.Path(row.get("local_file_path") or default_path(row))
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists() and not args.overwrite:
            print(f"skip existing {out}", flush=True)
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=args.timeout) as resp:
                data = resp.read()
            out.write_bytes(data)
            count += 1
            print(f"downloaded {out} {len(data)} bytes", flush=True)
        except Exception as exc:
            print(f"error {row.get('document_id', '')} {url} {exc}", flush=True)
            continue
        if args.limit and count >= args.limit:
            break

    print(f"downloaded_count={count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
