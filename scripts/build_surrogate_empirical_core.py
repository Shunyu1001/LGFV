#!/usr/bin/env python3
"""Build issuer-level empirical inputs from gold and surrogate labels."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GOLD = ROOT / "data" / "processed" / "human_validated_labels.csv"
DEFAULT_SCREENING = ROOT / "data" / "analysis_inputs" / "llm_screening_sample_2026_07_03_expanded.csv"
DEFAULT_ISSUERS = (
    ROOT / "data" / "analysis_inputs" / "codex_surrogate_issuer_summary_2026_07_03_expanded.csv"
)
DEFAULT_DSL = ROOT / "data" / "analysis_inputs" / "dsl_surrogate_diagnostics.csv"
DEFAULT_AUGMENTED = ROOT / "data" / "analysis_inputs" / "dsl_augmented_outcome_distribution.csv"
DEFAULT_FLOW = ROOT / "data" / "analysis_inputs" / "surrogate_empirical_flow.csv"
DEFAULT_INPUT = ROOT / "data" / "analysis_inputs" / "issuer_level_surrogate_empirical_input.csv"
DEFAULT_FLOW_TEX = ROOT / "paper" / "tables" / "surrogate_empirical_flow.tex"
DEFAULT_ADJUSTED_TEX = ROOT / "paper" / "tables" / "dsl_adjusted_outcome_distribution.tex"


INPUT_FIELDS = [
    "analytic_id",
    "analytic_role",
    "issuer_name",
    "province",
    "city",
    "source_row_ids",
    "observed_or_surrogate_label",
    "label_source",
    "gold_standard_overlap",
    "gold_case_id",
    "gold_final_label",
    "surrogate_rows",
    "source_coverage_score",
    "continued_function_evidence_score",
    "confidence",
    "include_in_adjusted_descriptive_sample",
    "notes",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def is_true(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def dsl_value(rows: list[dict[str, str]], quantity: str) -> str:
    for row in rows:
        if row.get("quantity") == quantity:
            return row.get("value", "")
    return ""


def tex_escape(value: str) -> str:
    return (
        str(value)
        .replace("\\", "\\textbackslash{}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("$", "\\$")
        .replace("#", "\\#")
        .replace("_", "\\_")
        .replace("{", "\\{")
        .replace("}", "\\}")
    )


def gold_input_row(row: dict[str, str], index: int) -> dict[str, str]:
    return {
        "analytic_id": f"gold_{index:04d}",
        "analytic_role": "gold_outcome",
        "issuer_name": row.get("company_name", ""),
        "province": row.get("province", ""),
        "city": row.get("city", ""),
        "source_row_ids": row.get("case_id", ""),
        "observed_or_surrogate_label": row.get("final_label", ""),
        "label_source": "human_gold_standard",
        "gold_standard_overlap": "true",
        "gold_case_id": row.get("case_id", ""),
        "gold_final_label": row.get("final_label", ""),
        "surrogate_rows": "",
        "source_coverage_score": row.get("source_coverage_score", ""),
        "continued_function_evidence_score": "",
        "confidence": row.get("final_confidence", ""),
        "include_in_adjusted_descriptive_sample": "true",
        "notes": "Human-validated gold-standard outcome.",
    }


def surrogate_input_row(row: dict[str, str], role: str, index: int) -> dict[str, str]:
    include = "true" if role == "surrogate_auxiliary_nonoverlap" else "false"
    notes = (
        "Non-overlap issuer-level surrogate used only for validation-adjusted descriptive counts."
        if role == "surrogate_auxiliary_nonoverlap"
        else "Issuer-level surrogate that overlaps a gold-standard case; retained only as a validation check."
    )
    return {
        "analytic_id": f"{role}_{index:04d}",
        "analytic_role": role,
        "issuer_name": row.get("issuer_name", ""),
        "province": "",
        "city": "",
        "source_row_ids": row.get("source_row_ids", ""),
        "observed_or_surrogate_label": row.get("exit_type", ""),
        "label_source": "codex_surrogate",
        "gold_standard_overlap": row.get("gold_standard_overlap", ""),
        "gold_case_id": row.get("gold_case_id", ""),
        "gold_final_label": row.get("gold_final_label", ""),
        "surrogate_rows": row.get("surrogate_rows", ""),
        "source_coverage_score": row.get("max_source_coverage_score", ""),
        "continued_function_evidence_score": row.get("max_continued_function_evidence_score", ""),
        "confidence": row.get("max_confidence", ""),
        "include_in_adjusted_descriptive_sample": include,
        "notes": notes,
    }


def write_flow_tex(path: Path, flow_rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write("% Auto-generated by scripts/build_surrogate_empirical_core.py\n")
        handle.write("\\begin{table}[htbp]\n")
        handle.write("\\centering\n")
        handle.write("\\caption{From disclosure screening to issuer-level empirical inputs}\n")
        handle.write("\\label{tab:surrogate-empirical-flow}\n")
        handle.write("\\small\n")
        handle.write("\\setlength{\\tabcolsep}{4pt}\n")
        handle.write("\\begin{tabular}{@{}p{0.43\\linewidth}rp{0.36\\linewidth}@{}}\n")
        handle.write("\\toprule\n")
        handle.write("Step & Count & Role \\\\\n")
        handle.write("\\midrule\n")
        for row in flow_rows:
            handle.write(
                f"{tex_escape(row['step'])} & {tex_escape(row['count'])} & {tex_escape(row['role'])} \\\\\n"
            )
        handle.write("\\bottomrule\n")
        handle.write("\\end{tabular}\n")
        handle.write(
            "\\begin{minipage}{0.94\\linewidth}\n"
            "\\vspace{0.5em}\\footnotesize Notes: Disclosure-level rows are source packets, "
            "while issuer-level rows deduplicate repeated bond disclosures for the same issuer. "
            "Surrogate issuers that already overlap gold-standard cases are used only to estimate "
            "surrogate precision. They are not counted as additional observations in the adjusted "
            "descriptive sample.\n"
            "\\end{minipage}\n"
        )
        handle.write("\\end{table}\n")


def write_adjusted_tex(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write("% Auto-generated by scripts/build_surrogate_empirical_core.py\n")
        handle.write("\\begin{table}[htbp]\n")
        handle.write("\\centering\n")
        handle.write("\\caption{Validation-adjusted outcome distribution}\n")
        handle.write("\\label{tab:dsl-adjusted-outcomes}\n")
        handle.write("\\small\n")
        handle.write("\\setlength{\\tabcolsep}{4pt}\n")
        handle.write("\\begin{tabular}{@{}p{0.32\\linewidth}rrrp{0.16\\linewidth}@{}}\n")
        handle.write("\\toprule\n")
        handle.write("Sample & Observations & Nominal exit & Other or error & Adjustment \\\\\n")
        handle.write("\\midrule\n")
        for row in rows:
            sample = row["sample"]
            if sample == "Gold standard only":
                adjustment = "Observed"
            elif "smoothed" in sample:
                adjustment = "Jeffreys"
            else:
                adjustment = "Wilson lower"
            handle.write(
                f"{tex_escape(sample)} & {row['observations']} & {row['nominal_exit']} & "
                f"{row['institutional_change_or_error']} & {tex_escape(adjustment)} \\\\\n"
            )
        handle.write("\\bottomrule\n")
        handle.write("\\end{tabular}\n")
        handle.write(
            "\\begin{minipage}{0.94\\linewidth}\n"
            "\\vspace{0.5em}\\footnotesize Notes: The adjusted rows add only non-overlap "
            "issuer-level surrogate labels to the gold-standard sample. Because the current "
            "surrogate rule is a one-sided nominal-exit screen, non-nominal cases in this table "
            "should be interpreted as expected classification error or unobserved institutional "
            "change, not as directly labeled outcomes.\n"
            "\\end{minipage}\n"
        )
        handle.write("\\end{table}\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", type=Path, default=DEFAULT_GOLD)
    parser.add_argument("--screening", type=Path, default=DEFAULT_SCREENING)
    parser.add_argument("--issuers", type=Path, default=DEFAULT_ISSUERS)
    parser.add_argument("--dsl", type=Path, default=DEFAULT_DSL)
    parser.add_argument("--augmented", type=Path, default=DEFAULT_AUGMENTED)
    parser.add_argument("--flow", type=Path, default=DEFAULT_FLOW)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--flow-tex", type=Path, default=DEFAULT_FLOW_TEX)
    parser.add_argument("--adjusted-tex", type=Path, default=DEFAULT_ADJUSTED_TEX)
    args = parser.parse_args()

    gold = read_csv(args.gold)
    screening = read_csv(args.screening)
    issuers = read_csv(args.issuers)
    dsl = read_csv(args.dsl)
    augmented = read_csv(args.augmented)

    candidate_rows = len(screening)
    usable_screening = sum(row["usable_for_llm_screening"] == "true" for row in screening)
    outcome_rows = sum(row["usable_for_exit_type_analysis"] == "true" for row in screening)
    surrogate_disclosure_rows = sum(
        row["screening_status"] == "llm_surrogate_exit_type" for row in screening
    )
    no_formal_rows = sum(
        row["screening_status"] == "llm_screened_no_direct_formal_event" for row in screening
    )
    source_missing = sum(row["screening_status"] == "source_packet_missing" for row in screening)
    overlap = [row for row in issuers if is_true(row.get("gold_standard_overlap", ""))]
    nonoverlap = [row for row in issuers if not is_true(row.get("gold_standard_overlap", ""))]
    adjusted_rows = len(gold) + len(nonoverlap)

    flow_rows = [
        {
            "step": "Candidate disclosure rows",
            "count": str(candidate_rows),
            "role": "Initial source-packet pool",
        },
        {
            "step": "Usable LLM screening rows",
            "count": str(usable_screening),
            "role": "Rows with source text or validated status",
        },
        {
            "step": "Exit-type outcome rows",
            "count": str(outcome_rows),
            "role": "Gold labels plus disclosure-level surrogate labels",
        },
        {
            "step": "LLM surrogate disclosure labels",
            "count": str(surrogate_disclosure_rows),
            "role": "Medium-confidence nominal-exit screens",
        },
        {
            "step": "Issuer-level surrogate rows",
            "count": str(len(issuers)),
            "role": "Deduplicated auxiliary labels",
        },
        {
            "step": "Surrogate issuers overlapping gold labels",
            "count": str(len(overlap)),
            "role": "Validation checks only",
        },
        {
            "step": "Non-overlap surrogate issuers",
            "count": str(len(nonoverlap)),
            "role": "Auxiliary rows for adjusted descriptive counts",
        },
        {
            "step": "Gold plus non-overlap issuer-level sample",
            "count": str(adjusted_rows),
            "role": "Validation-adjusted descriptive sample",
        },
        {
            "step": "Screened rows without direct formal event",
            "count": str(no_formal_rows),
            "role": "Screening attrition, not exit-type outcomes",
        },
        {
            "step": "Source-packet missing rows",
            "count": str(source_missing),
            "role": "Not used",
        },
    ]
    write_csv(args.flow, flow_rows, ["step", "count", "role"])
    write_flow_tex(args.flow_tex, flow_rows)
    write_adjusted_tex(args.adjusted_tex, augmented)

    input_rows: list[dict[str, str]] = []
    for index, row in enumerate(gold, start=1):
        input_rows.append(gold_input_row(row, index))
    overlap_index = 1
    nonoverlap_index = 1
    for row in issuers:
        if is_true(row.get("gold_standard_overlap", "")):
            input_rows.append(surrogate_input_row(row, "surrogate_overlap_check", overlap_index))
            overlap_index += 1
        else:
            input_rows.append(
                surrogate_input_row(row, "surrogate_auxiliary_nonoverlap", nonoverlap_index)
            )
            nonoverlap_index += 1
    write_csv(args.input, input_rows, INPUT_FIELDS)

    print(f"candidate_rows={candidate_rows}")
    print(f"usable_screening={usable_screening}")
    print(f"outcome_rows={outcome_rows}")
    print(f"surrogate_disclosure_rows={surrogate_disclosure_rows}")
    print(f"issuer_level_surrogates={len(issuers)}")
    print(f"surrogate_overlap={len(overlap)}")
    print(f"surrogate_nonoverlap={len(nonoverlap)}")
    print(f"adjusted_issuer_sample={adjusted_rows}")
    print(f"raw_precision={dsl_value(dsl, 'raw_nominal_precision')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
