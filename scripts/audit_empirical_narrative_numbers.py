#!/usr/bin/env python3
"""Audit empirical narrative quantities against generated outputs."""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "paper" / "sections" / "empirical_strategy.tex"
INPUTS = ROOT / "data" / "analysis_inputs"

NUMBER_WORDS = {
    "two": 2.0,
    "five": 5.0,
    "four": 4.0,
    "six": 6.0,
    "eight": 8.0,
    "nine": 9.0,
    "eleven": 11.0,
    "ten": 10.0,
    "twelve": 12.0,
    "fifteen": 15.0,
    "eighteen": 18.0,
    "forty-four": 44.0,
    "sixty-one": 61.0,
    "seventy-eight": 78.0,
    "eighty-two": 82.0,
    "eighty-four": 84.0,
    "ninety-four": 94.0,
    "ninety-seven": 97.0,
    "no": 0.0,
    "none": 0.0,
    "zero": 0.0,
}


@dataclass(frozen=True)
class ClaimSpec:
    claim_id: str
    pattern: str
    expected: Callable[["GeneratedMetrics"], float]
    decimals: int
    source_path: str
    source_locator: str
    capture: str = "reported"


class GeneratedMetrics:
    def __init__(self, root: Path = ROOT) -> None:
        self.root = root
        self.inputs = root / "data" / "analysis_inputs"
        self._cache: dict[str, list[dict[str, str]]] = {}
        self._json_cache: dict[str, object] = {}

    def rows(self, relative_path: str) -> list[dict[str, str]]:
        if relative_path not in self._cache:
            path = self.root / relative_path
            with path.open(newline="", encoding="utf-8") as handle:
                self._cache[relative_path] = list(csv.DictReader(handle))
        return self._cache[relative_path]

    def json_value(self, relative_path: str, *keys: str) -> float:
        if relative_path not in self._json_cache:
            path = self.root / relative_path
            self._json_cache[relative_path] = json.loads(path.read_text(encoding="utf-8"))
        value: object = self._json_cache[relative_path]
        for key in keys:
            if not isinstance(value, dict) or key not in value:
                raise ValueError(f"Missing JSON key {key!r} in {relative_path}")
            value = value[key]
        return float(value)

    def value(
        self,
        relative_path: str,
        key_column: str,
        key_value: str,
        value_column: str,
        **extra_keys: str,
    ) -> float:
        matches = []
        for row in self.rows(relative_path):
            if row.get(key_column) != key_value:
                continue
            if any(row.get(key) != value for key, value in extra_keys.items()):
                continue
            matches.append(row)
        if len(matches) != 1:
            raise ValueError(
                f"Expected one row in {relative_path} for {key_column}={key_value!r} "
                f"and {extra_keys}, found {len(matches)}"
            )
        return float(matches[0][value_column])


def parse_reported(value: str) -> float:
    cleaned = value.strip().lower().rstrip(".")
    if cleaned in NUMBER_WORDS:
        return NUMBER_WORDS[cleaned]
    return float(cleaned.replace(",", ""))


def source_value(
    path: str,
    key_column: str,
    key_value: str,
    value_column: str,
    **extra_keys: str,
) -> Callable[[GeneratedMetrics], float]:
    return lambda metrics: metrics.value(
        path, key_column, key_value, value_column, **extra_keys
    )


def pilot_coefficient(model: str, variable: str) -> Callable[[GeneratedMetrics], float]:
    return lambda metrics: 100.0 * metrics.value(
        "data/analysis_inputs/pilot_lpm_institutional_change.csv",
        "model",
        model,
        "coefficient",
        variable=variable,
    )


def dsl_metric(quantity: str) -> Callable[[GeneratedMetrics], float]:
    return source_value(
        "data/analysis_inputs/dsl_surrogate_diagnostics.csv",
        "quantity",
        quantity,
        "value",
    )


def flow_metric(step: str) -> Callable[[GeneratedMetrics], float]:
    return source_value(
        "data/analysis_inputs/surrogate_empirical_flow.csv",
        "step",
        step,
        "count",
    )


def coverage_metric(component: str) -> Callable[[GeneratedMetrics], float]:
    return source_value(
        "data/analysis_inputs/empirical_case_panel_coverage.csv",
        "component",
        component,
        "available",
    )


def exit_count(column: str) -> Callable[[GeneratedMetrics], float]:
    return source_value(
        "data/analysis_inputs/pilot_exit_type_distribution.csv",
        "validation_tier",
        "human_validated",
        column,
    )


