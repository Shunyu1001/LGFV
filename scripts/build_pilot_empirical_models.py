#!/usr/bin/env python3
"""Build exploratory pilot models and figures for the LGFV paper."""

from __future__ import annotations

import csv
import math
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-lgfv")

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PILOT_CASES = ROOT / "data" / "analysis_inputs" / "pilot_case_historical_capacity.csv"
LABELS = ROOT / "data" / "processed" / "human_validated_labels.csv"
OUT_MODEL_CSV = ROOT / "data" / "analysis_inputs" / "pilot_lpm_institutional_change.csv"
OUT_MODEL_TEX = ROOT / "paper" / "tables" / "pilot_lpm_institutional_change.tex"
OUT_BIN_FIG = ROOT / "paper" / "figures" / "pilot_exit_type_by_capacity_bin.png"

CAPACITY_BIN_LABELS = {
    "high": "High",
    "middle": "Middle",
    "low": "Low",
}
EXIT_LABELS = {
    "substantive_exit": "Substantive",
    "functional_transfer": "Functional transfer",
    "nominal_exit": "Nominal",
}
EXIT_COLORS = {
    "substantive_exit": "#3f5f76",
    "functional_transfer": "#9a6b3f",
    "nominal_exit": "#c8c2b8",
}


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


def normal_pvalue(z_score: float) -> float:
    return math.erfc(abs(z_score) / math.sqrt(2.0))


def stars(p_value: float) -> str:
    if p_value < 0.01:
        return "***"
    if p_value < 0.05:
        return "**"
    if p_value < 0.1:
        return "*"
    return ""


