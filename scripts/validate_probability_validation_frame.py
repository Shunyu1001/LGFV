#!/usr/bin/env python3
"""Validate the completed source review and probability-frame candidate."""

from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRAME = ROOT / "data/validation/proposed_one_sided_validation_frame_enriched.csv"
OLD_CROSSWALK = ROOT / "data/validation/source_supported_validation_geography_scope_crosswalk.csv"
DECISIONS = ROOT / "experiments/EXP-20260830-015/review_decisions.csv"
CROSSWALK = ROOT / "data/validation/probability_validation_geography_scope_crosswalk.csv"
UNRESOLVED = ROOT / "data/validation/probability_validation_unresolved_log.csv"
SOURCE_MANIFEST = ROOT / "data/validation/probability_validation_source_manifest.csv"
CANDIDATE = ROOT / "data/validation/probability_validation_frame_candidate.csv"
ORIGINS = ROOT / "data/validation/probability_validation_frame_origin_rows.csv"
FLOW = ROOT / "data/validation/probability_validation_frame_flow.csv"
DESIGN = ROOT / "data/validation/probability_validation_sampling_design.csv"
METRICS = ROOT / "experiments/EXP-20260830-015/metrics.json"

ALLOWED_GEOGRAPHY = {"source_supported_unique", "source_supported_multiple", "unresolved_after_search"}
ALLOWED_SCOPE = {"eligible", "ineligible", "unresolved_after_search"}
LOCAL_OWNER = {"municipality_public", "subprovincial_public"}
EXCLUDED_OWNER = {"central_public", "provincial_public", "private_or_natural_person"}
ALLOWED_ADMIN = {"central", "provincial", "municipality", "prefecture", "district", "county", "development_zone", "private", "unresolved"}
ALLOWED_SCREEN = {"screen_positive_nominal", "screened_no_direct_formal_event"}
FORBIDDEN_OUTPUT_HEADERS = {
    "exit_type", "formal_event_found", "formal_event_summary",
    "continued_function_found", "continued_function_summary", "alternative_label",
    "classification_rationale", "confidence", "selected_case", "selection_order",
}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def normalize(value: str) -> str:
    return re.sub(r"[\s()（）·,，。]", "", value).casefold()


def expected_stratum(row: dict[str, str]) -> str:
    return "__".join((
        row["screen_status"],
        row["source_coverage_bin"],
        f"historical_{row['historical_capacity_bin']}",
        f"debt_{row['debt_pressure_availability']}",
        f"admin_{row['administrative_level']}",
    ))


