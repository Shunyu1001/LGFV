# EXP-20260830-012 Sparse-outcome model audit

## Loop

Empirical simulation and identification.

## Falsifiable hypothesis

Replacing the two exhaustive platform indicators in the frozen 78-case
adjusted design with one indicator and a declared reference category will
restore full column rank. The resulting fixed LPM and Firth-logit audit will
determine whether the historical-capacity association is numerically and
case-deletion stable enough to report as an adjusted exploratory diagnostic.
The result may be null, negative, contradictory, or unstable.

## Base state and frozen inputs

- Base commit: `bf1bd7b99c7dd9261678015c9f050599ae862fe3`.
- Branch: `codex/sparse-outcome-models`.
- Case panel:
  `data/analysis_inputs/empirical_case_panel.csv`.
- Baseline comparison:
  `data/analysis_inputs/pilot_lpm_institutional_change.csv`.
- Outcome: one for substantive exit or functional transfer and zero for
  nominal exit.
- Exposure: Ming-Qing elite density matched to the contemporary prefecture,
  standardized separately within each fixed model sample.
- Samples: the recorded 84-case matched-gold flag and the recorded 78-case
  complete-control flag. No imputation, weighting, relabeling, new controls,
  sample restriction, or crosswalk change is permitted.

## Fixed model set

The experiment estimates four models and reports all four without selection
by coefficient sign, magnitude, or significance.

1. `matched_gold_historical_lpm`: an intercept and standardized elite density
   on the 84-case matched-gold sample, estimated by LPM with HC1 uncertainty.
2. `matched_gold_historical_firth`: the same sample and regressors estimated
   by Firth bias-reduced logit. The elite-density result is reported both in
   log-odds and as the sample average marginal effect. Curvature-based
   delta-method uncertainty is diagnostic only.
3. `complete_control_adjusted_lpm`: an intercept, standardized elite density,
   standardized GDP per capita, standardized fiscal self-sufficiency,
   standardized debt pressure, standardized land-finance dependence,
   standardized source coverage, and a prefecture/municipal platform
   indicator on the 78-case complete-control sample. District/county
   platforms are the reference category. The model is estimated by LPM with
   HC1 uncertainty.
4. `complete_control_adjusted_firth`: the same sample and corrected design as
   model 3, estimated by Firth bias-reduced logit and reported as in model 2.

The reference-category change removes the exact alias and does not add,
remove, or redefine a substantive control. The capital or sub-provincial
indicator is not added because it was not in the frozen full-control design
under review. Conventional logit, alternative control sets, interactions,
transformations, and outcome decompositions are outside the fixed model set.

## Predeclared diagnostics

1. Reproduce the 84-case historical-only LPM at the precision of the tracked
   pilot coefficient.
2. Report observations, events, independent columns, events per independent
   column, matrix rank, condition number, convergence, iterations, coefficient
   scale, and uncertainty for every fixed model.
3. Record the legacy two-dummy alias and verify that the corrected adjusted
   design has eight columns and rank eight. Report district/county and
   prefecture/municipal counts.
4. Report the six cases excluded from complete-control estimation, the
   missing controls that determine exclusion, and descriptive included versus
   excluded comparisons for outcome prevalence, elite density, source
   coverage, and platform level.
5. For both model samples and both estimators, refit after deleting each case
   while retaining the full-sample scaling. Report every deletion, convergence
   failure, change in the elite-density probability-scale effect, sign change,
   and the five largest absolute changes. Ranking by absolute influence is a
   diagnostic and cannot determine model retention.
6. Do not estimate province fixed effects. Report a feasibility audit of a
   saturated province-indicator candidate instead, including province count,
   within-province outcome variation, rank, and events per independent column.
   Province fixed effects remain outside the model set because the frozen
   outcome has only 12 events.

## Permitted files

- `scripts/build_sparse_outcome_model_audit.py`.
- `scripts/tests/test_sparse_outcome_model_audit.py`.
- Files under `experiments/EXP-20260830-012/`, including generated results,
  proposed manuscript and ledger text, and the review-gated recommendation.

Gold labels, codebook definitions, historical crosswalk inputs, contemporary
control values, central ledgers, existing model outputs, and manuscript prose
are outside scope.

## Success criteria

- The legacy adjusted design is reproduced as rank deficient and the fixed
  reference-category design is full rank without a sample or regressor change
  beyond removing the redundant indicator.
- All four fixed models and all leave-one-out attempts are reported, including
  null, adverse, nonconvergent, and sign-changing results.
- Model-specific sample selection, coefficient scale, uncertainty, rank,
  convergence, and influence are machine readable.
- The generated table and coefficient plot are labeled exploratory and state
  that the adjusted estimates use 12 events and first-pass controls.
- Regression tests verify deterministic output, the frozen model set, sample
  counts, rank repair, reference category, and the absence of result-based
  selection.
- Any proposed claim or reporting change remains review-gated and appears only
  inside this experiment directory.

The experiment may be kept for a valid reproducible audit even if the
adjusted estimate is unstable. Stability is evaluated from rank, convergence,
event support, and deletion influence rather than coefficient direction or a
p-value threshold.

## Commands

```text
python3 scripts/build_sparse_outcome_model_audit.py --output-dir experiments/EXP-20260830-012/artifacts
python3 -m unittest discover -s scripts/tests -p 'test_sparse_outcome_model_audit.py'
python3 scripts/validate_immutable.py
python3 scripts/validate_ledgers.py
python3 scripts/validate_labels.py
python3 scripts/validate_master_case_pool.py
python3 -m py_compile scripts/build_sparse_outcome_model_audit.py scripts/tests/test_sparse_outcome_model_audit.py
git diff --check
```

## Budget

One deterministic implementation and run, followed by the declared tests and
validation checks. At most two minimal mechanical retries are allowed. No
stochastic search, tuning by results, new data collection, or manuscript edit
is permitted.

## Status rules

`keep` if the run is reproducible and either validates or falsifies the
stability of the repaired fixed design. `discard` if it is valid but adds no
diagnostic information. `quarantine` applies to proposed main-text or
main-specification changes pending coordinator and human review. `crash`
records execution failure after the permitted retries, and `invalid` records
an input, model-set, or post-result criterion change.
