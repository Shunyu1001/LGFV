# EXP-20260830-004 Narrative number audit

## Loop

Claim evidence and reproducibility.

## Falsifiable hypothesis

A deterministic audit of the empirical section's reported sample counts,
effect sizes, surrogate-validation rates, and adjusted counts will identify
exactly the three coefficient discrepancies recorded in reviewer issue
`R-001`, while the remaining mapped narrative quantities will match generated
outputs at their displayed precision.

## Frozen inputs and estimand

- Base commit: `e178e195704fe6ad6ec353a28081e444995350e7`.
- Manuscript source is read-only:
  `paper/sections/empirical_strategy.tex`.
- Generated sources include the pilot LPM, screening-flow, DSL diagnostic,
  adjusted-distribution, and empirical-panel coverage CSV files under
  `data/analysis_inputs/`.
- No outcome, sample, model, or rounding rule may be changed to reconcile a
  narrative value.

## Permitted files

- A new deterministic audit script under `scripts/` and its tests under
  `scripts/tests/`.
- Files under `experiments/EXP-20260830-004/`, including proposed replacement
  text and proposed ledger rows.
- A new machine-readable report under `docs/empirical_audit/` if it contains
  no manuscript edits.

Gold labels, the codebook, historical crosswalk inputs, central ledgers,
generated model results, and existing manuscript prose are outside scope.

## Success criteria

- Every empirical effect size in prose is mapped to a generated CSV row and a
  declared rounding transformation.
- The audit also maps the quantitative sample and surrogate-validation claims
  needed to interpret those effects.
- Mismatches report manuscript location, reported value, generated value,
  difference, source path, and source row or formula.
- Proposed replacement text changes only the mismatched narrative values and
  remains explicitly exploratory and associational.
- Proposed claim, reviewer, and experiment ledger updates are stored only in
  the experiment artifacts.

The audit may not choose or suppress a number because of its sign or
significance.

## Commands

```text
python3 scripts/audit_empirical_narrative_numbers.py --output experiments/EXP-20260830-004/artifacts/narrative_number_audit.csv --summary experiments/EXP-20260830-004/artifacts/narrative_number_audit.json
python3 scripts/audit_empirical_narrative_numbers.py --check
python3 -m unittest discover -s scripts/tests -p 'test_audit_empirical_narrative_numbers.py'
```

## Budget

One audit implementation, one deterministic run, and at most two minimal
mechanical retries. No model re-estimation is permitted in this experiment.

## Status rules

`keep` if the audit is reproducible and either verifies all mapped quantities
or identifies traceable mismatches. `discard` if it adds no traceability.
`crash` for execution failure after permitted retries, `invalid` for a
post-result mapping or rounding change, and `quarantine` for any discrepancy
that cannot be resolved to an authoritative generated source.
