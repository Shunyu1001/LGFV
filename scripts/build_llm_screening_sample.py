#!/usr/bin/env python3
"""Build a full LLM screening sample from gold and surrogate labels.

This file separates two concepts:

1. Exit-type labels, which require a codable formal event.
2. LLM screening outcomes, which can also record that a source packet was
   reviewed but no direct formal exit or compliance event was found.

The second object is the 200+ usable LLM-coded sample used to document source
coverage, screening attrition, and measurement-error adjustment.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "analysis_inputs" / "codex_surrogate_labels_2026_07_02.csv"
DEFAULT_OUTPUT = ROOT / "data" / "analysis_inputs" / f"llm_screening_sample_{date.today():%Y_%m_%d}.csv"
DEFAULT_SUMMARY = ROOT / "data" / "analysis_inputs" / f"llm_screening_summary_{date.today():%Y_%m_%d}.csv"
DEFAULT_TEX = ROOT / "paper" / "tables" / "llm_screening_status.tex"


FIELDS = [
    "pool_id",
    "source_row_id",
    "province",
    "city",
    "issuer_name",
    "label_source",
    "surrogate_status",
    "screening_status",
    "screening_label",
    "exit_type",
    "confidence",
    "source_coverage_score",
    "continued_function_evidence_score",
    "usable_for_llm_screening",
    "usable_for_exit_type_analysis",
    "usable_for_validation_adjustment",
    "formal_event_found",
    "continued_function_found",
    "missing_information",
    "evidence_basis",
    "needs_human_review",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def numeric(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def is_true(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def classify(row: dict[str, str]) -> dict[str, str]:
    label_source = row.get("label_source", "")
    surrogate_status = row.get("surrogate_status", "")
    exit_type = row.get("exit_type", "")
    source_coverage = numeric(row.get("source_coverage_score", "0"))
    evidence_basis = row.get("evidence_basis", "").strip()

    usable_screening = True
    usable_exit_type = False
    usable_adjustment = False

    if label_source == "human_gold_standard":
        screening_status = "gold_standard_exit_type"
        screening_label = exit_type
        usable_exit_type = True
        usable_adjustment = True
    elif label_source == "human_reviewed_boundary":
        screening_status = "human_reviewed_boundary"
        screening_label = "boundary_outside_core_frame"
        usable_adjustment = True
    elif label_source == "codex_surrogate" and surrogate_status == "labeled":
        screening_status = "llm_surrogate_exit_type"
        screening_label = exit_type
        usable_exit_type = True
        usable_adjustment = True
    elif label_source == "codex_surrogate" and surrogate_status == "unresolved" and source_coverage > 0:
        screening_status = "llm_screened_no_direct_formal_event"
        screening_label = "no_direct_formal_event_observed"
        usable_adjustment = True
    elif label_source == "codex_surrogate" and surrogate_status == "unresolved" and evidence_basis:
        screening_status = "llm_screened_no_direct_formal_event"
        screening_label = "no_direct_formal_event_observed"
        usable_adjustment = True
    else:
        screening_status = "source_packet_missing"
        screening_label = "source_missing"
        usable_screening = False

    return {
        "pool_id": row.get("pool_id", ""),
        "source_row_id": row.get("source_row_id", ""),
        "province": row.get("province", ""),
        "city": row.get("city", ""),
        "issuer_name": row.get("issuer_name", ""),
        "label_source": label_source,
        "surrogate_status": surrogate_status,
        "screening_status": screening_status,
        "screening_label": screening_label,
        "exit_type": exit_type if usable_exit_type else "",
        "confidence": row.get("confidence", ""),
        "source_coverage_score": row.get("source_coverage_score", ""),
        "continued_function_evidence_score": row.get("continued_function_evidence_score", ""),
        "usable_for_llm_screening": str(usable_screening).lower(),
        "usable_for_exit_type_analysis": str(usable_exit_type).lower(),
        "usable_for_validation_adjustment": str(usable_adjustment).lower(),
        "formal_event_found": row.get("formal_event_found", ""),
        "continued_function_found": row.get("continued_function_found", ""),
        "missing_information": row.get("missing_information", ""),
        "evidence_basis": row.get("evidence_basis", ""),
        "needs_human_review": row.get("needs_human_review", ""),
    }


def tex_escape(value: str) -> str:
    return (
        value.replace("\\", "\\textbackslash{}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("$", "\\$")
        .replace("#", "\\#")
        .replace("_", "\\_")
        .replace("{", "\\{")
        .replace("}", "\\}")
    )


def main() -> int:
    rows = [classify(row) for row in read_csv(DEFAULT_INPUT)]
    write_csv(DEFAULT_OUTPUT, FIELDS, rows)

    total = len(rows)
    usable_screening = sum(1 for row in rows if is_true(row["usable_for_llm_screening"]))
    usable_exit_type = sum(1 for row in rows if is_true(row["usable_for_exit_type_analysis"]))
    usable_adjustment = sum(1 for row in rows if is_true(row["usable_for_validation_adjustment"]))
    status_counts = Counter(row["screening_status"] for row in rows)
    label_counts = Counter(row["screening_label"] for row in rows)

    summary_rows = [
        {"quantity": "candidate_pool_rows", "value": str(total)},
        {"quantity": "usable_llm_screening_rows", "value": str(usable_screening)},
        {"quantity": "usable_exit_type_rows", "value": str(usable_exit_type)},
        {"quantity": "usable_validation_adjustment_rows", "value": str(usable_adjustment)},
    ]
    for status, count in sorted(status_counts.items()):
        summary_rows.append({"quantity": f"screening_status:{status}", "value": str(count)})
    for label, count in sorted(label_counts.items()):
        summary_rows.append({"quantity": f"screening_label:{label}", "value": str(count)})
    write_csv(DEFAULT_SUMMARY, ["quantity", "value"], summary_rows)

    DEFAULT_TEX.parent.mkdir(parents=True, exist_ok=True)
    with DEFAULT_TEX.open("w", encoding="utf-8") as handle:
        handle.write("% Auto-generated by scripts/build_llm_screening_sample.py\n")
        handle.write("\\begin{table}[htbp]\n")
        handle.write("\\centering\n")
        handle.write("\\caption{LLM screening status for the candidate pool}\n")
        handle.write("\\label{tab:llm-screening-status}\n")
        handle.write("\\small\n")
        handle.write("\\begin{tabular}{@{}lrr@{}}\n")
        handle.write("\\toprule\n")
        handle.write("Screening status & Rows & Use \\\\\n")
        handle.write("\\midrule\n")
        rows_for_table = [
            ("Gold-standard exit type", status_counts["gold_standard_exit_type"], "Gold outcome"),
            ("LLM surrogate exit type", status_counts["llm_surrogate_exit_type"], "Surrogate outcome"),
            (
                "LLM screened, no direct formal event",
                status_counts["llm_screened_no_direct_formal_event"],
                "Screened non-outcome",
            ),
            ("Human-reviewed boundary", status_counts["human_reviewed_boundary"], "Scope condition"),
            ("Source packet missing", status_counts["source_packet_missing"], "Not usable"),
        ]
        for label, count, use in rows_for_table:
            handle.write(f"{tex_escape(label)} & {count} & {tex_escape(use)} \\\\\n")
        handle.write("\\midrule\n")
        handle.write(f"Usable LLM screening rows & {usable_screening} & Screening sample \\\\\n")
        handle.write(f"Usable exit-type rows & {usable_exit_type} & Outcome sample \\\\\n")
        handle.write("\\bottomrule\n")
        handle.write("\\end{tabular}\n")
        handle.write(
            "\\begin{minipage}{0.94\\linewidth}\n"
            "\\vspace{0.5em}\\footnotesize Notes: A usable LLM screening row has either a "
            "gold-standard label, an LLM surrogate exit-type label, a human-reviewed boundary "
            "decision, or source text that was screened and found to lack a direct formal "
            "exit or compliance event. The exit-type outcome sample is narrower because "
            "rows without a codable formal event are not assigned substantive, nominal, "
            "functional-transfer, or liquidation labels.\n"
            "\\end{minipage}\n"
        )
        handle.write("\\end{table}\n")

    print(f"candidate_pool_rows={total}")
    print(f"usable_llm_screening_rows={usable_screening}")
    print(f"usable_exit_type_rows={usable_exit_type}")
    print(f"source_packet_missing={status_counts['source_packet_missing']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
