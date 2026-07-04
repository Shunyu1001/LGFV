#!/usr/bin/env python3
"""Build controlled empirical models from the current case panel.

The full contemporary-control model should only be estimated after the
city-level fiscal, debt, and land-finance fields are source-backed. Until then,
this script estimates the strongest available-controls specification and
writes diagnostics that make the remaining data gap explicit.
"""

from __future__ import annotations

import csv
import math
from collections import Counter
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "data" / "analysis_inputs" / "empirical_case_panel.csv"
OUT_CSV = ROOT / "data" / "analysis_inputs" / "controlled_lpm_institutional_change.csv"
OUT_TEX = ROOT / "paper" / "tables" / "controlled_lpm_institutional_change.tex"
DIAG_CSV = ROOT / "data" / "analysis_inputs" / "full_controls_model_diagnostics.csv"
DIAG_TEX = ROOT / "paper" / "tables" / "full_controls_model_diagnostics.tex"


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


def nonempty(value: str | None) -> bool:
    return bool(value and value.strip())


def as_float(value: str) -> float:
    return float(value.strip())


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


def display_status(status: str) -> str:
    return {
        "available": "available",
        "partial": "partial",
        "not_collected": "not collected",
        "provisional_pending_human_audit": "provisional audit",
    }.get(status, status.replace("_", " "))


def standardize(values: list[float]) -> list[float]:
    arr = np.array(values, dtype=float)
    sd = float(arr.std(ddof=1))
    if sd == 0:
        return [0.0 for _ in values]
    mean = float(arr.mean())
    return [float((value - mean) / sd) for value in arr]


def dummy_from_text(value: str, needles: set[str]) -> float:
    text = value.lower()
    return 1.0 if any(needle in text for needle in needles) else 0.0


def current_model_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row.get("include_in_current_validated_model_sample") == "1"
        and nonempty(row.get("institutional_change"))
        and nonempty(row.get("elite_per_1000_sqkm"))
    ]


def add_model_variables(rows: list[dict[str, str]]) -> None:
    elite_z = standardize([as_float(row["elite_per_1000_sqkm"]) for row in rows])
    source_z = standardize([as_float(row["source_coverage_score"] or "0") for row in rows])
    for row, elite_value, source_value in zip(rows, elite_z, source_z):
        level = row.get("platform_administrative_level", "")
        row["_elite_density_z"] = elite_value
        row["_source_coverage_z"] = source_value
        row["_capital_or_subprovincial"] = float(row.get("capital_or_subprovincial_city") == "1")
        row["_platform_level_known"] = float(nonempty(level))
        row["_district_platform"] = dummy_from_text(
            level, {"district", "county", "development_zone", "park"}
        )
        row["_prefecture_platform"] = dummy_from_text(
            level, {"prefecture", "municipal", "city_level"}
        )


def province_fe_columns(rows: list[dict[str, str]], min_count: int = 3) -> list[str]:
    counts = Counter(row["province_fixed_effect"] for row in rows if nonempty(row["province_fixed_effect"]))
    provinces = sorted(province for province, count in counts.items() if count >= min_count)
    if len(provinces) <= 1:
        return []
    return provinces[1:]


def design_matrix(rows: list[dict[str, str]], variables: list[str], fe_provinces: list[str]) -> np.ndarray:
    columns = [np.ones(len(rows))]
    for variable in variables:
        columns.append(np.array([float(row[variable]) for row in rows], dtype=float))
    for province in fe_provinces:
        columns.append(
            np.array([float(row["province_fixed_effect"] == province) for row in rows], dtype=float)
        )
    return np.column_stack(columns)


