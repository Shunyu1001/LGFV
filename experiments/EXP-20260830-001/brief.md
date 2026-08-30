# EXP-20260830-001 Baseline reproduction

## Loop

Empirical and reproducibility.

## Hypothesis

The tracked source and analysis snapshots reproduce the manuscript's reported
sample counts, surrogate-validation counts, regression inputs, and compiled
page count without a research change.

## Success criteria

- Gold labels: 94.
- Historically matched model rows: 84.
- Expanded surrogate-gold overlap issuers: 61.
- Expanded non-overlap surrogate issuers: 97.
- Full-control rows: 78.
- Compiled PDF: 89 pages.
- No tracked research output changes after rebuilding with the authoritative
  inputs.

Any default command that silently selects a different input is a kept
reproducibility finding even if the authoritative outputs can be reproduced by
an explicit argument.

## Allowed changes

No research files. Generated outputs may be rebuilt and compared to the base
commit. Any unintended output is restored before assessment.

## Commands

The run uses the validation and build commands recorded in `AGENTS.md`. The DSL
step explicitly passes the expanded 2026-07-03 issuer summary.

## Status rules

Keep a verified mismatch or a fully reproduced baseline. Quarantine any data or
research-design discrepancy. Mark the run invalid if inputs cannot be
identified.
