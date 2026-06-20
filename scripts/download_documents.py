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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", default="data/document_inventory.csv")
    parser.add_argument("--case-id", default="")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    with open(args.inventory, newline="") as f:
        rows = list(csv.DictReader(f))

    count = 0
    for row in rows:
        if args.case_id and row["case_id"] != args.case_id:
            continue
        url = row.get("download_url", "")
        if not url:
            continue
        out = pathlib.Path(row.get("local_file_path") or default_path(row))
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists() and not args.overwrite:
            print(f"skip existing {out}")
            continue
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        out.write_bytes(data)
        count += 1
        print(f"downloaded {out} {len(data)} bytes")

    print(f"downloaded_count={count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
