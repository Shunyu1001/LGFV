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
    "ten": 10.0,
    "twelve": 12.0,
    "forty-four": 44.0,
    "sixty-one": 61.0,
    "seventy-eight": 78.0,
    "eighty-two": 82.0,
    "eighty-four": 84.0,
    "ninety-four": 94.0,
    "ninety-seven": 97.0,
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

    def rows(self, relative_path: str) -> list[dict[str, str]]:
        if relative_path not in self._cache:
            path = self.root / relative_path
            with path.open(newline="", encoding="utf-8") as handle:
                self._cache[relative_path] = list(csv.DictReader(handle))
        return self._cache[relative_path]

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
        "validated_gold_rows",
        r"current gold-standard file contains (?P<reported>ninety-four) human-validated",
        coverage_metric("Gold-standard labels"),
        0,
        "data/analysis_inputs/empirical_case_panel_coverage.csv",
        "component=Gold-standard labels, column=available",
    ),
    ClaimSpec(
        "initial_candidate_disclosures",
        r"broader screening file contains (?P<reported>361) candidate\s+disclosure rows",
        flow_metric("Candidate disclosure rows"),
        0,
        "data/analysis_inputs/surrogate_empirical_flow.csv",
        "step=Candidate disclosure rows, column=count",
    ),
    ClaimSpec(
        "historically_matched_rows",
        r"(?P<reported>Eighty-four) of the ninety-four validated labels can be matched",
        coverage_metric("Historical capacity match"),
        0,
        "data/analysis_inputs/empirical_case_panel_coverage.csv",
        "component=Historical capacity match, column=available",
    ),
    ClaimSpec(
        "historically_unmatched_rows",
        r"(?P<reported>Ten) validated cases remain unmatched",
        lambda metrics: coverage_metric("Gold-standard labels")(metrics)
        - coverage_metric("Historical capacity match")(metrics),
        0,
        "data/analysis_inputs/empirical_case_panel_coverage.csv",
        "Gold-standard labels available minus Historical capacity match available",
    ),
    ClaimSpec(
        "gold_substantive_exits",
        r"contains (?P<reported>two) substantive exits",
        exit_count("substantive_exit"),
        0,
        "data/analysis_inputs/pilot_exit_type_distribution.csv",
        "validation_tier=human_validated, column=substantive_exit",
    ),
    ClaimSpec(
        "gold_nominal_exits",
        r"two substantive exits, (?P<reported>eighty-two) nominal\s+exits",
        exit_count("nominal_exit"),
        0,
        "data/analysis_inputs/pilot_exit_type_distribution.csv",
        "validation_tier=human_validated, column=nominal_exit",
    ),
    ClaimSpec(
        "gold_functional_transfers",
        r"eighty-two nominal\s+exits, and (?P<reported>ten) functional transfers",
        exit_count("functional_transfer"),
        0,
        "data/analysis_inputs/pilot_exit_type_distribution.csv",
        "validation_tier=human_validated, column=functional_transfer",
    ),
    ClaimSpec(
        "elite_density_effect_pp",
        r"one-standard-deviation increase in elite density is\s+associated with a (?P<reported>[0-9.]+) percentage point increase",
        pilot_coefficient("Elite density", "Elite density, standardized"),
        1,
        "data/analysis_inputs/pilot_lpm_institutional_change.csv",
        "model=Elite density, variable=Elite density standardized, coefficient times 100",
    ),
    ClaimSpec(
        "high_capacity_effect_pp",
        r"high\s+historical-capacity bin is associated with a (?P<reported>[0-9.]+) percentage point increase",
        pilot_coefficient("High capacity", "High historical-capacity bin"),
        1,
        "data/analysis_inputs/pilot_lpm_institutional_change.csv",
        "model=High capacity, variable=High historical-capacity bin, coefficient times 100",
    ),
    ClaimSpec(
        "capacity_rank_effect_pp",
        r"low to middle to high capacity is\s+associated with a (?P<reported>[0-9.]+) percentage point increase",
        pilot_coefficient("Capacity rank", "Capacity bin rank"),
        1,
        "data/analysis_inputs/pilot_lpm_institutional_change.csv",
        "model=Capacity rank, variable=Capacity bin rank, coefficient times 100",
    ),
    ClaimSpec(
        "full_control_rows",
        r"full-controls sample contains (?P<reported>seventy-eight) rows",
        coverage_metric("Full-controls regression rows"),
        0,
        "data/analysis_inputs/empirical_case_panel_coverage.csv",
        "component=Full-controls regression rows, column=available",
    ),
    ClaimSpec(
        "screening_candidate_rows",
        r"It contains (?P<reported>361) candidate disclosure rows",
        flow_metric("Candidate disclosure rows"),
        0,
        "data/analysis_inputs/surrogate_empirical_flow.csv",
        "step=Candidate disclosure rows, column=count",
    ),
    ClaimSpec(
        "usable_screening_rows",
        r"of which (?P<reported>346)\s+are usable screening observations",
        flow_metric("Usable LLM screening rows"),
        0,
        "data/analysis_inputs/surrogate_empirical_flow.csv",
        "step=Usable LLM screening rows, column=count",
    ),
    ClaimSpec(
        "screening_gold_rows",
        r"outcome sample contains (?P<reported>ninety-four) gold-standard labels",
        coverage_metric("Gold-standard labels"),
        0,
        "data/analysis_inputs/empirical_case_panel_coverage.csv",
        "component=Gold-standard labels, column=available",
    ),
    ClaimSpec(
        "surrogate_disclosure_rows",
        r"and (?P<reported>203)\s+LLM surrogate exit-type labels",
        flow_metric("LLM surrogate disclosure labels"),
        0,
        "data/analysis_inputs/surrogate_empirical_flow.csv",
        "step=LLM surrogate disclosure labels, column=count",
    ),
    ClaimSpec(
        "no_formal_event_rows",
        r"include\s+(?P<reported>forty-four) source packets for which the model found no direct formal exit",
        flow_metric("Screened rows without direct formal event"),
        0,
        "data/analysis_inputs/surrogate_empirical_flow.csv",
        "step=Screened rows without direct formal event, column=count",
    ),
    ClaimSpec(
        "boundary_packet_rows",
        r"and (?P<reported>five) human-reviewed boundary packets",
        source_value(
            "data/analysis_inputs/llm_screening_summary_2026_07_03_expanded.csv",
            "quantity",
            "screening_status:human_reviewed_boundary",
            "value",
        ),
        0,
        "data/analysis_inputs/llm_screening_summary_2026_07_03_expanded.csv",
        "quantity=screening_status:human_reviewed_boundary, column=value",
    ),
    ClaimSpec(
        "surrogate_disclosures_repeated",
        r"The (?P<reported>203) disclosure-level surrogate labels",
        flow_metric("LLM surrogate disclosure labels"),
        0,
        "data/analysis_inputs/surrogate_empirical_flow.csv",
        "step=LLM surrogate disclosure labels, column=count",
    ),
    ClaimSpec(
        "surrogate_unique_issuers",
        r"correspond to (?P<reported>158) unique issuers",
        dsl_metric("surrogate_unique_issuers"),
        0,
        "data/analysis_inputs/dsl_surrogate_diagnostics.csv",
        "quantity=surrogate_unique_issuers, column=value",
    ),
    ClaimSpec(
        "surrogate_overlap_issuers",
        r"(?P<reported>Sixty-one) issuer-level surrogates overlap",
        dsl_metric("surrogate_gold_overlap_issuers"),
        0,
        "data/analysis_inputs/dsl_surrogate_diagnostics.csv",
        "quantity=surrogate_gold_overlap_issuers, column=value",
    ),
    ClaimSpec(
        "surrogate_nonoverlap_issuers",
        r"(?P<reported>Ninety-seven) non-overlap issuers enter",
        dsl_metric("nonoverlap_surrogate_issuers"),
        0,
        "data/analysis_inputs/dsl_surrogate_diagnostics.csv",
        "quantity=nonoverlap_surrogate_issuers, column=value",
    ),
    ClaimSpec(
        "raw_nominal_precision",
        r"raw precision of (?P<reported>[0-9.]+)",
        dsl_metric("raw_nominal_precision"),
        3,
        "data/analysis_inputs/dsl_surrogate_diagnostics.csv",
        "quantity=raw_nominal_precision, column=value",
    ),
    ClaimSpec(
        "jeffreys_nominal_precision",
        r"implied precision is (?P<reported>[0-9.]+)",
        dsl_metric("jeffreys_smoothed_nominal_precision"),
        3,
        "data/analysis_inputs/dsl_surrogate_diagnostics.csv",
        "quantity=jeffreys_smoothed_nominal_precision, column=value",
    ),
    ClaimSpec(
        "wilson_nominal_precision",
        r"conservative rate of (?P<reported>[0-9.]+)",
        dsl_metric("wilson_95_lower_nominal_precision"),
        3,
        "data/analysis_inputs/dsl_surrogate_diagnostics.csv",
        "quantity=wilson_95_lower_nominal_precision, column=value",
    ),
    ClaimSpec(
        "conservative_expected_nominal_nonoverlap",
        r"imply between (?P<reported>[0-9.]+) and [0-9.]+ expected nominal-exit cases",
        lambda metrics: adjusted_value(
            "Gold plus non-overlap surrogates, conservative", "nominal_exit"
        )(metrics)
        - dsl_metric("human_gold_nominal_exit")(metrics),
        2,
        "data/analysis_inputs/dsl_augmented_outcome_distribution.csv",
        "conservative nominal_exit minus human_gold_nominal_exit",
    ),
    ClaimSpec(
        "smoothed_expected_nominal_nonoverlap",
        r"imply between [0-9.]+ and (?P<reported>[0-9.]+) expected nominal-exit cases",
        lambda metrics: adjusted_value(
            "Gold plus non-overlap surrogates, smoothed", "nominal_exit"
        )(metrics)
        - dsl_metric("human_gold_nominal_exit")(metrics),
        2,
        "data/analysis_inputs/dsl_augmented_outcome_distribution.csv",
        "smoothed nominal_exit minus human_gold_nominal_exit",
    ),
    ClaimSpec(
        "adjusted_gold_rows",
        r"gold-standard file contains (?P<reported>ninety-four) cases",
        dsl_metric("human_gold_labels"),
        0,
        "data/analysis_inputs/dsl_surrogate_diagnostics.csv",
        "quantity=human_gold_labels, column=value",
    ),
    ClaimSpec(
        "adjusted_gold_nominal",
        r"of\s+which (?P<reported>eighty-two) are nominal exits",
        dsl_metric("human_gold_nominal_exit"),
        0,
        "data/analysis_inputs/dsl_surrogate_diagnostics.csv",
        "quantity=human_gold_nominal_exit, column=value",
    ),
    ClaimSpec(
        "adjusted_gold_change",
        r"and (?P<reported>twelve) are substantive exits or\s+functional transfers",
        dsl_metric("human_gold_institutional_change"),
        0,
        "data/analysis_inputs/dsl_surrogate_diagnostics.csv",
        "quantity=human_gold_institutional_change, column=value",
    ),
    ClaimSpec(
        "adjusted_nonoverlap_rows",
        r"Adding only the (?P<reported>ninety-seven) non-overlap issuer-level",
        dsl_metric("nonoverlap_surrogate_issuers"),
        0,
        "data/analysis_inputs/dsl_surrogate_diagnostics.csv",
        "quantity=nonoverlap_surrogate_issuers, column=value",
    ),
    ClaimSpec(
        "adjusted_sample_rows",
        r"produces a (?P<reported>191)-row adjusted descriptive sample",
        adjusted_value("Gold plus non-overlap surrogates, smoothed", "observations"),
        0,
        "data/analysis_inputs/dsl_augmented_outcome_distribution.csv",
        "sample=Gold plus non-overlap surrogates smoothed, column=observations",
    ),
    ClaimSpec(
        "adjusted_smoothed_nominal",
        r"sample contains (?P<reported>[0-9.]+) expected\s+nominal exits",
        adjusted_value("Gold plus non-overlap surrogates, smoothed", "nominal_exit"),
        2,
        "data/analysis_inputs/dsl_augmented_outcome_distribution.csv",
        "sample=Gold plus non-overlap surrogates smoothed, column=nominal_exit",
    ),
    ClaimSpec(
        "adjusted_conservative_nominal",
        r"conservative Wilson lower bound, it contains (?P<reported>[0-9.]+)\s+expected nominal exits",
        adjusted_value("Gold plus non-overlap surrogates, conservative", "nominal_exit"),
        2,
        "data/analysis_inputs/dsl_augmented_outcome_distribution.csv",
        "sample=Gold plus non-overlap surrogates conservative, column=nominal_exit",
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
