# Handoff: Empirical and identification audit

## Objective

Make the empirical core reproducible and determine the strongest defensible
historical-capacity analysis under the current sparse and nonrepresentative
measurement sample.

## Primary reviewer issues

- `R-001`: narrative effect sizes disagree with generated coefficients.
- `R-002`: the DSL script default points to an older issuer file.
- `R-006`: the adjusted capacity coefficient is near zero and only 12 of 84
  matched gold cases record institutional change.

## Required first experiments

First, repair the DSL default-input mismatch and add deterministic regression
checks for 61 overlap and 97 non-overlap issuers. Second, audit every reported
effect size against generated outputs. Third, evaluate sparse-outcome and
sample-selection diagnostics without choosing a model by significance or sign.

## Permitted primary files

- `scripts/build_dsl_surrogate_adjustment.py`
- new tests under `scripts/tests/`
- empirical construction and model scripts under `scripts/`
- generated empirical CSV, table, and figure files
- new reports under `docs/empirical_audit/`
- proposed manuscript text under `experiments/<EXP-ID>/artifacts/`

Do not change gold labels, the codebook, historical crosswalk inputs, central
ledgers, or existing manuscript prose directly. Return focused commits and
proposed claim updates to the coordinator.

## Success criteria

The default pipeline reproduces authoritative current counts; all prose numbers
have a machine-checkable source; the analysis reports outcome sparsity,
model-specific samples, control missingness, influence, and sensitivity; and
the recommended specification is justified by the declared estimand rather
than its coefficient.

Read `AGENTS.md`, `program.md`, the immutable files, and
`/Users/shunyuhao/Desktop/GAN GSC/SKILL.md` before writing prose.
