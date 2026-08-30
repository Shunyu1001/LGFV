#!/usr/bin/env python3
"""Validate blinding, source location, and row identity in coding packets."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GOLD_INPUT = ROOT / "data/processed/working_reference_labels.csv"
POOL_INPUT = ROOT / "data/analysis_inputs/master_case_pool.csv"
DOCUMENTS_INPUT = ROOT / "data/document_inventory.csv"
FRAME_INPUT = ROOT / "data/validation/proposed_one_sided_validation_frame_enriched.csv"
CROSSWALK_INPUT = ROOT / "data/validation/source_supported_validation_geography_scope_crosswalk.csv"
GOLD_PACKET = ROOT / "data/validation/independent_coding/blinded_gold_second_coder_packet.csv"
CANDIDATE_PACKET = ROOT / "data/validation/independent_coding/blinded_probability_validation_packet.csv"
ADJUDICATION_PACKET = ROOT / "data/validation/independent_coding/gold_adjudication_log_template.csv"
METRICS_PATH = ROOT / "experiments/EXP-20260830-014/metrics.json"

CODER_FIELDS = [
    "coder_id", "coding_date", "case_eligible", "formal_event_found",
    "formal_event_summary", "baseline_platform_function", "post_event_function",
    "final_label", "alternative_label", "confidence", "source_coverage_score",
    "continued_function_evidence_score", "key_source_references",
    "ambiguity_note", "remaining_caveat", "coder_signature",
]
ADJUDICATION_ENTRY_FIELDS = [
    "original_coder_id", "second_coder_id", "adjudication_date",
    "original_coder_label", "second_coder_label", "agreement_status",
    "disagreement_domain", "adjudicated_label", "adjudication_rationale",
    "adjudication_source_references", "original_coder_signature",
    "second_coder_signature", "adjudicator_signature",
]
FORBIDDEN_PACKET_HEADERS = {
    "official_exit_year", "official_exit_event", "reference_label_producer",
    "validation_date", "final_rationale", "notes", "llm_label",
    "llm_confidence", "llm_model", "screen_status", "design_stratum",
    "selection_stratum", "inclusion_probability", "design_weight",
    "selected_case", "random_seed", "random_draw_executed",
}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def semicolon(values: list[str]) -> str:
    return ";".join(value for value in values if value)


def expected_source_fields(document_ids: list[str], documents: dict[str, dict[str, str]]) -> dict[str, str]:
    records = [documents[value] for value in document_ids if value in documents]
    return {
        "packet_document_ids": semicolon([record["document_id"] for record in records]),
        "packet_document_titles": semicolon([record["document_title"] for record in records]),
        "packet_page_urls": semicolon([record["document_page_url"] for record in records]),
        "packet_download_urls": semicolon([record["download_url"] for record in records]),
        "packet_expected_archive_paths": semicolon([record["local_file_path"] for record in records]),
    }


def validate(check_metrics: bool = False) -> dict[str, int]:
    gold = {row["case_id"]: row for _, rows in [read_csv(GOLD_INPUT)] for row in rows}
    pool = {row["case_id"]: row for _, rows in [read_csv(POOL_INPUT)] for row in rows}
    documents = {row["document_id"]: row for _, rows in [read_csv(DOCUMENTS_INPUT)] for row in rows}
    frame = {row["validation_unit_id"]: row for _, rows in [read_csv(FRAME_INPUT)] for row in rows}
    crosswalk = {row["validation_unit_id"]: row for _, rows in [read_csv(CROSSWALK_INPUT)] for row in rows}
    gold_fields, gold_packet = read_csv(GOLD_PACKET)
    candidate_fields, candidate_packet = read_csv(CANDIDATE_PACKET)
    adjudication_fields, adjudication = read_csv(ADJUDICATION_PACKET)

    forbidden = sorted(
        FORBIDDEN_PACKET_HEADERS.intersection(gold_fields)
        | FORBIDDEN_PACKET_HEADERS.intersection(candidate_fields)
        | FORBIDDEN_PACKET_HEADERS.intersection(adjudication_fields)
    )
    if forbidden:
        raise ValueError(f"Forbidden fields exposed in packet: {forbidden}")
    if len(gold_packet) != 94 or len({row["packet_case_id"] for row in gold_packet}) != 94:
        raise ValueError("Gold packet must contain 94 unique cases")
    if {row["packet_case_id"] for row in gold_packet} != set(gold):
        raise ValueError("Gold packet IDs do not equal the frozen gold case IDs")
    eligible_ids = {
        unit_id for unit_id, row in crosswalk.items()
        if row["scope_disposition"] == "provisionally_eligible"
        and row["geography_status"] == "source_supported_unique"
    }
    if len(candidate_packet) != 4 or {row["packet_case_id"] for row in candidate_packet} != eligible_ids:
        raise ValueError("Candidate packet does not equal the four geography-verified provisionally eligible units")
    if len(adjudication) != 94 or {row["packet_case_id"] for row in adjudication} != set(gold):
        raise ValueError("Adjudication template must contain the 94 frozen case IDs")

    for row in gold_packet:
        case_id = row["packet_case_id"]
        source = gold[case_id]
        if (row["issuer_name"], row["province"], row["city"]) != (
            source["company_name"], source["province"], source["city"]
        ):
            raise ValueError(f"Gold packet identity drift: {case_id}")
        pool_row = pool.get(case_id, {})
        document_ids = [value for value in pool_row.get("source_doc_ids", "").split(";") if value]
        if not document_ids:
            document_ids = [source["primary_evidence_doc"]]
            document_ids.extend(value for value in source["secondary_evidence_doc"].split(";") if value)
        expected = expected_source_fields(document_ids, documents)
        for field, value in expected.items():
            if row[field] != value:
                raise ValueError(f"Gold packet source drift: {case_id} {field}")

    for row in candidate_packet:
        unit_id = row["packet_case_id"]
        source = crosswalk[unit_id]
        if source["geography_status"] != "source_supported_unique":
            raise ValueError(f"Candidate packet geography is not verified: {unit_id}")
        if (row["issuer_name"], row["province"], row["city"]) != (
            source["issuer_name"], source["province"], source["city"]
        ):
            raise ValueError(f"Candidate packet identity drift: {unit_id}")
        document_ids = [value for value in frame[unit_id]["evidence_document_ids"].split(";") if value]
        expected = expected_source_fields(document_ids, documents)
        for field, value in expected.items():
            if row[field] != value:
                raise ValueError(f"Candidate packet source drift: {unit_id} {field}")

    populated_coder = []
    for row in gold_packet + candidate_packet:
        if not row["packet_document_ids"] or not (row["packet_page_urls"] or row["packet_download_urls"] or row["packet_expected_archive_paths"]):
            raise ValueError(f"Packet lacks source location: {row['packet_case_id']}")
        populated_coder.extend((row["packet_case_id"], field) for field in CODER_FIELDS if row[field])
    if populated_coder:
        raise ValueError(f"Pre-populated coder cells: {populated_coder[:5]}")
    populated_adjudication = [
        (row["packet_case_id"], field)
        for row in adjudication
        for field in ADJUDICATION_ENTRY_FIELDS
        if row[field]
    ]
    if populated_adjudication:
        raise ValueError(f"Pre-populated adjudication cells: {populated_adjudication[:5]}")

    computed = {
        "gold_packet_rows": len(gold_packet),
        "unique_gold_case_ids": len({row["packet_case_id"] for row in gold_packet}),
        "gold_rows_with_document_ids": sum(bool(row["packet_document_ids"]) for row in gold_packet),
        "gold_rows_with_source_location": sum(bool(row["packet_page_urls"] or row["packet_download_urls"] or row["packet_expected_archive_paths"]) for row in gold_packet),
        "candidate_packet_rows": len(candidate_packet),
        "unique_candidate_case_ids": len({row["packet_case_id"] for row in candidate_packet}),
        "candidate_rows_with_document_ids": sum(bool(row["packet_document_ids"]) for row in candidate_packet),
        "candidate_rows_with_source_location": sum(bool(row["packet_page_urls"] or row["packet_download_urls"] or row["packet_expected_archive_paths"]) for row in candidate_packet),
        "adjudication_template_rows": len(adjudication),
        "unique_adjudication_case_ids": len({row["packet_case_id"] for row in adjudication}),
        "populated_coder_entry_cells": len(populated_coder),
        "populated_adjudication_entry_cells": len(populated_adjudication),
    }
    if check_metrics:
        metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        mismatch = {key: (metrics.get(key), value) for key, value in computed.items() if metrics.get(key) != value}
        for path in (GOLD_PACKET, CANDIDATE_PACKET, ADJUDICATION_PACKET):
            relative = str(path.relative_to(ROOT))
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if metrics.get("output_sha256", {}).get(relative) != digest:
                mismatch[f"output_sha256:{relative}"] = (metrics.get("output_sha256", {}).get(relative), digest)
        flags = {
            "random_draw_executed": False,
            "random_seed": None,
            "coding_executed": False,
            "adjudication_executed": False,
            "current_labels_copied": False,
            "model_outputs_copied": False,
            "screen_status_copied": False,
            "reviewer_identity_copied": False,
            "validation_date_copied": False,
        }
        for key, value in flags.items():
            if metrics.get(key) != value:
                mismatch[key] = (metrics.get(key), value)
        if mismatch:
            raise ValueError(f"Packet metrics mismatch: {mismatch}")
    return computed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-metrics", action="store_true")
    args = parser.parse_args()
    print(json.dumps(validate(check_metrics=args.check_metrics), sort_keys=True))


if __name__ == "__main__":
    main()
