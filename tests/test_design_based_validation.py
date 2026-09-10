"""Exhaustive finite-design checks; every numeric fixture is artificial."""

import csv
from dataclasses import asdict, replace
from itertools import combinations, product
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import design_based_validation as db


def fixture(sizes=((3, 2), (2, 2)), y=None, predictions=None, x=None, selected=None):
    """Synthetic approval/response metadata, never evidence about actual issuers."""
    n = sum(population for population, _ in sizes)
    y = tuple(i % 2 for i in range(n)) if y is None else tuple(y)
    predictions = tuple((i % 3 - 1) * 0.7 for i in range(n)) if predictions is None else predictions
    x = tuple((1.0, float(i)) for i in range(n)) if x is None else x
    strata, units, chosen = [], [], []
    index = 0
    for h, (population, sample) in enumerate(sizes):
        sid = f"synthetic:h{h}"
        strata.append(db.Stratum(sid, population, sample, "census" if sample == population else "srswor"))
        for j in range(population):
            uid = f"synthetic:u{index:03d}"
            units.append(db.FrameUnit(uid, sid, sample / population, predictions[index], tuple(x[index])))
            if j < sample:
                chosen.append(uid)
            index += 1
    chosen = tuple(chosen) if selected is None else tuple(selected)
    frame = db.Frame("synthetic:frame", "frozen_approved", "issuer", "all_units_verified",
                     "synthetic:eligibility-record", tuple(f"x{j}" for j in range(len(x[0]))), tuple(units))
    design = db.Design("synthetic:design", frame.frame_id, "approved", tuple(strata), True,
                       "synthetic:probability-record")
    spec = db.AnalysisSpec("synthetic:binary-outcome", "synthetic:outcome-protocol", "fixed_prespecified",
                           "synthetic:prediction-record", "synthetic:x-record", True)
    sample = db.Selection(frame.frame_id, design.design_id, "synthetic:selection", "realized_verified",
                          chosen, "synthetic:selection-record", "synthetic:selection-verification")
    responses = tuple(db.HumanResponse(
        uid, frame.frame_id, sample.selection_id, spec.outcome_id, "completed", "known", True,
        y[int(uid.rsplit("u", 1)[1])], "synthetic", "synthetic:reviewer", "2026-09-10",
        f"synthetic:review-record-{uid}"
    ) for uid in chosen)
    return db.Request("synthetic", frame, design, spec, sample, responses)


def approval(request):
    return db.Approval(request.frame.frame_id, request.design.design_id, request.mode,
                       db.specification_sha256(request), "approved", "synthetic:approver",
                       "synthetic:approval-record")


def run(request, projection=False, approvals=None):
    approvals = (approval(request),) if approvals is None else approvals
    method = db.estimate_fixed_x if projection else db.estimate_mean
    return method(request, approvals=approvals)


def change_unit(request, index=0, **kwargs):
    units = list(request.frame.units)
    units[index] = replace(units[index], **kwargs)
    return replace(request, frame=replace(request.frame, units=tuple(units)))


def change_response(request, index=0, **kwargs):
    rows = list(request.responses)
    rows[index] = replace(rows[index], **kwargs)
    return replace(request, responses=tuple(rows))


