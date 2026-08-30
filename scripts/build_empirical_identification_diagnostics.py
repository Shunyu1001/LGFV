#!/usr/bin/env python3
"""Build sparse-outcome and sample-selection diagnostics for the frozen estimand."""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PANEL = ROOT / "data" / "analysis_inputs" / "empirical_case_panel.csv"
DEFAULT_OUTPUT_DIR = ROOT / "experiments" / "EXP-20260830-005" / "artifacts"
PILOT_LPM = ROOT / "data" / "analysis_inputs" / "pilot_lpm_institutional_change.csv"

CONTEMPORARY_CONTROLS = [
    ("GDP per capita", "gdp_per_capita_value"),
    ("Fiscal self-sufficiency", "fiscal_self_sufficiency_value"),
    ("Debt pressure", "debt_pressure_value"),
    ("Land-finance dependence", "land_finance_dependence_value"),
]
OTHER_CONTROLS = [
    ("Source coverage", "source_coverage_score"),
    ("Platform administrative level", "platform_administrative_level"),
    ("Capital or sub-provincial status", "capital_or_subprovincial_city"),
    ("Province identifier", "province_fixed_effect"),
]


@dataclass(frozen=True)
class ModelData:
    specification: str
    rows: list[dict[str, str]]
    y: np.ndarray
    x: np.ndarray
    variable_names: list[str]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"Refusing to write empty diagnostic file: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def nonempty(value: str | None) -> bool:
    return bool(value and value.strip())


def as_float(row: dict[str, str], field: str) -> float:
    return float(row[field].strip())


def matched_gold_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row.get("include_in_current_validated_model_sample") == "1"
        and nonempty(row.get("institutional_change"))
        and nonempty(row.get("elite_per_1000_sqkm"))
    ]


def complete_control_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    required = [
        "institutional_change",
        "elite_per_1000_sqkm",
        "gdp_per_capita_value",
        "fiscal_self_sufficiency_value",
        "debt_pressure_value",
        "land_finance_dependence_value",
    ]
    return [
        row
        for row in rows
        if row.get("include_in_full_controls_regression_sample") == "1"
        and all(nonempty(row.get(field)) for field in required)
    ]


def standardize(values: np.ndarray) -> np.ndarray:
    sd = float(values.std(ddof=1))
    if sd == 0:
        return np.zeros_like(values, dtype=float)
    return (values - float(values.mean())) / sd


def platform_dummy(value: str, needles: set[str]) -> float:
    text = value.lower()
    return float(any(needle in text for needle in needles))


def make_model(
    specification: str, rows: list[dict[str, str]], full_controls: bool
) -> ModelData:
    y = np.array([as_float(row, "institutional_change") for row in rows], dtype=float)
    elite = standardize(
        np.array([as_float(row, "elite_per_1000_sqkm") for row in rows], dtype=float)
    )
    columns = [np.ones(len(rows), dtype=float), elite]
    variable_names = ["Intercept", "Elite density, standardized"]
    if full_controls:
        continuous = [
            ("GDP per capita, standardized", "gdp_per_capita_value"),
            ("Fiscal self-sufficiency, standardized", "fiscal_self_sufficiency_value"),
            ("Debt pressure, standardized", "debt_pressure_value"),
            ("Land-finance dependence, standardized", "land_finance_dependence_value"),
            ("Source coverage, standardized", "source_coverage_score"),
        ]
        for label, field in continuous:
            values = np.array([as_float(row, field) for row in rows], dtype=float)
            columns.append(standardize(values))
            variable_names.append(label)
        columns.append(
            np.array(
                [
                    platform_dummy(
                        row.get("platform_administrative_level", ""),
                        {"district", "county", "development_zone", "park"},
                    )
                    for row in rows
                ],
                dtype=float,
            )
        )
        variable_names.append("District/county platform")
        columns.append(
            np.array(
                [
                    platform_dummy(
                        row.get("platform_administrative_level", ""),
                        {"prefecture", "municipal", "city_level"},
                    )
                    for row in rows
                ],
                dtype=float,
            )
        )
        variable_names.append("Prefecture/municipal platform")
    return ModelData(
        specification=specification,
        rows=rows,
        y=y,
        x=np.column_stack(columns),
        variable_names=variable_names,
    )