def ols_hc1(y: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    beta = np.linalg.pinv(x.T @ x) @ (x.T @ y)
    residuals = y - x @ beta
    n, k = x.shape
    inv_xx = np.linalg.pinv(x.T @ x)
    meat = np.zeros((k, k))
    for i in range(n):
        xi = x[i : i + 1].T
        meat += float(residuals[i] ** 2) * (xi @ xi.T)
    scale = n / max(n - k, 1)
    variance = scale * inv_xx @ meat @ inv_xx
    se = np.sqrt(np.maximum(np.diag(variance), 0.0))
    p_values = []
    for beta_i, se_i in zip(beta, se):
        p_values.append(1.0 if se_i == 0 else normal_pvalue(float(beta_i / se_i)))
    return beta, se, np.array(p_values)


def model_specs(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    y = np.array([float(row["institutional_change"]) for row in rows], dtype=float)
    fe_provinces = province_fe_columns(rows)
    specs = [
        {
            "name": "Historical capacity",
            "variables": ["_elite_density_z"],
            "variable_labels": ["Elite density, standardized"],
            "province_fe": [],
            "controls": "No",
        },
        {
            "name": "Measurement controls",
            "variables": [
                "_elite_density_z",
                "_source_coverage_z",
                "_capital_or_subprovincial",
            ],
            "variable_labels": [
                "Elite density, standardized",
                "Source coverage score, standardized",
                "Capital or sub-provincial city",
            ],
            "province_fe": [],
            "controls": "Source coverage; capital/sub-provincial",
        },
        {
            "name": "Platform controls",
            "variables": [
                "_elite_density_z",
                "_source_coverage_z",
                "_capital_or_subprovincial",
                "_district_platform",
                "_prefecture_platform",
            ],
            "variable_labels": [
                "Elite density, standardized",
                "Source coverage score, standardized",
                "Capital or sub-provincial city",
                "District/county platform",
                "Prefecture/municipal platform",
            ],
            "province_fe": [],
            "controls": "Source coverage; capital/sub-provincial; platform hierarchy",
        },
        {
            "name": "Province FE",
            "variables": [
                "_elite_density_z",
                "_source_coverage_z",
                "_capital_or_subprovincial",
                "_district_platform",
                "_prefecture_platform",
            ],
            "variable_labels": [
                "Elite density, standardized",
                "Source coverage score, standardized",
                "Capital or sub-provincial city",
                "District/county platform",
                "Prefecture/municipal platform",
            ],
            "province_fe": fe_provinces,
            "controls": "Available controls plus province fixed effects",
        },
    ]
    output = []
    for spec in specs:
        x = design_matrix(rows, spec["variables"], spec["province_fe"])
        beta, se, p_values = ols_hc1(y, x)
        output.append(
            {
                **spec,
                "beta": beta,
                "se": se,
                "p_values": p_values,
                "n": len(rows),
                "dep_mean": float(y.mean()),
                "fe_count": len(spec["province_fe"]),
            }
        )
    return output


def write_model_outputs(specs: list[dict[str, object]]) -> None:
    rows: list[dict[str, str]] = []
    for spec in specs:
        variables = ["Intercept", *spec["variable_labels"]]
        for variable, beta, se, p_value in zip(
            variables, spec["beta"][: len(variables)], spec["se"][: len(variables)], spec["p_values"][: len(variables)]
        ):
            rows.append(
                {
                    "model": str(spec["name"]),
                    "variable": str(variable),
                    "coefficient": f"{float(beta):.4f}",
                    "robust_se": f"{float(se):.4f}",
                    "p_value": f"{float(p_value):.4f}",
                    "n": str(spec["n"]),
                    "dependent_mean": f"{float(spec['dep_mean']):.4f}",
                    "controls": str(spec["controls"]),
                    "province_fe_count": str(spec["fe_count"]),
                }
            )
    write_csv(
        OUT_CSV,
        [
            "model",
            "variable",
            "coefficient",
            "robust_se",
            "p_value",
            "n",
            "dependent_mean",
            "controls",
            "province_fe_count",
        ],
        rows,
    )

    variable_order = [
        "Elite density, standardized",
        "Source coverage score, standardized",
        "Capital or sub-provincial city",
        "District/county platform",
        "Prefecture/municipal platform",
        "Intercept",
    ]
    OUT_TEX.parent.mkdir(parents=True, exist_ok=True)
    with OUT_TEX.open("w", encoding="utf-8") as handle:
        handle.write("% Auto-generated by scripts/build_controlled_empirical_models.py\n")
        handle.write("\\begin{table}[htbp]\n")
        handle.write("\\centering\n")
        handle.write("\\caption{Available-controls models of institutional change}\n")
        handle.write("\\label{tab:controlled-lpm-institutional-change}\n")
        handle.write("\\scriptsize\n")
        handle.write("\\setlength{\\tabcolsep}{4pt}\n")
        handle.write("\\begin{tabular}{@{}lcccc@{}}\n")
        handle.write("\\toprule\n")
        handle.write(" & (1) & (2) & (3) & (4) \\\\\n")
        handle.write(" & Base & Quality & Platform & Province FE \\\\\n")
        handle.write("\\midrule\n")
        for variable in variable_order:
            coef_cells: list[str] = []
            se_cells: list[str] = []
            for spec in specs:
                variables = ["Intercept", *spec["variable_labels"]]
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
        handle.write(
            f"Observations & {specs[0]['n']} & {specs[1]['n']} & {specs[2]['n']} & {specs[3]['n']} \\\\\n"
        )
        handle.write(
            f"Mean of dependent variable & {float(specs[0]['dep_mean']):.3f} & "
            f"{float(specs[1]['dep_mean']):.3f} & {float(specs[2]['dep_mean']):.3f} & "
            f"{float(specs[3]['dep_mean']):.3f} \\\\\n"
        )
        handle.write("Province fixed effects & No & No & No & Yes \\\\\n")
        handle.write("\\bottomrule\n")
        handle.write("\\end{tabular}\n")
        handle.write("\\begin{minipage}{0.95\\linewidth}\n")
        handle.write(
            "\\vspace{0.5em}\\footnotesize Notes: The dependent variable equals one for "
            "substantive exit or functional transfer and zero for nominal exit. "
            "All models use the human-validated rows currently matched to the "
            "historical-capacity measure. Source coverage is a measurement-quality "
            "control; platform hierarchy is rule-based and remains pending human "
            "audit. Province fixed effects are included for provinces with at least "
            "three observations. Coefficients are linear probability models with "
            "HC1 robust standard errors in parentheses. $^{*}p<0.10$, "
            "$^{**}p<0.05$, $^{***}p<0.01$.\n"
        )
        handle.write("\\end{minipage}\n")
        handle.write("\\end{table}\n")


def diagnostics(rows: list[dict[str, str]], model_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    checks = [
        (
            "GDP per capita",
            "gdp_per_capita_value",
            "Contemporary economic capacity",
            "Needed for the full alternative-explanations model.",
        ),
        (
            "Fiscal self-sufficiency",
            "fiscal_self_sufficiency_value",
            "Contemporary fiscal capacity",
            "Needed to distinguish historical capacity from present fiscal strength.",
        ),
        (
            "Local debt pressure",
            "debt_pressure_value",
            "Contemporary fiscal stress",
            "Needed to test whether exit type reflects debt pressure rather than capacity.",
        ),
        (
            "Land finance dependence",
            "land_finance_dependence_value",
            "Land-finance alternative explanation",
            "Needed to test whether platform persistence follows land-development dependence.",
        ),
        (
            "Platform administrative level",
            "platform_administrative_level",
            "Issuer hierarchy control",
            "Usable as a provisional control after human audit of rule-based pre-codes.",
        ),
        (
            "Capital/sub-provincial status",
            "capital_or_subprovincial_city",
            "Administrative-rank control",
            "Already usable in the available-controls model.",
        ),
        (
            "Province fixed effects",
            "province_fixed_effect",
            "Province-level policy environment",
            "Already usable where provinces have repeated observations.",
        ),
        (
            "Source/bond disclosure quality",
            "source_coverage_score",
            "Measurement-quality control",
            "Already usable in the available-controls model.",
        ),
    ]
    diag_rows: list[dict[str, str]] = []
    for component, field, role, implication in checks:
        available = sum(1 for row in model_rows if nonempty(row.get(field)))
        status = "available" if available == len(model_rows) else "partial" if available else "not_collected"
        if component == "Platform administrative level" and available:
            status = "provisional_pending_human_audit"
        diag_rows.append(
            {
                "component": component,
                "available_in_current_model_rows": str(available),
                "current_model_rows": str(len(model_rows)),
                "available_in_full_panel": str(sum(1 for row in rows if nonempty(row.get(field)))),
                "full_panel_rows": str(len(rows)),
                "status": status,
                "role": role,
                "implication": implication,
            }
        )
    return diag_rows


def write_diagnostics_outputs(rows: list[dict[str, str]]) -> None:
    write_csv(
        DIAG_CSV,
        [
            "component",
            "available_in_current_model_rows",
            "current_model_rows",
            "available_in_full_panel",
            "full_panel_rows",
            "status",
            "role",
            "implication",
        ],
        rows,
    )
    DIAG_TEX.parent.mkdir(parents=True, exist_ok=True)
    with DIAG_TEX.open("w", encoding="utf-8") as handle:
        handle.write("% Auto-generated by scripts/build_controlled_empirical_models.py\n")
        handle.write("\\begin{table}[htbp]\n")
        handle.write("\\centering\n")
        handle.write("\\caption{Readiness of contemporary controls for the full model}\n")
        handle.write("\\label{tab:full-controls-model-diagnostics}\n")
        handle.write("\\small\n")
        handle.write("\\setlength{\\tabcolsep}{4pt}\n")
        handle.write("\\begin{tabular}{@{}p{0.28\\linewidth}rrp{0.25\\linewidth}@{}}\n")
        handle.write("\\toprule\n")
        handle.write("Control & Available & Model rows & Status \\\\\n")
        handle.write("\\midrule\n")
        for row in rows:
            handle.write(
                f"{tex_escape(row['component'])} & "
                f"{row['available_in_current_model_rows']} & "
                f"{row['current_model_rows']} & "
                f"{tex_escape(display_status(row['status']))} \\\\\n"
            )
        handle.write("\\bottomrule\n")
        handle.write("\\end{tabular}\n")
        handle.write("\\begin{minipage}{0.94\\linewidth}\n")
        handle.write(
            "\\vspace{0.5em}\\footnotesize Notes: Model rows are the human-validated "
            "cases currently matched to the historical-capacity measure. The table "
            "distinguishes controls that can be used now from contemporary fiscal, "
            "debt, and land-finance controls that still require source-backed city "
            "collection. Missing contemporary controls are not imputed.\n"
        )
        handle.write("\\end{minipage}\n")
        handle.write("\\end{table}\n")


def main() -> None:
    rows = read_csv(PANEL)
    model_rows = current_model_rows(rows)
    if not model_rows:
        raise SystemExit("No current validated model rows found.")
    add_model_variables(model_rows)
    specs = model_specs(model_rows)
    write_model_outputs(specs)
    diag_rows = diagnostics(rows, model_rows)
    write_diagnostics_outputs(diag_rows)
    print(f"Wrote {OUT_CSV.relative_to(ROOT)}")
    print(f"Wrote {OUT_TEX.relative_to(ROOT)}")
    print(f"Wrote {DIAG_CSV.relative_to(ROOT)}")
    print(f"Wrote {DIAG_TEX.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
