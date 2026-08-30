#!/usr/bin/env python3
"""Run the preregistered sparse-outcome audit for the frozen LGFV estimand."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import matplotlib
import numpy as np


matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PANEL = ROOT / "data" / "analysis_inputs" / "empirical_case_panel.csv"
PILOT_LPM = ROOT / "data" / "analysis_inputs" / "pilot_lpm_institutional_change.csv"
DEFAULT_OUTPUT_DIR = ROOT / "experiments" / "EXP-20260830-012" / "artifacts"

CONTINUOUS_ADJUSTED_FIELDS = [
    ("Elite density, standardized", "elite_per_1000_sqkm"),
    ("GDP per capita, standardized", "gdp_per_capita_value"),
    ("Fiscal self-sufficiency, standardized", "fiscal_self_sufficiency_value"),
    ("Debt pressure, standardized", "debt_pressure_value"),
    ("Land-finance dependence, standardized", "land_finance_dependence_value"),
    ("Source coverage, standardized", "source_coverage_score"),
]
REQUIRED_COMPLETE_FIELDS = [field for _, field in CONTINUOUS_ADJUSTED_FIELDS]
DISTRICT_NEEDLES = {"district", "county", "development_zone", "park"}
PREFECTURE_NEEDLES = {"prefecture", "municipal", "city_level"}
MODEL_IDS = [
    "matched_gold_historical_lpm",
    "matched_gold_historical_firth",
    "complete_control_adjusted_lpm",
    "complete_control_adjusted_firth",
]


@dataclass(frozen=True)
class Design:
    design_id: str
    sample_label: str
    rows: list[dict[str, str]]
    y: np.ndarray
    x: np.ndarray
    variable_names: list[str]
    reference_category: str


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write an empty artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
    required = ["institutional_change", *REQUIRED_COMPLETE_FIELDS]
    return [
        row
        for row in rows
        if row.get("include_in_full_controls_regression_sample") == "1"
        and all(nonempty(row.get(field)) for field in required)
    ]


def standardize(values: np.ndarray) -> np.ndarray:
    standard_deviation = float(values.std(ddof=1))
    if standard_deviation == 0:
        raise ValueError("A preregistered continuous regressor has zero sample variance.")
    return (values - float(values.mean())) / standard_deviation


def platform_indicators(row: dict[str, str]) -> tuple[float, float]:
    text = row.get("platform_administrative_level", "").lower()
    district = float(any(needle in text for needle in DISTRICT_NEEDLES))
    prefecture = float(any(needle in text for needle in PREFECTURE_NEEDLES))
    return district, prefecture


def historical_design(rows: list[dict[str, str]]) -> Design:
    y = np.array([as_float(row, "institutional_change") for row in rows], dtype=float)
    elite = standardize(
        np.array([as_float(row, "elite_per_1000_sqkm") for row in rows], dtype=float)
    )
    return Design(
        design_id="matched_gold_historical",
        sample_label="84 matched working-reference cases",
        rows=rows,
        y=y,
        x=np.column_stack([np.ones(len(rows)), elite]),
        variable_names=["Intercept", "Elite density, standardized"],
        reference_category="not applicable",
    )


def corrected_adjusted_design(rows: list[dict[str, str]]) -> Design:
    y = np.array([as_float(row, "institutional_change") for row in rows], dtype=float)
    columns = [np.ones(len(rows), dtype=float)]
    names = ["Intercept"]
    for label, field in CONTINUOUS_ADJUSTED_FIELDS:
        values = np.array([as_float(row, field) for row in rows], dtype=float)
        columns.append(standardize(values))
        names.append(label)
    platform = [platform_indicators(row) for row in rows]
    invalid = [
        rows[index].get("panel_id", "")
        for index, pair in enumerate(platform)
        if sum(pair) != 1.0
    ]
    if invalid:
        raise ValueError(
            "Corrected adjusted design requires exactly one platform category for: "
            + ", ".join(invalid)
        )
    columns.append(np.array([pair[1] for pair in platform], dtype=float))
    names.append("Prefecture/municipal platform")
    return Design(
        design_id="complete_control_adjusted",
        sample_label="78 complete-control working-reference cases",
        rows=rows,
        y=y,
        x=np.column_stack(columns),
        variable_names=names,
        reference_category="district/county platform",
    )


def legacy_adjusted_matrix(rows: list[dict[str, str]]) -> tuple[np.ndarray, list[str]]:
    corrected = corrected_adjusted_design(rows)
    district = np.array([platform_indicators(row)[0] for row in rows], dtype=float)
    legacy = np.column_stack([corrected.x[:, :-1], district, corrected.x[:, -1]])
    names = [
        *corrected.variable_names[:-1],
        "District/county platform",
        "Prefecture/municipal platform",
    ]
    return legacy, names


def normal_pvalue(z_score: float) -> float:
    return math.erfc(abs(z_score) / math.sqrt(2.0))


def lpm_fit(y: np.ndarray, x: np.ndarray) -> dict[str, object]:
    n, columns = x.shape
    if np.linalg.matrix_rank(x) != columns:
        raise ValueError("LPM design must be full rank.")
    inverse = np.linalg.inv(x.T @ x)
    beta = inverse @ (x.T @ y)
    residuals = y - x @ beta
    meat = np.zeros((columns, columns), dtype=float)
    for index in range(n):
        xi = x[index : index + 1].T
        meat += float(residuals[index] ** 2) * (xi @ xi.T)
    covariance = (n / (n - columns)) * inverse @ meat @ inverse
    standard_errors = np.sqrt(np.maximum(np.diag(covariance), 0.0))
    return {
        "beta": beta,
        "covariance": covariance,
        "standard_errors": standard_errors,
        "converged": True,
        "iterations": 1,
        "objective": "",
        "note": "",
    }


def sigmoid(values: np.ndarray) -> np.ndarray:
    output = np.empty_like(values, dtype=float)
    positive = values >= 0
    output[positive] = 1.0 / (1.0 + np.exp(-values[positive]))
    exponentiated = np.exp(values[~positive])
    output[~positive] = exponentiated / (1.0 + exponentiated)
    return output


def logistic_log_likelihood(y: np.ndarray, x: np.ndarray, beta: np.ndarray) -> float:
    linear_predictor = x @ beta
    return float(np.sum(y * linear_predictor - np.logaddexp(0.0, linear_predictor)))


def firth_fit(
    y: np.ndarray,
    x: np.ndarray,
    max_iterations: int = 200,
    tolerance: float = 1e-9,
) -> dict[str, object]:
    if np.linalg.matrix_rank(x) != x.shape[1]:
        raise ValueError("Firth-logit design must be full rank.")
    beta = np.zeros(x.shape[1], dtype=float)
    converged = False
    note = ""
    iterations = 0

    def objective(candidate: np.ndarray) -> float:
        probabilities = np.clip(sigmoid(x @ candidate), 1e-10, 1.0 - 1e-10)
        weights = probabilities * (1.0 - probabilities)
        information = x.T @ (weights[:, None] * x)
        sign, log_determinant = np.linalg.slogdet(information)
        if sign <= 0:
            return float("-inf")
        return logistic_log_likelihood(y, x, candidate) + 0.5 * float(log_determinant)

    for iteration in range(1, max_iterations + 1):
        iterations = iteration
        probabilities = np.clip(sigmoid(x @ beta), 1e-10, 1.0 - 1e-10)
        weights = probabilities * (1.0 - probabilities)
        information = x.T @ (weights[:, None] * x)
        inverse = np.linalg.inv(information)
        weighted_x = np.sqrt(weights)[:, None] * x
        leverage = np.sum((weighted_x @ inverse) * weighted_x, axis=1)
        score = x.T @ (y - probabilities + leverage * (0.5 - probabilities))
        step = inverse @ score
        current_objective = objective(beta)
        fraction = 1.0
        accepted = False
        while fraction >= 2.0**-24:
            candidate = beta + fraction * step
            if objective(candidate) >= current_objective - 1e-12:
                accepted = True
                break
            fraction /= 2.0
        if not accepted:
            note = "penalized-likelihood line search failed"
            break
        accepted_step = fraction * step
        beta = candidate
        if float(np.max(np.abs(accepted_step))) < tolerance:
            converged = True
            break

    probabilities = np.clip(sigmoid(x @ beta), 1e-10, 1.0 - 1e-10)
    weights = probabilities * (1.0 - probabilities)
    information = x.T @ (weights[:, None] * x)
    covariance = np.linalg.inv(information)
    standard_errors = np.sqrt(np.maximum(np.diag(covariance), 0.0))
    if not converged and not note:
        note = f"maximum iterations reached ({max_iterations})"
    return {
        "beta": beta,
        "covariance": covariance,
        "standard_errors": standard_errors,
        "probabilities": probabilities,
        "converged": converged,
        "iterations": iterations,
        "objective": objective(beta),
        "note": note,
    }


def elite_effect(
    design: Design, estimator: str, result: dict[str, object]
) -> tuple[float, float]:
    beta = np.asarray(result["beta"], dtype=float)
    covariance = np.asarray(result["covariance"], dtype=float)
    if estimator == "lpm":
        return float(beta[1]), float(math.sqrt(max(covariance[1, 1], 0.0)))
    probabilities = np.asarray(result["probabilities"], dtype=float)
    weights = probabilities * (1.0 - probabilities)
    effect = float(beta[1] * np.mean(weights))
    gradient = beta[1] * np.mean(
        (weights * (1.0 - 2.0 * probabilities))[:, None] * design.x,
        axis=0,
    )
    gradient[1] += float(np.mean(weights))
    variance = float(gradient @ covariance @ gradient)
    return effect, math.sqrt(max(variance, 0.0))


def fit_design(design: Design, estimator: str) -> dict[str, object]:
    if estimator == "lpm":
        return lpm_fit(design.y, design.x)
    if estimator == "firth":
        return firth_fit(design.y, design.x)
    raise KeyError(estimator)


def model_id(design: Design, estimator: str) -> str:
    return f"{design.design_id}_{estimator}"


def warning_text(design: Design, result: dict[str, object]) -> str:
    warnings: list[str] = []
    rank = int(np.linalg.matrix_rank(design.x))
    events = int(design.y.sum())
    if events / rank < 5:
        warnings.append("fewer than 5 events per independent column")
    if float(np.linalg.cond(design.x)) > 30:
        warnings.append("design-matrix condition number exceeds 30")
    if not result["converged"]:
        warnings.append("estimator did not converge")
    if result.get("note"):
        warnings.append(str(result["note"]))
    return "; ".join(dict.fromkeys(warnings))


def model_outputs(
    designs: list[Design],
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, dict[str, object]]]:
    diagnostics: list[dict[str, object]] = []
    coefficients: list[dict[str, object]] = []
    fitted: dict[str, dict[str, object]] = {}
    for design in designs:
        for estimator in ("lpm", "firth"):
            identifier = model_id(design, estimator)
            result = fit_design(design, estimator)
            fitted[identifier] = result
            effect, effect_se = elite_effect(design, estimator, result)
            rank = int(np.linalg.matrix_rank(design.x))
            events = int(design.y.sum())
            diagnostics.append(
                {
                    "model_id": identifier,
                    "design_id": design.design_id,
                    "estimator": "LPM with HC1" if estimator == "lpm" else "Firth bias-reduced logit",
                    "outcome": "1 = substantive exit or functional transfer; 0 = nominal exit",
                    "unit": "city-platform case",
                    "sample": design.sample_label,
                    "observations": len(design.rows),
                    "events": events,
                    "non_events": len(design.rows) - events,
                    "event_share": f"{events / len(design.rows):.8f}",
                    "columns": design.x.shape[1],
                    "independent_columns": rank,
                    "events_per_independent_column": f"{events / rank:.8f}",
                    "matrix_rank": rank,
                    "condition_number": f"{float(np.linalg.cond(design.x)):.8f}",
                    "converged": bool(result["converged"]),
                    "iterations": int(result["iterations"]),
                    "elite_effect_scale": "probability-point change per one sample SD of elite density",
                    "elite_effect": f"{effect:.8f}",
                    "elite_effect_standard_error": f"{effect_se:.8f}",
                    "elite_effect_ci95_low": f"{effect - 1.96 * effect_se:.8f}",
                    "elite_effect_ci95_high": f"{effect + 1.96 * effect_se:.8f}",
                    "uncertainty": (
                        "HC1 normal-approximation interval"
                        if estimator == "lpm"
                        else "inverse-information curvature and delta-method interval; diagnostic only"
                    ),
                    "province_fixed_effects": "No",
                    "platform_reference_category": design.reference_category,
                    "warning": warning_text(design, result),
                    "selection_role": "fixed preregistered model; not selected by sign or significance",
                }
            )
            beta = np.asarray(result["beta"], dtype=float)
            standard_errors = np.asarray(result["standard_errors"], dtype=float)
            for variable, coefficient, standard_error in zip(
                design.variable_names, beta, standard_errors
            ):
                coefficients.append(
                    {
                        "model_id": identifier,
                        "estimator": "lpm" if estimator == "lpm" else "firth_logit",
                        "variable": variable,
                        "coefficient_scale": "probability" if estimator == "lpm" else "log odds",
                        "coefficient": f"{float(coefficient):.8f}",
                        "standard_error": f"{float(standard_error):.8f}",
                        "ci95_low": f"{float(coefficient - 1.96 * standard_error):.8f}",
                        "ci95_high": f"{float(coefficient + 1.96 * standard_error):.8f}",
                        "uncertainty": (
                            "HC1" if estimator == "lpm" else "inverse-information curvature; diagnostic only"
                        ),
                    }
                )
    if [row["model_id"] for row in diagnostics] != MODEL_IDS:
        raise AssertionError("Generated model order differs from the preregistered model set.")
    return diagnostics, coefficients, fitted


def rank_repair_diagnostics(
    adjusted: Design,
) -> list[dict[str, object]]:
    legacy, _ = legacy_adjusted_matrix(adjusted.rows)
    district = np.array([platform_indicators(row)[0] for row in adjusted.rows], dtype=float)
    prefecture = np.array([platform_indicators(row)[1] for row in adjusted.rows], dtype=float)
    alias_residual = np.ones(len(adjusted.rows)) - district - prefecture
    return [
        {
            "design": "legacy_two_platform_indicators",
            "observations": len(adjusted.rows),
            "columns": legacy.shape[1],
            "matrix_rank": int(np.linalg.matrix_rank(legacy)),
            "rank_deficient": int(np.linalg.matrix_rank(legacy)) < legacy.shape[1],
            "condition_number": f"{float(np.linalg.cond(legacy)):.8f}",
            "district_count": int(district.sum()),
            "prefecture_count": int(prefecture.sum()),
            "maximum_absolute_alias_residual": f"{float(np.max(np.abs(alias_residual))):.8f}",
            "platform_reference_category": "none",
            "repair": "intercept equals district plus prefecture indicators",
        },
        {
            "design": "corrected_single_platform_indicator",
            "observations": len(adjusted.rows),
            "columns": adjusted.x.shape[1],
            "matrix_rank": int(np.linalg.matrix_rank(adjusted.x)),
            "rank_deficient": int(np.linalg.matrix_rank(adjusted.x)) < adjusted.x.shape[1],
            "condition_number": f"{float(np.linalg.cond(adjusted.x)):.8f}",
            "district_count": int(district.sum()),
            "prefecture_count": int(prefecture.sum()),
            "maximum_absolute_alias_residual": f"{float(np.max(np.abs(alias_residual))):.8f}",
            "platform_reference_category": "district/county platform",
            "repair": "omit district/county indicator and retain prefecture/municipal indicator",
        },
    ]


def sample_selection_outputs(
    matched: list[dict[str, str]], complete: list[dict[str, str]]
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    complete_ids = {row["panel_id"] for row in complete}
    included = [row for row in matched if row["panel_id"] in complete_ids]
    excluded = [row for row in matched if row["panel_id"] not in complete_ids]
    if len(included) != len(complete):
        raise ValueError("Complete-control rows are not a subset of the matched-gold sample.")
    elite_all = np.array([as_float(row, "elite_per_1000_sqkm") for row in matched])
    elite_mean = float(elite_all.mean())
    elite_sd = float(elite_all.std(ddof=1))

    flow = [
        {
            "stage": "matched_gold",
            "observations": len(matched),
            "events": int(sum(as_float(row, "institutional_change") for row in matched)),
            "excluded_from_prior_stage": 0,
            "sample_rule": "recorded matched-gold model flag with observed outcome and elite density",
        },
        {
            "stage": "complete_controls",
            "observations": len(complete),
            "events": int(sum(as_float(row, "institutional_change") for row in complete)),
            "excluded_from_prior_stage": len(excluded),
            "sample_rule": "recorded complete-control flag and all preregistered continuous fields observed",
        },
    ]

    def values(group: list[dict[str, str]], metric: str) -> list[float]:
        if metric == "institutional_change_share":
            return [as_float(row, "institutional_change") for row in group]
        if metric == "elite_density_raw_mean":
            return [as_float(row, "elite_per_1000_sqkm") for row in group]
        if metric == "elite_density_matched_sample_z_mean":
            return [
                (as_float(row, "elite_per_1000_sqkm") - elite_mean) / elite_sd
                for row in group
            ]
        if metric == "source_coverage_mean":
            return [as_float(row, "source_coverage_score") for row in group]
        if metric == "prefecture_platform_share":
            return [platform_indicators(row)[1] for row in group]
        if metric == "district_platform_share":
            return [platform_indicators(row)[0] for row in group]
        if metric == "platform_level_missing_share":
            return [float(sum(platform_indicators(row)) == 0) for row in group]
        raise KeyError(metric)

    comparisons: list[dict[str, object]] = []
    for metric in [
        "institutional_change_share",
        "elite_density_raw_mean",
        "elite_density_matched_sample_z_mean",
        "source_coverage_mean",
        "prefecture_platform_share",
        "district_platform_share",
        "platform_level_missing_share",
    ]:
        included_value = float(np.mean(values(included, metric)))
        excluded_value = float(np.mean(values(excluded, metric)))
        comparisons.append(
            {
                "metric": metric,
                "complete_control_subset": f"{included_value:.8f}",
                "excluded_matched_gold": f"{excluded_value:.8f}",
                "difference_complete_minus_excluded": f"{included_value - excluded_value:.8f}",
                "complete_control_n": len(included),
                "excluded_n": len(excluded),
                "interpretation": "descriptive only; no imputation or selection model",
            }
        )

    excluded_rows: list[dict[str, object]] = []
    for row in excluded:
        missing = [
            label
            for label, field in CONTINUOUS_ADJUSTED_FIELDS
            if not nonempty(row.get(field))
        ]
        excluded_rows.append(
            {
                "panel_id": row.get("panel_id", ""),
                "case_id": row.get("case_id", ""),
                "province": row.get("province", ""),
                "city": row.get("city", ""),
                "exit_type": row.get("exit_type", ""),
                "institutional_change": row.get("institutional_change", ""),
                "elite_per_1000_sqkm": row.get("elite_per_1000_sqkm", ""),
                "elite_density_matched_sample_z": f"{(as_float(row, 'elite_per_1000_sqkm') - elite_mean) / elite_sd:.8f}",
                "source_coverage_score": row.get("source_coverage_score", ""),
                "platform_administrative_level": row.get("platform_administrative_level", ""),
                "missing_preregistered_fields": "; ".join(missing),
                "exclusion_basis": "recorded complete-control flag and observed missing inputs",
            }
        )
    return flow, comparisons, excluded_rows


def province_feasibility(
    adjusted: Design,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    counts: dict[str, list[int]] = {}
    for row in adjusted.rows:
        province = row.get("province_fixed_effect", "").strip()
        if not province:
            raise ValueError("Province identifier missing in complete-control sample.")
        counts.setdefault(province, []).append(int(as_float(row, "institutional_change")))
    provinces = sorted(counts)
    reference = provinces[0]
    dummies = [
        np.array(
            [float(row.get("province_fixed_effect", "").strip() == province) for row in adjusted.rows],
            dtype=float,
        )
        for province in provinces[1:]
    ]
    candidate = np.column_stack([adjusted.x, *dummies])
    rank = int(np.linalg.matrix_rank(candidate))
    zero_event = [province for province in provinces if sum(counts[province]) == 0]
    all_event = [province for province in provinces if sum(counts[province]) == len(counts[province])]
    varying = [province for province in provinces if 0 < sum(counts[province]) < len(counts[province])]
    events = int(adjusted.y.sum())
    reasons = []
    if rank < candidate.shape[1]:
        reasons.append("candidate matrix is rank deficient")
    if zero_event or all_event:
        reasons.append("not every province has within-province outcome variation")
    if events / rank < 5:
        reasons.append("fewer than 5 events per independent column")
    audit = [
        {
            "candidate": "corrected adjusted design plus saturated province indicators",
            "observations": len(adjusted.rows),
            "events": events,
            "provinces": len(provinces),
            "reference_province_for_diagnostic": reference,
            "columns": candidate.shape[1],
            "matrix_rank": rank,
            "condition_number": f"{float(np.linalg.cond(candidate)):.8f}",
            "events_per_independent_column": f"{events / rank:.8f}",
            "provinces_with_outcome_variation": len(varying),
            "zero_event_provinces": len(zero_event),
            "all_event_provinces": len(all_event),
            "eligible_for_estimation": not reasons,
            "reason_not_estimated": "; ".join(reasons) if reasons else "outside preregistered fixed model set",
            "decision_rule": "diagnostic only; province fixed effects are not estimated in EXP-20260830-012",
        }
    ]
    allocation = [
        {
            "province": province,
            "observations": len(counts[province]),
            "events": sum(counts[province]),
            "non_events": len(counts[province]) - sum(counts[province]),
            "within_province_outcome_variation": 0 < sum(counts[province]) < len(counts[province]),
        }
        for province in provinces
    ]
    return audit, allocation


def leave_one_out_outputs(
    designs: list[Design], fitted: dict[str, dict[str, object]]
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    influence: list[dict[str, object]] = []
    for design in designs:
        for estimator in ("lpm", "firth"):
            identifier = model_id(design, estimator)
            full_effect, _ = elite_effect(design, estimator, fitted[identifier])
            for omitted_index, row in enumerate(design.rows):
                retained = np.arange(len(design.rows)) != omitted_index
                subset = Design(
                    design_id=design.design_id,
                    sample_label=design.sample_label,
                    rows=[case for index, case in enumerate(design.rows) if index != omitted_index],
                    y=design.y[retained],
                    x=design.x[retained],
                    variable_names=design.variable_names,
                    reference_category=design.reference_category,
                )
                rank = int(np.linalg.matrix_rank(subset.x))
                if rank < subset.x.shape[1]:
                    result = None
                    effect = float("nan")
                    converged = False
                    iterations = 0
                    note = "leave-one-out design is rank deficient"
                else:
                    result = fit_design(subset, estimator)
                    effect, _ = elite_effect(subset, estimator, result)
                    converged = bool(result["converged"])
                    iterations = int(result["iterations"])
                    note = str(result.get("note", ""))
                delta = effect - full_effect
                influence.append(
                    {
                        "model_id": identifier,
                        "estimator": "lpm" if estimator == "lpm" else "firth_logit",
                        "omitted_panel_id": row.get("panel_id", ""),
                        "omitted_case_id": row.get("case_id", ""),
                        "omitted_province": row.get("province", ""),
                        "omitted_city": row.get("city", ""),
                        "omitted_exit_type": row.get("exit_type", ""),
                        "omitted_outcome": row.get("institutional_change", ""),
                        "full_sample_elite_effect": f"{full_effect:.8f}",
                        "leave_one_out_elite_effect": "" if not math.isfinite(effect) else f"{effect:.8f}",
                        "delta": "" if not math.isfinite(delta) else f"{delta:.8f}",
                        "absolute_delta": "" if not math.isfinite(delta) else f"{abs(delta):.8f}",
                        "absolute_delta_relative_to_full_effect": (
                            ""
                            if not math.isfinite(delta)
                            else f"{abs(delta) / max(abs(full_effect), 1e-12):.8f}"
                        ),
                        "sign_changed": bool(math.isfinite(effect) and full_effect * effect < 0),
                        "matrix_rank": rank,
                        "columns": subset.x.shape[1],
                        "converged": converged,
                        "iterations": iterations,
                        "note": note,
                        "scaling_rule": "full-sample standardization retained after deletion",
                    }
                )

    summaries: list[dict[str, object]] = []
    top_cases: list[dict[str, object]] = []
    for identifier in MODEL_IDS:
        rows = [row for row in influence if row["model_id"] == identifier]
        finite_rows = [row for row in rows if row["absolute_delta"] != ""]
        ordered = sorted(finite_rows, key=lambda row: float(row["absolute_delta"]), reverse=True)
        summaries.append(
            {
                "model_id": identifier,
                "deletion_attempts": len(rows),
                "converged_attempts": sum(bool(row["converged"]) for row in rows),
                "nonconvergent_or_rank_deficient_attempts": sum(not bool(row["converged"]) for row in rows),
                "sign_changes": sum(bool(row["sign_changed"]) for row in rows),
                "leave_one_out_minimum": f"{min(float(row['leave_one_out_elite_effect']) for row in finite_rows):.8f}",
                "leave_one_out_maximum": f"{max(float(row['leave_one_out_elite_effect']) for row in finite_rows):.8f}",
                "largest_absolute_delta": f"{float(ordered[0]['absolute_delta']):.8f}",
                "most_influential_case_id": ordered[0]["omitted_case_id"],
                "most_influential_city": ordered[0]["omitted_city"],
                "selection_role": "reported for stability; not used to choose a model by direction or significance",
            }
        )
        for rank_number, row in enumerate(ordered[:5], start=1):
            top_cases.append(
                {
                    "model_id": identifier,
                    "influence_rank": rank_number,
                    "omitted_panel_id": row["omitted_panel_id"],
                    "omitted_case_id": row["omitted_case_id"],
                    "omitted_province": row["omitted_province"],
                    "omitted_city": row["omitted_city"],
                    "omitted_exit_type": row["omitted_exit_type"],
                    "omitted_outcome": row["omitted_outcome"],
                    "full_sample_elite_effect": row["full_sample_elite_effect"],
                    "leave_one_out_elite_effect": row["leave_one_out_elite_effect"],
                    "delta": row["delta"],
                    "absolute_delta": row["absolute_delta"],
                    "sign_changed": row["sign_changed"],
                    "ranking_rule": "descending absolute change in preregistered elite-density effect",
                }
            )
    return influence, summaries, top_cases


def pilot_lpm_reference() -> float:
    matches = [
        row
        for row in read_csv(PILOT_LPM)
        if row.get("model") == "Elite density"
        and row.get("variable") == "Elite density, standardized"
    ]
    if len(matches) != 1:
        raise ValueError("Pilot elite-density LPM reference is missing or ambiguous.")
    return float(matches[0]["coefficient"])


def write_exploratory_table(path: Path, diagnostics: list[dict[str, object]]) -> None:
    rows = {str(row["model_id"]): row for row in diagnostics}

    def effect_cell(identifier: str) -> str:
        row = rows[identifier]
        return f"{float(row['elite_effect']):.3f}"

    def se_cell(identifier: str) -> str:
        row = rows[identifier]
        return f"({float(row['elite_effect_standard_error']):.3f})"

    path.write_text(
        "% Auto-generated by scripts/build_sparse_outcome_model_audit.py\n"
        "\\begin{table}[htbp]\n"
        "\\centering\n"
        "\\caption{Exploratory sparse-outcome audit of historical capacity}\n"
        "\\label{tab:exploratory-sparse-outcome-audit}\n"
        "\\begin{tabular}{@{}lcccc@{}}\n"
        "\\toprule\n"
        " & Historical LPM & Historical Firth & Adjusted LPM & Adjusted Firth \\\\\n"
        "\\midrule\n"
        f"Elite-density effect & {effect_cell(MODEL_IDS[0])} & {effect_cell(MODEL_IDS[1])} & {effect_cell(MODEL_IDS[2])} & {effect_cell(MODEL_IDS[3])} \\\\\n"
        f" & {se_cell(MODEL_IDS[0])} & {se_cell(MODEL_IDS[1])} & {se_cell(MODEL_IDS[2])} & {se_cell(MODEL_IDS[3])} \\\\\n"
        "\\midrule\n"
        "Observations & 84 & 84 & 78 & 78 \\\\\n"
        "Institutional-change events & 12 & 12 & 12 & 12 \\\\\n"
        "Contemporary controls & No & No & Yes & Yes \\\\\n"
        "Province fixed effects & No & No & No & No \\\\\n"
        "\\bottomrule\n"
        "\\end{tabular}\n"
        "\\begin{minipage}{0.97\\linewidth}\n"
        "\\vspace{0.5em}\\footnotesize Notes: This table is an exploratory diagnostic, not a causal estimate. "
        "The outcome equals one for substantive exit or functional transfer and zero for nominal exit. "
        "Effects are probability-point changes for a one-sample-standard-deviation increase in elite density. "
        "LPM uncertainty is HC1; Firth effects are average marginal effects with curvature-based delta-method "
        "uncertainty shown only as a diagnostic. The adjusted models use 12 events, first-pass controls, and "
        "district/county platforms as the reference category. All fixed models are reported without selection "
        "by sign or statistical significance.\n"
        "\\end{minipage}\n"
        "\\end{table}\n",
        encoding="utf-8",
    )


def write_coefficient_plot(path: Path, diagnostics: list[dict[str, object]]) -> None:
    labels = [
        "Historical LPM (84 cases)",
        "Historical Firth AME (84 cases)",
        "Adjusted LPM (78 cases)",
        "Adjusted Firth AME (78 cases)",
    ]
    effects = np.array([float(row["elite_effect"]) for row in diagnostics])
    lower = np.array([float(row["elite_effect_ci95_low"]) for row in diagnostics])
    upper = np.array([float(row["elite_effect_ci95_high"]) for row in diagnostics])
    positions = np.arange(len(labels))[::-1]
    colors = ["#3B6FB6", "#78A6D0", "#B55D46", "#D59784"]
    figure, axis = plt.subplots(figsize=(9.6, 5.2))
    axis.axvline(0.0, color="#555555", linewidth=1.0, linestyle="--")
    for index, position in enumerate(positions):
        axis.errorbar(
            effects[index],
            position,
            xerr=[[effects[index] - lower[index]], [upper[index] - effects[index]]],
            fmt="o",
            markersize=6,
            capsize=3,
            color=colors[index],
            ecolor=colors[index],
            linewidth=1.5,
        )
    axis.set_yticks(positions, labels)
    axis.set_xlabel("Change in predicted probability per one sample SD of elite density")
    figure.suptitle(
        "Exploratory historical-capacity associations",
        x=0.34,
        y=0.965,
        ha="left",
        fontweight="bold",
    )
    figure.text(
        0.34,
        0.915,
        "Fixed models with 95% diagnostic intervals\n"
        "Adjusted sample: 12 events and first-pass controls",
        fontsize=9,
        color="#444444",
        ha="left",
        va="top",
    )
    axis.grid(axis="x", color="#dddddd", linewidth=0.7)
    axis.spines[["top", "right", "left"]].set_visible(False)
    figure.subplots_adjust(left=0.34, right=0.97, top=0.79, bottom=0.16)
    figure.savefig(
        path,
        dpi=180,
        metadata={"Software": "LGFV preregistered sparse-outcome audit"},
    )
    plt.close(figure)


def summarize(
    panel: Path,
    matched: list[dict[str, str]],
    complete: list[dict[str, str]],
    diagnostics: list[dict[str, object]],
    rank_rows: list[dict[str, object]],
    influence_summary: list[dict[str, object]],
    province_audit: list[dict[str, object]],
) -> dict[str, object]:
    model_lookup = {str(row["model_id"]): row for row in diagnostics}
    baseline_effect = float(model_lookup[MODEL_IDS[0]]["elite_effect"])
    pilot = pilot_lpm_reference()
    corrected_rank = next(row for row in rank_rows if row["design"].startswith("corrected"))
    legacy_rank = next(row for row in rank_rows if row["design"].startswith("legacy"))
    return {
        "experiment_id": "EXP-20260830-012",
        "base_commit": "bf1bd7b99c7dd9261678015c9f050599ae862fe3",
        "branch": "codex/sparse-outcome-models",
        "input": {
            "panel": str(panel.relative_to(ROOT)) if panel.is_relative_to(ROOT) else str(panel),
            "panel_sha256": sha256(panel),
            "pilot_lpm": str(PILOT_LPM.relative_to(ROOT)),
            "pilot_lpm_sha256": sha256(PILOT_LPM),
        },
        "frozen_estimand": {
            "outcome": "one for substantive exit or functional transfer; zero for nominal exit",
            "exposure": "within-model-sample standardized Ming-Qing elite density",
            "matched_gold_observations": len(matched),
            "matched_gold_events": int(sum(as_float(row, "institutional_change") for row in matched)),
            "complete_control_observations": len(complete),
            "complete_control_events": int(sum(as_float(row, "institutional_change") for row in complete)),
            "excluded_matched_gold_observations": len(matched) - len(complete),
        },
        "model_ids": MODEL_IDS,
        "baseline_reproduction": {
            "audit_effect": baseline_effect,
            "tracked_pilot_displayed_effect": pilot,
            "matches_at_pilot_precision": round(baseline_effect, 3) == pilot,
        },
        "rank_repair": {
            "legacy_columns": legacy_rank["columns"],
            "legacy_rank": legacy_rank["matrix_rank"],
            "corrected_columns": corrected_rank["columns"],
            "corrected_rank": corrected_rank["matrix_rank"],
            "reference_category": corrected_rank["platform_reference_category"],
        },
        "model_diagnostics": diagnostics,
        "leave_one_out_summary": influence_summary,
        "province_fixed_effect_feasibility": province_audit[0],
        "selection_by_sign_or_significance": False,
        "review_gate": (
            "Any main-specification, main-text, claim, or ledger change requires coordinator and human review."
        ),
    }


def run(panel: Path = DEFAULT_PANEL, output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, object]:
    all_rows = read_csv(panel)
    matched = matched_gold_rows(all_rows)
    complete = complete_control_rows(all_rows)
    if len(matched) != 84:
        raise ValueError(f"Expected 84 matched-gold cases, found {len(matched)}.")
    if len(complete) != 78:
        raise ValueError(f"Expected 78 complete-control cases, found {len(complete)}.")
    if int(sum(as_float(row, "institutional_change") for row in matched)) != 12:
        raise ValueError("Frozen matched-gold outcome count differs from 12 events.")
    if int(sum(as_float(row, "institutional_change") for row in complete)) != 12:
        raise ValueError("Frozen complete-control outcome count differs from 12 events.")

    designs = [historical_design(matched), corrected_adjusted_design(complete)]
    diagnostics, coefficients, fitted = model_outputs(designs)
    rank_rows = rank_repair_diagnostics(designs[1])
    flow, selection, excluded = sample_selection_outputs(matched, complete)
    province_audit, province_allocation = province_feasibility(designs[1])
    influence, influence_summary, influential_cases = leave_one_out_outputs(designs, fitted)
    summary = summarize(
        panel,
        matched,
        complete,
        diagnostics,
        rank_rows,
        influence_summary,
        province_audit,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "model_diagnostics.csv", diagnostics)
    write_csv(output_dir / "coefficient_estimates.csv", coefficients)
    write_csv(output_dir / "rank_repair_diagnostics.csv", rank_rows)
    write_csv(output_dir / "sample_flow.csv", flow)
    write_csv(output_dir / "sample_selection_diagnostics.csv", selection)
    write_csv(output_dir / "excluded_complete_control_cases.csv", excluded)
    write_csv(output_dir / "province_feasibility.csv", province_audit)
    write_csv(output_dir / "province_event_allocation.csv", province_allocation)
    write_csv(output_dir / "leave_one_out_influence.csv", influence)
    write_csv(output_dir / "leave_one_out_summary.csv", influence_summary)
    write_csv(output_dir / "influential_cases.csv", influential_cases)
    (output_dir / "audit_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_exploratory_table(output_dir / "exploratory_sparse_outcome_table.tex", diagnostics)
    write_coefficient_plot(output_dir / "exploratory_sparse_outcome_coefficients.png", diagnostics)
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
                "matched_gold_observations": summary["frozen_estimand"]["matched_gold_observations"],
                "matched_gold_events": summary["frozen_estimand"]["matched_gold_events"],
                "complete_control_observations": summary["frozen_estimand"]["complete_control_observations"],
                "complete_control_events": summary["frozen_estimand"]["complete_control_events"],
                "legacy_rank": summary["rank_repair"]["legacy_rank"],
                "corrected_rank": summary["rank_repair"]["corrected_rank"],
                "baseline_reproduced": summary["baseline_reproduction"]["matches_at_pilot_precision"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
