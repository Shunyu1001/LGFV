# Handoff: sparse-outcome models

## Objective

Repair the rank-deficient adjusted specification and determine which frozen
historical-capacity associations, if any, remain interpretable with 12 events.
The result is an exploratory robustness audit, not a search for significance.

## Governing records

Read `AGENTS.md`, `program.md`, every file under `immutable/`,
`ledgers/research_state.yaml`, `ledgers/reviewer_issues.tsv`,
`docs/empirical_audit/empirical_identification_validation.md`, and Experiments
`EXP-20260830-004` and `EXP-20260830-005`. Read
`/Users/shunyuhao/Desktop/GAN GSC/SKILL.md` before proposing prose.

## Fixed boundaries

- Do not edit gold labels, codebook definitions, historical crosswalk inputs,
  or contemporary-control source values.
- Do not select a specification by coefficient sign, magnitude, or
  significance.
- Do not add controls after inspecting results.
- Do not edit central ledgers or existing manuscript prose.
- Keep the measurement framework as the primary contribution and the
  historical-capacity application as exploratory.

## Predeclared model set

Create a pre-result experiment brief that freezes the analysis sample, outcome,
historical-capacity measure, and model set. At minimum, reproduce the 84-case
historical-only LPM; repair the 78-case adjusted LPM by omitting one exhaustive
platform category; fit a predeclared penalized logistic or Firth model suitable
for rare outcomes; and report leave-one-out influence and complete-case
selection diagnostics. Province fixed effects may be reported only when the
design matrix and event allocation support them. Do not invent missing values.

## Evaluation

Report coefficient scale, uncertainty, rank, convergence, events per independent
column, influential cases, and the six excluded complete-control cases. Compare
models for numerical and design stability, not for favorable results. If the
adjusted evidence remains unstable, say so and recommend its removal from the
main text.

## Deliverables

- Corrected model-building code and regression tests.
- Machine-readable model, rank, convergence, influence, and selection outputs.
- A table and coefficient plot clearly labeled exploratory.
- Experiment assessment and a review-gated recommendation.
- Proposed ledger and manuscript text stored only in experiment artifacts.

Commit coherent work on `codex/sparse-outcome-models` and push the branch for
coordinator review.
