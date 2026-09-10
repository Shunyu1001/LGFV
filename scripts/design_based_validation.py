"""Guarded finite-frame difference estimates; no current-data adapter or CLI.

Public entry points require separately vetted approval records. Metadata checks
cannot authenticate PI approval, actual randomization, eligibility, or human
review: those facts must be checked against source records by the coordinator.
See experiments/EXP-20260910-005/method.md for the contract and derivation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
import hashlib
import json
import math
from numbers import Real
from typing import Sequence

import numpy as np


MAX_X_CONDITION = 1e8
UNRESOLVED = {"unknown", "unclear", "pending", "not_reported", "none", "na", "n/a"}
UNCERTAINTY_SCOPE = (
    "Label-selection uncertainty conditional on this assembled frame, fixed X, "
    "fixed predictions, and well-defined human outcomes. Excludes measurement, "
    "nonresponse, eligibility, frame coverage, and national-population uncertainty."
)


class InputError(ValueError):
    """An input gate failed; no estimate was computed."""


class NumericalError(ValueError):
    """Numerical estimation failed; never replaced by a fallback estimate."""


@dataclass(frozen=True)
class FrameUnit:
    unit_id: str
    stratum_id: str
    inclusion_probability: float
    prediction: float
    covariates: tuple[float, ...]


@dataclass(frozen=True)
class Frame:
    frame_id: str
    status: str
    unit_type: str
    outcome_eligibility_status: str
    eligibility_record_id: str
    covariate_names: tuple[str, ...]
    units: tuple[FrameUnit, ...]


@dataclass(frozen=True)
class Stratum:
    stratum_id: str
    population_n: int
    sample_n: int
    method: str


@dataclass(frozen=True)
class Design:
    design_id: str
    frame_id: str
    status: str
    strata: tuple[Stratum, ...]
    independent_strata: bool
    probability_record_id: str


@dataclass(frozen=True)
class AnalysisSpec:
    outcome_id: str
    outcome_definition_record_id: str
    prediction_assumption: str
    prediction_record_id: str
    covariate_record_id: str
    inputs_fixed_before_selection: bool


@dataclass(frozen=True)
class Selection:
    frame_id: str
    design_id: str
    selection_id: str
    status: str
    selected_unit_ids: tuple[str, ...]
    selection_record_id: str
    verification_record_id: str


@dataclass(frozen=True)
class HumanResponse:
    unit_id: str
    frame_id: str
    selection_id: str
    outcome_id: str
    response_status: str
    outcome_status: str
    downstream_eligible: bool
    value: float | None
    label_origin: str
    reviewer_id: str
    reviewed_at: str
    review_record_id: str


@dataclass(frozen=True)
class Request:
    mode: str
    frame: Frame
    design: Design
    spec: AnalysisSpec
    selection: Selection
    responses: tuple[HumanResponse, ...]


@dataclass(frozen=True)
class Approval:
    """Externally vetted frozen-spec approval, not issued by this module."""

    frame_id: str
    design_id: str
    mode: str
    spec_sha256: str
    status: str
    approved_by: str
    approval_record_id: str


@dataclass(frozen=True)
class Estimate:
    estimand: str
    mode: str
    frame_id: str
    design_id: str
    selection_id: str
    outcome_id: str
    approval_record_id: str
    spec_sha256: str
    input_sha256: str
    parameter_names: tuple[str, ...]
    point: tuple[float, ...]
    covariance: tuple[tuple[float, ...], ...] | None
    standard_errors: tuple[float, ...] | None
    variance_status: str
    unsupported_strata: tuple[str, ...]
    frame_n: int
    selected_n: int
    response_n: int
    response_origins: tuple[tuple[str, int], ...]
    prediction_assumption: str
    x_condition_number: float | None
    uncertainty_scope: str = UNCERTAINTY_SCOPE


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise InputError(message)


def _identifier(value: str, name: str) -> None:
    _require(
        isinstance(value, str) and bool(value) and value == value.strip()
        and value.lower() not in UNRESOLVED,
        f"{name} must be an explicit nonmissing identifier",
    )


def _number(value: float, name: str) -> None:
    _require(
        isinstance(value, Real) and not isinstance(value, (bool, np.bool_))
        and math.isfinite(value), f"{name} must be a finite numeric value",
    )


def _unique(values: Sequence[str], name: str) -> None:
    for value in values:
        _identifier(value, name)
    _require(len(values) == len(set(values)), f"duplicate {name}")


def _digest(value: dict) -> str:
    try:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True, allow_nan=False).encode("ascii")
    except (TypeError, ValueError) as exc:
        raise InputError("inputs must be finite JSON-compatible schema values") from exc
    return hashlib.sha256(encoded).hexdigest()


def _frozen_payload(request: Request) -> dict:
    frame = asdict(request.frame)
    frame["units"] = sorted(frame["units"], key=lambda row: row["unit_id"])
    design = asdict(request.design)
    design["strata"] = sorted(design["strata"], key=lambda row: row["stratum_id"])
    return {"schema_version": 1, "mode": request.mode, "frame": frame,
            "design": design, "spec": asdict(request.spec)}


def specification_sha256(request: Request) -> str:
    """Fingerprint only; does not validate or approve inputs or authorize use."""
    return _digest(_frozen_payload(request))


def _input_sha256(request: Request) -> str:
    payload = _frozen_payload(request)
    selection = asdict(request.selection)
    selection["selected_unit_ids"] = sorted(selection["selected_unit_ids"])
    payload["selection"] = selection
    payload["responses"] = sorted(
        (asdict(row) for row in request.responses), key=lambda row: row["unit_id"]
    )
    return _digest(payload)


def validate_sources(request: Request, *, approvals: Sequence[Approval] = ()) -> Approval:
    """Fail closed on documentary/schema inconsistencies, before numeric work.

    The caller must independently verify the referenced records. In particular,
    a selected-unit roster is not inferred from the received human responses.
    """
    _require(isinstance(request, Request), "expected a Request, not a proposal CSV")
    frame, design, spec, sample = (
        request.frame, request.design, request.spec, request.selection
    )
    _require(isinstance(frame, Frame) and isinstance(design, Design)
             and isinstance(spec, AnalysisSpec) and isinstance(sample, Selection),
             "request objects must follow the dataclass schema")
    _require(request.mode in ("actual", "synthetic"), "mode must be actual or synthetic")
    _require(frame.status == "frozen_approved", "frame is not frozen_approved")
    _require(design.status == "approved", "design is not approved; proposals cannot be estimated")
    _require(frame.unit_type == "issuer", "unit type must be issuer")
    _require(frame.outcome_eligibility_status == "all_units_verified",
             "downstream outcome eligibility must be verified for the entire frame")
    for name, value in (
        ("frame_id", frame.frame_id), ("design_id", design.design_id),
        ("eligibility_record_id", frame.eligibility_record_id),
        ("probability_record_id", design.probability_record_id),
        ("outcome_id", spec.outcome_id),
        ("outcome_definition_record_id", spec.outcome_definition_record_id),
        ("prediction_record_id", spec.prediction_record_id),
        ("covariate_record_id", spec.covariate_record_id),
        ("selection_id", sample.selection_id),
        ("selection_record_id", sample.selection_record_id),
        ("verification_record_id", sample.verification_record_id),
    ):
        _identifier(value, name)
    _require(design.frame_id == frame.frame_id == sample.frame_id,
             "frame IDs do not match")
    _require(design.design_id == sample.design_id, "design IDs do not match")
    _require(design.independent_strata is True, "independent stratum sampling is required")
    _require(spec.inputs_fixed_before_selection is True,
             "X, outcome definition, and predictions must be fixed before selection")
    _require(spec.prediction_assumption in (
        "fixed_prespecified", "external_training_independent_of_selection_and_outcomes"
    ), "prediction assumption must be fixed/prespecified or independent external training; not crossfit")
    _require(sample.status == "realized_verified", "sample selection is not realized_verified")
    _require(isinstance(frame.units, tuple) and len(frame.units) > 0, "frame must be a nonempty tuple")
    _require(isinstance(design.strata, tuple) and len(design.strata) > 0,
             "strata must be a nonempty tuple")
    _require(all(isinstance(row, FrameUnit) for row in frame.units), "invalid frame row schema")
    _require(all(isinstance(row, Stratum) for row in design.strata), "invalid stratum row schema")
    _require(isinstance(frame.covariate_names, tuple), "covariate_names must be a tuple")
    _unique(frame.covariate_names, "covariate name")
    _unique([row.unit_id for row in frame.units], "frame unit ID")
    _unique([row.stratum_id for row in design.strata], "stratum ID")
    strata = {row.stratum_id: row for row in design.strata}
    units = {row.unit_id: row for row in frame.units}
    for row in design.strata:
        _require(type(row.population_n) is int and type(row.sample_n) is int,
                 "stratum sizes must be integers, not booleans or strings")
        _require(0 < row.sample_n <= row.population_n, "require 0 < n_h <= N_h")
        expected_method = "census" if row.sample_n == row.population_n else "srswor"
        _require(row.method == expected_method, "stratum method must match census or srswor sizes")
        _require(sum(unit.stratum_id == row.stratum_id for unit in frame.units) == row.population_n,
                 "stratum population size does not match full frame")
    for row in frame.units:
        _identifier(row.stratum_id, "unit stratum ID")
        _require(row.stratum_id in strata, "unit has an unknown stratum")
        _number(row.inclusion_probability, "inclusion probability")
        _number(row.prediction, "prediction")
        _require(isinstance(row.covariates, tuple)
                 and len(row.covariates) == len(frame.covariate_names),
                 "covariates must match the full fixed column schema")
        for value in row.covariates:
            _number(value, "covariate")
        stratum = strata[row.stratum_id]
        pi = row.inclusion_probability
        _require(0 < pi <= 1, "inclusion probability must be in (0,1]")
        # Only floating-point representation tolerance; never accept rounded survey weights.
        _require(math.isclose(pi, stratum.sample_n / stratum.population_n,
                              rel_tol=1e-12, abs_tol=0),
                 "inclusion probability disagrees with the recorded SRSWOR design")
    _require(isinstance(sample.selected_unit_ids, tuple), "selected_unit_ids must be a tuple")
    _unique(sample.selected_unit_ids, "selected unit ID")
    _require(set(sample.selected_unit_ids) <= set(units), "selected ID is outside the frame")
    for row in design.strata:
        _require(sum(units[unit_id].stratum_id == row.stratum_id
                     for unit_id in sample.selected_unit_ids) == row.sample_n,
                 "realized sample count does not match n_h; do not infer sample from responses")
    _require(isinstance(request.responses, tuple)
             and all(isinstance(row, HumanResponse) for row in request.responses),
             "responses must follow the tuple schema")
    _unique([row.unit_id for row in request.responses], "response unit ID")
    _require({row.unit_id for row in request.responses} == set(sample.selected_unit_ids),
             "response coverage must equal the actual selection; nonresponse is not unsampled")
    for row in request.responses:
        _require(row.frame_id == frame.frame_id and row.selection_id == sample.selection_id
                 and row.outcome_id == spec.outcome_id, "response frame/selection/outcome IDs do not match")
        _require(row.response_status == "completed", "selected unit has nonresponse or incomplete review")
        _require(row.outcome_status == "known", "unknown, censored, or unresolved outcomes are rejected")
        _require(row.downstream_eligible is True, "response fails downstream outcome eligibility")
        _number(row.value, "human outcome")
        _require(row.value in (0, 1), "human outcome must be a prespecified numeric binary 0/1")
        permitted_origins = ("synthetic",) if request.mode == "synthetic" else (
            "human_coded", "human_confirmed_ai"
        )
        _require(row.label_origin in permitted_origins,
                 "outcome provenance is not documented human review (or explicit synthetic data)")
        _identifier(row.reviewer_id, "reviewer_id")
        _identifier(row.review_record_id, "review_record_id")
        try:
            parsed_date = date.fromisoformat(row.reviewed_at)
        except (ValueError, TypeError) as exc:
            raise InputError("reviewed_at must be an actual ISO date YYYY-MM-DD") from exc
        _require(parsed_date.isoformat() == row.reviewed_at, "review date must use YYYY-MM-DD")
    core_ids = [frame.frame_id, design.design_id, sample.selection_id, *units]
    if request.mode == "synthetic":
        _require(all(value.startswith("synthetic:") for value in core_ids),
                 "synthetic requests require synthetic: frame, design, selection, and unit IDs")
    else:
        _require(not any(value.startswith("synthetic:") for value in core_ids),
                 "synthetic IDs cannot be used for actual-data estimates")
    _require(all(isinstance(row, Approval) for row in approvals), "invalid approval record schema")
    matches = [row for row in approvals if (row.frame_id, row.design_id, row.mode)
               == (frame.frame_id, design.design_id, request.mode)]
    _require(len(matches) == 1, "exactly one separately vetted frame/design approval is required")
    approval = matches[0]
    _require(approval.status == "approved", "external approval is not approved")
    _identifier(approval.approved_by, "approved_by")
    _identifier(approval.approval_record_id, "approval_record_id")
    _require(approval.spec_sha256 == specification_sha256(request),
             "frozen specification differs from the approved content hash")
    return approval


def _linear_functional(request: Request, weights: np.ndarray):
    """Pure finite-design calculation after validation; columns are fixed a_i."""
    units = sorted(request.frame.units, key=lambda row: row.unit_id)
    responses = {row.unit_id: row.value for row in request.responses}
    dimension = weights.shape[0]
    point = np.zeros(dimension)
    covariance = np.zeros((dimension, dimension))
    unsupported = []
    for stratum in sorted(request.design.strata, key=lambda row: row.stratum_id):
        full = [i for i, row in enumerate(units) if row.stratum_id == stratum.stratum_id]
        selected = [i for i in full if units[i].unit_id in responses]
        y = np.array([responses[units[i].unit_id] for i in selected], dtype=float)
        if stratum.sample_n == stratum.population_n:
            # Exact census identity avoids cancellation of large auxiliary predictions.
            point += weights[:, selected] @ y
            continue
        predictions = np.array([units[i].prediction for i in full], dtype=float)
        if np.any((1.0 - predictions) == -predictions):
            raise NumericalError("predictions are too large to resolve binary outcome residuals")
        residuals = y - np.array([units[i].prediction for i in selected], dtype=float)
        weighted_residuals = weights[:, selected] * residuals
        pi = np.array([units[i].inclusion_probability for i in selected], dtype=float)
        point += weights[:, full] @ predictions + (weighted_residuals / pi).sum(axis=1)
        if stratum.sample_n == 1:
            unsupported.append(stratum.stratum_id)
            continue
        centered = weighted_residuals - weighted_residuals.mean(axis=1, keepdims=True)
        sample_covariance = centered @ centered.T / (stratum.sample_n - 1)
        factor = (stratum.population_n * (stratum.population_n - stratum.sample_n)
                  / stratum.sample_n)
        covariance += factor * sample_covariance
    return point, None if unsupported else covariance, tuple(unsupported)


def _estimate(request: Request, approvals: Sequence[Approval], projection: bool) -> Estimate:
    approval = validate_sources(request, approvals=approvals)
    units = sorted(request.frame.units, key=lambda row: row.unit_id)
    condition = None
    try:
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            if projection:
                _require(len(request.frame.covariate_names) > 0, "fixed-X projection requires columns")
                x = np.array([row.covariates for row in units], dtype=float)
                _require(x.shape[0] >= x.shape[1], "fixed-X design has more columns than rows")
                singular_values = np.linalg.svd(x, compute_uv=False)
                _require(singular_values[-1] > 0, "fixed-X design is rank deficient")
                condition = float(singular_values[0] / singular_values[-1])
                _require(math.isfinite(condition) and condition <= MAX_X_CONDITION,
                         "fixed-X design is rank deficient or numerically ill-conditioned")
                # QR evaluates (X'X)^(-1)X' without squaring the condition number.
                q, r = np.linalg.qr(x, mode="reduced")
                weights = np.linalg.solve(r, q.T)
                names = request.frame.covariate_names
            else:
                weights = np.full((1, len(units)), 1 / len(units))
                names = ("mean",)
            point, covariance, unsupported = _linear_functional(request, weights)
            if not np.isfinite(point).all() or (covariance is not None
                                               and not np.isfinite(covariance).all()):
                raise NumericalError("nonfinite estimate; no fallback, clipping, or regularization")
            if covariance is not None and np.any(np.diag(covariance) < 0):
                raise NumericalError("negative computed variance; no fallback")
            errors = None if covariance is None else tuple(float(v) for v in np.sqrt(np.diag(covariance)))
    except (np.linalg.LinAlgError, FloatingPointError, OverflowError) as exc:
        raise NumericalError(f"numeric estimation failed: {exc}") from exc
    all_census = all(row.sample_n == row.population_n for row in request.design.strata)
    variance_status = ("unavailable_singleton_noncensus" if unsupported else
                       "census_zero_label_selection_only" if all_census else
                       "estimated_stratified_srswor")
    origins = sorted({row.label_origin for row in request.responses})
    return Estimate(
        estimand="finite_frame_fixed_x_linear_projection" if projection else "finite_frame_outcome_mean",
        mode=request.mode, frame_id=request.frame.frame_id, design_id=request.design.design_id,
        selection_id=request.selection.selection_id, outcome_id=request.spec.outcome_id,
        approval_record_id=approval.approval_record_id, spec_sha256=approval.spec_sha256,
        input_sha256=_input_sha256(request), parameter_names=names,
        point=tuple(float(v) for v in point),
        covariance=None if covariance is None else tuple(tuple(float(v) for v in row) for row in covariance),
        standard_errors=errors, variance_status=variance_status, unsupported_strata=unsupported,
        frame_n=len(units), selected_n=len(request.selection.selected_unit_ids),
        response_n=len(request.responses),
        response_origins=tuple((origin, sum(row.label_origin == origin for row in request.responses))
                               for origin in origins),
        prediction_assumption=request.spec.prediction_assumption, x_condition_number=condition,
    )


def estimate_mean(request: Request, *, approvals: Sequence[Approval] = ()) -> Estimate:
    """Fixed prediction mean plus known-pi human residual correction. No clipping."""
    return _estimate(request, approvals, projection=False)


def estimate_fixed_x(request: Request, *, approvals: Sequence[Approval] = ()) -> Estimate:
    """Full-frame fixed-X linear projection, not regression on the labeled subset.

    No intercept, standardization, complete-case selection, ridge, or fitted
    prediction model is supplied implicitly. All X columns must be prespecified.
    """
    return _estimate(request, approvals, projection=True)
