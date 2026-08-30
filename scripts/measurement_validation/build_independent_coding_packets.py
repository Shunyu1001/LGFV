#!/usr/bin/env python3
"""Build prediction-free packets for genuine independent human coding."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GOLD_PATH = ROOT / "data/processed/human_validated_labels.csv"
POOL_PATH = ROOT / "data/analysis_inputs/master_case_pool.csv"
DOCUMENTS_PATH = ROOT / "data/document_inventory.csv"
FRAME_PATH = ROOT / "data/validation/proposed_one_sided_validation_frame_enriched.csv"
CROSSWALK_PATH = ROOT / "data/validation/source_supported_validation_geography_scope_crosswalk.csv"
OUTPUT_DIR = ROOT / "data/validation/independent_coding"
GOLD_PACKET_PATH = OUTPUT_DIR / "blinded_gold_second_coder_packet.csv"
CANDIDATE_PACKET_PATH = OUTPUT_DIR / "blinded_probability_validation_packet.csv"
ADJUDICATION_PATH = OUTPUT_DIR / "gold_adjudication_log_template.csv"
METRICS_PATH = ROOT / "experiments/EXP-20260830-014/metrics.json"

EXPERIMENT_ID = "EXP-20260830-014"
BASE_COMMIT = "538d99ac0424e0814c88dab2b00b6ce7257ab6b8"
PACKET_FIELDS = [
    "packet_case_id", "issuer_name", "province", "city",
    "packet_document_ids", "packet_document_titles", "packet_page_urls",
    "packet_download_urls", "packet_expected_archive_paths",
    "source_access_note", "coder_id", "coding_date", "case_eligible",
    "formal_event_found", "formal_event_summary", "baseline_platform_function",
    "post_event_function", "final_label", "alternative_label", "confidence",
    "source_coverage_score", "continued_function_evidence_score",
    "key_source_references", "ambiguity_note", "remaining_caveat",
    "coder_signature",
]
PACKET_ID_FIELDS = PACKET_FIELDS[:10]
CODER_FIELDS = PACKET_FIELDS[10:]
ADJUDICATION_FIELDS = [
    "packet_case_id", "original_coder_id", "second_coder_id",
    "adjudication_date", "original_coder_label", "second_coder_label",
    "agreement_status", "disagreement_domain", "adjudicated_label",
    "adjudication_rationale", "adjudication_source_references",
    "original_coder_signature", "second_coder_signature",
    "adjudicator_signature",
]
ADJUDICATION_ENTRY_FIELDS = ADJUDICATION_FIELDS[1:]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def csv_bytes(rows: list[dict[str, str]], fields: list[str]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row.get(field, "") for field in fields})
    return buffer.getvalue().encode("utf-8")


def packet_source_fields(
    document_ids: list[str], documents: dict[str, dict[str, str]]
) -> dict[str, str]:
    records = [documents[document_id] for document_id in document_ids if document_id in documents]
    return {
        "packet_document_ids": ";".join(record["document_id"] for record in records),
        "packet_document_titles": ";".join(record["document_title"] for record in records),
        "packet_page_urls": ";".join(record["document_page_url"] for record in records if record["document_page_url"]),
        "packet_download_urls": ";".join(record["download_url"] for record in records if record["download_url"]),
        "packet_expected_archive_paths": ";".join(record["local_file_path"] for record in records if record["local_file_path"]),
        "source_access_note": "Use the rights-approved source archive or recorded public disclosure URLs; repository paths are inventory locations and may not contain local files.",
    }


def blank_coder_fields() -> dict[str, str]:
    return {field: "" for field in CODER_FIELDS}


def build_rows() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    gold = read_csv(GOLD_PATH)
    pool = {row["case_id"]: row for row in read_csv(POOL_PATH)}
    documents = {row["document_id"]: row for row in read_csv(DOCUMENTS_PATH)}
    frame = {row["validation_unit_id"]: row for row in read_csv(FRAME_PATH)}
    crosswalk = read_csv(CROSSWALK_PATH)

    gold_rows: list[dict[str, str]] = []
    for row in sorted(gold, key=lambda item: item["case_id"]):
        pool_row = pool.get(row["case_id"], {})
        document_ids = [value for value in pool_row.get("source_doc_ids", "").split(";") if value]
        if not document_ids:
            document_ids = [row["primary_evidence_doc"]]
            document_ids.extend(value for value in row["secondary_evidence_doc"].split(";") if value)
        gold_rows.append({
            "packet_case_id": row["case_id"],
            "issuer_name": row["company_name"],
            "province": row["province"],
            "city": row["city"],
            **packet_source_fields(document_ids, documents),
            **blank_coder_fields(),
        })

    candidate_rows: list[dict[str, str]] = []
    eligible = [
        row for row in crosswalk
        if row["scope_disposition"] == "provisionally_eligible"
        and row["geography_status"] == "source_supported_unique"
    ]
    for row in sorted(eligible, key=lambda item: item["validation_unit_id"]):
        frame_row = frame[row["validation_unit_id"]]
        document_ids = [value for value in frame_row["evidence_document_ids"].split(";") if value]
        candidate_rows.append({
            "packet_case_id": row["validation_unit_id"],
            "issuer_name": row["issuer_name"],
            "province": row["province"],
            "city": row["city"],
            **packet_source_fields(document_ids, documents),
            **blank_coder_fields(),
        })

    adjudication_rows = [
        {"packet_case_id": row["packet_case_id"], **{field: "" for field in ADJUDICATION_ENTRY_FIELDS}}
        for row in gold_rows
    ]
    return gold_rows, candidate_rows, adjudication_rows


def build_outputs() -> dict[Path, bytes]:
    gold_rows, candidate_rows, adjudication_rows = build_rows()
    crosswalk = read_csv(CROSSWALK_PATH)
    provisional_eligible = [row for row in crosswalk if row["scope_disposition"] == "provisionally_eligible"]
    outputs = {
        GOLD_PACKET_PATH: csv_bytes(gold_rows, PACKET_FIELDS),
        CANDIDATE_PACKET_PATH: csv_bytes(candidate_rows, PACKET_FIELDS),
        ADJUDICATION_PATH: csv_bytes(adjudication_rows, ADJUDICATION_FIELDS),
    }
    populated_coder_cells = sum(
        bool(row[field])
        for row in gold_rows + candidate_rows
        for field in CODER_FIELDS
    )
    populated_adjudication_cells = sum(
        bool(row[field])
        for row in adjudication_rows
        for field in ADJUDICATION_ENTRY_FIELDS
    )
    metrics = {
        "experiment_id": EXPERIMENT_ID,
        "base_commit": BASE_COMMIT,
        "gold_packet_rows": len(gold_rows),
        "unique_gold_case_ids": len({row["packet_case_id"] for row in gold_rows}),
        "gold_rows_with_document_ids": sum(bool(row["packet_document_ids"]) for row in gold_rows),
        "gold_rows_with_source_location": sum(bool(row["packet_page_urls"] or row["packet_download_urls"] or row["packet_expected_archive_paths"]) for row in gold_rows),
        "candidate_packet_rows": len(candidate_rows),
        "candidate_target_hypothesis_rows": 13,
        "candidate_hypothesis_passed": len(candidate_rows) == 13,
        "provisionally_eligible_scope_units": len(provisional_eligible),
        "provisionally_eligible_missing_verified_geography": sum(
            row["geography_status"] != "source_supported_unique" for row in provisional_eligible
        ),
        "unique_candidate_case_ids": len({row["packet_case_id"] for row in candidate_rows}),
        "candidate_rows_with_document_ids": sum(bool(row["packet_document_ids"]) for row in candidate_rows),
        "candidate_rows_with_source_location": sum(bool(row["packet_page_urls"] or row["packet_download_urls"] or row["packet_expected_archive_paths"]) for row in candidate_rows),
        "adjudication_template_rows": len(adjudication_rows),
        "unique_adjudication_case_ids": len({row["packet_case_id"] for row in adjudication_rows}),
        "populated_coder_entry_cells": populated_coder_cells,
        "populated_adjudication_entry_cells": populated_adjudication_cells,
        "gold_packet_fields": PACKET_FIELDS,
        "candidate_packet_fields": PACKET_FIELDS,
        "adjudication_fields": ADJUDICATION_FIELDS,
        "output_sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(content).hexdigest()
            for path, content in outputs.items()
        },
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
    outputs[METRICS_PATH] = (json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs()
    if args.check:
        mismatches = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.exists() or path.read_bytes() != content]
        if mismatches:
            raise SystemExit(f"Non-deterministic or stale packet outputs: {mismatches}")
        print("independent_coding_packet_regeneration=byte_identical")
        return
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print("independent_coding_packets_written=3")


if __name__ == "__main__":
    main()
