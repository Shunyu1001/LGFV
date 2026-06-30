#!/usr/bin/env python3
"""Validate the 50-case expansion target queue."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "data" / "analysis_inputs" / "validation_expansion_targets.csv"

REQUIRED_COLUMNS = [
    "target_id",
    "priority",
    "province",
    "city",
    "target_platform",
    "platform_status",
    "selection_stratum",
    "historical_capacity_bin",
    "debt_pressure_target",
    "land_finance_target",
    "source_search_status",
    "next_search_terms",
    "notes",
]

ALLOWED_PLATFORM_STATUS = {
    "documented_candidate",
    "needs_confirmation",
    "to_identify",
}

ALLOWED_SOURCE_STATUS = {
    "already_documented",
    "complete_started_source_collection",
    "documents_found",
    "not_started",
    "source_started",
}


def main() -> None:
    with TARGETS.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != REQUIRED_COLUMNS:
            raise ValueError(
                "Unexpected columns. "
                f"Expected {REQUIRED_COLUMNS}, found {reader.fieldnames}"
            )
        rows = list(reader)

    if len(rows) < 50:
        raise ValueError(f"Expected at least 50 targets, found {len(rows)}")

    seen: set[str] = set()
    for idx, row in enumerate(rows, start=2):
        target_id = row["target_id"].strip()
        if not target_id:
            raise ValueError(f"Missing target_id at line {idx}")
        if target_id in seen:
            raise ValueError(f"Duplicate target_id {target_id} at line {idx}")
        seen.add(target_id)

        for column in ["priority", "province", "city", "selection_stratum"]:
            if not row[column].strip():
                raise ValueError(f"Missing {column} at line {idx}")

        if row["platform_status"] not in ALLOWED_PLATFORM_STATUS:
            raise ValueError(
                f"Unexpected platform_status {row['platform_status']} at line {idx}"
            )

        if row["source_search_status"] not in ALLOWED_SOURCE_STATUS:
            raise ValueError(
                f"Unexpected source_search_status {row['source_search_status']} "
                f"at line {idx}"
            )

        if row["platform_status"] == "to_identify" and row["target_platform"].strip():
            raise ValueError(
                f"Line {idx} has a platform name but platform_status=to_identify"
            )

        if row["platform_status"] != "to_identify" and not row[
            "target_platform"
        ].strip():
            raise ValueError(
                f"Line {idx} has platform_status={row['platform_status']} "
                "but no target_platform"
            )

        if not row["next_search_terms"].strip():
            raise ValueError(f"Missing next_search_terms at line {idx}")

    print("validation_expansion_targets_validation=ok")
    print(f"rows={len(rows)}")


if __name__ == "__main__":
    main()