def adjusted_value(sample: str, column: str) -> Callable[[GeneratedMetrics], float]:
    return source_value(
        "data/analysis_inputs/dsl_augmented_outcome_distribution.csv",
        "sample",
        sample,
        column,
    )


CLAIMS = [
    ClaimSpec(
        "reference_cases",
        r"reference file contains\s+(?P<reported>94) city-platform cases",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-006/metrics.json", "gold", "cases"
        ),
        0,
        "experiments/EXP-20260830-006/metrics.json",
        "gold.cases",
    ),
    ClaimSpec(
        "reference_substantive",
        r"labels comprise\s+(?P<reported>two)\s+substantive",
        exit_count("substantive_exit"),
        0,
        "data/analysis_inputs/pilot_exit_type_distribution.csv",
        "validation_tier=human_validated, column=substantive_exit",
    ),
    ClaimSpec(
        "reference_nominal",
        r"substantive\s+exits, (?P<reported>82) nominal exits",
        exit_count("nominal_exit"),
        0,
        "data/analysis_inputs/pilot_exit_type_distribution.csv",
        "validation_tier=human_validated, column=nominal_exit",
    ),
    ClaimSpec(
        "reference_transfer",
        r"nominal exits, (?P<reported>ten) functional transfers",
        exit_count("functional_transfer"),
        0,
        "data/analysis_inputs/pilot_exit_type_distribution.csv",
        "validation_tier=human_validated, column=functional_transfer",
    ),
    ClaimSpec(
        "reference_liquidation",
        r"functional transfers, and (?P<reported>no)\s+liquidations",
        lambda metrics: 0.0,
        0,
        "experiments/EXP-20260830-006/metrics.json",
        "gold.label_counts has no liquidation row",
    ),
    ClaimSpec(
        "historically_matched",
        r"(?P<reported>Eighty-four) reference cases match",
        coverage_metric("Historical capacity match"),
        0,
        "data/analysis_inputs/empirical_case_panel_coverage.csv",
        "component=Historical capacity match, column=available",
    ),
    ClaimSpec(
        "historically_unmatched",
        r"The (?P<reported>ten) unmatched cases",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-006/metrics.json", "gold", "cases"
        )
        - coverage_metric("Historical capacity match")(metrics),
        0,
        "experiments/EXP-20260830-006/metrics.json",
        "gold.cases minus Historical capacity match",
    ),
    ClaimSpec(
        "source_identifiers_resolved",
        r"All (?P<reported>94) evidence identifiers resolve",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-002/metrics.json",
            "cases_all_identifiers_resolved",
        ),
        0,
        "experiments/EXP-20260830-002/metrics.json",
        "cases_all_identifiers_resolved",
    ),
    ClaimSpec(
        "complete_local_packets",
        r"(?P<reported>93) cases have\s+complete local copies",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-002/metrics.json",
            "cases_all_evidence_files_local",
        ),
        0,
        "experiments/EXP-20260830-002/metrics.json",
        "cases_all_evidence_files_local",
    ),
    ClaimSpec(
        "recovery_url_packets",
        r"all (?P<reported>94) have recovery URLs",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-002/metrics.json",
            "cases_all_documents_have_recovery_url",
        ),
        0,
        "experiments/EXP-20260830-002/metrics.json",
        "cases_all_documents_have_recovery_url",
    ),
    ClaimSpec(
        "exact_evidence_memos",
        r"and (?P<reported>62) have exact case-level evidence memos",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-002/metrics.json",
            "cases_with_exact_evidence_memo_match",
        ),
        0,
        "experiments/EXP-20260830-002/metrics.json",
        "cases_with_exact_evidence_memo_match",
    ),
    ClaimSpec(
        "elite_density_effect_pp",
        r"elite\s+density is associated with a (?P<reported>[0-9.]+) percentage point increase",
        pilot_coefficient("Elite density", "Elite density, standardized"),
        1,
        "data/analysis_inputs/pilot_lpm_institutional_change.csv",
        "model=Elite density, variable=Elite density standardized, coefficient times 100",
    ),
    ClaimSpec(
        "high_capacity_effect_pp",
        r"high-capacity bin is associated with a (?P<reported>[0-9.]+)\s+percentage point increase",
        pilot_coefficient("High capacity", "High historical-capacity bin"),
        1,
        "data/analysis_inputs/pilot_lpm_institutional_change.csv",
        "model=High capacity, variable=High historical-capacity bin, coefficient times 100",
    ),
    ClaimSpec(
        "capacity_rank_effect_pp",
        r"low to middle to high\s+is associated with a (?P<reported>[0-9.]+) percentage point increase",
        pilot_coefficient("Capacity rank", "Capacity bin rank"),
        1,
        "data/analysis_inputs/pilot_lpm_institutional_change.csv",
        "model=Capacity rank, variable=Capacity bin rank, coefficient times 100",
    ),
    ClaimSpec(
        "complete_control_rows",
        r"controls are available for\s+(?P<reported>78) of the 84",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-005/metrics.json",
            "complete_control_observations",
        ),
        0,
        "experiments/EXP-20260830-005/metrics.json",
        "complete_control_observations",
    ),
    ClaimSpec(
        "excluded_nominal_rows",
        r"restriction removes (?P<reported>six)\s+low-capacity\s+nominal exits",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-005/metrics.json",
            "excluded_matched_gold_observations",
        ),
        0,
        "experiments/EXP-20260830-005/metrics.json",
        "excluded_matched_gold_observations",
    ),
    ClaimSpec(
        "complete_control_events",
        r"retaining all (?P<reported>twelve) institutional-change\s+events",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-005/metrics.json",
            "complete_control_events",
        ),
        0,
        "experiments/EXP-20260830-005/metrics.json",
        "complete_control_events",
    ),
    ClaimSpec(
        "corrected_design_columns",
        r"corrected design\s+has (?P<reported>eight) independent columns",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-012/metrics.json",
            "corrected_adjusted_design",
            "columns",
        ),
        0,
        "experiments/EXP-20260830-012/metrics.json",
        "corrected_adjusted_design.columns",
    ),
    ClaimSpec(
        "corrected_design_rank",
        r"corrected design\s+has (?P<reported>eight) independent columns",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-012/metrics.json",
            "corrected_adjusted_design",
            "matrix_rank",
        ),
        0,
        "experiments/EXP-20260830-012/metrics.json",
        "corrected_adjusted_design.matrix_rank",
    ),
    ClaimSpec(
        "events_per_independent_column",
        r"or (?P<reported>[0-9.]+) events per column",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-012/metrics.json",
            "corrected_adjusted_design",
            "events_per_independent_column",
        ),
        1,
        "experiments/EXP-20260830-012/metrics.json",
        "corrected_adjusted_design.events_per_independent_column",
    ),
    ClaimSpec(
        "adjusted_lpm_effect_pp",
        r"effects are (?P<reported>[0-9.]+) and 0.3 percentage",
        lambda metrics: 100.0 * metrics.json_value(
            "experiments/EXP-20260830-012/metrics.json",
            "complete_control_adjusted_lpm",
            "probability_effect",
        ),
        1,
        "experiments/EXP-20260830-012/metrics.json",
        "complete_control_adjusted_lpm.probability_effect times 100",
    ),
    ClaimSpec(
        "adjusted_firth_effect_pp",
        r"effects are 0.5 and (?P<reported>[0-9.]+) percentage",
        lambda metrics: 100.0 * metrics.json_value(
            "experiments/EXP-20260830-012/metrics.json",
            "complete_control_adjusted_firth",
            "average_marginal_effect",
        ),
        1,
        "experiments/EXP-20260830-012/metrics.json",
        "complete_control_adjusted_firth.average_marginal_effect times 100",
    ),
    ClaimSpec(
        "adjusted_lpm_sign_changes",
        r"signs in (?P<reported>nine) and\s+eleven of 78",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-012/metrics.json",
            "complete_control_adjusted_lpm",
            "leave_one_out_sign_changes",
        ),
        0,
        "experiments/EXP-20260830-012/metrics.json",
        "complete_control_adjusted_lpm.leave_one_out_sign_changes",
    ),
    ClaimSpec(
        "adjusted_firth_sign_changes",
        r"signs in nine and\s+(?P<reported>eleven) of 78",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-012/metrics.json",
            "complete_control_adjusted_firth",
            "leave_one_out_sign_changes",
        ),
        0,
        "experiments/EXP-20260830-012/metrics.json",
        "complete_control_adjusted_firth.leave_one_out_sign_changes",
    ),
    ClaimSpec(
        "historical_sign_changes",
        r"historical-only effects change sign\s+in (?P<reported>zero) deletions",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-012/metrics.json",
            "matched_gold_historical_lpm",
            "leave_one_out_sign_changes",
        ),
        0,
        "experiments/EXP-20260830-012/metrics.json",
        "matched_gold_historical_lpm.leave_one_out_sign_changes",
    ),
    ClaimSpec(
        "provinces_with_outcome_variation",
        r"only (?P<reported>four) of eighteen provinces",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-012/metrics.json",
            "province_feasibility",
            "provinces_with_outcome_variation",
        ),
        0,
        "experiments/EXP-20260830-012/metrics.json",
        "province_feasibility.provinces_with_outcome_variation",
    ),
    ClaimSpec(
        "province_count",
        r"four of (?P<reported>eighteen) provinces",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-012/metrics.json",
            "province_feasibility",
            "provinces",
        ),
        0,
        "experiments/EXP-20260830-012/metrics.json",
        "province_feasibility.provinces",
    ),
    ClaimSpec(
        "province_fe_candidate_columns",
        r"candidate design would contain (?P<reported>25) columns",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-012/metrics.json",
            "province_feasibility",
            "candidate_columns",
        ),
        0,
        "experiments/EXP-20260830-012/metrics.json",
        "province_feasibility.candidate_columns",
    ),
    ClaimSpec(
        "candidate_disclosures",
        r"Among (?P<reported>361) candidate disclosure rows",
        flow_metric("Candidate disclosure rows"),
        0,
        "data/analysis_inputs/surrogate_empirical_flow.csv",
        "step=Candidate disclosure rows, column=count",
    ),
    ClaimSpec(
        "usable_screening",
        r"(?P<reported>346) have usable source",
        flow_metric("Usable LLM screening rows"),
        0,
        "data/analysis_inputs/surrogate_empirical_flow.csv",
        "step=Usable LLM screening rows, column=count",
    ),
    ClaimSpec(
        "screening_reference_rows",
        r"contains the (?P<reported>94) reference\s+labels",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-006/metrics.json", "gold", "cases"
        ),
        0,
        "experiments/EXP-20260830-006/metrics.json",
        "gold.cases",
    ),
    ClaimSpec(
        "surrogate_disclosures",
        r"and (?P<reported>203) one-sided nominal-exit surrogates",
        flow_metric("LLM surrogate disclosure labels"),
        0,
        "data/analysis_inputs/surrogate_empirical_flow.csv",
        "step=LLM surrogate disclosure labels, column=count",
    ),
    ClaimSpec(
        "no_formal_rows",
        r"(?P<reported>Forty-four) reviewed packets\s+lack a directly documented formal event",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-006/metrics.json",
            "screening",
            "no_direct_formal_event_disclosure_rows",
        ),
        0,
        "experiments/EXP-20260830-006/metrics.json",
        "screening.no_direct_formal_event_disclosure_rows",
    ),
    ClaimSpec(
        "boundary_rows",
        r"(?P<reported>five) are boundary packets",
        source_value(
            "data/analysis_inputs/llm_screening_summary_2026_07_03_expanded.csv",
            "quantity",
            "screening_status:working_reference_boundary",
            "value",
        ),
        0,
        "data/analysis_inputs/llm_screening_summary_2026_07_03_expanded.csv",
        "quantity=screening_status:working_reference_boundary, column=value",
    ),
    ClaimSpec(
        "source_missing_rows",
        r"and (?P<reported>fifteen)\s+lack a usable source packet",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-006/metrics.json",
            "screening",
            "source_missing_rows_with_blank_issuer",
        ),
        0,
        "experiments/EXP-20260830-006/metrics.json",
        "screening.source_missing_rows_with_blank_issuer",
    ),
    ClaimSpec(
        "surrogate_issuers",
        r"203 surrogate rows to (?P<reported>158) issuers",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-006/metrics.json",
            "screening",
            "positive_issuers",
        ),
        0,
        "experiments/EXP-20260830-006/metrics.json",
        "screening.positive_issuers",
    ),
    ClaimSpec(
        "overlap_issuers",
        r"(?P<reported>Sixty-one)\s+issuers also appear",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-006/metrics.json",
            "overlap",
            "selected_issuers",
        ),
        0,
        "experiments/EXP-20260830-006/metrics.json",
        "overlap.selected_issuers",
    ),
    ClaimSpec(
        "nonoverlap_issuers",
        r"(?P<reported>97) do not",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-006/metrics.json",
            "proposed_probability_design",
            "positive_stratum_n",
        ),
        0,
        "experiments/EXP-20260830-006/metrics.json",
        "proposed_probability_design.positive_stratum_n",
    ),
    ClaimSpec(
        "proposed_frame_rows",
        r"proposed (?P<reported>133)-issuer frame",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-008/metrics.json", "frame_rows"
        ),
        0,
        "experiments/EXP-20260830-008/metrics.json",
        "frame_rows",
    ),
    ClaimSpec(
        "source_supported_geography_rows",
        r"province-city pair for (?P<reported>40)\s+of the 128",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-011/metrics.json",
            "source_supported_unique_geography_units",
        ),
        0,
        "experiments/EXP-20260830-011/metrics.json",
        "source_supported_unique_geography_units",
    ),
    ClaimSpec(
        "unresolved_geography_rows",
        r"leaving (?P<reported>88) unresolved",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-011/metrics.json",
            "unresolved_geography_units",
        ),
        0,
        "experiments/EXP-20260830-011/metrics.json",
        "unresolved_geography_units",
    ),
    ClaimSpec(
        "fully_supported_scope_rows",
        r"Only (?P<reported>five)\s+issuers have source support for identity",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-011/metrics.json",
            "fully_supported_identity_geography_owner_role_units",
        ),
        0,
        "experiments/EXP-20260830-011/metrics.json",
        "fully_supported_identity_geography_owner_role_units",
    ),
    ClaimSpec(
        "candidate_packet_rows",
        r"only (?P<reported>four) enter the current blinded candidate",
        lambda metrics: metrics.json_value(
            "experiments/EXP-20260830-014/metrics.json",
            "candidate_packet_rows",
        ),
        0,
        "experiments/EXP-20260830-014/metrics.json",
        "candidate_packet_rows",
    ),
]