class ExactDesignTests(unittest.TestCase):
    def test_actual_schema_rejects_synthetic_provenance(self):
        from build_validation_inference_status import decode_request

        # Artificial schema-only fixture; never a record of actual human review.
        def unmark(value):
            if isinstance(value, str):
                return value.removeprefix("synthetic:")
            if isinstance(value, dict):
                return {key: unmark(item) for key, item in value.items()}
            if isinstance(value, (list, tuple)):
                return [unmark(item) for item in value]
            return value

        raw = unmark(asdict(fixture()))
        raw["mode"] = "actual"
        for row in raw["responses"]:
            row["label_origin"] = "human_coded"
        request = decode_request(raw)
        approved = replace(approval(request), approved_by="test-approver",
                           approval_record_id="test-approval")
        db.validate_sources(request, approvals=(approved,))
        mutations = [
            replace(request, frame=replace(request.frame, eligibility_record_id="synthetic:record")),
            replace(request, design=replace(request.design, probability_record_id="synthetic:record")),
        ]
        for name in ("outcome_definition_record_id", "prediction_record_id", "covariate_record_id"):
            mutations.append(replace(request, spec=replace(request.spec, **{name: "synthetic:record"})))
        for name in ("selection_record_id", "verification_record_id"):
            mutations.append(replace(request, selection=replace(request.selection, **{name: "synthetic:record"})))
        for name in ("reviewer_id", "review_record_id"):
            mutations.append(change_response(request, **{name: "SYNTHETIC:record"}))
        for changed in mutations:
            with self.subTest(changed=changed):
                refreshed = replace(approved, spec_sha256=db.specification_sha256(changed))
                with self.assertRaisesRegex(db.InputError, "synthetic provenance"):
                    db.validate_sources(changed, approvals=(refreshed,))
        for name in ("approved_by", "approval_record_id"):
            with self.subTest(approval_field=name):
                changed = replace(approved, **{name: "synthetic:record"})
                with self.assertRaisesRegex(db.InputError, "synthetic provenance"):
                    db.validate_sources(request, approvals=(changed,))

    def enumerate_design(self, sizes, y, predictions, x):
        base = fixture(sizes, y, predictions, x)
        choices = [list(combinations([u.unit_id for u in base.frame.units if u.stratum_id == h.stratum_id],
                                     h.sample_n)) for h in base.design.strata]
        points = [[], []]
        variances = [[], []]
        has_singleton = any(sample == 1 < population for population, sample in sizes)
        frozen_approval = approval(base)
        for selection in product(*choices):
            ids = tuple(uid for stratum in selection for uid in stratum)
            request = fixture(sizes, y, predictions, x, ids)
            pseudo_y = np.array(predictions, dtype=float)
            for i, unit in enumerate(request.frame.units):
                if unit.unit_id in ids:
                    pseudo_y[i] += (y[i] - predictions[i]) / unit.inclusion_probability
            oracles = (np.array([np.mean(pseudo_y)]), np.linalg.lstsq(x, pseudo_y, rcond=None)[0])
            for projection in (False, True):
                estimate = run(request, projection, (frozen_approval,))
                np.testing.assert_allclose(estimate.point, oracles[projection], atol=1e-10, rtol=0)
                points[projection].append(estimate.point)
                self.assertEqual(estimate.frame_n, len(y))
                self.assertEqual(estimate.response_n, len(ids))
                if has_singleton:
                    self.assertIsNone(estimate.covariance)
                    self.assertIsNone(estimate.standard_errors)
                    self.assertEqual(estimate.variance_status, "unavailable_singleton_noncensus")
                else:
                    variances[projection].append(estimate.covariance)
                    covariance = np.array(estimate.covariance)
                    np.testing.assert_allclose(covariance, covariance.T, atol=1e-12, rtol=0)
                    self.assertGreaterEqual(np.linalg.eigvalsh(covariance).min(), -1e-12)
        targets = (np.array([np.mean(y)]), np.linalg.lstsq(x, y, rcond=None)[0])
        for projection in (False, True):
            values = np.array(points[projection])
            np.testing.assert_allclose(values.mean(axis=0), targets[projection], atol=1e-10, rtol=0)
            centered = values - targets[projection]
            exact_covariance = centered.T @ centered / len(values)
            if not has_singleton:
                np.testing.assert_allclose(np.mean(variances[projection], axis=0), exact_covariance,
                                           atol=1e-10, rtol=0)
        return len(points[0])

    def test_all_binary_populations_all_allocations_two_strata(self):
        count = 0
        x = tuple((1.0, float(i), float(i * i)) for i in range(5))
        predictions = (-0.4, 0.2, 1.6, -0.1, 0.9)
        for n_a, n_b in product(range(1, 4), range(1, 3)):
            for y in product((0, 1), repeat=5):
                with self.subTest(n_a=n_a, n_b=n_b, y=y):
                    count += self.enumerate_design(((3, n_a), (2, n_b)), y, predictions, x)
        self.assertEqual(count, 672)

    def test_unequal_fractions_multicolumn_x_and_census_singleton(self):
        x = tuple((1.0, float(i - 3), float(i % 3)) for i in range(8))
        count = self.enumerate_design(((4, 2), (3, 2), (1, 1)),
                                     (1, 0, 1, 0, 1, 1, 0, 0),
                                     (0.9, 0.2, -0.7, 1.4, 0.8, 0.0, -0.1, 1.1), x)
        self.assertEqual(count, 18)

    def test_zero_predictions_horvitz_thompson_special_case(self):
        self.enumerate_design(((4, 2), (3, 2)), (1, 1, 0, 1, 0, 0, 1), (0,) * 7,
                              tuple((1.0, float(i)) for i in range(7)))

    def test_perfect_predictions_all_samples_zero_covariance(self):
        y = (0, 1, 1, 0, 1)
        self.enumerate_design(((3, 2), (2, 2)), y, y,
                              tuple((1.0, float(i)) for i in range(5)))
        for subset in combinations(range(3), 2):
            r = fixture(y=y, predictions=y, selected=tuple(f"synthetic:u{i:03d}" for i in (*subset, 3, 4)))
            for projection in (False, True):
                np.testing.assert_array_equal(np.array(run(r, projection).covariance), 0)

    def test_constant_residual_zero_mean_variance_not_zero_slope_variance(self):
        r = fixture(((4, 2),), y=(1, 1, 1, 1), predictions=(0.7,) * 4)
        self.assertAlmostEqual(run(r).covariance[0][0], 0, places=15)
        self.assertGreater(run(r, True).covariance[1][1], 0)
        self.enumerate_design(((4, 2),), (1,) * 4, (0.7,) * 4,
                              tuple((1.0, float(i)) for i in range(4)))

    def test_census_large_bad_predictions_no_cancellation(self):
        r = fixture(((2, 2), (1, 1)), y=(1, 0, 1), predictions=(1e300, -1e300, 1e300))
        for projection in (False, True):
            result = run(r, projection)
            truth = np.linalg.lstsq([u.covariates for u in r.frame.units], (1, 0, 1), rcond=None)[0]
            np.testing.assert_allclose(result.point, truth if projection else (2 / 3,), atol=1e-12)
            np.testing.assert_array_equal(np.array(result.covariance), 0)
            self.assertEqual(result.variance_status, "census_zero_label_selection_only")
            self.assertIn("Excludes measurement", result.uncertainty_scope)

    def test_single_unit_census_and_empty_x_mean(self):
        r = fixture(((1, 1),), y=(1,), x=((1.0,),))
        self.assertEqual(run(r).point, (1,))
        self.assertEqual(run(r, True).point, (1,))
        empty = fixture(((2, 2),), x=((), ()))
        self.assertEqual(run(empty).point, (0.5,))
        with self.assertRaisesRegex(db.InputError, "requires columns"):
            run(empty, True)

    def test_singleton_does_not_borrow_or_assume_zero_variance(self):
        r = fixture(((3, 1), (3, 2), (1, 1)))
        for projection in (False, True):
            result = run(r, projection)
            self.assertIsNone(result.covariance)
            self.assertIsNone(result.standard_errors)
            self.assertEqual(result.unsupported_strata, ("synthetic:h0",))
            self.assertTrue(np.isfinite(result.point).all())
        perfect = fixture(((2, 1),), y=(0, 1), predictions=(0, 1))
        self.assertIsNone(run(perfect).covariance)

    def test_intercept_only_equals_mean_including_variance(self):
        r = fixture(x=((1,),) * 5)
        np.testing.assert_allclose(run(r).point, run(r, True).point, atol=1e-12)
        np.testing.assert_allclose(run(r).covariance, run(r, True).covariance, atol=1e-12)

    def test_sample_x_need_not_be_full_rank_and_no_implicit_intercept(self):
        r = fixture(((3, 1),), x=((1, 0, 0), (1, 1, 0), (1, 0, 1)))
        self.assertEqual(len(run(r, True).point), 3)
        r = fixture(((3, 3),), y=(0, 1, 1), x=((1,), (2,), (3,)))
        self.assertAlmostEqual(run(r, True).point[0], 5 / 14)

    def test_row_order_invariance_and_hashes(self):
        r = fixture()
        shuffled = replace(r, frame=replace(r.frame, units=tuple(reversed(r.frame.units))),
                           design=replace(r.design, strata=tuple(reversed(r.design.strata))),
                           selection=replace(r.selection, selected_unit_ids=tuple(reversed(r.selection.selected_unit_ids))),
                           responses=tuple(reversed(r.responses)))
        for projection in (False, True):
            self.assertEqual(run(r, projection), run(shuffled, projection, (approval(r),)))

    def test_negative_and_above_one_points_are_not_clipped(self):
        for prediction, expected in (((2, 2, 0), -2 / 3), ((0, 0, 4), 4 / 3)):
            r = fixture(((3, 2),), y=(0, 0, 0), predictions=prediction, x=((1,),) * 3)
            for projection in (False, True):
                self.assertAlmostEqual(run(r, projection).point[0], expected)

    def test_external_training_allowed_only_as_explicit_fixed_assumption(self):
        r = fixture()
        r = replace(r, spec=replace(r.spec, prediction_assumption="external_training_independent_of_selection_and_outcomes"))
        self.assertEqual(run(r).prediction_assumption, r.spec.prediction_assumption)

    def test_crossfit_alone_counterexample_under_fixed_size_sampling(self):
        # Two fixed folds, one unit each; the training rule returns the other
        # fold's observed Y, or zero if no label is selected in that fold.
        values = []
        for selected in (0, 1):
            y = np.ones(2)
            inclusion = np.zeros(2)
            inclusion[selected] = 1
            predictions = np.array([inclusion[1] * y[1], inclusion[0] * y[0]])
            values.append(np.mean(predictions + inclusion / 0.5 * (y - predictions)))
        self.assertEqual(values, [1.5, 1.5])
        self.assertNotEqual(np.mean(values), 1.0)