def assign_capacity_bins(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    sorted_rows = sorted(rows, key=lambda row: float(row["elite_per_1000_sqkm"]), reverse=True)
    total = len(sorted_rows)
    for rank_desc, row in enumerate(sorted_rows, start=1):
        percentile = 1.0 if total == 1 else 1.0 - ((rank_desc - 1) / (total - 1))
        if percentile >= 2 / 3:
            bin_name = "high"
        elif percentile >= 1 / 3:
            bin_name = "middle"
        else:
            bin_name = "low"
        row["historical_capacity_bin"] = bin_name
        row["capacity_rank"] = {"low": "0", "middle": "1", "high": "2"}[bin_name]
    return sorted_rows


def analysis_rows() -> list[dict[str, str]]:
    labels_by_id = {row["case_id"]: row for row in read_csv(LABELS)}
    rows = [
        row
        for row in read_csv(PILOT_CASES)
        if row["case_status"] == "human_validated"
        and row["exit_type_or_status"] in EXIT_LABELS
    ]
    rows = assign_capacity_bins(rows)
    elite_values = np.array([float(row["elite_per_1000_sqkm"]) for row in rows])
    elite_mean = float(elite_values.mean())
    elite_sd = float(elite_values.std(ddof=1))
    for row in rows:
        label = row["exit_type_or_status"]
        label_row = labels_by_id[row["case_id"]]
        row["institutional_change"] = "1" if label in {"substantive_exit", "functional_transfer"} else "0"
        row["substantive_exit"] = "1" if label == "substantive_exit" else "0"
        row["elite_z"] = f"{(float(row['elite_per_1000_sqkm']) - elite_mean) / elite_sd:.8f}"
        row["high_capacity"] = "1" if row["historical_capacity_bin"] == "high" else "0"
        row["source_coverage_score"] = label_row["source_coverage_score"]
        row["high_confidence"] = "1" if label_row["final_confidence"] == "high" else "0"
    return rows


def ols(y: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    beta = np.linalg.solve(x.T @ x, x.T @ y)
    residuals = y - x @ beta
    n, k = x.shape
    inv_xx = np.linalg.inv(x.T @ x)
    meat = np.zeros((k, k))
    for i in range(n):
        xi = x[i : i + 1].T
        meat += float(residuals[i] ** 2) * (xi @ xi.T)
    variance = (n / (n - k)) * inv_xx @ meat @ inv_xx
    se = np.sqrt(np.diag(variance))
    p_values = np.array([normal_pvalue(beta_i / se_i) for beta_i, se_i in zip(beta, se)])
    return beta, se, p_values


def model_specs(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    y = np.array([float(row["institutional_change"]) for row in rows])
    elite_z = np.array([float(row["elite_z"]) for row in rows])
    high_capacity = np.array([float(row["high_capacity"]) for row in rows])
    capacity_rank = np.array([float(row["capacity_rank"]) for row in rows])
    specs = [
        {
            "name": "Elite density",
            "variables": ["Elite density, standardized"],
            "x": np.column_stack([np.ones(len(rows)), elite_z]),
        },
        {
            "name": "High capacity",
            "variables": ["High historical-capacity bin"],
            "x": np.column_stack([np.ones(len(rows)), high_capacity]),
        },
        {
            "name": "Capacity rank",
            "variables": ["Capacity bin rank"],
            "x": np.column_stack([np.ones(len(rows)), capacity_rank]),
        },
    ]

    output = []
    for spec in specs:
        beta, se, p_values = ols(y, spec["x"])
        output.append(
            {
                **spec,
                "beta": beta,
                "se": se,
                "p_values": p_values,
                "n": len(rows),
                "dep_mean": float(y.mean()),
            }
        )
    return output


def write_model_outputs(specs: list[dict[str, object]]) -> None:
    rows: list[dict[str, str]] = []
    for spec in specs:
        variables = ["Intercept", *spec["variables"]]
        for variable, beta, se, p_value in zip(
            variables, spec["beta"], spec["se"], spec["p_values"]
        ):
            rows.append(
                {
                    "model": str(spec["name"]),
                    "variable": str(variable),
                    "coefficient": f"{float(beta):.3f}",
                    "robust_se": f"{float(se):.3f}",
                    "p_value": f"{float(p_value):.3f}",
                    "n": str(spec["n"]),
                    "dependent_mean": f"{float(spec['dep_mean']):.3f}",
                }
            )
    write_csv(
        OUT_MODEL_CSV,
        ["model", "variable", "coefficient", "robust_se", "p_value", "n", "dependent_mean"],
        rows,
    )

    variable_order = [
        "Elite density, standardized",
        "High historical-capacity bin",
        "Capacity bin rank",
        "Intercept",
    ]
    spec_by_name = {str(spec["name"]): spec for spec in specs}
    OUT_MODEL_TEX.parent.mkdir(parents=True, exist_ok=True)
    with OUT_MODEL_TEX.open("w", encoding="utf-8") as handle:
        handle.write("% Auto-generated by scripts/build_pilot_empirical_models.py\n")
        handle.write("\\begin{table}[htbp]\n")
        handle.write("\\centering\n")
        handle.write("\\caption{Exploratory pilot association between historical capacity and institutional change}\n")
        handle.write("\\label{tab:pilot-lpm-institutional-change}\n")
        handle.write("\\small\n")
        handle.write("\\setlength{\\tabcolsep}{4pt}\n")
        handle.write("\\begin{tabular}{@{}lccc@{}}\n")
        handle.write("\\toprule\n")
        handle.write(" & (1) & (2) & (3) \\\\\n")
        handle.write(" & Institutional change & Institutional change & Institutional change \\\\\n")
        handle.write("\\midrule\n")
        for variable in variable_order:
            coef_cells = []
            se_cells = []
            for spec in specs:
                variables = ["Intercept", *spec["variables"]]
                if variable in variables:
                    idx = variables.index(variable)
                    beta = float(spec["beta"][idx])
                    se = float(spec["se"][idx])
                    p_value = float(spec["p_values"][idx])
                    coef_cells.append(f"{beta:.3f}{stars(p_value)}")
                    se_cells.append(f"({se:.3f})")
                else:
                    coef_cells.append("")
                    se_cells.append("")
            handle.write(f"{tex_escape(variable)} & {' & '.join(coef_cells)} \\\\\n")
            handle.write(f" & {' & '.join(se_cells)} \\\\\n")
        handle.write("\\midrule\n")
        handle.write(f"Observations & {specs[0]['n']} & {specs[1]['n']} & {specs[2]['n']} \\\\\n")
        handle.write(
            f"Mean of dependent variable & {float(specs[0]['dep_mean']):.3f} & "
            f"{float(specs[1]['dep_mean']):.3f} & {float(specs[2]['dep_mean']):.3f} \\\\\n"
        )
        handle.write("\\bottomrule\n")
        handle.write("\\end{tabular}\n")
        handle.write(
            "\\begin{minipage}{0.94\\linewidth}\n"
            "\\vspace{0.5em}\\footnotesize Notes: The dependent variable equals one for "
            "substantive exit or functional transfer and zero for nominal exit. "
            "The table uses the sixty human-validated cases currently matched to "
            "the CBDB-GADM historical-capacity measure. Coefficients are linear "
            "probability models with HC1 robust standard errors in parentheses. "
            "These estimates are exploratory pilot associations rather than "
            "population or causal estimates. $^{*}p<0.10$, $^{**}p<0.05$, "
            "$^{***}p<0.01$.\n"
            "\\end{minipage}\n"
        )
        handle.write("\\end{table}\n")


def write_capacity_bin_figure(rows: list[dict[str, str]]) -> None:
    bin_order = ["low", "middle", "high"]
    exit_order = ["nominal_exit", "functional_transfer", "substantive_exit"]
    counts = {bin_name: {label: 0 for label in exit_order} for bin_name in bin_order}
    for row in rows:
        counts[row["historical_capacity_bin"]][row["exit_type_or_status"]] += 1

    fig, ax = plt.subplots(figsize=(6.8, 3.8))
    x = np.arange(len(bin_order))
    bottom = np.zeros(len(bin_order))
    for label in exit_order:
        values = np.array([counts[bin_name][label] for bin_name in bin_order], dtype=float)
        totals = np.array([sum(counts[bin_name].values()) for bin_name in bin_order], dtype=float)
        shares = np.divide(values, totals, out=np.zeros_like(values), where=totals != 0)
        ax.bar(
            x,
            shares,
            bottom=bottom,
            label=EXIT_LABELS[label],
            color=EXIT_COLORS[label],
            edgecolor="white",
            linewidth=0.8,
        )
        for idx, share in enumerate(shares):
            if share > 0.08:
                ax.text(
                    idx,
                    bottom[idx] + share / 2,
                    str(int(values[idx])),
                    ha="center",
                    va="center",
                    fontsize=9,
                    color="white" if label != "nominal_exit" else "#333333",
                )
        bottom += shares

    ax.set_xticks(x)
    ax.set_xticklabels([CAPACITY_BIN_LABELS[bin_name] for bin_name in bin_order])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Share of matched validated cases")
    ax.set_xlabel("Historical-capacity bin")
    ax.set_title("Exit type by historical-capacity bin")
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.02, 1.0))
    ax.grid(axis="y", color="#dddddd", linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    OUT_BIN_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_BIN_FIG, dpi=220)
    plt.close(fig)


def main() -> int:
    rows = analysis_rows()
    specs = model_specs(rows)
    write_model_outputs(specs)
    write_capacity_bin_figure(rows)
    print(f"rows={len(rows)}")
    print(f"model_csv={OUT_MODEL_CSV}")
    print(f"model_tex={OUT_MODEL_TEX}")
    print(f"capacity_bin_figure={OUT_BIN_FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