def normal_pvalue(z_score: float) -> float:
    return math.erfc(abs(z_score) / math.sqrt(2.0))


def lpm_hc1(y: np.ndarray, x: np.ndarray) -> dict[str, object]:
    beta = np.linalg.pinv(x.T @ x) @ (x.T @ y)
    residuals = y - x @ beta
    n, k = x.shape
    inverse = np.linalg.pinv(x.T @ x)
    meat = np.zeros((k, k), dtype=float)
    for index in range(n):
        xi = x[index : index + 1].T
        meat += float(residuals[index] ** 2) * (xi @ xi.T)
    variance = (n / max(n - k, 1)) * inverse @ meat @ inverse
    standard_errors = np.sqrt(np.maximum(np.diag(variance), 0.0))
    p_values = np.array(
        [
            1.0 if se == 0 else normal_pvalue(float(coefficient / se))
            for coefficient, se in zip(beta, standard_errors)
        ],
        dtype=float,
    )
    leverage = np.diag(x @ inverse @ x.T)
    mse = float(np.sum(residuals**2) / max(n - k, 1))
    cook = np.zeros(n, dtype=float)
    if mse > 0:
        denominator = np.maximum((1.0 - leverage) ** 2, 1e-12)
        cook = (residuals**2 / (k * mse)) * (leverage / denominator)
    return {
        "beta": beta,
        "standard_errors": standard_errors,
        "p_values": p_values,
        "residuals": residuals,
        "leverage": leverage,
        "cook_distance": cook,
        "converged": True,
        "iterations": 1,
    }


def sigmoid(eta: np.ndarray) -> np.ndarray:
    output = np.empty_like(eta, dtype=float)
    positive = eta >= 0
    output[positive] = 1.0 / (1.0 + np.exp(-eta[positive]))
    exp_eta = np.exp(eta[~positive])
    output[~positive] = exp_eta / (1.0 + exp_eta)
    return output


def log_likelihood(y: np.ndarray, x: np.ndarray, beta: np.ndarray) -> float:
    eta = x @ beta
    return float(np.sum(y * eta - np.logaddexp(0.0, eta)))


def log_pseudodeterminant(matrix: np.ndarray) -> float:
    eigenvalues = np.linalg.eigvalsh(matrix)
    positive = eigenvalues[eigenvalues > 1e-12]
    if len(positive) == 0:
        return float("-inf")
    return float(np.log(positive).sum())


def logistic_fit(
    y: np.ndarray,
    x: np.ndarray,
    firth: bool,
    max_iter: int = 200,
    tolerance: float = 1e-9,
) -> dict[str, object]:
    beta = np.zeros(x.shape[1], dtype=float)
    converged = False
    note = ""
    iterations = 0

    def objective(candidate: np.ndarray) -> float:
        value = log_likelihood(y, x, candidate)
        if not firth:
            return value
        probabilities = np.clip(sigmoid(x @ candidate), 1e-9, 1.0 - 1e-9)
        information = x.T @ ((probabilities * (1.0 - probabilities))[:, None] * x)
        return value + 0.5 * log_pseudodeterminant(information)

    for iteration in range(1, max_iter + 1):
        iterations = iteration
        probabilities = np.clip(sigmoid(x @ beta), 1e-9, 1.0 - 1e-9)
        weights = probabilities * (1.0 - probabilities)
        information = x.T @ (weights[:, None] * x)
        inverse = np.linalg.pinv(information)
        if firth:
            weighted_x = np.sqrt(weights)[:, None] * x
            leverage = np.sum((weighted_x @ inverse) * weighted_x, axis=1)
            score = x.T @ (y - probabilities + leverage * (0.5 - probabilities))
        else:
            score = x.T @ (y - probabilities)
        delta = inverse @ score
        current_objective = objective(beta)
        step_fraction = 1.0
        accepted = False
        while step_fraction >= 2.0**-20:
            candidate = beta + step_fraction * delta
            if objective(candidate) >= current_objective - 1e-12:
                accepted = True
                break
            step_fraction /= 2.0
        if not accepted:
            note = "line search failed"
            break
        step = step_fraction * delta
        beta = candidate
        if float(np.max(np.abs(step))) < tolerance:
            converged = True
            break

    probabilities = np.clip(sigmoid(x @ beta), 1e-9, 1.0 - 1e-9)
    weights = probabilities * (1.0 - probabilities)
    information = x.T @ (weights[:, None] * x)
    covariance = np.linalg.pinv(information)
    standard_errors = np.sqrt(np.maximum(np.diag(covariance), 0.0))
    p_values = np.array(
        [
            1.0 if se == 0 else normal_pvalue(float(coefficient / se))
            for coefficient, se in zip(beta, standard_errors)
        ],
        dtype=float,
    )
    if not converged and not note:
        note = f"maximum iterations reached ({max_iter})"
    if float(np.max(np.abs(beta))) > 25:
        note = (note + "; " if note else "") + "large coefficient indicates possible separation"
    return {
        "beta": beta,
        "standard_errors": standard_errors,
        "p_values": p_values,
        "probabilities": probabilities,
        "average_marginal_effect": float(np.mean(weights) * beta[1]),
        "converged": converged,
        "iterations": iterations,
        "note": note,
    }


