#!/usr/bin/env python3
"""Build a human-review queue from issuer-level Codex surrogate labels."""

from __future__ import annotations

import argparse
import csv
import pathlib
from datetime import date


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_LABELS = ROOT / "data" / "analysis_inputs" / f"codex_surrogate_labels_{date.today():%Y_%m_%d}.csv"
DEFAULT_ISSUERS = ROOT / "data" / "analysis_inputs" / f"codex_surrogate_issuer_summary_{date.today():%Y_%m_%d}.csv"
DEFAULT_SOURCES = ROOT / "data" / "source_inventory.csv"
DEFAULT_DOCS = ROOT / "data" / "document_inventory.csv"
DEFAULT_OUTPUT = ROOT / "data" / "analysis_inputs" / f"surrogate_validation_queue_{date.today():%Y_%m_%d}.csv"

FIELDS = [
    "queue_id",
    "review_priority",
    "issuer_name",
    "selected_source_row_id",
    "selected_pool_id",
    "surrogate_exit_type",
    "surrogate_confidence",
    "surrogate_rows",
    "repeated_disclosure_count",
    "source_coverage_score",
    "continued_function_evidence_score",
    "source_date",
    "source_url",
    "source_title",
    "document_count",
    "usable_text_count",
    "formal_event_example",
    "continued_function_example",
    "review_task",
    "gold_standard_overlap",
    "gold_case_id",
    "validation_status",
]

CONFIDENCE_ORDER = {"low": 1, "medium": 2, "high": 3}


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def score_label(row: dict[str, str]) -> tuple[int, int, int]:
    try:
        coverage = int(row.get("source_coverage_score", "0"))
    except ValueError:
        coverage = 0
    try:
        function = int(row.get("continued_function_evidence_score", "0"))
    except ValueError:
        function = 0
    confidence = CONFIDENCE_ORDER.get(row.get("confidence", ""), 0)
    return coverage, function, confidence


def priority(row: dict[str, str], issuer_row: dict[str, str]) -> str:
    coverage, function, confidence = score_label(row)
    repeated = int(issuer_row.get("surrogate_rows", "1") or "1")
    if coverage >= 3 and function >= 3 and repeated >= 2:
        return "A"
    if coverage >= 3 and function >= 3:
        return "B"
    if coverage >= 3 and confidence >= 2:
        return "C"
    return "D"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", type=pathlib.Path, default=DEFAULT_LABELS)
    parser.add_argument("--issuers", type=pathlib.Path, default=DEFAULT_ISSUERS)
    parser.add_argument("--sources", type=pathlib.Path, default=DEFAULT_SOURCES)
    parser.add_argument("--documents", type=pathlib.Path, default=DEFAULT_DOCS)
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--include-overlap", action="store_true")
    args = parser.parse_args()

    labels = [
        row
        for row in read_csv(args.labels)
        if row.get("label_source") == "codex_surrogate" and row.get("surrogate_status") == "labeled"
    ]
    labels_by_issuer: dict[str, list[dict[str, str]]] = {}
    for row in labels:
        labels_by_issuer.setdefault(row.get("issuer_name", ""), []).append(row)

    sources_by_case = {row.get("case_id", ""): row for row in read_csv(args.sources)}
    docs_by_case: dict[str, list[dict[str, str]]] = {}
    for row in read_csv(args.documents):
        docs_by_case.setdefault(row.get("case_id", ""), []).append(row)

    output: list[dict[str, str]] = []
    for issuer_row in read_csv(args.issuers):
        if issuer_row.get("gold_standard_overlap") == "true" and not args.include_overlap:
            continue
        issuer = issuer_row.get("issuer_name", "")
        issuer_labels = labels_by_issuer.get(issuer, [])
        if not issuer_labels:
            continue
        selected = max(issuer_labels, key=score_label)
        case_id = selected.get("source_row_id", "")
        source = sources_by_case.get(case_id, {})
        documents = docs_by_case.get(case_id, [])
        usable = [row for row in documents if row.get("text_extracted") == "yes"]
        output.append(
            {
                "queue_id": f"svq_{len(output) + 1:03d}",
                "review_priority": priority(selected, issuer_row),
                "issuer_name": issuer,
                "selected_source_row_id": case_id,
                "selected_pool_id": selected.get("pool_id", ""),
                "surrogate_exit_type": selected.get("exit_type", ""),
                "surrogate_confidence": selected.get("confidence", ""),
                "surrogate_rows": issuer_row.get("surrogate_rows", ""),
                "repeated_disclosure_count": issuer_row.get("surrogate_rows", ""),
                "source_coverage_score": selected.get("source_coverage_score", ""),
                "continued_function_evidence_score": selected.get("continued_function_evidence_score", ""),
                "source_date": source.get("source_date", ""),
                "source_url": source.get("source_url", ""),
                "source_title": source.get("source_title", ""),
                "document_count": str(len(documents)),
                "usable_text_count": str(len(usable)),
                "formal_event_example": selected.get("formal_event_summary", ""),
                "continued_function_example": selected.get("continued_function_summary", ""),
                "review_task": "Check original PDFs and extracted text; decide whether to promote to gold-standard label, mark as duplicate, or reject as boundary/non-LGFV.",
                "gold_standard_overlap": issuer_row.get("gold_standard_overlap", ""),
                "gold_case_id": issuer_row.get("gold_case_id", ""),
                "validation_status": "queued_for_human_review",
            }
        )

    output.sort(key=lambda row: (row["review_priority"], -int(row["usable_text_count"] or "0"), row["issuer_name"]))
    for idx, row in enumerate(output, start=1):
        row["queue_id"] = f"svq_{idx:03d}"

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    print(f"wrote {len(output)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
