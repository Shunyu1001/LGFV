# Proposed ledger updates

These entries are proposals for coordinator review. No central ledger was
edited by this experiment.

## Experiments ledger

```tsv
EXP-20260830-012	2026-08-30T16:13:40+08:00	empirical_simulation	bf1bd7b99c7dd9261678015c9f050599ae862fe3		A reference-category repair and fixed sparse-outcome models will determine whether the adjusted historical-capacity association is numerically and deletion stable.	rank_convergence_selection_and_influence_audit	Legacy adjusted design: 9 columns, rank 8, 12 events	Corrected design: 8 columns, rank 8; adjusted LPM and Firth effects change sign in 9 and 11 leave-one-out runs.	Fixed models and criteria; no selection by sign or significance	keep	experiments/EXP-20260830-012	Repairs the exact alias and preserves the adverse conclusion that the adjusted association is not stable evidence.
```

## Claims ledger

- For `C-004`, add `EXP-20260830-012` to `evidence_ids` and retain `supported`
  only for the simple exploratory association. Add that the fixed Firth
  sensitivity has a 5.6-percentage-point average marginal effect and that both
  historical-only diagnostic intervals include zero.
- For `C-005`, add `EXP-20260830-012` to `evidence_ids` and retain
  `contradicted`. Replace the rank-deficiency limitation after the mechanical
  repair with the remaining limits: 12 events across eight independent
  columns, complete-case selection, and sign changes in 9 LPM and 11 Firth
  leave-one-out runs.

## Reviewer issues

- Propose closing `R-009` after coordinator reproduction because the adjusted
  design now uses district/county platforms as the reference and has eight
  columns with rank eight.
- Keep `R-006` open and add `EXP-20260830-012` as evidence. The mechanical rank
  repair does not resolve sparse event support, complete-case selection, or
  deletion sensitivity.

## Research state

Keep `empirical_simulation.status` at `red`. Replace the rank-deficiency clause
in its main gap after review with: the gold outcome has 12 institutional-change
cases, complete controls exclude six low-capacity nominal exits, and the
corrected adjusted estimates remain deletion-sensitive. Do not change the
measurement contribution's priority or the exploratory, associational label.
