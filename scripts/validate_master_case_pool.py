#!/usr/bin/env python3
"""Validate the master LGFV case-pool file."""

from __future__ import annotations

import argparse
import csv
import pathlib
import sys


REQUIRED_COLUMNS = [
    "case_id",
    "case_pool_status",
    "validation_status",
    "province",
    "city",
    "platform",
    "source_doc_ids",
    "formal_event",
    "continued_function",
    "exit_type",
    "confidence",
    "historical_capacity_bin",
    "debt_pressure_status",
    "land_finance_dependence_status",
]

ALLOWED_POOL_STATUS = {
    "human_validated",
    "llm_candidate_ready",
    "source_started",
    "candidate_not_started",
}

ALLOWED_VALIDATION_STATUS = {
    "human_validated",
    "llm_coded",
    "not_validated",
}

ALLOWED_EXIT_TYPES = {
    "",
    "substantive_exit",
    "nominal_exit",
    "functional_transfer",
    "liquidation",
    "unclear",
}

ALLOWED_CONFIDENCE = {"", "high", "medium", "low"}
ALLOWED_CAPACITY_BINS = {"", "high", "middle", "low"}
ALLOWED_STATUS = {"", "not_collected", "targeted_for_collection", "collected"}


def read_csv(path: pathlib.Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)


def nonempty(row: dict[str, str], column: str) -> bool:
    return bool(row.get(column, "").strip())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/analysis_inputs/master_case_pool.csv")
    args = parser.parse_args()

    columns, rows = read_csv(pathlib.Path(args.input))
    errors: list[str] = []
    warnings: list[str] = []

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in columns]
    if missing_columns:
        errors.append(f"missing required columns: {', '.join(missing_columns)}")

    seen: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        case_id = row.get("case_id", "").strip()
        if not case_id:
            errors.append(f"row {row_number}: missing case_id")
            continue
        if case_id in seen:
            errors.append(f"row {row_number}: duplicate case_id {case_id}")
        seen.add(case_id)

        if row.get("case_pool_status", "") not in ALLOWED_POOL_STATUS:
            errors.append(
                f"row {row_number} {case_id}: invalid case_pool_status "
                f"{row.get('case_pool_status', '')!r}"
            )
        if row.get("validation_status", "") not in ALLOWED_VALIDATION_STATUS:
            errors.append(
                f"row {row_number} {case_id}: invalid validation_status "
                f"{row.get('validation_status', '')!r}"
            )
        if row.get("exit_type", "") not in ALLOWED_EXIT_TYPES:
            errors.append(
                f"row {row_number} {case_id}: invalid exit_type {row.get('exit_type', '')!r}"
            )
        if row.get("confidence", "") not in ALLOWED_CONFIDENCE:
            errors.append(
                f"row {row_number} {case_id}: invalid confidence {row.get('confidence', '')!r}"
            )
        if row.get("historical_capacity_bin", "") not in ALLOWED_CAPACITY_BINS:
            errors.append(
                f"row {row_number} {case_id}: invalid historical_capacity_bin "
                f"{row.get('historical_capacity_bin', '')!r}"
            )
        for column in ["debt_pressure_status", "land_finance_dependence_status"]:
            if row.get(column, "") not in ALLOWED_STATUS:
                errors.append(
                    f"row {row_number} {case_id}: invalid {column} {row.get(column, '')!r}"
                )

        is_validated = row.get("validation_status", "") == "human_validated"
        if is_validated:
            for column in [
                "province",
                "city",
                "platform",
                "formal_event",
                "continued_function",
                "exit_type",
                "confidence",
                "source_coverage_score",
                "human_reviewer",
                "validation_date",
            ]:
                if not nonempty(row, column):
                    errors.append(f"row {row_number} {case_id}: validated row missing {column}")
        else:
            if nonempty(row, "exit_type") and row.get("validation_status", "") == "not_validated":
                warnings.append(
                    f"row {row_number} {case_id}: unvalidated row has exit_type "
                    f"{row.get('exit_type')!r}"
                )

    if errors:
        print("master_case_pool_validation=failed")
        for error in errors:
            print(f"ERROR: {error}")
        for warning in warnings:
            print(f"WARNING: {warning}")
        return 1

    print("master_case_pool_validation=ok")
    print(f"rows={len(rows)}")
    print(f"cases={len(seen)}")
    if warnings:
        for warning in warnings:
            print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
