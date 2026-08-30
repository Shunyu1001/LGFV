#!/usr/bin/env python3
"""Audit exact-key geography joins for the proposed validation frame."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FRAME = ROOT / "data" / "validation" / "proposed_one_sided_validation_frame.csv"
MASTER = ROOT / "data" / "analysis_inputs" / "master_case_pool.csv"
SEED = (
    ROOT
    / "data"
    / "analysis_inputs"
    / "llm_candidate_pool_seed_2026_07_03_expanded.csv"
)
SOURCES = ROOT / "data" / "source_inventory.csv"
DOCUMENTS = ROOT / "data" / "document_inventory.csv"
OUT_CROSSWALK = (
    ROOT / "data" / "validation" / "proposed_validation_geography_crosswalk.csv"
)
OUT_ENRICHED = (
    ROOT
    / "data"
    / "validation"
    / "proposed_one_sided_validation_frame_enriched.csv"
)
OUT_METRICS = ROOT / "experiments" / "EXP-20260830-008" / "metrics.json"

REQUIRED_RESOLVED = 116


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def compact_name(value: str) -> str:
    return re.sub(r"[^\w\u4e00-\u9fff]", "", (value or "").lower())


def split_ids(value: str) -> set[str]:
    return {item.strip() for item in (value or "").split(";") if item.strip()}


def geography_pairs(rows: list[dict[str, str]]) -> set[tuple[str, str]]:
    return {
        (row.get("province", "").strip(), row.get("city", "").strip())
        for row in rows
        if row.get("province", "").strip() and row.get("city", "").strip()
    }


def csv_text(fieldnames: list[str], rows: list[dict[str, object]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def index_rows(
    rows: list[dict[str, str]], field: str, *, normalize_name: bool = False
) -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        value = row.get(field, "").strip()
        if not value:
            continue
        key = compact_name(value) if normalize_name else value
        result[key].append(row)
    return result


def candidate_match(
    source_label: str,
    index: dict[str, list[dict[str, str]]],
    keys: set[str],
) -> tuple[str, str, set[tuple[str, str]]] | None:
    matched_rows: list[dict[str, str]] = []
    matched_keys: list[str] = []
    for key in sorted(keys):
        rows = index.get(key, [])
        if rows:
            matched_rows.extend(rows)
            matched_keys.append(key)
    pairs = geography_pairs(matched_rows)
    if not pairs:
        return None
    return source_label, ";".join(matched_keys), pairs


def build_outputs() -> tuple[dict[Path, str], dict[str, object]]:
    frame = read_csv(FRAME)
    master = read_csv(MASTER)
    seed = read_csv(SEED)
    sources = read_csv(SOURCES)
    documents = read_csv(DOCUMENTS)

    indexes = {
        "master_case_pool.case_id": index_rows(master, "case_id"),
        "candidate_seed.source_row_id": index_rows(seed, "source_row_id"),
        "candidate_seed.pool_id": index_rows(seed, "pool_id"),
        "source_inventory.case_id": index_rows(sources, "case_id"),
        "source_inventory.source_id": index_rows(sources, "source_id"),
        "document_inventory.document_id": index_rows(documents, "document_id"),
        "document_inventory.case_id": index_rows(documents, "case_id"),
    }
    name_indexes = {
        "master_case_pool.company_name": index_rows(
            master, "company_name", normalize_name=True
        ),
        "candidate_seed.issuer_name": index_rows(
            seed, "issuer_name", normalize_name=True
        ),
        "source_inventory.company_name": index_rows(
            sources, "company_name", normalize_name=True
        ),
        "document_inventory.company_name": index_rows(
            documents, "company_name", normalize_name=True
        ),
    }

    crosswalk_fields = [
        "validation_unit_id",
        "issuer_name",
        "original_province",
        "original_city",
        "proposed_province",
        "proposed_city",
        "resolution_status",
        "join_source",
        "join_key",
        "candidate_geography_pairs",
        "random_draw_executed",
    ]
    crosswalk: list[dict[str, object]] = []
    enriched: list[dict[str, object]] = []
    initial_incomplete = 0

    for row in frame:
        original_province = row["province"].strip()
        original_city = row["city"].strip()
        proposed_province = original_province
        proposed_city = original_city
        join_source = "experiment_003_frame"
        join_key = row["validation_unit_id"]
        candidate_pairs: set[tuple[str, str]] = set()
        if original_province and original_city:
            status = "preexisting"
        else:
            initial_incomplete += 1
            source_row_ids = split_ids(row["source_row_ids"])
            pool_ids = split_ids(row["pool_ids"])
            document_ids = split_ids(row["evidence_document_ids"])
            attempts = [
                candidate_match(
                    "master_case_pool.case_id",
                    indexes["master_case_pool.case_id"],
                    source_row_ids,
                ),
                candidate_match(
                    "candidate_seed.source_row_id",
                    indexes["candidate_seed.source_row_id"],
                    source_row_ids,
                ),
                candidate_match(
                    "candidate_seed.pool_id",
                    indexes["candidate_seed.pool_id"],
                    pool_ids,
                ),
                candidate_match(
                    "source_inventory.case_id",
                    indexes["source_inventory.case_id"],
                    source_row_ids,
                ),
                candidate_match(
                    "source_inventory.source_id",
                    indexes["source_inventory.source_id"],
                    source_row_ids,
                ),
                candidate_match(
                    "document_inventory.document_id",
                    indexes["document_inventory.document_id"],
                    document_ids,
                ),
                candidate_match(
                    "document_inventory.case_id",
                    indexes["document_inventory.case_id"],
                    source_row_ids,
                ),
            ]
            match = next((attempt for attempt in attempts if attempt is not None), None)

            if match is None:
                issuer_key = compact_name(row["issuer_name"])
                name_attempts = [
                    candidate_match(label, index, {issuer_key})
                    for label, index in name_indexes.items()
                ]
                match = next(
                    (attempt for attempt in name_attempts if attempt is not None), None
                )

            if match is None:
                status = "unresolved"
                join_source = ""
                join_key = ""
            else:
                join_source, join_key, candidate_pairs = match
                if len(candidate_pairs) == 1:
                    proposed_province, proposed_city = next(iter(candidate_pairs))
                    status = "resolved_exact_join"
                else:
                    status = "conflict"

        pair_text = ";".join(
            f"{province}|{city}" for province, city in sorted(candidate_pairs)
        )
        crosswalk.append(
            {
                "validation_unit_id": row["validation_unit_id"],
                "issuer_name": row["issuer_name"],
                "original_province": original_province,
                "original_city": original_city,
                "proposed_province": proposed_province,
                "proposed_city": proposed_city,
                "resolution_status": status,
                "join_source": join_source,
                "join_key": join_key,
                "candidate_geography_pairs": pair_text,
                "random_draw_executed": "false",
            }
        )
        enriched_row: dict[str, object] = dict(row)
        enriched_row["province"] = proposed_province
        enriched_row["city"] = proposed_city
        enriched_row["geography_resolution_status"] = status
        enriched_row["geography_join_source"] = join_source
        enriched_row["geography_join_key"] = join_key
        enriched.append(enriched_row)

    status_counts = Counter(str(row["resolution_status"]) for row in crosswalk)
    newly_resolved = status_counts["resolved_exact_join"]
    conflicts = status_counts["conflict"]
    unresolved = status_counts["unresolved"]
    sources_used = Counter(
        str(row["join_source"])
        for row in crosswalk
        if row["resolution_status"] == "resolved_exact_join"
    )
    threshold_passed = newly_resolved >= REQUIRED_RESOLVED
    metrics: dict[str, object] = {
        "experiment_id": "EXP-20260830-008",
        "base_commit": "45714fa884580f4a6c77e7fbce30d3c46f41e2c9",
        "frame_rows": len(frame),
        "initial_incomplete_units": initial_incomplete,
        "preexisting_complete_units": status_counts["preexisting"],
        "newly_resolved_units": newly_resolved,
        "unresolved_units": unresolved,
        "conflicting_units": conflicts,
        "required_newly_resolved_units": REQUIRED_RESOLVED,
        "coverage_threshold_passed": threshold_passed,
        "join_sources_used": dict(sorted(sources_used.items())),
        "company_name_parsing_used": False,
        "exact_normalized_name_fallback_allowed": True,
        "external_lookup_used": False,
        "random_draw_executed": False,
        "random_seed": None,
        "experiment_gate_passed": threshold_passed and conflicts == 0,
    }

    enriched_fields = list(frame[0].keys()) + [
        "geography_resolution_status",
        "geography_join_source",
        "geography_join_key",
    ]
    outputs = {
        OUT_CROSSWALK: csv_text(crosswalk_fields, crosswalk),
        OUT_ENRICHED: csv_text(enriched_fields, enriched),
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
        print("validation-geography outputs are reproducible")
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        print("wrote validation-geography outputs")
    print(f"newly_resolved_units={metrics['newly_resolved_units']}")
    print(f"unresolved_units={metrics['unresolved_units']}")
    print(f"conflicting_units={metrics['conflicting_units']}")
    print(f"experiment_gate_passed={str(metrics['experiment_gate_passed']).lower()}")
    print("random_draw_executed=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