def audit(
    manuscript: Path = MANUSCRIPT, root: Path = ROOT
) -> tuple[list[dict[str, object]], dict[str, object]]:
    text = manuscript.read_text(encoding="utf-8")
    metrics = GeneratedMetrics(root)
    rows: list[dict[str, object]] = []
    for spec in CLAIMS:
        matches = list(re.finditer(spec.pattern, text, flags=re.IGNORECASE | re.MULTILINE))
        if len(matches) != 1:
            rows.append(
                {
                    "claim_id": spec.claim_id,
                    "manuscript_path": str(manuscript.relative_to(root)),
                    "line": "",
                    "reported_text": "",
                    "reported_value": "",
                    "generated_value": "",
                    "display_decimals": spec.decimals,
                    "difference": "",
                    "status": "missing_text" if not matches else "ambiguous_text",
                    "source_path": spec.source_path,
                    "source_locator": spec.source_locator,
                }
            )
            continue
        match = matches[0]
        reported_text = match.group(spec.capture)
        reported = parse_reported(reported_text)
        generated_raw = spec.expected(metrics)
        generated = round(generated_raw, spec.decimals)
        difference = round(reported - generated, max(spec.decimals, 3))
        status = "match" if reported == generated else "mismatch"
        rows.append(
            {
                "claim_id": spec.claim_id,
                "manuscript_path": str(manuscript.relative_to(root)),
                "line": text.count("\n", 0, match.start()) + 1,
                "reported_text": reported_text,
                "reported_value": f"{reported:.{spec.decimals}f}",
                "generated_value": f"{generated:.{spec.decimals}f}",
                "display_decimals": spec.decimals,
                "difference": f"{difference:.{max(spec.decimals, 3)}f}",
                "status": status,
                "source_path": spec.source_path,
                "source_locator": spec.source_locator,
            }
        )
    counts = {
        status: sum(row["status"] == status for row in rows)
        for status in ["match", "mismatch", "missing_text", "ambiguous_text"]
    }
    summary: dict[str, object] = {
        "manuscript": str(manuscript.relative_to(root)),
        "claims_audited": len(rows),
        **counts,
        "mismatch_claim_ids": [
            row["claim_id"] for row in rows if row["status"] == "mismatch"
        ],
        "selection_by_sign_or_significance": False,
    }
    return rows, summary


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manuscript", type=Path, default=MANUSCRIPT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rows, summary = audit(args.manuscript)
    if args.output:
        write_csv(args.output, rows)
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, sort_keys=True))
    if args.check and any(
        summary[status] for status in ["mismatch", "missing_text", "ambiguous_text"]
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