def validate() -> dict[str, object]:
    frame_fields, frame_rows = read_csv(FRAME)
    old_fields, old_rows = read_csv(OLD_CROSSWALK)
    decision_fields, decisions = read_csv(DECISIONS)
    crosswalk_fields, crosswalk_rows = read_csv(CROSSWALK)
    unresolved_fields, unresolved_rows = read_csv(UNRESOLVED)
    manifest_fields, manifest_rows = read_csv(SOURCE_MANIFEST)
    candidate_fields, candidate_rows = read_csv(CANDIDATE)
    origin_fields, origin_rows = read_csv(ORIGINS)
    flow_fields, flow_rows = read_csv(FLOW)
    design_fields, design_rows = read_csv(DESIGN)
    del frame_fields, old_fields, decision_fields, unresolved_fields, flow_fields

    for path, fields in ((CROSSWALK, crosswalk_fields), (CANDIDATE, candidate_fields), (ORIGINS, origin_fields), (DESIGN, design_fields)):
        forbidden = sorted(FORBIDDEN_OUTPUT_HEADERS.intersection(fields))
        if forbidden:
            raise ValueError(f"Outcome or selection fields appear in {path}: {forbidden}")

    frame = {row["validation_unit_id"]: row for row in frame_rows}
    old = {row["validation_unit_id"]: row for row in old_rows}
    decision = {row["validation_unit_id"]: row for row in decisions}
    crosswalk = {row["validation_unit_id"]: row for row in crosswalk_rows}
    if any(len(rows) != len({row["validation_unit_id"] for row in rows}) for rows in (frame_rows, decisions, crosswalk_rows)):
        raise ValueError("Duplicate validation_unit_id in a unit-level input")
    if len(frame_rows) != 133 or len(decisions) != 133 or len(crosswalk_rows) != 133:
        raise ValueError("Frame, decisions, and completed crosswalk must each contain 133 units")
    if set(frame) != set(decision) or set(frame) != set(crosswalk):
        raise ValueError("Unit IDs differ across frame, decisions, and completed crosswalk")

    manifest = {(row["validation_unit_id"], row["document_id"]): row for row in manifest_rows}
    if len(manifest) != len(manifest_rows):
        raise ValueError("Duplicate unit-document pair in source manifest")
    for row in manifest_rows:
        if row["local_copy_committed"] != "false":
            raise ValueError(f"Raw source marked committed: {row['document_id']}")
        if not row["rights_note"]:
            raise ValueError(f"Missing rights note: {row['document_id']}")
        if row["access_status"].startswith("retrieved_"):
            if len(row["sha256"]) != 64 or not row["document_page_url"] or not row["download_url"] or not row["retrieval_date"]:
                raise ValueError(f"Retrieved source lacks traceability: {row['document_id']}")

    baseline_geography_ids = {unit_id for unit_id, row in old.items() if row["geography_status"] != "source_supported_unique"}
    baseline_scope_ids = {unit_id for unit_id, row in old.items() if row["scope_disposition"] == "review_required"}
    if len(baseline_geography_ids) != 88 or len(baseline_scope_ids) != 98:
        raise ValueError("The quarantined 88-geography and 98-scope baselines were not reproduced")

    for unit_id, row in crosswalk.items():
        if row["issuer_name"] != frame[unit_id]["issuer_name"] or row["issuer_name"] != decision[unit_id]["issuer_name"]:
            raise ValueError(f"Issuer identity drift: {unit_id}")
        if row["geography_status"] not in ALLOWED_GEOGRAPHY:
            raise ValueError(f"Invalid geography disposition: {unit_id}")
        if row["scope_disposition"] not in ALLOWED_SCOPE:
            raise ValueError(f"Invalid scope disposition: {unit_id}")
        if row["administrative_level"] not in ALLOWED_ADMIN:
            raise ValueError(f"Invalid administrative level: {unit_id}")
        for field in ("geography_status", "administrative_level", "owner_level", "scope_disposition", "scope_reason_code", "audit_note"):
            if row[field] != decision[unit_id][field]:
                raise ValueError(f"Completed review diverges from registered decision {field}: {unit_id}")
        for field in ("province", "city"):
            if row[field] != decision[unit_id][field]:
                raise ValueError(f"Geography diverges from registered decision: {unit_id}")
        expected_baseline_geography = "true" if unit_id in baseline_geography_ids else "false"
        expected_baseline_scope = "true" if unit_id in baseline_scope_ids else "false"
        if row["baseline_geography_gap"] != expected_baseline_geography or row["baseline_scope_review"] != expected_baseline_scope:
            raise ValueError(f"Baseline audit flag mismatch: {unit_id}")
        if row["review_gate"] != "PI approval required before frame freeze or sampling":
            raise ValueError(f"Missing review gate: {unit_id}")

        if not row["identity_document_id"] or not row["identity_page"] or not row["identity_supporting_text"]:
            raise ValueError(f"Identity evidence is incomplete: {unit_id}")
        if row["geography_status"] == "source_supported_unique":
            required = ("supported_legal_issuer_name", "province", "city", "geography_document_id", "geography_page", "geography_supporting_text")
            if any(not row[field] for field in required):
                raise ValueError(f"Resolved geography lacks evidence: {unit_id}")
            city_token = row["city"].removesuffix("市")
            if city_token and city_token not in row["geography_supporting_text"]:
                raise ValueError(f"Geography excerpt does not contain city token: {unit_id}")
        elif row["province"] or row["city"]:
            raise ValueError(f"Unresolved geography retains a coerced place: {unit_id}")

        if row["scope_disposition"] == "eligible":
            if row["owner_level"] not in LOCAL_OWNER:
                raise ValueError(f"Eligible unit lacks local public control: {unit_id}")
            if not row["owner_document_id"] or not row["owner_supporting_text"] or not row["role_document_id"] or not row["role_supporting_text"]:
                raise ValueError(f"Eligible unit lacks owner or platform-role evidence: {unit_id}")
        elif row["scope_reason_code"] in {"excluded_central_public", "excluded_provincial_public", "excluded_private"}:
            if row["owner_level"] not in EXCLUDED_OWNER or not row["owner_document_id"] or not row["owner_supporting_text"]:
                raise ValueError(f"Owner-based exclusion lacks evidence: {unit_id}")
        elif row["scope_reason_code"] == "excluded_commercial_no_platform_role":
            if row["owner_level"] not in LOCAL_OWNER or not row["owner_document_id"] or not row["role_document_id"] or not row["role_supporting_text"]:
                raise ValueError(f"Commercial-function exclusion lacks owner/business evidence: {unit_id}")

        for prefix in ("identity", "geography", "owner", "role"):
            document_id = row[f"{prefix}_document_id"]
            if not document_id:
                continue
            source = manifest.get((unit_id, document_id))
            if not source or not source["access_status"].startswith("retrieved_"):
                raise ValueError(f"Evidence source does not join to a retrieved manifest row: {unit_id} {prefix}")
            if not row[f"{prefix}_page"] or not row[f"{prefix}_supporting_text"]:
                raise ValueError(f"Evidence locator is incomplete: {unit_id} {prefix}")

    if sum(crosswalk[unit_id]["geography_status"] == "source_supported_unique" for unit_id in baseline_geography_ids) != 88:
        raise ValueError("Not all 88 baseline geography gaps were resolved")
    baseline_scope_resolved = sum(crosswalk[unit_id]["scope_disposition"] in {"eligible", "ineligible"} for unit_id in baseline_scope_ids)
    baseline_scope_unresolved = sum(crosswalk[unit_id]["scope_disposition"] == "unresolved_after_search" for unit_id in baseline_scope_ids)
    if (baseline_scope_resolved, baseline_scope_unresolved) != (96, 2):
        raise ValueError(f"Unexpected resolution of 98 baseline scope reviews: {(baseline_scope_resolved, baseline_scope_unresolved)}")

    expected_failed_gates = Counter()
    for row in crosswalk_rows:
        if row["geography_status"] != "source_supported_unique":
            expected_failed_gates[(row["validation_unit_id"], "geography_and_identity")] += 1
        if row["scope_disposition"] == "unresolved_after_search":
            expected_failed_gates[(row["validation_unit_id"], "scope")] += 1
    observed_failed_gates = Counter((row["validation_unit_id"], row["failed_gate"]) for row in unresolved_rows)
    if expected_failed_gates != observed_failed_gates:
        raise ValueError(f"Unresolved log does not contain one row per failed gate: {observed_failed_gates}")
    if any(row["review_required"] != "true" or row["disposition"] != "unresolved_after_search" or not row["source_document_ids"] for row in unresolved_rows):
        raise ValueError("An unresolved-log row lacks traceability or an explicit review gate")

    eligible_ids = {unit_id for unit_id, row in crosswalk.items() if row["scope_disposition"] == "eligible"}
    candidate_ids = [row["validation_unit_id"] for row in candidate_rows]
    if len(candidate_ids) != len(set(candidate_ids)) or set(candidate_ids) != eligible_ids:
        raise ValueError("Candidate units are not the unique eligible crosswalk units")
    legal_keys = [row["normalized_legal_issuer_key"] for row in candidate_rows]
    if any(not key for key in legal_keys) or len(legal_keys) != len(set(legal_keys)):
        raise ValueError("Candidate legal-issuer keys are blank or duplicated")

    members_by_stratum: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in candidate_rows:
        if row["eligibility_flag"] != "true" or row["scope_disposition"] != "eligible":
            raise ValueError(f"Candidate contains a noneligible unit: {row['validation_unit_id']}")
        if row["screen_status"] not in ALLOWED_SCREEN:
            raise ValueError(f"Invalid screen stratum: {row['validation_unit_id']}")
        if row["frozen_stratum_id"] != expected_stratum(row):
            raise ValueError(f"Frozen stratum contains a disallowed or inconsistent component: {row['validation_unit_id']}")
        probability = float(row["inclusion_probability"])
        if not 0 < probability <= 1 or not math.isclose(float(row["proposed_design_weight"]), 1 / probability, rel_tol=1e-10):
            raise ValueError(f"Invalid probability or design weight: {row['validation_unit_id']}")
        if row["random_draw_executed"] != "false" or not row["deterministic_random_seed"]:
            raise ValueError(f"Random draw state is invalid: {row['validation_unit_id']}")
        members_by_stratum[row["frozen_stratum_id"]].append(row)
    if {row["screen_status"] for row in candidate_rows} != ALLOWED_SCREEN:
        raise ValueError("Eligible candidate does not retain both screen strata")

    design = {row["frozen_stratum_id"]: row for row in design_rows}
    if len(design) != len(design_rows) or set(design) != set(members_by_stratum):
        raise ValueError("Sampling design does not have one row per frozen stratum")
    for stratum_id, members in members_by_stratum.items():
        row = design[stratum_id]
        population_n = len(members)
        target_n = int(row["proposed_stratum_sample_n"])
        probability = target_n / population_n
        if int(row["stratum_population_n"]) != population_n or not 0 < target_n <= population_n:
            raise ValueError(f"Invalid sampling allocation: {stratum_id}")
        if not math.isclose(float(row["inclusion_probability"]), probability, rel_tol=1e-12):
            raise ValueError(f"Sampling probability mismatch: {stratum_id}")
        if row["random_draw_executed"] != "false" or row["approval_status"] != "proposal_only_PI_approval_required":
            raise ValueError(f"Sampling proposal was executed or lacks approval gate: {stratum_id}")
        for member in members:
            if int(member["stratum_population_n"]) != population_n or int(member["proposed_stratum_sample_n"]) != target_n:
                raise ValueError(f"Unit-level stratum allocation mismatch: {member['validation_unit_id']}")

    expected_origins = []
    for row in frame_rows:
        source_rows = [value for value in row["source_row_ids"].split(";") if value]
        pool_ids = [value for value in row["pool_ids"].split(";") if value]
        for position, pair in enumerate(zip(source_rows, pool_ids), start=1):
            expected_origins.append((row["validation_unit_id"], str(position), *pair))
    observed_origins = [(row["validation_unit_id"], row["origin_position"], row["source_row_id"], row["pool_id"]) for row in origin_rows]
    if len(expected_origins) != 157 or observed_origins != expected_origins:
        raise ValueError("All 157 originating disclosure rows were not retained in stable order")

    scope_counts = Counter(row["scope_disposition"] for row in crosswalk_rows)
    geography_counts = Counter(row["geography_status"] for row in crosswalk_rows)
    screen_counts = Counter(row["screen_status"] for row in candidate_rows)
    metrics = json.loads(METRICS.read_text(encoding="utf-8"))
    expected_metrics = {
        "proposed_issuer_units": 133,
        "originating_disclosure_rows": 157,
        "baseline_geography_gaps": 88,
        "baseline_geography_resolved": 88,
        "baseline_geography_unresolved": 0,
        "baseline_scope_reviews": 98,
        "baseline_scope_resolved": 96,
        "baseline_scope_unresolved": 2,
        "all_geography_statuses": dict(sorted(geography_counts.items())),
        "all_scope_dispositions": dict(sorted(scope_counts.items())),
        "eligible_candidate_units": len(candidate_rows),
        "eligible_screen_statuses": dict(sorted(screen_counts.items())),
        "frozen_strata": len(design_rows),
        "all_eligible_units_have_nonzero_probability": True,
        "random_draw_executed": False,
        "frame_ready_to_freeze": False,
    }
    mismatches = {key: (metrics.get(key), value) for key, value in expected_metrics.items() if metrics.get(key) != value}
    if mismatches:
        raise ValueError(f"Metrics mismatch: {mismatches}")

    flow_keys = {(row["stage"], row["disposition"]): int(row["issuer_unit_count"]) for row in flow_rows}
    if flow_keys.get(("proposed_frame", "all_legal_issuer_units")) != 133:
        raise ValueError("Frame-flow table does not start from 133 units")
    for disposition, count in scope_counts.items():
        if flow_keys.get(("scope_gate", disposition)) != count:
            raise ValueError(f"Frame-flow scope count mismatch: {disposition}")

    return {
        "baseline_geography_resolved": 88,
        "baseline_geography_unresolved": 0,
        "baseline_scope_resolved": 96,
        "baseline_scope_unresolved": 2,
        "all_geography_statuses": dict(sorted(geography_counts.items())),
        "all_scope_dispositions": dict(sorted(scope_counts.items())),
        "candidate_units": len(candidate_rows),
        "originating_disclosure_rows": len(origin_rows),
        "frozen_strata": len(design_rows),
        "random_draw_executed": False,
    }


if __name__ == "__main__":
    print(json.dumps(validate(), ensure_ascii=False, sort_keys=True))
