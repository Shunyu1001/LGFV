#!/usr/bin/env python3
"""Make working-reference provenance explicit in the canonical label file."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LABELS = ROOT / "data" / "processed" / "working_reference_labels.csv"


def main() -> None:
    with LABELS.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    legacy = "reference_label_producer"
    producer = "reference_label_producer"
    if legacy in fieldnames:
        fieldnames[fieldnames.index(legacy)] = producer
    elif producer not in fieldnames:
        raise ValueError("Expected a reviewer or producer provenance column")

    insert_at = fieldnames.index(producer) + 1
    for name in ("label_role", "human_confirmation_status"):
        if name not in fieldnames:
            fieldnames.insert(insert_at, name)
            insert_at += 1

    for row in rows:
        row.pop(legacy, None)
        row[producer] = "Codex source-packet review on behalf of Shunyu Hao"
        row["label_role"] = "working_reference"
        row["human_confirmation_status"] = "pending_human_confirmation"

    temp = LABELS.with_suffix(".csv.tmp")
    with temp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(LABELS)

    print(f"working_reference_rows={len(rows)}")
    print("human_confirmation_status=pending_human_confirmation")


if __name__ == "__main__":
    main()
