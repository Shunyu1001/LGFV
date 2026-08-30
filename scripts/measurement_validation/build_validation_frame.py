#!/usr/bin/env python3
"""Build the proposed one-sided screen-validation frame without sampling it."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCREENING = (
    ROOT
    / "data"
    / "analysis_inputs"
    / "llm_screening_sample_2026_07_03_expanded.csv"
)
QUEUE = (
    ROOT
    / "data"
    / "analysis_inputs"
    / "surrogate_validation_queue_2026_07_03_expanded.csv"
)
GOLD = ROOT / "data" / "processed" / "human_validated_labels.csv"
OUT_FRAME = (
    ROOT / "data" / "validation" / "proposed_one_sided_validation_frame.csv"
)
OUT_BLINDED = (
    ROOT
    / "experiments"
    / "EXP-20260830-007"
    / "artifacts"
    / "blinded_review_template.csv"
)
OUT_METRICS = ROOT / "experiments" / "EXP-20260830-007" / "metrics.json"

POSITIVE_N = 97
POSITIVE_SAMPLE_N = 60
NONPOSITIVE_N = 36


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def compact_name(value: str) -> str:
    return re.sub(r"[^\w\u4e00-\u9fff]", "", (value or "").lower())


def unique_nonblank(rows: list[dict[str, str]], field: str) -> list[str]:
    return sorted({row[field].strip() for row in rows if row[field].strip()})


def joined_unique(rows: list[dict[str, str]], field: str) -> str:
    return ";".join(unique_nonblank(rows, field))


def document_ids(rows: list[dict[str, str]]) -> str:
    identifiers: set[str] = set()
    for row in rows:
        for value in row["evidence_basis"].split(";"):
            cleaned = value.strip()
            if cleaned:
                identifiers.add(cleaned)
    return ";".join(sorted(identifiers))


def csv_text(fieldnames: list[str], rows: list[dict[str, object]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def build_outputs() -> tuple[dict[Path, str], dict[str, object]]:
    screening = read_csv(SCREENING)
    queue = read_csv(QUEUE)
    gold = read_csv(GOLD)

    gold_keys = {
        compact_name(row["company_name"])
        for row in gold
        if row["company_name"].strip()
    }
    candidate_by_key: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in screening:
        if row["label_source"] != "codex_surrogate":
            continue
        key = compact_name(row["issuer_name"])
        if key:
            candidate_by_key[key].append(row)

    frame_groups: dict[str, tuple[str, list[dict[str, str]]]] = {}
    for key, rows in candidate_by_key.items():
        if key in gold_keys:
            continue
        statuses = {row["screening_status"] for row in rows}
        if "llm_surrogate_exit_type" in statuses:
            stratum = "screen_positive_nominal"
        elif "llm_screened_no_direct_formal_event" in statuses:
            stratum = "screened_no_direct_formal_event"
        else:
            continue
        frame_groups[key] = (stratum, rows)

    queue_by_key: dict[str, dict[str, str]] = {}
    duplicate_queue_keys: list[str] = []
    for row in queue:
        key = compact_name(row["issuer_name"])
        if key in queue_by_key:
            duplicate_queue_keys.append(key)
        queue_by_key[key] = row

    positive_keys = {
        key for key, (stratum, _) in frame_groups.items() if stratum == "screen_positive_nominal"
    }
    nonpositive_keys = {
        key
        for key, (stratum, _) in frame_groups.items()
        if stratum == "screened_no_direct_formal_event"
    }
    queue_keys = set(queue_by_key)
    positive_missing_queue = sorted(positive_keys - queue_keys)
    queue_not_positive = sorted(queue_keys - positive_keys)

    structural_errors: list[str] = []
    if len(frame_groups) != POSITIVE_N + NONPOSITIVE_N:
        structural_errors.append(f"frame rows {len(frame_groups)} != 133")
    if len(positive_keys) != POSITIVE_N:
        structural_errors.append(f"positive rows {len(positive_keys)} != {POSITIVE_N}")
    if len(nonpositive_keys) != NONPOSITIVE_N:
        structural_errors.append(f"nonpositive rows {len(nonpositive_keys)} != {NONPOSITIVE_N}")
    if duplicate_queue_keys:
        structural_errors.append(f"duplicate queue keys: {duplicate_queue_keys}")
    if positive_missing_queue:
        structural_errors.append(f"positive issuers missing queue rows: {positive_missing_queue}")
    if queue_not_positive:
        structural_errors.append(f"queue rows outside positive frame: {queue_not_positive}")

    frame_fields = [
        "validation_unit_id",
        "issuer_key",
        "issuer_name",
        "province",
        "city",
        "design_stratum",
        "stratum_population_n",
        "proposed_stratum_sample_n",
        "inclusion_probability",
        "design_weight",
        "disclosure_rows",
        "source_row_ids",
        "pool_ids",
        "evidence_document_ids",
        "queue_id",
        "random_draw_executed",
    ]
    frame_rows: list[dict[str, object]] = []
    unresolved_identifier_fields: list[dict[str, str]] = []
    for key in sorted(frame_groups):
        stratum, rows = frame_groups[key]
        names = unique_nonblank(rows, "issuer_name")
        provinces = unique_nonblank(rows, "province")
        cities = unique_nonblank(rows, "city")
        sources = joined_unique(rows, "source_row_id")
        pools = joined_unique(rows, "pool_id")
        documents = document_ids(rows)
        if len(names) != 1:
            structural_errors.append(f"issuer name conflict for {key}: {names}")
        if len(provinces) != 1:
            unresolved_identifier_fields.append({"issuer_key": key, "field": "province"})
        if len(cities) != 1:
            unresolved_identifier_fields.append({"issuer_key": key, "field": "city"})
        if not sources:
            unresolved_identifier_fields.append({"issuer_key": key, "field": "source_row_ids"})
        if not pools:
            unresolved_identifier_fields.append({"issuer_key": key, "field": "pool_ids"})
        if not documents:
            unresolved_identifier_fields.append(
                {"issuer_key": key, "field": "evidence_document_ids"}
            )

        if stratum == "screen_positive_nominal":
            population_n = POSITIVE_N
            proposed_n = POSITIVE_SAMPLE_N
            inclusion_probability = POSITIVE_SAMPLE_N / POSITIVE_N
            queue_id = queue_by_key.get(key, {}).get("queue_id", "")
        else:
            population_n = NONPOSITIVE_N
            proposed_n = NONPOSITIVE_N
            inclusion_probability = 1.0
            queue_id = ""
        frame_rows.append(
            {
                "validation_unit_id": "mv_" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:12],
                "issuer_key": key,
                "issuer_name": names[0] if len(names) == 1 else "",
                "province": provinces[0] if len(provinces) == 1 else "",
                "city": cities[0] if len(cities) == 1 else "",
                "design_stratum": stratum,
                "stratum_population_n": population_n,
                "proposed_stratum_sample_n": proposed_n,
                "inclusion_probability": f"{inclusion_probability:.6f}",
                "design_weight": f"{1 / inclusion_probability:.6f}",
                "disclosure_rows": len(rows),
                "source_row_ids": sources,
                "pool_ids": pools,
                "evidence_document_ids": documents,
                "queue_id": queue_id,
                "random_draw_executed": "false",
            }
        )

    unit_ids = [row["validation_unit_id"] for row in frame_rows]
    if len(unit_ids) != len(set(unit_ids)):
        structural_errors.append("hashed validation unit IDs are not unique")
    if structural_errors:
        raise ValueError("; ".join(structural_errors))

    blinded_fields = [
        "validation_unit_id",
        "issuer_name",
        "province",
        "city",
        "packet_source_row_ids",
        "packet_document_ids",
        "coder_id",
        "coding_date",
        "case_eligible",
        "formal_event_found",
        "formal_event_summary",
        "baseline_platform_function",
        "post_event_function",
        "final_label",
        "alternative_label",
        "confidence",
        "source_coverage_score",
        "continued_function_evidence_score",
        "key_source_references",
        "ambiguity_note",
        "remaining_caveat",
        "adjudication_required",
        "coder_signature",
    ]
    entry_fields = set(blinded_fields[6:])
    blinded_rows: list[dict[str, object]] = []
    for frame_row in frame_rows:
        row = {field: "" for field in blinded_fields}
        row.update(
            {
                "validation_unit_id": frame_row["validation_unit_id"],
                "issuer_name": frame_row["issuer_name"],
                "province": frame_row["province"],
                "city": frame_row["city"],
                "packet_source_row_ids": frame_row["source_row_ids"],
                "packet_document_ids": frame_row["evidence_document_ids"],
            }
        )
        blinded_rows.append(row)

    forbidden_tokens = {
        "stratum",
        "screen",
        "surrogate",
        "prediction",
        "model",
        "rationale",
        "existing_label",
        "gold",
        "selected",
    }
    forbidden_fields = sorted(
        field
        for field in blinded_fields
        if any(token in field.lower() for token in forbidden_tokens)
    )
    populated_entry_cells = sum(
        bool(str(row[field]).strip()) for row in blinded_rows for field in entry_fields
    )
    if forbidden_fields:
        raise ValueError(f"blinded template contains forbidden fields: {forbidden_fields}")
    if populated_entry_cells:
        raise ValueError("blinded template contains pre-populated coder-entry cells")

    metrics: dict[str, object] = {
        "experiment_id": "EXP-20260830-007",
        "base_commit": "fe2c98b9e86d15603804e06cb564c19310cf561d",
        "frame_rows": len(frame_rows),
        "unique_validation_unit_ids": len(set(unit_ids)),
        "strata": dict(Counter(row["design_stratum"] for row in frame_rows)),
        "positive_queue_rows": len(queue),
        "positive_missing_queue_rows": len(positive_missing_queue),
        "queue_rows_outside_positive_frame": len(queue_not_positive),
        "gold_overlap_rows": sum(
            compact_name(str(row["issuer_name"])) in gold_keys for row in frame_rows
        ),
        "blank_required_design_fields": sum(
            not str(row[field]).strip()
            for row in frame_rows
            for field in (
                "issuer_name",
                "province",
                "city",
                "source_row_ids",
                "pool_ids",
                "evidence_document_ids",
            )
        ),
        "blinded_template_rows": len(blinded_rows),
        "blinded_forbidden_fields": forbidden_fields,
        "blinded_populated_coder_entry_cells": populated_entry_cells,
        "unresolved_identifier_fields": len(unresolved_identifier_fields),
        "unresolved_identifier_field_counts": dict(
            Counter(row["field"] for row in unresolved_identifier_fields)
        ),
        "frame_gate_passed": not unresolved_identifier_fields,
        "random_draw_executed": False,
        "random_seed": None,
    }

    outputs = {
        OUT_FRAME: csv_text(frame_fields, frame_rows),
        OUT_BLINDED: csv_text(blinded_fields, blinded_rows),
        OUT_METRICS: json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n",
    }
    return outputs, metrics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if tracked outputs differ from deterministic regeneration.",
    )
    args = parser.parse_args()

    outputs, metrics = build_outputs()
    if args.check:
        mismatches = []
        for path, expected in outputs.items():
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                mismatches.append(str(path.relative_to(ROOT)))
        if mismatches:
            raise SystemExit("Output mismatch: " + ", ".join(mismatches))
        print("validation-frame outputs are reproducible")
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        print("wrote validation-frame outputs")
    print(f"validation_frame_rows={metrics['frame_rows']}")
    print(f"frame_gate_passed={str(metrics['frame_gate_passed']).lower()}")
    print(f"random_draw_executed={str(metrics['random_draw_executed']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
