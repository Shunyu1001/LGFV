#!/usr/bin/env python3
"""Validate human-reviewed LGFV exit-type labels.

The script checks that the final label file is internally consistent with the
codebook and tracked source inventories. It intentionally does not assign
labels.
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import re
import sys


ALLOWED_LABELS = {
    "substantive_exit",
    "nominal_exit",
    "functional_transfer",
    "liquidation",
    "unclear",
}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}
REQUIRED_COLUMNS = [
    "case_id",
    "province",
    "city",
    "company_name",
    "official_exit_year",
    "official_exit_event",
    "final_label",
    "final_confidence",
    "human_reviewer",
    "validation_date",
    "primary_evidence_doc",
    "primary_evidence_lines",
    "final_rationale",
    "alternative_label",
    "ambiguity_note",
    "caveat",
]
LINE_RANGE_RE = re.compile(r"^\d+(?:-\d+)?(?:;\d+(?:-\d+)?)*$")


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def split_values(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def validate_line_ranges(value: str) -> bool:
    return bool(value and LINE_RANGE_RE.match(value))


def text_line_count(case_id: str, document_id: str) -> int | None:
    path = pathlib.Path("data/processed") / case_id / f"{document_id}.txt"
    if not path.exists():
        return None
    return len(path.read_text(encoding="utf-8").splitlines())


def range_endpoints(value: str) -> list[int]:
    endpoints: list[int] = []
    for part in split_values(value):
        if "-" in part:
            _, end = part.split("-", 1)
            endpoints.append(int(end))
        else:
            endpoints.append(int(part))
    return endpoints


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", default="data/processed/human_validated_labels.csv")
    parser.add_argument("--documents", default="data/document_inventory.csv")
    parser.add_argument("--sources", default="data/source_inventory.csv")
    args = parser.parse_args()

    label_path = pathlib.Path(args.labels)
    rows = read_csv(label_path)
    document_rows = read_csv(pathlib.Path(args.documents))
    source_rows = read_csv(pathlib.Path(args.sources))

    document_ids = {row["document_id"] for row in document_rows}
    source_ids = {row["source_id"] for row in source_rows}

    errors: list[str] = []
    warnings: list[str] = []

    with label_path.open(newline="") as f:
        reader = csv.DictReader(f)
        missing = [col for col in REQUIRED_COLUMNS if col not in (reader.fieldnames or [])]
    if missing:
        errors.append(f"missing required columns: {', '.join(missing)}")

    seen_cases: set[str] = set()
    for index, row in enumerate(rows, start=2):
        case_id = row.get("case_id", "").strip()
        if not case_id:
            errors.append(f"row {index}: missing case_id")
            continue
        if case_id in seen_cases:
            errors.append(f"row {index}: duplicate case_id {case_id}")
        seen_cases.add(case_id)

        for column in REQUIRED_COLUMNS:
            if not row.get(column, "").strip():
                errors.append(f"row {index} {case_id}: missing {column}")

        label = row.get("final_label", "").strip()
        if label not in ALLOWED_LABELS:
            errors.append(f"row {index} {case_id}: invalid final_label {label!r}")

        confidence = row.get("final_confidence", "").strip()
        if confidence not in ALLOWED_CONFIDENCE:
            errors.append(f"row {index} {case_id}: invalid final_confidence {confidence!r}")

        alt_label = row.get("alternative_label", "").strip()
        if alt_label and alt_label not in ALLOWED_LABELS:
            errors.append(f"row {index} {case_id}: invalid alternative_label {alt_label!r}")

        evidence_docs = split_values(row.get("primary_evidence_doc", ""))
        evidence_docs.extend(split_values(row.get("secondary_evidence_doc", "")))
        for doc_id in evidence_docs:
            if doc_id not in document_ids:
                errors.append(f"row {index} {case_id}: unknown evidence document {doc_id}")

        for source_id in split_values(row.get("supplementary_source_id", "")):
            if source_id not in source_ids:
                errors.append(f"row {index} {case_id}: unknown supplementary source {source_id}")

        for field in ["primary_evidence_lines", "secondary_evidence_lines"]:
            value = row.get(field, "").strip()
            if value and not validate_line_ranges(value):
                errors.append(f"row {index} {case_id}: invalid {field} {value!r}")

        primary_docs = split_values(row.get("primary_evidence_doc", ""))
        primary_lines = row.get("primary_evidence_lines", "").strip()
        if len(primary_docs) == 1 and validate_line_ranges(primary_lines):
            line_count = text_line_count(case_id, primary_docs[0])
            if line_count is None:
                warnings.append(
                    f"row {index} {case_id}: extracted text not found for {primary_docs[0]}"
                )
            elif any(endpoint > line_count for endpoint in range_endpoints(primary_lines)):
                errors.append(
                    f"row {index} {case_id}: primary evidence line exceeds text length"
                )

    if errors:
        print("validation_status=failed")
        for error in errors:
            print(f"ERROR: {error}")
        for warning in warnings:
            print(f"WARNING: {warning}")
        return 1

    print("validation_status=ok")
    print(f"rows={len(rows)}")
    print(f"cases={len(seen_cases)}")
    if warnings:
        for warning in warnings:
            print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
