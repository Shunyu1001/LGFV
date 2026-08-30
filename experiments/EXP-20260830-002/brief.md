# Experiment brief: Current measurement estimands

## Experiment identity

- Experiment ID: `EXP-20260830-002`
- Loop: `empirical_simulation`
- Base commit: `e178e195704fe6ad6ec353a28081e444995350e7`
- Started at: `2026-08-30T12:30:00+08:00`
- Owner: measurement-validation worktree

## Falsifiable bottleneck

The repository describes several human- and LLM-label comparisons, but it is
not yet clear which unit, sampling mechanism, target population, and error
quantity each comparison identifies. The experiment tests whether the current
tracked artifacts support an auditable estimand map that separates observed
agreement from population precision, recall, calibration, four-category error,
and sampling error.

## Hypothesis

The current data can reproduce the declared case, disclosure, issuer, and
overlap counts and can compute descriptive label concordance within observed
overlap units. They cannot identify population recall, calibration, or
four-category error because the one-sided surrogate construction and the
non-probability overlap mechanism omit human labels for the required
denominators.

## Inputs

- `coding/codebook.md`
- `paper/sections/coding_strategy.tex`
- `data/processed/human_validated_labels.csv`
- `data/analysis_inputs/llm_screening_sample_2026_07_03_expanded.csv`
- `data/analysis_inputs/codex_surrogate_issuer_summary_2026_07_03_expanded.csv`
- `data/analysis_inputs/codex_surrogate_labels_2026_07_03_expanded.csv`
- `data/analysis_inputs/surrogate_validation_queue_2026_07_03_expanded.csv`
- `data/analysis_inputs/validation_batch1_review.csv`
- validation memos and surrogate-label reports under `docs/`

Input hashes will be recorded in the run manifest before the analysis script is
executed.

## Permitted files

- New scripts under `scripts/measurement_validation/`
- New outputs under `data/validation/`
- New reports under `docs/measurement_validation/`
- New files under `experiments/EXP-20260830-002/`

The experiment must not modify gold labels, central ledgers, `paper/main.tex`,
or existing manuscript sections.

## Planned change

Add a deterministic audit script that inventories the relevant units and label
fields, checks deduplication and overlap invariants, calculates only estimands
whose numerators and denominators are observed, and emits a machine-readable
estimand map. Write a report that distinguishes identified descriptive
quantities from quantities requiring a new probability sample and independent
human coding.

## Success criteria

The experiment succeeds if all of the following hold:

1. The audit reproduces the declared counts or records each discrepancy.
2. Every reported error quantity states its unit, observed denominator,
   selection mechanism, target population, and identification limit.
3. Precision, recall, calibration, four-category error, and sampling error are
   separated explicitly.
4. The report defines a feasible probability-based validation design without
   selecting or coding cases under an unapproved design.
5. The report identifies the exact independent human work required for
   inter-coder agreement and adjudication.
6. Re-running the audit produces byte-identical tabular outputs.
7. Repository integrity, ledger, label, and master-case-pool checks pass.

The direction or magnitude of any agreement statistic is not a success
criterion.

## Commands

```text
python3 scripts/measurement_validation/audit_measurement_estimands.py
python3 scripts/measurement_validation/audit_measurement_estimands.py --check
python3 scripts/validate_immutable.py
python3 scripts/validate_ledgers.py
python3 scripts/validate_labels.py
python3 scripts/validate_master_case_pool.py
git diff --check
```

## Budget

- One deterministic audit script.
- At most four new machine-readable outputs and two narrative reports.
- At most two minimal mechanical retries if execution fails.
- No web retrieval, model relabeling, or human-label changes.

## Status rule

Assign `keep` only if all hard gates pass and the estimand map materially
improves traceability without overstating identification. Assign `quarantine`
if the map is useful but depends on an unresolved design or source ambiguity;
assign `discard`, `crash`, or `invalid` according to `program.md` otherwise.
