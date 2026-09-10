# Finite-frame estimation

## Scope

This is a future-input implementation of a finite-frame difference estimator,
also expressible as an augmented inverse-probability weighted (AIPW) mean, and
its fixed-X linear-projection counterpart. It does not fit a learned model or
implement the full cross-fitted DSL procedure. There is no actual-data adapter,
CLI, bundled actual approval registry, automatic label conversion, or change to
the project's main analysis.

Every numeric example in the tests is artificial. The read-only current-data
check supplies no observed outcomes or invented approvals. At the base commit,
the 67 scope-eligible issuers include ten with no directly screened formal event.
Scope eligibility does not make an exit outcome defined. Such a screen result
is neither institutional-change zero nor a fifth exit category. Before using
this engine, the coordinator must verify that the prespecified binary outcome
is defined for every member of a separately approved analytical frame. Neither
the 67-unit proposal nor the 94-case reference file is automatically that frame.

## Verified source

Naoki Egami, Musashi Hinck, Brandon M. Stewart, and Hanying Wei (2023),
"Using Imperfect Surrogates for Downstream Inference: Design-based Supervised
Learning for Social Science Applications of Large Language Models," Advances
in Neural Information Processing Systems 36. The official
[publication page](https://proceedings.neurips.cc/paper_files/paper/2023/hash/d862f7f5445255090de13b825b880d59-Abstract-Conference.html)
and [published PDF](https://proceedings.neurips.cc/paper_files/paper/2023/file/d862f7f5445255090de13b825b880d59-Paper-Conference.pdf)
were opened on 2026-09-10. Section 4, Equation 4 uses a prediction plus a
known-probability labeled residual correction. Algorithm 1 uses cross-fitting;
Proposition 1 states consistency and asymptotic normality. These statements do
not by themselves establish the exact fixed-size finite-population covariance
implemented here. The following derivation conditions on a fixed finite frame
and fixed predictions and establishes that narrower result directly.

## Targets and assumptions

Let F be the assembled issuer frame, of size N. Each issuer has exactly one
prespecified, well-defined binary outcome Y_i, fixed finite prediction m_i,
and, for projection, a finite covariate vector x_i. Define

```text
mu_F = N^(-1) sum_F Y_i
G = sum_F x_i x_i'
beta_F = G^(-1) sum_F x_i Y_i.
```

The projection is a descriptive finite-frame least-squares target, not a causal
parameter or an asserted correctly specified conditional mean. X must have full
column rank; the engine inserts no intercept, standardization, missing-value
imputation, or subset restriction. The mean alone permits an empty X schema.

Within each prespecified stratum h, select exactly n_h of N_h units uniformly
without replacement, independently across strata. The actual inclusion
probabilities are known, positive, and equal to n_h/N_h. Census strata have
n_h=N_h. All selected units must have completed documented human responses.
The selected roster exists independently of the received responses. Outcome
nonresponse, undefined outcomes, and eligibility changes are not handled by
discarding rows or altering denominators.

Predictions, X, frame membership, the outcome definition, and design are fixed
relative to selection. The permitted prediction assumptions are prespecified
fixed predictions or external training independent of selection and validation
outcomes, conditioning on the externally fitted predictions. This engine does
not check training data or prove independence from declarations. A frozen
prediction file built using the realized sample is insufficient. The caller's
approval review must establish the actual timing and independence conditions.

## Point estimates

Write e_i=Y_i-m_i and R_i for the actual selection indicator. The mean is

```text
mu_hat = (sum_F m_i + sum_{i:R_i=1} e_i/pi_i) / N.
```

Because E_d[R_i]=pi_i with Y, m, X, and F held fixed,
E_d[mu_hat]=mu_F irrespective of fixed prediction quality. For the fixed-X
projection, apply the correction to the outcome moment:

```text
beta_hat = G^(-1) [sum_F x_i m_i + sum_{i:R_i=1} x_i e_i/pi_i].
```

G is known from the whole frame rather than estimated using selected units, so
E_d[beta_hat]=beta_F exactly in mathematical arithmetic. Full rank of the sampled
X is not required. Regressing only labeled rows, dividing by an estimated
denominator, estimating G with weights on the sampled X, or fitting logistic
regression would produce different estimators and is not implemented. Poor
fixed predictions can increase design variance. Estimates are not clipped to
[0,1]; clipping would generally destroy design unbiasedness.

## Design covariance

For distinct units in the same non-singleton stratum,
E_d[R_i R_j]=n_h(n_h-1)/(N_h(N_h-1)); independence holds across strata. These
inclusion moments imply the SRSWOR variance of the residual total. If S^2_e,h
uses the full stratum denominator N_h-1, the exact mean variance is

```text
Var_d(mu_hat) = sum_{h:n_h<N_h} (N_h/N)^2 (1-n_h/N_h) S^2_e,h / n_h.
```

For n_h>=2, the sample residual variance s^2_e,h with denominator n_h-1 is
unbiased for S^2_e,h. Substitution gives an unbiased design variance estimator.
No normal approximation, hypothesis test, p-value, or confidence interval is
implied by this variance identity. A sampled stratum can have zero observed
residual variation without establishing zero true design variance.

For coefficients, replace e_i by z_i=x_i e_i, use its within-stratum sample
covariance matrix s_z,h, and transform the residual-total covariance:

```text
V_hat(beta_hat) = G^(-1)
  [sum_{h:n_h<N_h} N_h^2 (1-n_h/N_h) s_z,h / n_h]
  G^(-1)'.
```

This includes every off-diagonal covariance. It is not an OLS model-error,
heteroskedasticity-robust, or city-clustered covariance. The residual here is
Y_i-m_i, not Y_i-x_i'beta_hat. Constant e_i can yield zero mean variance while
coefficient variance is nonzero because x_i varies.

The implementation evaluates both formulas as a known linear functional with
columns a_i: a_i=1/N for the mean, or a_i=G^(-1)x_i for the projection. It sums
the sample covariance of a_i e_i multiplied by N_h(N_h-n_h)/n_h. QR computes
G^(-1)X' without explicitly forming or inverting the Gram matrix.

For n_h=1<N_h, the point estimate remains valid but the unrestricted within-stratum
residual variance cannot be estimated unbiasedly from one observation. The
engine returns covariance=None and standard_errors=None for the whole result,
with the affected strata listed. It does not return a partial covariance as if
it were total uncertainty, pool strata, or assert zero variance even when the
single observed residual is zero.

Census strata contribute exactly zero by definition, including n_h=N_h=1;
there is no attempt to compute an undefined sample variance and multiply it by
zero. A complete census returns the observed human-outcome functional directly,
avoiding auxiliary-prediction cancellation. Its zero covariance concerns only
label selection. Coding error, source availability, eligibility, frame coverage,
broader-population uncertainty, and causal uncertainty remain outside the engine.

## Cross-fitting limitation

Holding out a unit's own label does not make its prediction independent of its
selection indicator under every fixed-size design. Consider N=2, n=1, Y=(1,1),
and two fixed folds, one unit each. Predict unit i using the other fold's
observed label if that fold has one, and zero otherwise. Neither prediction
uses its own label. However, the selected unit has prediction zero and the
unselected unit has prediction one, so the nominal correction produces 1.5
under both legitimate samples although the true mean is 1. The test preserves
this counterexample. It refutes an unconditional extension of this finite-design
formula to arbitrary cross-fitting, not the published DSL theorem under its
own assumptions. Cross-fitted training, fold-specific design conditioning, and
variance for adaptive predictions require a separately justified implementation.

## Interface and trust boundary

The importable module is scripts/design_based_validation.py. The runtime is
Python with NumPy; checks used Python 3.13.4 and NumPy 2.2.6. There is no install
step or added dependency manifest. All record constructors are frozen dataclasses,
and all record collections and covariate vectors use tuples.

```python
validate_sources(request, approvals=(verified_approval,))
estimate_mean(request, approvals=(verified_approval,))
estimate_fixed_x(request, approvals=(verified_approval,))
specification_sha256(request)
```

The first function checks source/schema consistency without estimating anything.
The last computes a fingerprint only. Neither issues approval. Public estimation
always calls the source checks; the private _linear_functional function performs
only arithmetic after those checks. The coordinator may use InputError for a
blocked status in an actual-data adapter but must not turn missing values or
exceptions into zero estimates. NumericalError is distinct and propagates;
there is no alternate estimator on failure.

| Record | Fields and required values |
| --- | --- |
| Request | mode: actual or synthetic; frame; design; spec; selection; responses |
| FrameUnit | unit_id; stratum_id; inclusion_probability (finite numeric known pi); prediction (finite numeric m); covariates (finite numeric tuple) |
| Frame | frame_id; status=frozen_approved; unit_type=issuer; outcome_eligibility_status=all_units_verified; eligibility_record_id; covariate_names (unique ordered names); units (full frame) |
| Stratum | stratum_id; population_n; sample_n (positive integers n<=N); method=census if n=N, otherwise srswor |
| Design | design_id; frame_id; status=approved; strata; independent_strata=True; probability_record_id |
| AnalysisSpec | outcome_id; outcome_definition_record_id; prediction_assumption=fixed_prespecified or external_training_independent_of_selection_and_outcomes; prediction_record_id; covariate_record_id; inputs_fixed_before_selection=True |
| Selection | frame_id; design_id; selection_id; status=realized_verified; selected_unit_ids; selection_record_id; verification_record_id |
| HumanResponse | unit_id; frame_id; selection_id; outcome_id; response_status=completed; outcome_status=known; downstream_eligible=True; value (numeric 0 or 1); label_origin; reviewer_id; reviewed_at (YYYY-MM-DD); review_record_id |
| Approval | frame_id; design_id; mode; spec_sha256; status=approved; approved_by; approval_record_id |

String numerals, booleans as numbers, NaN, infinity, unknown/censored outcomes,
screen-status text, and raw exit labels are rejected. There is no implicit
category mapping. For actual requests, label_origin is human_coded or
human_confirmed_ai with documented reviewer/date/record fields; the latter is
retained as such in output and does not imply blind or independent double coding.
For synthetic requests, label_origin must be synthetic and frame, design,
selection, and unit IDs must start with synthetic:. Synthetic and actual-mode
approvals cannot substitute for one another. The actual-path integration check
uses deliberately artificial metadata to exercise that contract, not LGFV data.

Approval matching requires exactly one externally vetted record for the exact
frame ID, design ID, and mode, and a matching specification digest. The digest
binds all full-frame units, strata, pi, predictions, X, covariate order, outcome
definition, prediction assumptions, and their record IDs. It excludes realized
selection and responses so it can exist before selection. Canonical ordering
makes reordering units, strata, selection IDs, or response rows immaterial;
changing numeric representation (1 versus 1.0) changes the strict specification
hash. Use plain Python int/float schema values consistently when freezing it.

The output additionally fingerprints the actual selection roster and human
responses. Exact duplicate IDs, extra/missing response IDs, mismatched sample
counts, and mismatched frame/design/outcome identifiers are rejected. The caller
must separately establish one canonical issuer per unit, the authenticity and
chronology of approvals, actual uniform without-replacement selection, and
truthful human/eligibility records. Hash equality proves content agreement,
not documentary truth or a signature. No untrusted submitted file should be
allowed to create its own entry in the adapter's trusted approval registry.

## Returned values and numerical limits

Estimate returns point as a tuple, covariance as a square tuple of tuples,
standard_errors as a tuple, and parameter_names. The mean has dimension one;
projection columns follow covariate_names. It also returns frame/design/
selection/outcome IDs, approval record, specification and realized-input hashes,
frame/selected/response counts, response-origin counts, prediction assumption,
X condition number for projection, unsupported_strata, and uncertainty_scope.

variance_status is estimated_stratified_srswor,
unavailable_singleton_noncensus, or census_zero_label_selection_only. The last
is used only when all strata are censused, not merely when a sample variance
happens to be zero. No effect direction, significance, or clipping rule governs
acceptance. Approval remains necessary even for a complete census.

Supplied pi must match n_h/N_h with relative floating-point tolerance 1e-12 and
zero absolute tolerance; rounded exported probabilities are not accepted as
known probabilities. This comparison checks an asserted design and does not
infer actual sampling from a proposed allocation. Fixed-X condition numbers
above 1e8 or deficient rank are rejected without ridge, column dropping, or
rescaling. Ordinary floating-point limitations still apply. Overflow and
nonfinite results fail; noncensus predictions so large that floating-point
subtraction cannot distinguish binary zero and one also fail. The exact-design
claims are mathematical identities, checked to 1e-10 on well-scaled examples,
not arbitrary-precision guarantees for pathological magnitudes.

There is no domain/ratio estimator for an outcome-defined subpopulation, no
nonresponse adjustment, no unequal-probability design within strata, no cluster
or multistage design, no causal interpretation, no national generalization, and
no claimed completed LGFV validation estimate. Revising the analytical frame
after selection requires a new design justification, not just deleting records
and reusing the old pi.
