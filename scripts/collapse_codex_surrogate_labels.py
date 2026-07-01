#!/usr/bin/env python3
"""Collapse disclosure-level Codex surrogate labels to issuer-level rows."""

from __future__ import annotations

import argparse
import csv
import pathlib
from collections import Counter, defaultdict
from datetime import date


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "analysis_inputs" / f"codex_surrogate_labels_{date.today():%Y_%m_%d}.csv"
DEFAULT_OUTPUT = ROOT / "data" / "analysis_inputs" / f"codex_surrogate_issuer_summary_{date.today():%Y_%m_%d}.csv"

FIELDS = [
    "issuer_name",
    "surrogate_rows",
    "source_row_ids",
    "pool_ids",
    "exit_type",
    "exit_type_counts",
    "max_confidence",
    "max_source_coverage_score",
    "max_continued_function_evidence_score",
    "formal_event_examples",
    "continued_function_examples",
    "needs_human_review",
]

CONFIDENCE_ORDER = {"low": 1, "medium": 2, "high": 3}


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def max_by_order(values: list[str], order: dict[str, int]) -> str:
    cleaned = [value for value in values if value]
    if not cleaned:
        return ""
    return max(cleaned, key=lambda value: order.get(value, 0))


def max_numeric(values: list[str]) -> str:
    nums = []
    for value in values:
        try:
            nums.append(int(value))
        except (TypeError, ValueError):
            continue
    return str(max(nums)) if nums else ""


def compact_examples(values: list[str], limit: int = 2) -> str:
    seen: list[str] = []
    for value in values:
        text = " ".join((value or "").split())
        if not text or text in seen:
            continue
        seen.append(text[:220])
        if len(seen) >= limit:
            break
    return " | ".join(seen)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=pathlib.Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    rows = [
        row
        for row in read_csv(args.input)
        if row.get("label_source") == "codex_surrogate" and row.get("surrogate_status") == "labeled"
    ]
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row.get("issuer_name", "")].append(row)

    output: list[dict[str, str]] = []
    for issuer, issuer_rows in sorted(groups.items()):
        label_counts = Counter(row.get("exit_type", "") for row in issuer_rows)
        if len(label_counts) == 1:
            exit_type = next(iter(label_counts))
        else:
            exit_type = "mixed"
        output.append(
            {
                "issuer_name": issuer,
                "surrogate_rows": str(len(issuer_rows)),
                "source_row_ids": "; ".join(row.get("source_row_id", "") for row in issuer_rows),
                "pool_ids": "; ".join(row.get("pool_id", "") for row in issuer_rows),
                "exit_type": exit_type,
                "exit_type_counts": "; ".join(f"{label}:{count}" for label, count in sorted(label_counts.items())),
                "max_confidence": max_by_order([row.get("confidence", "") for row in issuer_rows], CONFIDENCE_ORDER),
                "max_source_coverage_score": max_numeric([row.get("source_coverage_score", "") for row in issuer_rows]),
                "max_continued_function_evidence_score": max_numeric(
                    [row.get("continued_function_evidence_score", "") for row in issuer_rows]
                ),
                "formal_event_examples": compact_examples([row.get("formal_event_summary", "") for row in issuer_rows]),
                "continued_function_examples": compact_examples(
                    [row.get("continued_function_summary", "") for row in issuer_rows]
                ),
                "needs_human_review": "true",
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    print(f"wrote {len(output)} issuer rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
