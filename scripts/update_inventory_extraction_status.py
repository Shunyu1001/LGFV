#!/usr/bin/env python3
"""Synchronize inventory extraction flags with processed text files."""

from __future__ import annotations

import argparse
import csv
import pathlib
from collections import defaultdict


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_DOCS = ROOT / "data" / "document_inventory.csv"
DEFAULT_SOURCES = ROOT / "data" / "source_inventory.csv"
DEFAULT_PROCESSED = ROOT / "data" / "processed"


def read_csv(path: pathlib.Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: pathlib.Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def text_status(processed_dir: pathlib.Path, case_id: str, local_file_path: str, min_chars: int) -> str:
    if not local_file_path:
        return "no"
    txt_path = processed_dir / case_id / f"{pathlib.Path(local_file_path).stem}.txt"
    if not txt_path.exists():
        return "no"
    text = txt_path.read_text(encoding="utf-8", errors="ignore").strip()
    return "yes" if len(text) >= min_chars else "no"


def source_status(statuses: list[str]) -> str:
    if not statuses:
        return "no"
    yes_count = sum(status == "yes" for status in statuses)
    if yes_count == 0:
        return "no"
    if yes_count == len(statuses):
        return "yes"
    return "partial"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--documents", type=pathlib.Path, default=DEFAULT_DOCS)
    parser.add_argument("--sources", type=pathlib.Path, default=DEFAULT_SOURCES)
    parser.add_argument("--processed-dir", type=pathlib.Path, default=DEFAULT_PROCESSED)
    parser.add_argument("--min-chars", type=int, default=200)
    parser.add_argument("--case-prefix", default="")
    args = parser.parse_args()

    doc_fields, documents = read_csv(args.documents)
    source_fields, sources = read_csv(args.sources)

    statuses_by_case: dict[str, list[str]] = defaultdict(list)
    changed_docs = 0
    for row in documents:
        case_id = row.get("case_id", "")
        if args.case_prefix and not case_id.startswith(args.case_prefix):
            statuses_by_case[case_id].append(row.get("text_extracted", "no"))
            continue
        status = text_status(args.processed_dir, case_id, row.get("local_file_path", ""), args.min_chars)
        if row.get("text_extracted") != status:
            row["text_extracted"] = status
            changed_docs += 1
        statuses_by_case[case_id].append(status)

    changed_sources = 0
    for row in sources:
        case_id = row.get("case_id", "")
        if args.case_prefix and not case_id.startswith(args.case_prefix):
            continue
        status = source_status(statuses_by_case.get(case_id, []))
        if row.get("text_extracted") != status:
            row["text_extracted"] = status
            changed_sources += 1

    write_csv(args.documents, doc_fields, documents)
    write_csv(args.sources, source_fields, sources)

    print(f"documents_changed={changed_docs}")
    print(f"sources_changed={changed_sources}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