class GuardTests(unittest.TestCase):
    def assertRejected(self, request, pattern, projection=False, approvals=()):
        method = db.estimate_fixed_x if projection else db.estimate_mean
        with self.assertRaisesRegex(db.InputError, pattern):
            method(request, approvals=approvals)

    def test_default_has_no_approval_or_actual_data_loader(self):
        self.assertRejected(fixture(), "separately vetted")
        self.assertRejected({}, "Request")

    def test_proposals_and_outcome_eligibility(self):
        r = fixture()
        for field, value, pattern in (("status", "proposal", "frozen_approved"),
                                       ("unit_type", "disclosure", "issuer"),
                                       ("outcome_eligibility_status", "scope_eligible_only", "downstream outcome eligibility")):
            self.assertRejected(replace(r, frame=replace(r.frame, **{field: value})), pattern)
        self.assertRejected(replace(r, design=replace(r.design, status="proposal_only_PI_approval_required")), "not approved")
        self.assertRejected(replace(r, selection=replace(r.selection, status="planned")), "not realized")

    def test_actual_current_67_proposal_rejected_without_inventing_labels(self):
        with (ROOT / "data/validation/probability_validation_frame_candidate.csv").open() as handle:
            rows = list(csv.DictReader(handle))
        with (ROOT / "data/validation/probability_validation_sampling_design.csv").open() as handle:
            designs = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 67)
        self.assertEqual(sum(row["screen_status"] == "screened_no_direct_formal_event" for row in rows), 10)
        self.assertTrue(all(row["random_draw_executed"] == "false" for row in rows))
        self.assertTrue(all(row["approval_status"] == "proposal_only_PI_approval_required" for row in designs))
        self.assertRejected(rows, "Request")
        # No approved IDs, numeric predictions, X, response values, or selection
        # are supplied. Existing scope eligibility is not outcome eligibility.
        r = db.Request("actual", db.Frame("", "proposal", "issuer", "unverified", "", (), tuple(
            db.FrameUnit(row["validation_unit_id"], row["frozen_stratum_id"],
                         float(row["inclusion_probability"]), None, ()) for row in rows
        )), db.Design("", "", "proposal", (), False, ""),
            db.AnalysisSpec("", "", "", "", "", False),
            db.Selection("", "", "", "not_executed", (), "", ""), ())
        for projection in (False, True):
            self.assertRejected(r, "frozen_approved", projection)

    def test_missing_mismatched_duplicate_and_stale_approvals(self):
        r = fixture()
        a = approval(r)
        for invalid in (replace(a, frame_id="wrong"), replace(a, design_id="wrong"), replace(a, mode="actual")):
            self.assertRejected(r, "separately vetted", approvals=(invalid,))
        self.assertRejected(r, "separately vetted", approvals=(a, a))
        self.assertRejected(r, "not approved", approvals=(replace(a, status="pending"),))
        for field in ("approved_by", "approval_record_id"):
            self.assertRejected(r, "nonmissing", approvals=(replace(a, **{field: ""}),))
        self.assertRejected(change_unit(r, prediction=0.6), "content hash", approvals=(a,))
        self.assertRejected(change_unit(r, covariates=(1, 2.5)), "content hash", approvals=(a,))
        self.assertRejected(replace(r, spec=replace(r.spec, prediction_record_id="different")), "content hash", approvals=(a,))

    def test_nonresponse_never_becomes_unsampled_and_extras_rejected(self):
        r = fixture()
        self.assertRejected(replace(r, responses=r.responses[:-1]), "response coverage")
        self.assertRejected(replace(r, selection=replace(r.selection, selected_unit_ids=r.selection.selected_unit_ids[:-1]),
                                    responses=r.responses[:-1]), "realized sample count")
        self.assertRejected(change_response(r, unit_id="synthetic:u002"), "response coverage")
        for value in ("nonresponse", "partial", "refused", "pending", "censored"):
            self.assertRejected(change_response(r, response_status=value), "nonresponse")
        self.assertRejected(change_response(r, downstream_eligible=False), "downstream outcome eligibility")
        self.assertRejected(change_response(r, downstream_eligible="true"), "downstream outcome eligibility")

    def test_unknown_censored_or_categorical_outcomes_never_recode_to_zero(self):
        r = fixture()
        for value in (None, "", "unknown", "unclear", "screened_no_direct_formal_event", "nominal_exit",
                      "liquidation", "0", "1", np.nan, np.inf, -np.inf, True, False):
            with self.subTest(value=value):
                self.assertRejected(change_response(r, value=value), "finite numeric")
        for value in (-1, 0.5, 2):
            self.assertRejected(change_response(r, value=value), "numeric binary")
        for status in ("unknown", "censored", "unclear", "unresolved"):
            self.assertRejected(change_response(r, outcome_status=status, value=0), "outcomes are rejected")

    def test_duplicate_unit_stratum_sample_response_and_covariate_ids(self):
        r = fixture()
        self.assertRejected(replace(r, frame=replace(r.frame, units=r.frame.units + (r.frame.units[0],))), "duplicate frame")
        self.assertRejected(replace(r, design=replace(r.design, strata=r.design.strata + (r.design.strata[0],))), "duplicate stratum")
        self.assertRejected(replace(r, selection=replace(r.selection, selected_unit_ids=r.selection.selected_unit_ids + (r.selection.selected_unit_ids[0],))), "duplicate selected")
        self.assertRejected(replace(r, responses=r.responses + (r.responses[0],)), "duplicate response")
        self.assertRejected(replace(r, frame=replace(r.frame, covariate_names=("x", "x"))), "duplicate covariate")

    def test_unit_ids_not_silently_normalized_or_joined_to_other_units(self):
        r = fixture()
        self.assertRejected(change_unit(r, unit_id=" synthetic:u000"), "nonmissing")
        self.assertRejected(replace(r, selection=replace(r.selection, selected_unit_ids=("synthetic:absent",))), "outside the frame")
        self.assertRejected(change_unit(r, stratum_id="missing"), "population size")
        for field in ("frame_id", "selection_id", "outcome_id"):
            self.assertRejected(change_response(r, **{field: "wrong"}), "IDs do not match")
        self.assertRejected(replace(r, design=replace(r.design, frame_id="wrong")), "frame IDs")
        self.assertRejected(replace(r, selection=replace(r.selection, design_id="wrong")), "design IDs")

    def test_pi_not_guessed_rounded_or_substituted(self):
        r = fixture()
        for value in (None, "", "0.666667", True, np.nan, np.inf):
            self.assertRejected(change_unit(r, inclusion_probability=value), "finite numeric")
        for value in (0, -0.1, 1.1):
            self.assertRejected(change_unit(r, inclusion_probability=value), r"in \(0,1\]")
        for value in (1, 0.5, 0.666667, 0.666666666):
            self.assertRejected(change_unit(r, inclusion_probability=value), "disagrees")
        self.assertRejected(change_unit(r, index=3, inclusion_probability=0.999999), "disagrees")

    def test_stratum_counts_methods_and_dependence_guards(self):
        r = fixture()
        for field, value, pattern in (("population_n", 0, "0 < n_h"), ("sample_n", 0, "0 < n_h"),
                                       ("sample_n", 4, "0 < n_h"), ("sample_n", 1.5, "integers"),
                                       ("sample_n", True, "integers"), ("population_n", 4, "population size"),
                                       ("method", "bernoulli", "stratum method"), ("method", "census", "stratum method")):
            bad = replace(r.design.strata[0], **{field: value})
            self.assertRejected(replace(r, design=replace(r.design, strata=(bad, r.design.strata[1]))), pattern)
        self.assertRejected(replace(r, design=replace(r.design, independent_strata=False)), "independent stratum")
        self.assertRejected(replace(r, design=replace(r.design, independent_strata="true")), "independent stratum")

    def test_frame_covariates_predictions_and_prediction_assumptions(self):
        r = fixture()
        for value in (None, "1", True, np.nan, np.inf, -np.inf):
            self.assertRejected(change_unit(r, covariates=(1, value)), "finite numeric")
            self.assertRejected(change_unit(r, prediction=value), "finite numeric")
        self.assertRejected(change_unit(r, covariates=(1,)), "column schema")
        self.assertRejected(replace(r, frame=replace(r.frame, units=())), "nonempty")
        self.assertRejected(replace(r, design=replace(r.design, strata=())), "nonempty")
        for assumption in ("crossfit", "cross_fitted_independent", "in_sample_fit", "unknown"):
            self.assertRejected(replace(r, spec=replace(r.spec, prediction_assumption=assumption)), "not crossfit")
        self.assertRejected(replace(r, spec=replace(r.spec, inputs_fixed_before_selection=False)), "fixed before")

    def test_rank_and_numerical_condition_rejection_no_silent_ridge(self):
        for x in (((1, 1),) * 5, ((1, 0),) * 5,
                  tuple((1, i * 1e-12) for i in range(5))):
            r = fixture(x=x)
            self.assertRejected(r, "rank deficient|ill-conditioned", True, (approval(r),))
        r = fixture(((1, 1),), x=((1, 2),))
        self.assertRejected(r, "more columns", True, (approval(r),))

    def test_numeric_and_point_errors_propagate(self):
        r = fixture(predictions=(1e308,) * 5)
        with self.assertRaises(db.NumericalError):
            run(r)
        with patch.object(db, "_linear_functional", side_effect=ValueError("sentinel point failure")):
            with self.assertRaisesRegex(ValueError, "sentinel point failure"):
                run(fixture())

    def test_provenance_and_synthetic_actual_separation(self):
        r = fixture()
        for origin in ("ai_only", "codex", "working_reference", "human_coded"):
            self.assertRejected(change_response(r, label_origin=origin), "provenance")
        for field in ("reviewer_id", "review_record_id"):
            self.assertRejected(change_response(r, **{field: "not_reported"}), "nonmissing")
        for value in ("", "not_reported", "2026-02-30", "20260910", None):
            self.assertRejected(change_response(r, reviewed_at=value), "ISO date|YYYY-MM-DD")
        self.assertRejected(replace(r, mode="actual"), "provenance")
        r = change_unit(r, index=2, unit_id="mv_real_unit")
        self.assertRejected(r, "synthetic requests")

    def test_actual_path_rejects_partially_relabelled_synthetic_records(self):
        # Changing core IDs and label origins cannot authorize synthetic metadata.
        r = fixture()
        convert = lambda value: value.replace("synthetic:", "artificial-contract-check:")
        r = replace(r, mode="actual",
                    frame=replace(r.frame, frame_id=convert(r.frame.frame_id),
                                  units=tuple(replace(u, unit_id=convert(u.unit_id)) for u in r.frame.units)),
                    design=replace(r.design, frame_id=convert(r.frame.frame_id), design_id=convert(r.design.design_id)),
                    selection=replace(r.selection, frame_id=convert(r.frame.frame_id),
                                      design_id=convert(r.design.design_id), selection_id=convert(r.selection.selection_id),
                                      selected_unit_ids=tuple(map(convert, r.selection.selected_unit_ids))),
                    responses=tuple(replace(row, unit_id=convert(row.unit_id), frame_id=convert(row.frame_id),
                                            selection_id=convert(row.selection_id), label_origin="human_coded")
                                    for row in r.responses))
        r = change_response(r, label_origin="human_confirmed_ai")
        self.assertRejected(r, "synthetic provenance", approvals=(approval(r),))
        self.assertRejected(change_response(r, label_origin="ai_only"), "provenance")
        self.assertRejected(r, "separately vetted")


if __name__ == "__main__":
    unittest.main()
