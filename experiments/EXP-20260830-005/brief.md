# EXP-20260830-005 Sparse-outcome and sample-selection diagnostics

## Loop

Empirical simulation and identification.

## Falsifiable hypothesis

Under the frozen binary exploratory outcome and historical-capacity exposure,
predeclared sparsity, complete-case selection, functional-form, and
leave-one-out diagnostics will show whether the current adjusted analysis is
stable enough to support more than a descriptive associational claim.

## Frozen inputs and estimand

- Base commit: `e178e195704fe6ad6ec353a28081e444995350e7`.
- Case panel: `data/analysis_inputs/empirical_case_panel.csv`.
- The outcome equals one for substantive exit or functional transfer and zero
  for nominal exit.
- The exposure is standardized Ming-Qing elite density matched to the
  contemporary prefecture.
- The current matched-gold and source-backed full-control inclusion flags are
  used as recorded. No imputation, weighting, relabeling, or new sample rule is
  permitted.

## Predeclared diagnostics

1. Report outcome counts and event shares for every model-specific sample.
2. Report contemporary-control missingness in the 84-row matched-gold sample.
3. Compare the 78-row complete-control subset with excluded matched-gold rows
   on outcome prevalence, standardized elite density, source coverage, and
   capacity-bin composition. These are descriptive comparisons because the
   excluded group is expected to be small.
4. Estimate the same binary association with an LPM, conventional logit, and
   Firth bias-reduced logit for three fixed specifications: matched-gold
   historical-only, complete-control historical-only, and complete-control
   full available controls. Report every result on the probability scale when
   defined; do not rank the specifications by sign or significance.
5. Report parameter counts, events per parameter, matrix rank, condition
   number, convergence, and leave-one-out changes in the elite-density effect
   for both historical-only samples and the complete-control LPM.

The alternative links are sensitivity diagnostics. Promoting one to a main
specification or changing the estimand remains review-gated.

## Permitted files

- A new diagnostic script under `scripts/` and its tests under
  `scripts/tests/`.
- Files under `experiments/EXP-20260830-005/`, including generated CSV/JSON
  diagnostics, proposed manuscript text, and proposed ledger rows.
- A new report under `docs/empirical_audit/` if it does not edit the
  manuscript.

Gold labels, the codebook, historical crosswalk inputs, central ledgers,
existing generated model tables, and manuscript prose are outside scope.

## Success criteria

- The diagnostic run is deterministic and reproduces the declared 84-row
  matched-gold sample before interpretation.
- All model-specific sample sizes, positive outcomes, missing controls,
  convergence failures, and influence results are reported, including adverse
  or null findings.
- Any recommended current specification is justified by estimand alignment,
  input coverage, and stability rather than coefficient sign or significance.
- Any proposal to change the reported model or claim is identified as a
  review-gated decision and stored only in experiment artifacts.

## Commands

```text
python3 scripts/build_empirical_identification_diagnostics.py --output-dir experiments/EXP-20260830-005/artifacts
python3 -m unittest discover -s scripts/tests -p 'test_empirical_identification_diagnostics.py'
```

## Budget

One deterministic diagnostic implementation and run, with at most two minimal
mechanical retries. No stochastic search, model selection, imputation, new
data collection, or manuscript editing.

## Status rules

`keep` if the run adds reproducible information about sparsity, selection, or
stability, including a null or unstable result. `discard` if the diagnostics
are valid but add no information. `crash` for execution failure after
permitted retries, `invalid` for an estimand or sample-rule change, and
`quarantine` for any proposed main-specification change pending human review.
