#!/usr/bin/env python3
"""Audit the estimands identified by the current measurement artifacts.

The audit is deliberately descriptive. It does not interpret the observed
surrogate-gold overlap as a probability sample and does not modify labels.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "data" / "processed" / "human_validated_labels.csv"
SCREENING = (
    ROOT
    / "data"
    / "analysis_inputs"
    / "llm_screening_sample_2026_07_03_expanded.csv"
)
ISSUERS = (
    ROOT
    / "data"
    / "analysis_inputs"
    / "codex_surrogate_issuer_summary_2026_07_03_expanded.csv"
)
OUT_COUNTS = ROOT / "data" / "validation" / "current_measurement_counts.csv"
OUT_ESTIMANDS = ROOT / "data" / "validation" / "current_measurement_estimands.csv"
OUT_DESIGN = ROOT / "data" / "validation" / "validation_design_requirements.csv"
OUT_METRICS = ROOT / "experiments" / "EXP-20260830-002" / "metrics.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def is_true(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def compact_name(value: str) -> str:
    return re.sub(r"[^\w\u4e00-\u9fff]", "", (value or "").lower())


def csv_text(fieldnames: list[str], rows: list[dict[str, object]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def output_texts() -> tuple[dict[Path, str], dict[str, object]]:
    gold = read_csv(GOLD)
    screening = read_csv(SCREENING)
    issuers = read_csv(ISSUERS)

    gold_counts = Counter(row["final_label"] for row in gold)
    screening_counts = Counter(row["screening_status"] for row in screening)
    candidate_rows = [
        row for row in screening if row["label_source"] == "codex_surrogate"
    ]
    named_candidate_rows = [row for row in candidate_rows if row["issuer_name"].strip()]
    source_missing_rows = [
        row
        for row in candidate_rows
        if row["screening_status"] == "source_packet_missing"
    ]

    candidate_by_issuer: dict[str, list[dict[str, str]]] = defaultdict(list)
    display_name: dict[str, str] = {}
    for row in named_candidate_rows:
        key = compact_name(row["issuer_name"])
        candidate_by_issuer[key].append(row)
        display_name.setdefault(key, row["issuer_name"])

    candidate_status: dict[str, str] = {}
    for key, rows in candidate_by_issuer.items():
        statuses = {row["screening_status"] for row in rows}
        if "llm_surrogate_exit_type" in statuses:
            candidate_status[key] = "screen_positive_nominal"
        elif "llm_screened_no_direct_formal_event" in statuses:
            candidate_status[key] = "screened_no_direct_formal_event"
        else:
            candidate_status[key] = "unresolved_named_issuer"

    status_counts = Counter(candidate_status.values())
    gold_by_issuer = {
        compact_name(row["company_name"]): row
        for row in gold
        if row["company_name"].strip()
    }
    overlap_keys = sorted(
        key
        for key, status in candidate_status.items()
        if status == "screen_positive_nominal" and key in gold_by_issuer
    )
    nonoverlap_positive_keys = sorted(
        key
        for key, status in candidate_status.items()
        if status == "screen_positive_nominal" and key not in gold_by_issuer
    )
    nonoverlap_nonpositive_keys = sorted(
        key
        for key, status in candidate_status.items()
        if status == "screened_no_direct_formal_event" and key not in gold_by_issuer
    )
    overlap_pairs = Counter(
        ("nominal_exit", gold_by_issuer[key]["final_label"]) for key in overlap_keys
    )
    overlap_codex_assisted = sum(
        "Codex-assisted" in gold_by_issuer[key]["human_reviewer"]
        for key in overlap_keys
    )
    overlap_nominal_matches = overlap_pairs[("nominal_exit", "nominal_exit")]
    overlap_match_rate = (
        overlap_nominal_matches / len(overlap_keys) if overlap_keys else 0.0
    )

    issuer_overlap_rows = [
        row for row in issuers if is_true(row["gold_standard_overlap"])
    ]
    issuer_nonoverlap_rows = [
        row for row in issuers if not is_true(row["gold_standard_overlap"])
    ]

    expected = {
        "gold_rows": 94,
        "gold_nominal_exit": 82,
        "gold_substantive_exit": 2,
        "gold_functional_transfer": 10,
        "screening_rows": 361,
        "candidate_rows": 262,
        "surrogate_positive_disclosures": 203,
        "screened_no_formal_event_disclosures": 44,
        "source_missing_disclosures": 15,
        "surrogate_positive_issuers": 158,
        "surrogate_overlap_issuers": 61,
        "surrogate_nonoverlap_positive_issuers": 97,
    }
    observed = {
        "gold_rows": len(gold),
        "gold_nominal_exit": gold_counts["nominal_exit"],
        "gold_substantive_exit": gold_counts["substantive_exit"],
        "gold_functional_transfer": gold_counts["functional_transfer"],
        "screening_rows": len(screening),
        "candidate_rows": len(candidate_rows),
        "surrogate_positive_disclosures": screening_counts[
            "llm_surrogate_exit_type"
        ],
        "screened_no_formal_event_disclosures": screening_counts[
            "llm_screened_no_direct_formal_event"
        ],
        "source_missing_disclosures": screening_counts["source_packet_missing"],
        "surrogate_positive_issuers": status_counts["screen_positive_nominal"],
        "surrogate_overlap_issuers": len(overlap_keys),
        "surrogate_nonoverlap_positive_issuers": len(nonoverlap_positive_keys),
    }
    discrepancies = {
        key: {"expected": expected[key], "observed": observed[key]}
        for key in expected
        if expected[key] != observed[key]
    }

    if len(issuers) != status_counts["screen_positive_nominal"]:
        raise ValueError("Issuer summary does not match the positive issuer count")
    if len(issuer_overlap_rows) != len(overlap_keys):
        raise ValueError("Issuer-summary overlap count does not match screening audit")
    if len(issuer_nonoverlap_rows) != len(nonoverlap_positive_keys):
        raise ValueError("Issuer-summary non-overlap count does not match screening audit")
    if any(row["issuer_name"].strip() for row in source_missing_rows):
        raise ValueError("Source-missing rows unexpectedly contain issuer names")
    if discrepancies:
        raise ValueError(f"Declared-count discrepancies: {discrepancies}")

    counts_rows: list[dict[str, object]] = [
        {
            "object_id": "gold_cases",
            "unit": "city-platform case",
            "quantity": "rows",
            "value": len(gold),
            "note": "Assembled human-reviewed file; not a probability sample.",
        },
        *[
            {
                "object_id": f"gold_{label}",
                "unit": "city-platform case",
                "quantity": "final_label count",
                "value": gold_counts[label],
                "note": "Observed within the 94-case gold file.",
            }
            for label in ("substantive_exit", "nominal_exit", "functional_transfer")
        ],
        {
            "object_id": "gold_liquidation",
            "unit": "city-platform case",
            "quantity": "final_label count",
            "value": gold_counts["liquidation"],
            "note": "No liquidation case is present, so category-specific reliability is not observed.",
        },
        {
            "object_id": "gold_codex_assisted_reviewer_field",
            "unit": "city-platform case",
            "quantity": "rows",
            "value": sum(
                "Codex-assisted" in row["human_reviewer"] for row in gold
            ),
            "note": "The field still identifies Shunyu Hao as the human reviewer; it does not document an independent second human.",
        },
        {
            "object_id": "candidate_disclosures",
            "unit": "candidate disclosure row",
            "quantity": "rows",
            "value": len(candidate_rows),
            "note": "Rows assigned to Codex screening rather than human gold or boundary review.",
        },
        {
            "object_id": "surrogate_positive_disclosures",
            "unit": "candidate disclosure row",
            "quantity": "rows",
            "value": screening_counts["llm_surrogate_exit_type"],
            "note": "All current surrogate exit-type predictions are nominal_exit.",
        },
        {
            "object_id": "screened_no_formal_event_disclosures",
            "unit": "candidate disclosure row",
            "quantity": "rows",
            "value": screening_counts["llm_screened_no_direct_formal_event"],
            "note": "These are screening outcomes, not negative exit-type labels.",
        },
        {
            "object_id": "source_missing_disclosures",
            "unit": "candidate disclosure row",
            "quantity": "rows",
            "value": len(source_missing_rows),
            "note": "Issuer names are blank, so these rows cannot be deduplicated to issuer units from this file.",
        },
        {
            "object_id": "named_source_available_candidate_issuers",
            "unit": "issuer",
            "quantity": "unique normalized issuer names",
            "value": len(candidate_by_issuer),
            "note": "Excludes the 15 source-missing rows with blank issuer names.",
        },
        {
            "object_id": "surrogate_positive_issuers",
            "unit": "issuer",
            "quantity": "unique issuers",
            "value": status_counts["screen_positive_nominal"],
            "note": "At least one disclosure received the one-sided nominal screen.",
        },
        {
            "object_id": "screened_no_formal_event_issuers",
            "unit": "issuer",
            "quantity": "unique issuers",
            "value": status_counts["screened_no_direct_formal_event"],
            "note": "No disclosure for the issuer received a surrogate exit-type label.",
        },
        {
            "object_id": "selected_overlap_issuers",
            "unit": "issuer",
            "quantity": "unique issuers",
            "value": len(overlap_keys),
            "note": "Post-hoc identity overlap between surrogate-positive and gold files.",
        },
        {
            "object_id": "selected_overlap_nominal_matches",
            "unit": "issuer",
            "quantity": "nominal surrogate and nominal gold",
            "value": overlap_nominal_matches,
            "note": "Descriptive agreement in selected overlap units.",
        },
        {
            "object_id": "nonoverlap_positive_issuers",
            "unit": "issuer",
            "quantity": "unique issuers",
            "value": len(nonoverlap_positive_keys),
            "note": "Current positive-screen validation queue.",
        },
        {
            "object_id": "nonoverlap_nonpositive_issuers",
            "unit": "issuer",
            "quantity": "unique issuers",
            "value": len(nonoverlap_nonpositive_keys),
            "note": "Source-available issuers needed to measure false negatives and recall.",
        },
    ]

    estimand_fields = [
        "estimand_id",
        "evidence_object",
        "unit",
        "selection_mechanism",
        "target_population",
        "error_quantity",
        "current_value",
        "numerator",
        "denominator",
        "identification_status",
        "uncertainty_status",
        "limitation",
        "required_new_data",
    ]
    estimand_rows: list[dict[str, object]] = [
        {
            "estimand_id": "E01_gold_distribution",
            "evidence_object": "human_validated_labels",
            "unit": "city-platform case",
            "selection_mechanism": "assembled and human-reviewed cases",
            "target_population": "the 94 cases in the tracked gold file",
            "error_quantity": "none; descriptive label distribution",
            "current_value": "2 substantive; 82 nominal; 10 transfer; 0 liquidation",
            "numerator": "category-specific observed count",
            "denominator": "94",
            "identification_status": "identified within assembled sample",
            "uncertainty_status": "no population sampling design",
            "limitation": "Does not estimate national prevalence or label accuracy.",
            "required_new_data": "Probability frame for prevalence; independent coding for reliability.",
        },
        {
            "estimand_id": "E02_screening_flow",
            "evidence_object": "llm_screening_sample",
            "unit": "candidate disclosure row",
            "selection_mechanism": "assembled disclosure pool and deterministic screening rules",
            "target_population": "the 361 tracked disclosure rows",
            "error_quantity": "none; screening and source-availability flow",
            "current_value": "203 positive; 44 no direct formal event; 15 source missing; 99 human rows",
            "numerator": "status-specific observed count",
            "denominator": "361",
            "identification_status": "identified within assembled disclosure pool",
            "uncertainty_status": "no population sampling design",
            "limitation": "Disclosure rows are clustered within issuers and are not independent cases.",
            "required_new_data": "None for the tracked flow; an issuer frame is needed for issuer-level rates.",
        },
        {
            "estimand_id": "E03_selected_overlap_concordance",
            "evidence_object": "issuer_summary joined to gold by normalized issuer name",
            "unit": "issuer",
            "selection_mechanism": "post-hoc overlap among surrogate-positive issuers and the gold file",
            "target_population": "the 61 observed overlap issuers",
            "error_quantity": "conditional nominal-label concordance",
            "current_value": f"{overlap_match_rate:.3f}",
            "numerator": str(overlap_nominal_matches),
            "denominator": str(len(overlap_keys)),
            "identification_status": "identified only as descriptive overlap concordance",
            "uncertainty_status": "no design-based population interval",
            "limitation": f"Overlap was not probability sampled; all overlap labels are nominal and {overlap_codex_assisted} of {len(overlap_keys)} reviewer fields record Codex-assisted review.",
            "required_new_data": "Probability-sampled positives with human coding blinded to the surrogate output.",
        },
        {
            "estimand_id": "E04_positive_predictive_value",
            "evidence_object": "one-sided nominal screen",
            "unit": "issuer",
            "selection_mechanism": "no probability validation sample",
            "target_population": "source-available surrogate-positive issuers in a defined candidate frame",
            "error_quantity": "precision / positive predictive value",
            "current_value": "not identified",
            "numerator": "human nominal labels among sampled positive issuers",
            "denominator": "all sampled positive issuers",
            "identification_status": "not identified for a target population",
            "uncertainty_status": "Jeffreys or Wilson calculations on 61 selected overlaps do not repair selection",
            "limitation": "The 97 non-overlap positives lack independent human labels and overlap inclusion probabilities are unknown.",
            "required_new_data": "Known-probability sample of positive issuers and independent blind human labels.",
        },
        {
            "estimand_id": "E05_recall",
            "evidence_object": "one-sided nominal screen",
            "unit": "issuer",
            "selection_mechanism": "no human validation of the screen-nonpositive stratum",
            "target_population": "source-available issuers in a defined candidate frame",
            "error_quantity": "recall / sensitivity for human nominal exit",
            "current_value": "not identified",
            "numerator": "screen-positive human nominal issuers",
            "denominator": "all human nominal issuers in positive and nonpositive screen strata",
            "identification_status": "not identified",
            "uncertainty_status": "no estimable sampling error",
            "limitation": "None of the 36 named no-formal-event issuers has a gold overlap in the current files.",
            "required_new_data": "Human labels from a probability sample that includes all screen statuses.",
        },
        {
            "estimand_id": "E06_calibration",
            "evidence_object": "surrogate confidence field",
            "unit": "issuer",
            "selection_mechanism": "categorical evidence confidence, not predictive probabilities",
            "target_population": "undefined",
            "error_quantity": "calibration",
            "current_value": "not identified",
            "numerator": "not observed",
            "denominator": "not observed",
            "identification_status": "not identified",
            "uncertainty_status": "not applicable",
            "limitation": "The current output has no frozen probability score and no independent outcome sample across score levels.",
            "required_new_data": "Pre-outcome probability scores plus probability-sampled human labels.",
        },
        {
            "estimand_id": "E07_four_category_error",
            "evidence_object": "one-sided nominal screen",
            "unit": "issuer",
            "selection_mechanism": "surrogate rule emits only nominal_exit",
            "target_population": "undefined for a four-category classifier",
            "error_quantity": "four-category confusion matrix and category-specific error",
            "current_value": "not identified",
            "numerator": "not observed for three surrogate prediction categories",
            "denominator": "not observed in a common validation frame",
            "identification_status": "not identified",
            "uncertainty_status": "not applicable",
            "limitation": "Substantive exit, functional transfer, and liquidation are never surrogate predictions; liquidation is also absent from gold.",
            "required_new_data": "Frozen multiclass predictions and independent human labels sampled from the same eligible frame.",
        },
        {
            "estimand_id": "E08_intercoder_agreement",
            "evidence_object": "human gold labels",
            "unit": "city-platform case",
            "selection_mechanism": "one identified human reviewer with Codex assistance on most rows",
            "target_population": "the assembled gold cases",
            "error_quantity": "raw agreement, category agreement, kappa, and adjudication count",
            "current_value": "not identified",
            "numerator": "no independent coder pair observed",
            "denominator": "no independently double-coded cases observed",
            "identification_status": "not identified",
            "uncertainty_status": "not applicable",
            "limitation": "LLM assistance is not an independent second human coder.",
            "required_new_data": "A second human must code frozen packets without seeing current labels; disagreements must be adjudicated and logged.",
        },
        {
            "estimand_id": "E09_sampling_error",
            "evidence_object": "gold and overlap files",
            "unit": "case or issuer, depending on target",
            "selection_mechanism": "assembled samples with unknown inclusion probabilities",
            "target_population": "no probability target is currently defined",
            "error_quantity": "design-based sampling error",
            "current_value": "not identified",
            "numerator": "not applicable",
            "denominator": "not applicable",
            "identification_status": "not identified",
            "uncertainty_status": "binomial intervals do not account for unknown selection",
            "limitation": "Finite-sample smoothing addresses boundary estimates, not selection or transportability.",
            "required_new_data": "Frozen frame, random seed, stratum counts, inclusion probabilities, and completed sampled reviews.",
        },
    ]

    positive_population = len(nonoverlap_positive_keys)
    positive_sample = min(60, positive_population)
    nonpositive_population = len(nonoverlap_nonpositive_keys)
    nonpositive_sample = nonpositive_population
    positive_pi = positive_sample / positive_population
    design_fields = [
        "component",
        "target_frame",
        "unit",
        "stratum",
        "population_n",
        "proposed_sample_n",
        "inclusion_probability",
        "selection_rule",
        "human_work",
        "identified_quantity_after_completion",
        "review_gate",
    ]
    design_rows: list[dict[str, object]] = [
        {
            "component": "one_sided_screen_validation",
            "target_frame": "133 named, source-available, non-overlap candidate issuers",
            "unit": "issuer",
            "stratum": "screen_positive_nominal",
            "population_n": positive_population,
            "proposed_sample_n": positive_sample,
            "inclusion_probability": f"{positive_pi:.6f}",
            "selection_rule": "Simple random sample without replacement using a frozen seed after human approval.",
            "human_work": "Review original packets blind to screen output and assign eligibility plus the frozen four-category label or unclear.",
            "identified_quantity_after_completion": "Design-weighted positive predictive value and contribution to recall in this fixed frame.",
            "review_gate": "Human approval required before freezing or drawing the validation sample.",
        },
        {
            "component": "one_sided_screen_validation",
            "target_frame": "133 named, source-available, non-overlap candidate issuers",
            "unit": "issuer",
            "stratum": "screened_no_direct_formal_event",
            "population_n": nonpositive_population,
            "proposed_sample_n": nonpositive_sample,
            "inclusion_probability": "1.000000",
            "selection_rule": "Census the small nonpositive stratum after human approval.",
            "human_work": "Search and review original packets blind to screen output; record whether a formal event and any human exit label are found.",
            "identified_quantity_after_completion": "False-negative count, design-weighted recall, and source-screening error in this fixed frame.",
            "review_gate": "Human approval required before freezing or drawing the validation sample.",
        },
        {
            "component": "source_availability",
            "target_frame": "15 candidate rows with missing source packets and blank issuer names",
            "unit": "candidate row until entity resolution",
            "stratum": "source_packet_missing",
            "population_n": len(source_missing_rows),
            "proposed_sample_n": len(source_missing_rows),
            "inclusion_probability": "1.000000",
            "selection_rule": "Resolve issuer identity and source availability for every row before deduplication.",
            "human_work": "Recover permitted source packets or document permanent unavailability; do not assign a negative outcome.",
            "identified_quantity_after_completion": "Coverage and attrition only; label accuracy remains undefined without sources.",
            "review_gate": "No label change; any addition to the validation accuracy frame requires approved eligibility handling.",
        },
        {
            "component": "human_label_reliability",
            "target_frame": "94 frozen gold case packets",
            "unit": "city-platform case",
            "stratum": "all current gold cases",
            "population_n": len(gold),
            "proposed_sample_n": len(gold),
            "inclusion_probability": "1.000000",
            "selection_rule": "Independent census recoding by a second human, blind to current and LLM labels.",
            "human_work": "A second human applies the frozen codebook to all 94 packets; the original reviewer and second coder adjudicate every disagreement afterward.",
            "identified_quantity_after_completion": "Raw and category-specific agreement, kappa or an appropriate sparse-category alternative, and adjudication counts within the assembled gold cases.",
            "review_gate": "Human approval and a real second coder are required; liquidation agreement remains unobservable with no liquidation cases.",
        },
        {
            "component": "future_multiclass_validation",
            "target_frame": "new eligible issuer frame defined before outcomes",
            "unit": "issuer",
            "stratum": "predeclared prediction and source-quality strata",
            "population_n": "not yet defined",
            "proposed_sample_n": "not yet defined",
            "inclusion_probability": "must be recorded",
            "selection_rule": "Freeze four-category predictions and probabilities before human coding, then sample with known probabilities.",
            "human_work": "Independent blinded labels by two humans for the sampled cases, followed by logged adjudication.",
            "identified_quantity_after_completion": "Four-category confusion, category-specific error, and calibration for a genuinely multiclass model.",
            "review_gate": "Requires an approved validation-design change and a multiclass prediction rule; current one-sided screen is insufficient.",
        },
    ]

    metrics: dict[str, object] = {
        "experiment_id": "EXP-20260830-002",
        "base_commit": "e178e195704fe6ad6ec353a28081e444995350e7",
        "declared_count_discrepancies": discrepancies,
        "gold": {
            "cases": len(gold),
            "label_counts": dict(sorted(gold_counts.items())),
            "codex_assisted_reviewer_rows": sum(
                "Codex-assisted" in row["human_reviewer"] for row in gold
            ),
            "independently_double_coded_cases_documented": 0,
        },
        "screening": {
            "candidate_disclosure_rows": len(candidate_rows),
            "positive_disclosure_rows": screening_counts["llm_surrogate_exit_type"],
            "no_direct_formal_event_disclosure_rows": screening_counts[
                "llm_screened_no_direct_formal_event"
            ],
            "source_missing_rows_with_blank_issuer": len(source_missing_rows),
            "named_source_available_candidate_issuers": len(candidate_by_issuer),
            "positive_issuers": status_counts["screen_positive_nominal"],
            "no_direct_formal_event_issuers": status_counts[
                "screened_no_direct_formal_event"
            ],
        },
        "overlap": {
            "selected_issuers": len(overlap_keys),
            "nominal_matches": overlap_nominal_matches,
            "codex_assisted_reviewer_rows": overlap_codex_assisted,
            "descriptive_concordance": round(overlap_match_rate, 6),
            "target_population_ppv_identified": False,
            "recall_identified": False,
            "calibration_identified": False,
            "four_category_error_identified": False,
            "sampling_error_identified": False,
        },
        "proposed_probability_design": {
            "target_named_source_available_nonoverlap_issuers": (
                positive_population + nonpositive_population
            ),
            "positive_stratum_n": positive_population,
            "positive_sample_n": positive_sample,
            "positive_inclusion_probability": round(positive_pi, 6),
            "nonpositive_stratum_n": nonpositive_population,
            "nonpositive_sample_n": nonpositive_sample,
            "nonpositive_inclusion_probability": 1.0,
            "draw_executed": False,
        },
    }

    outputs = {
        OUT_COUNTS: csv_text(
            ["object_id", "unit", "quantity", "value", "note"], counts_rows
        ),
        OUT_ESTIMANDS: csv_text(estimand_fields, estimand_rows),
        OUT_DESIGN: csv_text(design_fields, design_rows),
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

    outputs, metrics = output_texts()
    if args.check:
        mismatches = []
        for path, expected in outputs.items():
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                mismatches.append(str(path.relative_to(ROOT)))
        if mismatches:
            raise SystemExit("Output mismatch: " + ", ".join(mismatches))
        print("measurement estimand outputs are reproducible")
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        print("wrote measurement estimand audit outputs")

    print(
        "selected_overlap_concordance="
        f"{metrics['overlap']['nominal_matches']}/"
        f"{metrics['overlap']['selected_issuers']}"
    )
    print(
        "probability_design_frame="
        f"{metrics['proposed_probability_design']['target_named_source_available_nonoverlap_issuers']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
