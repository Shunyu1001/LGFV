#!/usr/bin/env python3
"""Build the deduplicated, pre-outcome probability-validation frame candidate."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRAME_INPUT = ROOT / "data/validation/proposed_one_sided_validation_frame_enriched.csv"
CROSSWALK_INPUT = ROOT / "data/validation/probability_validation_geography_scope_crosswalk.csv"
SURROGATE_INPUT = ROOT / "data/analysis_inputs/codex_surrogate_labels_2026_07_03_expanded.csv"
DOCUMENTS_INPUT = ROOT / "data/document_inventory.csv"
HISTORICAL_INPUT = ROOT / "data/analysis_inputs/candidate_city_historical_capacity.csv"
CONTROLS_INPUT = ROOT / "data/analysis_inputs/contemporary_city_controls.csv"

CANDIDATE_OUTPUT = ROOT / "data/validation/probability_validation_frame_candidate.csv"
ORIGIN_OUTPUT = ROOT / "data/validation/probability_validation_frame_origin_rows.csv"
FLOW_OUTPUT = ROOT / "data/validation/probability_validation_frame_flow.csv"
DESIGN_OUTPUT = ROOT / "data/validation/probability_validation_sampling_design.csv"
METRICS_OUTPUT = ROOT / "experiments/EXP-20260831-001/metrics.json"

SEED = "20260830015"
POSITIVE_TARGET = 60
NONPOSITIVE_TARGET = 36
ALLOWED_SCREEN = {"screen_positive_nominal", "screened_no_direct_formal_event"}

PREFECTURE_ROLLUPS = {
    "太仓市": "苏州市",
    "如皋市": "南通市",
}

HISTORICAL_ENGLISH_JOIN = {
    "乌鲁木齐市": ("Xinjiang", "Urumqi"),
    "福州市": ("Fujian", "Fuzhou"),
}

CANDIDATE_FIELDS = [
    "validation_unit_id", "issuer_key", "issuer_name", "normalized_legal_issuer_key",
    "scope_disposition", "eligibility_flag", "province", "city",
    "administrative_level", "geography_status", "screen_status",
    "source_coverage_score", "source_coverage_bin", "historical_capacity_bin",
    "historical_capacity_join_status", "historical_capacity_source_case_ids",
    "debt_pressure_availability", "debt_pressure_control_unit_id",
    "frozen_stratum_id", "stratum_population_n", "proposed_stratum_sample_n",
    "inclusion_probability", "proposed_design_weight", "deterministic_random_seed",
    "random_draw_executed",
]

ORIGIN_FIELDS = [
    "validation_unit_id", "issuer_name", "scope_disposition", "eligibility_flag",
    "screen_status", "origin_position", "source_row_id", "pool_id",
    "evidence_document_ids",
]

DESIGN_FIELDS = [
    "frozen_stratum_id", "screen_status", "source_coverage_bin",
    "historical_capacity_bin", "debt_pressure_availability", "administrative_level",
    "stratum_population_n", "proposed_stratum_sample_n", "inclusion_probability",
    "deterministic_random_seed", "random_draw_executed", "approval_status",
]

FLOW_FIELDS = [
    "stage", "disposition", "issuer_unit_count", "originating_disclosure_row_count",
    "notes",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def normalize_legal_name(value: str) -> str:
    return re.sub(r"[\s()（）·,，。]", "", value).casefold()


def surrogate_origin_lookup() -> tuple[dict[str, set[str]], dict[tuple[str, str], float]]:
    """Read only origin identifiers and coverage from the surrogate file."""
    with SURROGATE_INPUT.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        source_index = header.index("source_row_id")
        pool_index = header.index("pool_id")
        coverage_index = header.index("source_coverage_score")
        pools: dict[str, set[str]] = defaultdict(set)
        coverage: dict[tuple[str, str], float] = {}
        for values in reader:
            source_row_id = values[source_index]
            pool_id = values[pool_index]
            score = float(values[coverage_index])
            pools[source_row_id].add(pool_id)
            pair = (source_row_id, pool_id)
            if pair in coverage and coverage[pair] != score:
                raise ValueError(f"Conflicting source coverage for origin pair: {pair}")
            coverage[pair] = score
    return dict(pools), coverage


def resolve_origin_pairs(
    source_row_ids: list[str],
    declared_pool_ids: list[str],
    surrogate_pools: dict[str, set[str]],
    context: str,
) -> list[tuple[str, str]]:
    """Resolve each source row to its uniquely declared pool without free text."""
    missing_origins = [source_id for source_id in source_row_ids if source_id not in surrogate_pools]
    if missing_origins:
        raise ValueError(f"Origin rows are missing from the surrogate input: {context} {missing_origins}")
    declared_pool_set = set(declared_pool_ids)
    pool_choices = [surrogate_pools[source_id].intersection(declared_pool_set) for source_id in source_row_ids]
    if any(len(choices) != 1 for choices in pool_choices):
        raise ValueError(f"Origin pairs are not uniquely identified by safe surrogate columns: {context}")
    resolved_pool_ids = [next(iter(choices)) for choices in pool_choices]
    if Counter(resolved_pool_ids) != Counter(declared_pool_ids):
        raise ValueError(f"Origin pool-ID membership mismatch: {context}")
    return list(zip(source_row_ids, resolved_pool_ids))


def coverage_for_origin_pairs(
    origin_pairs: list[tuple[str, str]],
    coverage: dict[tuple[str, str], float],
    context: str,
) -> float:
    """Return coverage for the resolved origin pairs, never a cross-pool maximum."""
    missing_pairs = [pair for pair in origin_pairs if pair not in coverage]
    if missing_pairs:
        raise ValueError(f"Source coverage is missing for {context}: {missing_pairs}")
    return max(coverage[pair] for pair in origin_pairs)


def document_ids_by_source_row() -> tuple[dict[str, list[str]], set[str]]:
    """Index valid inventory documents without treating free text as an ID."""
    by_source: dict[str, list[str]] = defaultdict(list)
    valid_ids: set[str] = set()
    for row in read_csv(DOCUMENTS_INPUT):
        document_id = row["document_id"]
        if not document_id:
            continue
        valid_ids.add(document_id)
        if row["usable_for_labeling"] == "yes":
            by_source[row["case_id"]].append(document_id)
    return dict(by_source), valid_ids


def origin_evidence_document_ids(
    source_row_id: str,
    aggregate_ids: str,
    by_source: dict[str, list[str]],
    valid_ids: set[str],
) -> str:
    direct = by_source.get(source_row_id, [])
    if direct:
        return ";".join(dict.fromkeys(direct))
    fallback = [value for value in aggregate_ids.split(";") if value in valid_ids]
    return ";".join(dict.fromkeys(fallback))


def coverage_bin(score: float) -> str:
    if score >= 4:
        return "high_4_plus"
    if score >= 2:
        return "moderate_2_3"
    return "low_0_1"


def historical_lookup() -> dict[str, dict[str, str]]:
    rows = read_csv(HISTORICAL_INPUT)
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        capacity_bin = row["historical_capacity_bin"]
        if not capacity_bin:
            continue
        keys = [value for value in row["capacity_prefecture_name_chn"].split("|") if value]
        for chinese_city, english_pair in HISTORICAL_ENGLISH_JOIN.items():
            if (row["province"], row["city"]) == english_pair:
                keys.append(chinese_city)
        for key in keys:
            existing = result.get(key)
            if existing and existing["historical_capacity_bin"] != capacity_bin:
                raise ValueError(f"Conflicting historical-capacity bins for {key}")
            if existing:
                case_ids = sorted(set(existing["case_ids"].split(";") + [row["case_id"]]))
                existing["case_ids"] = ";".join(case_ids)
            else:
                result[key] = {
                    "historical_capacity_bin": capacity_bin,
                    "case_ids": row["case_id"],
                }
    return result


def analysis_prefecture_city(city: str) -> str:
    return PREFECTURE_ROLLUPS.get(city, city)


def canonical_control_city(city: str) -> str:
    if city in {"北京", "天津", "上海", "重庆"}:
        return f"{city}市"
    return city


def debt_availability() -> dict[str, tuple[str, str]]:
    result: dict[str, tuple[str, str]] = {}
    for row in read_csv(CONTROLS_INPUT):
        status = row["debt_pressure_status"]
        city = canonical_control_city(row["control_city_chn"])
        if not city:
            continue
        if status.startswith("source_backed") or status.startswith("latest_source_backed"):
            value = (row["control_unit_id"], "available")
        else:
            value = (row["control_unit_id"], "not_available")
        if city in result and result[city] != value:
            raise ValueError(f"Conflicting contemporary-control rows for {city}")
        result[city] = value
    return result


def proposed_target(screen_status: str, population_n: int) -> int:
    target = POSITIVE_TARGET if screen_status == "screen_positive_nominal" else NONPOSITIVE_TARGET
    return min(population_n, target)


def build() -> dict[str, object]:
    frame_rows = read_csv(FRAME_INPUT)
    crosswalk_rows = read_csv(CROSSWALK_INPUT)
    frame = {row["validation_unit_id"]: row for row in frame_rows}
    crosswalk = {row["validation_unit_id"]: row for row in crosswalk_rows}
    if len(frame) != 133 or len(crosswalk) != 133 or set(frame) != set(crosswalk):
        raise ValueError("The frame and completed crosswalk must contain the same 133 units")

    surrogate_pools, coverage = surrogate_origin_lookup()
    documents_by_source, valid_document_ids = document_ids_by_source_row()
    historical = historical_lookup()
    debt = debt_availability()
    origins: list[dict[str, object]] = []
    candidate: list[dict[str, object]] = []

    for frame_row in frame_rows:
        unit_id = frame_row["validation_unit_id"]
        review = crosswalk[unit_id]
        if frame_row["design_stratum"] not in ALLOWED_SCREEN:
            raise ValueError(f"Unexpected screen status: {unit_id}")
        source_row_ids = [value for value in frame_row["source_row_ids"].split(";") if value]
        declared_pool_ids = [value for value in frame_row["pool_ids"].split(";") if value]
        if len(source_row_ids) != len(declared_pool_ids) or len(source_row_ids) != int(frame_row["disclosure_rows"]):
            raise ValueError(f"Origin-row traceability mismatch: {unit_id}")
        resolved_origin_pairs = resolve_origin_pairs(
            source_row_ids, declared_pool_ids, surrogate_pools, unit_id
        )
        for position, (source_row_id, pool_id) in enumerate(resolved_origin_pairs, start=1):
            origins.append({
                "validation_unit_id": unit_id,
                "issuer_name": frame_row["issuer_name"],
                "scope_disposition": review["scope_disposition"],
                "eligibility_flag": "true" if review["scope_disposition"] == "eligible" else "false",
                "screen_status": frame_row["design_stratum"],
                "origin_position": position,
                "source_row_id": source_row_id,
                "pool_id": pool_id,
                "evidence_document_ids": origin_evidence_document_ids(
                    source_row_id,
                    frame_row["evidence_document_ids"],
                    documents_by_source,
                    valid_document_ids,
                ),
            })

        if review["scope_disposition"] != "eligible":
            continue
        if review["geography_status"] != "source_supported_unique":
            raise ValueError(f"Eligible unit lacks unique geography: {unit_id}")
        score = coverage_for_origin_pairs(resolved_origin_pairs, coverage, unit_id)
        prefecture_city = analysis_prefecture_city(review["city"])
        historical_match = historical.get(prefecture_city)
        if historical_match:
            historical_bin = historical_match["historical_capacity_bin"]
            historical_status = "source_backed_match"
            historical_cases = historical_match["case_ids"]
        else:
            historical_bin = "not_available"
            historical_status = "not_available"
            historical_cases = ""
        control_unit_id, debt_status = debt.get(prefecture_city, ("", "not_available"))
        screen_status = frame_row["design_stratum"]
        source_bin = coverage_bin(score)
        stratum_id = "__".join((
            screen_status,
            source_bin,
            f"historical_{historical_bin}",
            f"debt_{debt_status}",
            f"admin_{review['administrative_level']}",
        ))
        candidate.append({
            "validation_unit_id": unit_id,
            "issuer_key": frame_row["issuer_key"],
            "issuer_name": frame_row["issuer_name"],
            "normalized_legal_issuer_key": normalize_legal_name(review["supported_legal_issuer_name"]),
            "scope_disposition": "eligible",
            "eligibility_flag": "true",
            "province": review["province"],
            "city": review["city"],
            "administrative_level": review["administrative_level"],
            "geography_status": review["geography_status"],
            "screen_status": screen_status,
            "source_coverage_score": f"{score:g}",
            "source_coverage_bin": source_bin,
            "historical_capacity_bin": historical_bin,
            "historical_capacity_join_status": historical_status,
            "historical_capacity_source_case_ids": historical_cases,
            "debt_pressure_availability": debt_status,
            "debt_pressure_control_unit_id": control_unit_id,
            "frozen_stratum_id": stratum_id,
            "deterministic_random_seed": SEED,
            "random_draw_executed": "false",
        })

    stratum_members: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in candidate:
        stratum_members[str(row["frozen_stratum_id"])].append(row)

    design: list[dict[str, object]] = []
    for stratum_id in sorted(stratum_members):
        members = stratum_members[stratum_id]
        first = members[0]
        population_n = len(members)
        target_n = proposed_target(str(first["screen_status"]), population_n)
        probability = target_n / population_n
        for member in members:
            member["stratum_population_n"] = population_n
            member["proposed_stratum_sample_n"] = target_n
            member["inclusion_probability"] = f"{probability:.12g}"
            member["proposed_design_weight"] = f"{1 / probability:.12g}"
        design.append({
            "frozen_stratum_id": stratum_id,
            "screen_status": first["screen_status"],
            "source_coverage_bin": first["source_coverage_bin"],
            "historical_capacity_bin": first["historical_capacity_bin"],
            "debt_pressure_availability": first["debt_pressure_availability"],
            "administrative_level": first["administrative_level"],
            "stratum_population_n": population_n,
            "proposed_stratum_sample_n": target_n,
            "inclusion_probability": f"{probability:.12g}",
            "deterministic_random_seed": SEED,
            "random_draw_executed": "false",
            "approval_status": "proposal_only_PI_approval_required",
        })

    candidate.sort(key=lambda row: next(i for i, item in enumerate(frame_rows) if item["validation_unit_id"] == row["validation_unit_id"]))
    origins.sort(key=lambda row: (next(i for i, item in enumerate(frame_rows) if item["validation_unit_id"] == row["validation_unit_id"]), int(row["origin_position"])))

    disclosure_by_scope: Counter[str] = Counter()
    for row in origins:
        disclosure_by_scope[str(row["scope_disposition"])] += 1
    screen_counts = Counter(str(row["screen_status"]) for row in candidate)
    screen_origin_counts = Counter(
        str(row["screen_status"]) for row in origins if row["scope_disposition"] == "eligible"
    )
    scope_counts = Counter(row["scope_disposition"] for row in crosswalk_rows)
    geography_counts = Counter(row["geography_status"] for row in crosswalk_rows)
    flow = [
        {
            "stage": "proposed_frame", "disposition": "all_legal_issuer_units",
            "issuer_unit_count": len(frame_rows), "originating_disclosure_row_count": len(origins),
            "notes": "Frozen 133-unit input before geography and scope review.",
        },
        *(
            {
                "stage": "geography_gate", "disposition": status,
                "issuer_unit_count": count,
                "originating_disclosure_row_count": sum(int(frame[unit_id]["disclosure_rows"]) for unit_id, row in crosswalk.items() if row["geography_status"] == status),
                "notes": "Completed source-supported geography review.",
            }
            for status, count in sorted(geography_counts.items())
        ),
        *(
            {
                "stage": "scope_gate", "disposition": status,
                "issuer_unit_count": count,
                "originating_disclosure_row_count": disclosure_by_scope[status],
                "notes": "Completed source-supported scope disposition; unresolved units are not in the candidate frame.",
            }
            for status, count in sorted(scope_counts.items())
        ),
        *(
            {
                "stage": "eligible_screen_coverage", "disposition": status,
                "issuer_unit_count": count,
                "originating_disclosure_row_count": screen_origin_counts[status],
                "notes": "Eligible units retained from both pre-outcome screen strata.",
            }
            for status, count in sorted(screen_counts.items())
        ),
    ]

    write_csv(CANDIDATE_OUTPUT, candidate, CANDIDATE_FIELDS)
    write_csv(ORIGIN_OUTPUT, origins, ORIGIN_FIELDS)
    write_csv(FLOW_OUTPUT, flow, FLOW_FIELDS)
    write_csv(DESIGN_OUTPUT, design, DESIGN_FIELDS)

    baseline_geography = [row for row in crosswalk_rows if row["baseline_geography_gap"] == "true"]
    baseline_scope = [row for row in crosswalk_rows if row["baseline_scope_review"] == "true"]
    metrics: dict[str, object] = {
        "proposed_issuer_units": len(frame_rows),
        "originating_disclosure_rows": len(origins),
        "baseline_geography_gaps": len(baseline_geography),
        "baseline_geography_resolved": sum(row["geography_status"] == "source_supported_unique" for row in baseline_geography),
        "baseline_geography_multiple": sum(row["geography_status"] == "source_supported_multiple" for row in baseline_geography),
        "baseline_geography_unresolved": sum(row["geography_status"] == "unresolved_after_search" for row in baseline_geography),
        "baseline_scope_reviews": len(baseline_scope),
        "baseline_scope_resolved": sum(row["scope_disposition"] in {"eligible", "ineligible"} for row in baseline_scope),
        "baseline_scope_unresolved": sum(row["scope_disposition"] == "unresolved_after_search" for row in baseline_scope),
        "all_geography_statuses": dict(sorted(geography_counts.items())),
        "all_scope_dispositions": dict(sorted(scope_counts.items())),
        "eligible_candidate_units": len(candidate),
        "eligible_screen_statuses": dict(sorted(screen_counts.items())),
        "candidate_originating_disclosure_rows": sum(disclosure_by_scope[status] for status in ("eligible",)),
        "frozen_strata": len(design),
        "all_eligible_units_have_nonzero_probability": all(float(row["inclusion_probability"]) > 0 for row in candidate),
        "random_draw_executed": False,
        "deterministic_random_seed": SEED,
        "frame_ready_to_freeze": not any(row["scope_disposition"] == "unresolved_after_search" or row["geography_status"] != "source_supported_unique" for row in crosswalk_rows),
    }
    METRICS_OUTPUT.write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, sort_keys=True))
    return metrics


if __name__ == "__main__":
    build()
