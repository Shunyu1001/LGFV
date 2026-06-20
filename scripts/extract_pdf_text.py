#!/usr/bin/env python3
"""Extract text from downloaded PDF documents.

The output is written under data/processed, which is ignored by git. The script
prints a compact extraction report that can be copied into collection notes.
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import sys

from pypdf import PdfReader


def default_path(row: dict[str, str]) -> pathlib.Path:
    return pathlib.Path("data/raw") / row["case_id"] / f"{row['document_id']}.pdf"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", default="data/document_inventory.csv")
    parser.add_argument("--case-id", default="")
    args = parser.parse_args()

    with open(args.inventory, newline="") as f:
        rows = list(csv.DictReader(f))

    print("document_id,pages,chars,status")
    for row in rows:
        if args.case_id and row["case_id"] != args.case_id:
            continue
        local = row.get("local_file_path", "")
        pdf_path = pathlib.Path(local) if local else default_path(row)
        if not pdf_path.exists():
            print(f"{row['document_id']},0,0,missing_pdf")
            continue

        out_dir = pathlib.Path("data/processed") / row["case_id"]
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{row['document_id']}.txt"

        try:
            reader = PdfReader(str(pdf_path))
            parts = []
            for index, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                if text.strip():
                    parts.append(f"\n\n--- page {index} ---\n{text}")
            output = "".join(parts).strip()
            out_path.write_text(output, encoding="utf-8")
            status = "ok" if output else "no_text"
            print(f"{row['document_id']},{len(reader.pages)},{len(output)},{status}")
        except Exception as exc:
            print(f"{row['document_id']},0,0,error:{exc}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
