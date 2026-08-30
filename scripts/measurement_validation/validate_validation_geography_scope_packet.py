#!/usr/bin/env python3
"""Validate the authoritative geography and scope evidence packet."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FRAME_PATH = ROOT / "data/validation/proposed_one_sided_validation_frame_enriched.csv"
CROSSWALK_PATH = ROOT / "data/validation/source_supported_validation_geography_scope_crosswalk.csv"
RETRIEVAL_PATH = ROOT / "data/validation/validation_geography_retrieval_manifest.csv"
CONFLICT_PATH = ROOT / "data/validation/validation_geography_conflict_log.csv"
METRICS_PATH = ROOT / "experiments/EXP-20260830-011/metrics.json"

ALLOWED_SCOPE = {"provisionally_eligible", "provisionally_ineligible", "review_required"}
ALLOWED_OWNER = {
    "central_public", "municipality_public", "private_or_natural_person",
    "provincial_public", "subprovincial_public", "no_controller", "unknown",
}
FORBIDDEN_HEADERS = {
    "final_label", "alternative_label", "screen_status", "design_stratum",
    "model_prediction", "confidence", "rationale", "inclusion_probability",
    "design_weight", "selected_case", "random_seed", "random_draw_executed",
}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def validate(check_metrics: bool = False) -> dict[str, int]:
    frame_fields, frame = read_csv(FRAME_PATH)
    crosswalk_fields, crosswalk = read_csv(CROSSWALK_PATH)
    retrieval_fields, retrieval = read_csv(RETRIEVAL_PATH)
    conflict_fields, conflicts = read_csv(CONFLICT_PATH)
    del frame_fields, retrieval_fields, conflict_fields

    unresolved = {
        row["validation_unit_id"]: row
        for row in frame
        if not row["province"] or not row["city"]
    }
    if len(unresolved) != 128:
        raise ValueError(f"Expected 128 unresolved frame units, found {len(unresolved)}")
    if len(crosswalk) != 128:
        raise ValueError(f"Expected 128 crosswalk rows, found {len(crosswalk)}")
    ids = [row["validation_unit_id"] for row in crosswalk]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate validation_unit_id in geography crosswalk")
    if set(ids) != set(unresolved):
        raise ValueError("Crosswalk unit IDs do not match the 128 unresolved frame units")
    forbidden = sorted(FORBIDDEN_HEADERS.intersection(crosswalk_fields))
    if forbidden:
        raise ValueError(f"Forbidden crosswalk fields: {forbidden}")

    retrieval_by_unit_doc = {
        (row["validation_unit_id"], row["document_id"]): row for row in retrieval
    }
    if len(retrieval_by_unit_doc) != len(retrieval):
        raise ValueError("Duplicate unit-document row in retrieval manifest")
    for row in retrieval:
        if row["local_copy_committed"] != "false":
            raise ValueError(f"Raw source marked committed: {row['document_id']}")
        if not row["rights_note"]:
            raise ValueError(f"Missing rights note: {row['document_id']}")
        if row["access_status"] == "retrieved_public_disclosure":
            if not row["sha256"] or len(row["sha256"]) != 64:
                raise ValueError(f"Missing or invalid source hash: {row['document_id']}")
            if not row["document_page_url"] or not row["download_url"]:
                raise ValueError(f"Missing source URL: {row['document_id']}")

    for row in crosswalk:
        unit_id = row["validation_unit_id"]
        if row["issuer_name"] != unresolved[unit_id]["issuer_name"]:
            raise ValueError(f"Issuer identity drift: {unit_id}")
        if row["scope_disposition"] not in ALLOWED_SCOPE:
            raise ValueError(f"Invalid scope disposition: {unit_id}")
        if row["owner_level"] not in ALLOWED_OWNER:
            raise ValueError(f"Invalid owner level: {unit_id}")
        if row["review_gate"] != "PI approval required before frame inclusion or sampling":
            raise ValueError(f"Missing review gate: {unit_id}")
        if row["geography_status"] == "source_supported_unique":
            required = (
                "supported_legal_issuer_name", "province", "city",
                "geography_document_id", "geography_page",
                "geography_supporting_text", "source_publisher",
                "source_page_url", "source_download_url", "source_title",
                "source_date", "retrieval_date", "retrieved_file_sha256",
                "access_status", "rights_note",
            )
            blank = [field for field in required if not row[field]]
            if blank:
                raise ValueError(f"Resolved geography lacks evidence {blank}: {unit_id}")
        elif row["province"] or row["city"]:
            raise ValueError(f"Unresolved geography retains a place value: {unit_id}")

        if row["scope_disposition"] == "provisionally_eligible":
            if row["owner_level"] not in {"municipality_public", "subprovincial_public"}:
                raise ValueError(f"Eligible disposition lacks local public owner: {unit_id}")
            if not row["role_document_id"] or not row["role_supporting_text"]:
                raise ValueError(f"Eligible disposition lacks platform-role evidence: {unit_id}")
        if row["scope_disposition"] == "provisionally_ineligible":
            if row["owner_level"] not in {"central_public", "provincial_public", "private_or_natural_person"}:
                raise ValueError(f"Ineligible disposition lacks excluded owner level: {unit_id}")

        for prefix in ("identity", "geography", "owner", "role"):
            document_id = row[f"{prefix}_document_id"]
            if not document_id:
                continue
            source = retrieval_by_unit_doc.get((unit_id, document_id))
            if source is None:
                raise ValueError(f"Missing manifest join for {prefix} evidence: {unit_id}")
            if source["access_status"] != "retrieved_public_disclosure":
                raise ValueError(f"Evidence source was not retrieved: {unit_id} {document_id}")
            if not row[f"{prefix}_page"] or not row[f"{prefix}_supporting_text"]:
                raise ValueError(f"Evidence locator incomplete: {unit_id} {prefix}")

    conflict_ids = {row["validation_unit_id"] for row in conflicts}
    if not conflict_ids.issubset(set(ids)):
        raise ValueError("Conflict log contains unit outside crosswalk")
    for row in conflicts:
        if row["review_required"] != "true" or not row["observed_values"]:
            raise ValueError(f"Conflict is not explicit: {row['validation_unit_id']}")

    computed = {
        "processed_units": len(crosswalk),
        "fixed_source_documents_attempted": len(retrieval),
        "retrieved_documents": sum(row["access_status"] == "retrieved_public_disclosure" for row in retrieval),
        "extracted_documents": sum(row["text_extraction_status"].startswith("extracted_") for row in retrieval),
        "source_supported_unique_geography_units": sum(row["geography_status"] == "source_supported_unique" for row in crosswalk),
        "explicit_scope_disposition_units": sum(row["scope_disposition"] in ALLOWED_SCOPE for row in crosswalk),
        "decisive_scope_disposition_units": sum(row["scope_disposition"] != "review_required" for row in crosswalk),
        "combined_geography_and_explicit_scope_units": sum(row["geography_status"] == "source_supported_unique" and row["scope_disposition"] in ALLOWED_SCOPE for row in crosswalk),
        "conflicting_units": len(conflict_ids),
    }
    if check_metrics:
        metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        mismatches = {
            key: (metrics.get(key), value)
            for key, value in computed.items()
            if metrics.get(key) != value
        }
        scope_counts = dict(sorted(Counter(row["scope_disposition"] for row in crosswalk).items()))
        owner_counts = dict(sorted(Counter(row["owner_level"] for row in crosswalk).items()))
        if metrics.get("scope_dispositions") != scope_counts:
            mismatches["scope_dispositions"] = (metrics.get("scope_dispositions"), scope_counts)
        if metrics.get("owner_levels") != owner_counts:
            mismatches["owner_levels"] = (metrics.get("owner_levels"), owner_counts)
        if metrics.get("company_name_geography_parsing_used") is not False:
            mismatches["company_name_geography_parsing_used"] = (
                metrics.get("company_name_geography_parsing_used"), False
            )
        if metrics.get("random_draw_executed") is not False or metrics.get("random_seed") is not None:
            mismatches["randomization"] = (
                metrics.get("random_draw_executed"), metrics.get("random_seed")
            )
        if mismatches:
            raise ValueError(f"Metrics mismatch: {mismatches}")
    return computed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-metrics", action="store_true")
    args = parser.parse_args()
    computed = validate(check_metrics=args.check_metrics)
    print(json.dumps(computed, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
