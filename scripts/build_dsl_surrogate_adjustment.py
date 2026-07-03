#!/usr/bin/env python3
"""Build first-pass DSL-style surrogate-label diagnostics.

The current Codex pass is intentionally conservative: it creates a surrogate
label only when a source packet contains both formal no-government-financing
language and evidence of continued public functions. At this stage the useful
estimand is therefore the precision of a surrogate nominal-exit label, not a
full multiclass classifier.
"""

from __future__ import annotations

import csv
import argparse
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HUMAN_LABELS = ROOT / "data" / "processed" / "human_validated_labels.csv"
SURROGATE_ISSUERS = (
    ROOT / "data" / "analysis_inputs" / "codex_surrogate_issuer_summary_2026_07_02.csv"
)
OUT_DIAGNOSTICS = ROOT / "data" / "analysis_inputs" / "dsl_surrogate_diagnostics.csv"
OUT_AUGMENTED = ROOT / "data" / "analysis_inputs" / "dsl_augmented_outcome_distribution.csv"
OUT_TEX = ROOT / "paper" / "tables" / "dsl_surrogate_validation.tex"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


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


def is_true(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def wilson_lower_bound(successes: int, trials: int, z: float = 1.96) -> float:
    if trials == 0:
        return 0.0
    phat = successes / trials
    denom = 1 + (z * z / trials)
    center = phat + (z * z / (2 * trials))
    spread = z * math.sqrt((phat * (1 - phat) / trials) + (z * z / (4 * trials * trials)))
    return max(0.0, (center - spread) / denom)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--human", type=Path, default=HUMAN_LABELS)
    parser.add_argument("--issuers", type=Path, default=SURROGATE_ISSUERS)
    parser.add_argument("--diagnostics", type=Path, default=OUT_DIAGNOSTICS)
    parser.add_argument("--augmented", type=Path, default=OUT_AUGMENTED)
    parser.add_argument("--tex", type=Path, default=OUT_TEX)
    args = parser.parse_args()

    human = read_csv(args.human)
    issuers = read_csv(args.issuers)

    human_counts: dict[str, int] = {}
    for row in human:
        label = row["final_label"]
        human_counts[label] = human_counts.get(label, 0) + 1

    institutional_change = human_counts.get("substantive_exit", 0) + human_counts.get(
        "functional_transfer", 0
    )
    nominal_gold = human_counts.get("nominal_exit", 0)

    overlap_rows = [row for row in issuers if is_true(row.get("gold_standard_overlap", ""))]
    nonoverlap_rows = [row for row in issuers if not is_true(row.get("gold_standard_overlap", ""))]
    validated_nominal = [
        row
        for row in overlap_rows
        if row.get("exit_type") == "nominal_exit" and row.get("gold_final_label") == "nominal_exit"
    ]

    validation_trials = len(overlap_rows)
    validation_successes = len(validated_nominal)
    raw_precision = validation_successes / validation_trials if validation_trials else 0.0
    # Jeffreys smoothing avoids treating a finite validation sample as literal certainty.
    smoothed_precision = (validation_successes + 0.5) / (validation_trials + 1.0)
    wilson_lower = wilson_lower_bound(validation_successes, validation_trials)
    nonoverlap_issuers = len(nonoverlap_rows)

    expected_nominal_surrogate = smoothed_precision * nonoverlap_issuers
    expected_error_surrogate = (1 - smoothed_precision) * nonoverlap_issuers
    conservative_nominal_surrogate = wilson_lower * nonoverlap_issuers
    conservative_error_surrogate = (1 - wilson_lower) * nonoverlap_issuers

    diagnostics = [
        {
            "quantity": "human_gold_labels",
            "value": str(len(human)),
            "description": "Human-validated gold-standard labels.",
        },
        {
            "quantity": "human_gold_nominal_exit",
            "value": str(nominal_gold),
            "description": "Gold-standard nominal-exit labels.",
        },
        {
            "quantity": "human_gold_institutional_change",
            "value": str(institutional_change),
            "description": "Gold-standard substantive-exit plus functional-transfer labels.",
        },
        {
            "quantity": "surrogate_unique_issuers",
            "value": str(len(issuers)),
            "description": "Issuer-level Codex surrogate nominal-exit rows after deduplication.",
        },
        {
            "quantity": "surrogate_gold_overlap_issuers",
            "value": str(validation_trials),
            "description": "Surrogate issuers already matched to gold-standard validated cases.",
        },
        {
            "quantity": "surrogate_overlap_nominal_matches",
            "value": str(validation_successes),
            "description": "Overlap issuers where surrogate nominal exit matches the gold label.",
        },
        {
            "quantity": "raw_nominal_precision",
            "value": f"{raw_precision:.3f}",
            "description": "Unsmoothed positive predictive value for surrogate nominal-exit labels.",
        },
        {
            "quantity": "jeffreys_smoothed_nominal_precision",
            "value": f"{smoothed_precision:.3f}",
            "description": "Jeffreys-smoothed precision used for validation-adjusted descriptive counts.",
        },
        {
            "quantity": "wilson_95_lower_nominal_precision",
            "value": f"{wilson_lower:.3f}",
            "description": "Conservative 95 percent Wilson lower bound for nominal-exit precision.",
        },
        {
            "quantity": "nonoverlap_surrogate_issuers",
            "value": str(nonoverlap_issuers),
            "description": "Surrogate issuers not yet in the gold-standard file.",
        },
    ]
    write_csv(args.diagnostics, ["quantity", "value", "description"], diagnostics)

    augmented_rows = [
        {
            "sample": "Gold standard only",
            "observations": f"{len(human):.0f}",
            "nominal_exit": f"{nominal_gold:.2f}",
            "institutional_change_or_error": f"{institutional_change:.2f}",
            "nominal_share": f"{nominal_gold / len(human):.3f}",
            "note": "Observed human labels.",
        },
        {
            "sample": "Gold plus non-overlap surrogates, smoothed",
            "observations": f"{len(human) + nonoverlap_issuers:.0f}",
            "nominal_exit": f"{nominal_gold + expected_nominal_surrogate:.2f}",
            "institutional_change_or_error": f"{institutional_change + expected_error_surrogate:.2f}",
            "nominal_share": f"{(nominal_gold + expected_nominal_surrogate) / (len(human) + nonoverlap_issuers):.3f}",
            "note": "Uses Jeffreys-smoothed surrogate nominal precision.",
        },
        {
            "sample": "Gold plus non-overlap surrogates, conservative",
            "observations": f"{len(human) + nonoverlap_issuers:.0f}",
            "nominal_exit": f"{nominal_gold + conservative_nominal_surrogate:.2f}",
            "institutional_change_or_error": f"{institutional_change + conservative_error_surrogate:.2f}",
            "nominal_share": f"{(nominal_gold + conservative_nominal_surrogate) / (len(human) + nonoverlap_issuers):.3f}",
            "note": "Uses Wilson 95 percent lower bound for surrogate nominal precision.",
        },
    ]
    write_csv(
        args.augmented,
        [
            "sample",
            "observations",
            "nominal_exit",
            "institutional_change_or_error",
            "nominal_share",
            "note",
        ],
        augmented_rows,
    )

    args.tex.parent.mkdir(parents=True, exist_ok=True)
    with args.tex.open("w", encoding="utf-8") as handle:
        handle.write("% Auto-generated by scripts/build_dsl_surrogate_adjustment.py\n")
        handle.write("\\begin{table}[htbp]\n")
        handle.write("\\centering\n")
        handle.write("\\caption{Surrogate-label validation and adjusted nominal-exit counts}\n")
        handle.write("\\label{tab:dsl-surrogate-validation}\n")
        handle.write("\\small\n")
        handle.write("\\setlength{\\tabcolsep}{4pt}\n")
        handle.write("\\begin{tabular}{@{}lrrr@{}}\n")
        handle.write("\\toprule\n")
        handle.write("Quantity & Count & Rate & Adjusted count \\\\\n")
        handle.write("\\midrule\n")
        handle.write(
            f"Gold-standard labels & {len(human)} &  &  \\\\\n"
            f"Gold nominal exits & {nominal_gold} & {nominal_gold / len(human):.3f} &  \\\\\n"
            f"Gold institutional change & {institutional_change} & {institutional_change / len(human):.3f} &  \\\\\n"
            f"Surrogate issuers with gold overlap & {validation_trials} &  &  \\\\\n"
            f"Nominal matches in overlap & {validation_successes} & {raw_precision:.3f} &  \\\\\n"
            f"Non-overlap surrogate issuers & {nonoverlap_issuers} &  &  \\\\\n"
            f"Smoothed expected nominal among non-overlap & {nonoverlap_issuers} & {smoothed_precision:.3f} & {expected_nominal_surrogate:.2f} \\\\\n"
            f"Conservative expected nominal among non-overlap & {nonoverlap_issuers} & {wilson_lower:.3f} & {conservative_nominal_surrogate:.2f} \\\\\n"
        )
        handle.write("\\bottomrule\n")
        handle.write("\\end{tabular}\n")
        handle.write(
            "\\begin{minipage}{0.94\\linewidth}\n"
            "\\vspace{0.5em}\\footnotesize Notes: The validation sample consists of issuer-level "
            "Codex surrogate nominal-exit labels that overlap with independently human-validated "
            "gold-standard cases. The raw precision is the share of overlap issuers for which a "
            "surrogate nominal-exit label matches the gold-standard label. The smoothed rate uses "
            "a Jeffreys correction, $(x+0.5)/(n+1)$, and the conservative rate is the Wilson "
            "95 percent lower bound. This table validates the current surrogate rule as a "
            "high-precision nominal-exit screen. It does not treat unresolved rows as negative "
            "outcomes or use raw surrogate labels as final labels.\n"
            "\\end{minipage}\n"
        )
        handle.write("\\end{table}\n")

    print(f"human_gold={len(human)}")
    print(f"validation_overlap={validation_trials}")
    print(f"raw_precision={raw_precision:.3f}")
    print(f"smoothed_precision={smoothed_precision:.3f}")
    print(f"wilson_lower={wilson_lower:.3f}")
    print(f"nonoverlap_surrogate_issuers={nonoverlap_issuers}")


if __name__ == "__main__":
    main()
