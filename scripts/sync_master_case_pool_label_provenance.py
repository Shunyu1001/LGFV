#!/usr/bin/env python3
"""Synchronize working-reference producer metadata into the master case pool."""

from __future__ import annotations

import argparse
import csv
import io
import pathlib
import sys


PRODUCER_COLUMN = "reference_label_producer"
VALIDATED_STATUS = "human_validated"


def read_csv(path: pathlib.Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def render_csv(
    columns: list[str], rows: list[dict[str, str]], lineterminator: str = "\n"
) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer, fieldnames=columns, lineterminator=lineterminator
    )
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def synchronize(
    master_columns: list[str],
    master_rows: list[dict[str, str]],
    reference_rows: list[dict[str, str]],
) -> tuple[list[str], list[dict[str, str]]]:
    reference_by_case: dict[str, str] = {}
    for row in reference_rows:
        case_id = row.get("case_id", "").strip()
        producer = row.get(PRODUCER_COLUMN, "").strip()
        if not case_id or not producer:
            raise ValueError("working-reference row lacks case_id or producer")
        if case_id in reference_by_case:
            raise ValueError(f"duplicate working-reference case_id: {case_id}")
        reference_by_case[case_id] = producer

    validated_ids = {
        row.get("case_id", "").strip()
        for row in master_rows
        if row.get("validation_status", "").strip() == VALIDATED_STATUS
    }
    if validated_ids != set(reference_by_case):
        missing = sorted(validated_ids - set(reference_by_case))
        extra = sorted(set(reference_by_case) - validated_ids)
        raise ValueError(
            "working-reference/master case mismatch: "
            f"missing_reference={missing}; extra_reference={extra}"
        )

    output_columns = list(master_columns)
    if PRODUCER_COLUMN not in output_columns:
        insert_at = output_columns.index("human_reviewer")
        output_columns.insert(insert_at, PRODUCER_COLUMN)

    output_rows: list[dict[str, str]] = []
    for source_row in master_rows:
        row = dict(source_row)
        case_id = row.get("case_id", "").strip()
        expected = reference_by_case.get(case_id, "")
        existing = row.get(PRODUCER_COLUMN, "").strip()
        if existing and existing != expected:
            raise ValueError(
                f"conflicting producer for {case_id}: {existing!r} != {expected!r}"
            )
        row[PRODUCER_COLUMN] = expected
        output_rows.append(row)

    return output_columns, output_rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--master", default="data/analysis_inputs/master_case_pool.csv"
    )
    parser.add_argument(
        "--references", default="data/processed/working_reference_labels.csv"
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    master_path = pathlib.Path(args.master)
    master_columns, master_rows = read_csv(master_path)
    _, reference_rows = read_csv(pathlib.Path(args.references))
    output_columns, output_rows = synchronize(
        master_columns, master_rows, reference_rows
    )
    raw_current = master_path.read_bytes()
    lineterminator = "\r\n" if b"\r\n" in raw_current else "\n"
    output = render_csv(output_columns, output_rows, lineterminator)
    current = raw_current.decode("utf-8")
    if args.check:
        if current != output:
            print("provenance_sync=stale")
            return 1
        print("provenance_sync=ok")
        print(f"rows={len(output_rows)}")
        print(f"working_reference_rows={len(reference_rows)}")
        return 0

    master_path.write_bytes(output.encode("utf-8"))
    print("provenance_sync=written")
    print(f"rows={len(output_rows)}")
    print(f"working_reference_rows={len(reference_rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