def sample_outcomes(models: list[ModelData]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for model in models:
        positives = int(model.y.sum())
        substantive = sum(row.get("substantive_exit") == "1" for row in model.rows)
        functional = sum(row.get("functional_transfer") == "1" for row in model.rows)
        nominal = sum(row.get("nominal_exit") == "1" for row in model.rows)
        rows.append(
            {
                "specification": model.specification,
                "observations": len(model.rows),
                "institutional_change": positives,
                "nominal_exit": nominal,
                "substantive_exit": substantive,
                "functional_transfer": functional,
                "event_share": f"{positives / len(model.rows):.6f}",
                "parameters_including_intercept": model.x.shape[1],
                "events_per_parameter": f"{positives / model.x.shape[1]:.6f}",
            }
        )
    return rows


def missingness(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for label, field in [*CONTEMPORARY_CONTROLS, *OTHER_CONTROLS]:
        available = sum(nonempty(row.get(field)) for row in rows)
        output.append(
            {
                "control": label,
                "field": field,
                "available": available,
                "missing": len(rows) - available,
                "matched_gold_rows": len(rows),
                "missing_share": f"{(len(rows) - available) / len(rows):.6f}",
                "imputed": False,
            }
        )
    return output


def mean(values: list[float]) -> float:
    return float(np.mean(values)) if values else float("nan")


def selection_diagnostics(
    matched: list[dict[str, str]], complete: list[dict[str, str]]
) -> list[dict[str, object]]:
    complete_ids = {row["panel_id"] for row in complete}
    included = [row for row in matched if row["panel_id"] in complete_ids]
    excluded = [row for row in matched if row["panel_id"] not in complete_ids]
    elite_all = np.array([as_float(row, "elite_per_1000_sqkm") for row in matched])
    elite_mean = float(elite_all.mean())
    elite_sd = float(elite_all.std(ddof=1))

    def metric(group: list[dict[str, str]], name: str) -> float:
        if name == "observation_count":
            return float(len(group))
        if name == "institutional_change_share":
            return mean([as_float(row, "institutional_change") for row in group])
        if name == "substantive_exit_share":
            return mean([as_float(row, "substantive_exit") for row in group])
        if name == "functional_transfer_share":
            return mean([as_float(row, "functional_transfer") for row in group])
        if name == "elite_density_mean":
            return mean([as_float(row, "elite_per_1000_sqkm") for row in group])
        if name == "elite_density_z_mean":
            return mean(
                [
                    (as_float(row, "elite_per_1000_sqkm") - elite_mean) / elite_sd
                    for row in group
                ]
            )
        if name == "source_coverage_mean":
            return mean([as_float(row, "source_coverage_score") for row in group])
        if name.startswith("capacity_bin_"):
            capacity_bin = name.removeprefix("capacity_bin_")
            if capacity_bin == "missing":
                return mean(
                    [float(not nonempty(row.get("historical_capacity_bin"))) for row in group]
                )
            return mean(
                [float(row.get("historical_capacity_bin") == capacity_bin) for row in group]
            )
        raise KeyError(name)

    metric_names = [
        "observation_count",
        "institutional_change_share",
        "substantive_exit_share",
        "functional_transfer_share",
        "elite_density_mean",
        "elite_density_z_mean",
        "source_coverage_mean",
        "capacity_bin_low",
        "capacity_bin_middle",
        "capacity_bin_high",
        "capacity_bin_missing",
    ]
    output = []
    for metric_name in metric_names:
        included_value = metric(included, metric_name)
        excluded_value = metric(excluded, metric_name)
        output.append(
            {
                "metric": metric_name,
                "complete_control_subset": f"{included_value:.6f}",
                "excluded_matched_gold": f"{excluded_value:.6f}",
                "difference_complete_minus_excluded": f"{included_value - excluded_value:.6f}",
                "complete_control_n": len(included),
                "excluded_n": len(excluded),
                "interpretation": "descriptive; no selection model or significance test",
            }
        )
    return output


def excluded_case_diagnostics(
    matched: list[dict[str, str]], complete: list[dict[str, str]]
) -> list[dict[str, object]]:
    complete_ids = {row["panel_id"] for row in complete}
    output: list[dict[str, object]] = []
    for row in matched:
        if row["panel_id"] in complete_ids:
            continue
        missing_controls = [
            label
            for label, field in CONTEMPORARY_CONTROLS
            if not nonempty(row.get(field))
        ]
        output.append(
            {
                "panel_id": row.get("panel_id", ""),
                "case_id": row.get("case_id", ""),
                "province": row.get("province", ""),
                "city": row.get("city", ""),
                "exit_type": row.get("exit_type", ""),
                "institutional_change": row.get("institutional_change", ""),
                "elite_per_1000_sqkm": row.get("elite_per_1000_sqkm", ""),
                "historical_capacity_bin": row.get("historical_capacity_bin", ""),
                "source_coverage_score": row.get("source_coverage_score", ""),
                "missing_contemporary_controls": "; ".join(missing_controls),
                "exclusion_basis": "recorded complete-control flag and observed missing values",
            }
        )
    return output


def model_warning(model: ModelData, converged: bool, note: str = "") -> str:
    warnings = []
    events = int(model.y.sum())
    parameters = model.x.shape[1]
    rank = int(np.linalg.matrix_rank(model.x))
    condition_number = float(np.linalg.cond(model.x))
    if events / parameters < 5:
        warnings.append("fewer than 5 events per parameter")
    if rank < parameters:
        warnings.append("design matrix is rank deficient")
    if condition_number > 30:
        warnings.append("design-matrix condition number exceeds 30")
    if not converged:
        warnings.append("estimator did not converge")
    if note:
        warnings.append(note)
    return "; ".join(dict.fromkeys(warnings))


def functional_form_diagnostics(
    models: list[ModelData],
) -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    output: list[dict[str, object]] = []
    fitted: dict[str, dict[str, object]] = {}
    for model in models:
        lpm = lpm_hc1(model.y, model.x)
        logit = logistic_fit(model.y, model.x, firth=False)
        firth = logistic_fit(model.y, model.x, firth=True)
        fitted[model.specification] = {"lpm": lpm, "logit": logit, "firth_logit": firth}
        for method, result in [("lpm", lpm), ("logit", logit), ("firth_logit", firth)]:
            if method == "lpm":
                probability_effect = float(result["beta"][1])
                log_odds = ""
            else:
                probability_effect = float(result["average_marginal_effect"])
                log_odds = f"{float(result['beta'][1]):.8f}"
            output.append(
                {
                    "specification": model.specification,
                    "method": method,
                    "observations": len(model.rows),
                    "events": int(model.y.sum()),
                    "parameters_including_intercept": model.x.shape[1],
                    "events_per_parameter": f"{int(model.y.sum()) / model.x.shape[1]:.8f}",
                    "matrix_rank": int(np.linalg.matrix_rank(model.x)),
                    "condition_number": f"{float(np.linalg.cond(model.x)):.8f}",
                    "converged": bool(result["converged"]),
                    "iterations": int(result["iterations"]),
                    "elite_effect_probability_scale": f"{probability_effect:.8f}",
                    "elite_log_odds_coefficient": log_odds,
                    "coefficient_standard_error_diagnostic": f"{float(result['standard_errors'][1]):.8f}",
                    "coefficient_wald_p_value_diagnostic": f"{float(result['p_values'][1]):.8f}",
                    "inference_note": (
                        "HC1 normal approximation"
                        if method == "lpm"
                        else "inverse-information curvature diagnostic; not used for specification selection"
                    ),
                    "warning": model_warning(
                        model, bool(result["converged"]), str(result.get("note", ""))
                    ),
                    "selection_role": "fixed sensitivity diagnostic; not ranked by sign or significance",
                }
            )
    return output, fitted


def design_alias_diagnostics(models: list[ModelData]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for model in models:
        rank = int(np.linalg.matrix_rank(model.x))
        columns = model.x.shape[1]
        relation = ""
        maximum_residual = ""
        category_counts = ""
        if {
            "District/county platform",
            "Prefecture/municipal platform",
        }.issubset(model.variable_names):
            district_index = model.variable_names.index("District/county platform")
            prefecture_index = model.variable_names.index("Prefecture/municipal platform")
            residual = (
                model.x[:, 0]
                - model.x[:, district_index]
                - model.x[:, prefecture_index]
            )
            maximum_residual = f"{float(np.max(np.abs(residual))):.8f}"
            district_count = int(model.x[:, district_index].sum())
            prefecture_count = int(model.x[:, prefecture_index].sum())
            category_counts = (
                f"district_or_county={district_count};"
                f"prefecture_or_municipal={prefecture_count}"
            )
            if float(np.max(np.abs(residual))) < 1e-12:
                relation = (
                    "intercept equals district/county dummy plus "
                    "prefecture/municipal dummy for every row"
                )
        output.append(
            {
                "specification": model.specification,
                "columns": columns,
                "matrix_rank": rank,
                "rank_deficient": rank < columns,
                "identified_exact_alias": relation,
                "maximum_absolute_alias_residual": maximum_residual,
                "platform_category_counts": category_counts,
                "proposed_mechanical_resolution": (
                    "use one platform category as the reference before interpreting the full-control model"
                    if relation
                    else "not applicable"
                ),
                "review_status": (
                    "coordinator review required; existing model outputs are not changed by this experiment"
                    if relation
                    else "not applicable"
                ),
            }
        )
    return output


def leave_one_out_diagnostics(
    models: list[ModelData], fitted: dict[str, dict[str, object]]
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for model in models:
        full_effect = float(fitted[model.specification]["lpm"]["beta"][1])
        for index, row in enumerate(model.rows):
            keep = np.arange(len(model.rows)) != index
            leave_one_out = lpm_hc1(model.y[keep], model.x[keep])
            effect = float(leave_one_out["beta"][1])
            delta = effect - full_effect
            output.append(
                {
                    "specification": model.specification,
                    "omitted_panel_id": row.get("panel_id", ""),
                    "omitted_case_id": row.get("case_id", ""),
                    "omitted_city": row.get("city", ""),
                    "omitted_outcome": row.get("institutional_change", ""),
                    "full_sample_elite_effect": f"{full_effect:.8f}",
                    "leave_one_out_elite_effect": f"{effect:.8f}",
                    "delta": f"{delta:.8f}",
                    "absolute_delta": f"{abs(delta):.8f}",
                    "sign_changed": bool(full_effect * effect < 0),
                    "scaling_rule": "full-sample standardization retained after deletion",
                }
            )
    return output


def pilot_reference() -> float:
    rows = read_csv(PILOT_LPM)
    matches = [
        row
        for row in rows
        if row["model"] == "Elite density"
        and row["variable"] == "Elite density, standardized"
    ]
    if len(matches) != 1:
        raise ValueError("Pilot LPM reference row is missing or ambiguous.")
    return float(matches[0]["coefficient"])


def summarize(
    matched: list[dict[str, str]],
    complete: list[dict[str, str]],
    model_rows: list[dict[str, object]],
    influence_rows: list[dict[str, object]],
    fitted: dict[str, dict[str, object]],
) -> dict[str, object]:
    influence_summary: dict[str, object] = {}
    for specification in fitted:
        candidates = [row for row in influence_rows if row["specification"] == specification]
        largest = max(candidates, key=lambda row: float(row["absolute_delta"]))
        influence_summary[specification] = {
            "largest_absolute_delta": float(largest["absolute_delta"]),
            "most_influential_case_id": largest["omitted_case_id"],
            "most_influential_city": largest["omitted_city"],
            "sign_changes": sum(row["sign_changed"] for row in candidates),
            "leave_one_out_min": min(float(row["leave_one_out_elite_effect"]) for row in candidates),
            "leave_one_out_max": max(float(row["leave_one_out_elite_effect"]) for row in candidates),
        }

    matched_model = next(
        row
        for row in model_rows
        if row["specification"] == "matched_gold_historical_only" and row["method"] == "lpm"
    )
    reproduced_effect = float(matched_model["elite_effect_probability_scale"])
    reference_effect = pilot_reference()
    return {
        "estimand": "institutional_change equals substantive exit or functional transfer; nominal exit is zero",
        "exposure": "standardized Ming-Qing elite density matched to the contemporary prefecture",
        "matched_gold": {
            "observations": len(matched),
            "events": sum(as_float(row, "institutional_change") for row in matched),
            "event_share": mean([as_float(row, "institutional_change") for row in matched]),
        },
        "complete_control_subset": {
            "observations": len(complete),
            "events": sum(as_float(row, "institutional_change") for row in complete),
            "event_share": mean([as_float(row, "institutional_change") for row in complete]),
        },
        "excluded_matched_gold_observations": len(matched) - len(complete),
        "baseline_reproduction": {
            "diagnostic_lpm_elite_effect": reproduced_effect,
            "pilot_csv_displayed_coefficient": reference_effect,
            "matches_at_pilot_precision": round(reproduced_effect, 3) == reference_effect,
        },
        "functional_form_results": model_rows,
        "influence": influence_summary,
        "selection_by_sign_or_significance": False,
        "review_gate": (
            "Promoting a bias-reduced logit, changing the main specification, or strengthening "
            "the adjusted historical-capacity claim requires coordinator and human review."
        ),
    }


def run(panel: Path = DEFAULT_PANEL, output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, object]:
    all_rows = read_csv(panel)
    matched = matched_gold_rows(all_rows)
    complete = complete_control_rows(all_rows)
    if len(matched) != 84:
        raise ValueError(f"Expected 84 matched-gold rows, found {len(matched)}")
    if not complete:
        raise ValueError("No complete-control rows found.")

    models = [
        make_model("matched_gold_historical_only", matched, full_controls=False),
        make_model("complete_control_historical_only", complete, full_controls=False),
        make_model("complete_control_full_available_controls", complete, full_controls=True),
    ]
    outcome_rows = sample_outcomes(models)
    missingness_rows = missingness(matched)
    selection_rows = selection_diagnostics(matched, complete)
    excluded_rows = excluded_case_diagnostics(matched, complete)
    functional_rows, fitted = functional_form_diagnostics(models)
    alias_rows = design_alias_diagnostics(models)
    influence_rows = leave_one_out_diagnostics(models, fitted)
    summary = summarize(matched, complete, functional_rows, influence_rows, fitted)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "sample_outcome_diagnostics.csv", outcome_rows)
    write_csv(output_dir / "control_missingness.csv", missingness_rows)
    write_csv(output_dir / "sample_selection_diagnostics.csv", selection_rows)
    write_csv(output_dir / "excluded_matched_gold_cases.csv", excluded_rows)
    write_csv(output_dir / "functional_form_sensitivity.csv", functional_rows)
    write_csv(output_dir / "design_alias_diagnostics.csv", alias_rows)
    write_csv(output_dir / "leave_one_out_influence.csv", influence_rows)
    (output_dir / "diagnostic_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel", type=Path, default=DEFAULT_PANEL)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    summary = run(args.panel, args.output_dir)
    print(
        json.dumps(
            {
                "matched_gold_observations": summary["matched_gold"]["observations"],
                "matched_gold_events": summary["matched_gold"]["events"],
                "complete_control_observations": summary["complete_control_subset"]["observations"],
                "complete_control_events": summary["complete_control_subset"]["events"],
                "baseline_reproduced": summary["baseline_reproduction"][
                    "matches_at_pilot_precision"
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
