# Design-based estimator implementation

- Experiment: EXP-20260910-005
- Started: 2026-09-10T14:20:49+08:00
- Loop: empirical_simulation
- Base commit: 4330c5728dec64ba30c1faec972fad0097622e9d
- Branch: codex/design-estimator-20260910
- Worktree: /Users/shunyuhao/.codex/worktrees/lgfv-design-estimator/LGFV
- Status at registration: prospective; no implementation or estimator results

## Bottleneck and hypothesis

A bounded future-input engine can recover finite assembled-frame outcome means
and fixed-X linear projections without design bias using fixed auxiliary
predictions and known-probability human residual corrections. Under independent
stratified simple random sampling without replacement (SRSWOR), its estimated
label-selection covariance will equal the exact design covariance in
expectation whenever every noncensus stratum has at least two sampled units.
Fail-closed input checks will prevent the current unapproved 67-unit proposal,
unresolved outcomes, incomplete human response, or invalid sampling records
from producing numeric inference.

## Authority and permitted files

Only these new paths may be changed:

- scripts/design_based_validation.py
- tests/test_design_based_validation.py
- experiments/EXP-20260910-005/*

No manuscript, raw data, existing estimator, immutable document, global ledger,
or current analysis input is changed. The main estimand and method are unchanged.
No actual-data adapter, human review, frame approval, draw, merge, push, or paper
build is authorized. The explicit worker scope overrides the general global
ledger-update rule: attempt records and a coordinator ledger handoff will be
stored in this experiment directory. The coordinator owns global integration.

## Prespecified implementation

Use the full-frame mean of fixed predictions plus Horvitz-Thompson human
residual corrections; use the corresponding fixed-X outcome moments and the
known full-frame Gram matrix for the linear projection. Include the SRSWOR
finite-population correction and all coefficient covariances. Do not substitute
model-based or city-cluster uncertainty for label-selection uncertainty.

Require consistent unique issuer IDs, full-frame finite nonmissing X and
predictions, full-rank and numerically usable X, explicit frame/design approval
and provenance, a realized selected-unit roster matching fixed stratum sample
sizes, verified inclusion probabilities, and a completed human response for
every selected unit. Reject unknown/censored outcomes, AI-only decisions,
unapproved or proposed designs, zero-probability strata, and nonresponse rather
than recoding or dropping them. Prediction provenance must assert fixed
prespecification before selection or external training independent of selection
and validation outcomes. Cross-fitting alone is not sufficient for exact design
unbiasedness or this covariance formula.

For n_h = 1 < N_h, retain the valid point estimate but return no total variance
estimate and explicitly identify unsupported strata. A complete census returns
zero label-selection covariance, not zero measurement, frame, or population
uncertainty. Do not clip points to [0,1], regularize singular X, fit a prediction
model, guess probabilities, or generate confidence intervals/p-values.

## Success criteria

1. Exhaustively enumerate every legitimate sample for multiple small frames,
   including unequal sampling fractions, mixed census/SRSWOR strata, negative
   and inaccurate fixed predictions, and nonconstant multicolumn X. Average
   means and coefficients must equal their finite-frame targets; average
   estimated variances/covariances must equal exact enumeration covariance
   within 1e-10 absolute tolerance on well-scaled examples.
2. Exhaustively check binary outcome configurations on a bounded small frame,
   along with census, singleton, constant residual, and perfect-prediction cases.
   Include a counterexample to exact independence from cross-fitting alone.
3. Negative checks cover approval/ID mismatches, proposals, absent/duplicate
   sample IDs, nonresponse, censored/unknown labels, AI-only provenance, invalid
   pi, invalid strata, and missing/nonfinite/rank-deficient covariates. Verify
   permutation invariance and preservation of out-of-range point estimates.
4. A read-only regression check demonstrates that the actual current 67-unit
   proposal cannot produce a numeric result; no labels or approvals are invented
   for that check.
5. Repository immutable, ledger, label, master-case-pool, and relevant existing
   validation checks pass or their pre-existing failures are preserved explicitly.
6. The method memo cites an opened authoritative primary publication and clearly
   distinguishes the finite-design derivation from broader DSL claims. The API,
   approval trust boundary, schema, numerical requirements, and limitations are
   documented. No actual LGFV inference is produced.

## Commands and budget

Planned validation commands (run from this worktree):

```text
python3 -m unittest discover -s tests -p 'test_design_based_validation.py' -v
python3 -m unittest discover -s tests -v
python3 scripts/validate_immutable.py
python3 scripts/validate_ledgers.py
python3 scripts/validate_labels.py
python3 scripts/validate_master_case_pool.py
python3 scripts/validate_probability_validation_frame.py
git diff --check
git diff --name-only 4330c5728dec64ba30c1faec972fad0097622e9d
```

Budget: at most 3 hours; one estimator family and one test module; at most
100,000 enumerated sample/outcome combinations per full suite. Use the existing
Python environment and a standard numerical library if available; no new ML
system or dependency installation. Preserve every implementation-check attempt
in an experiment-local log. Mechanical crashes allow at most two minimal
retries under program.md. Do not revise criteria based on results.

## Disposition rule

Keep the implementation only if the hard gates and mathematical checks pass.
Quarantine actual-data use until separately documented PI approval, frozen
frame/design records, realized selection, and complete human labels are supplied.
Retain adverse findings and any unresolved limitations in the assessment.
