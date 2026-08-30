# EXP-20260830-003 Authoritative DSL input

## Loop

Empirical simulation and reproducibility.

## Falsifiable hypothesis

Changing the DSL adjustment script's default issuer input from the older
2026-07-02 snapshot to the authoritative expanded 2026-07-03 snapshot will
make the default and explicit-authoritative commands produce identical
outputs with 61 overlap and 97 non-overlap issuers.

## Frozen inputs and estimand

- Base commit: `e178e195704fe6ad6ec353a28081e444995350e7`.
- Human labels: `data/processed/human_validated_labels.csv`.
- Authoritative issuer input:
  `data/analysis_inputs/codex_surrogate_issuer_summary_2026_07_03_expanded.csv`.
- The one-sided nominal-exit screening estimand and all label definitions
  remain unchanged.

## Permitted files

- `scripts/build_dsl_surrogate_adjustment.py`.
- New regression checks under `scripts/tests/`.
- Files under `experiments/EXP-20260830-003/`.
- Generated DSL outputs may be rebuilt for comparison but may not be retained
  if they differ from the authoritative current outputs.

Gold labels, the codebook, historical crosswalk inputs, central ledgers, and
manuscript prose are outside scope.

## Success criteria

- The default command reads 158 unique issuer rows, including 61 overlap and
  97 non-overlap issuers.
- The default and explicit-authoritative commands produce byte-identical CSV
  and LaTeX outputs.
- A deterministic regression check fails if the default returns to the older
  issuer input or if the 61/97 counts change.
- The authoritative generated outputs remain unchanged.

The result is assessed without regard to coefficient direction or
statistical significance.

## Commands

```text
python3 -m unittest discover -s scripts/tests -p 'test_build_dsl_surrogate_adjustment.py'
python3 scripts/build_dsl_surrogate_adjustment.py
python3 scripts/build_dsl_surrogate_adjustment.py --issuers data/analysis_inputs/codex_surrogate_issuer_summary_2026_07_03_expanded.csv
git diff --exit-code -- data/analysis_inputs/dsl_surrogate_diagnostics.csv data/analysis_inputs/dsl_augmented_outcome_distribution.csv paper/tables/dsl_surrogate_validation.tex
```

## Budget

One implementation pass and at most two minimal mechanical retries. No new
data collection and no model estimation.

## Status rules

`keep` if the deterministic default-input defect is repaired without changing
authoritative outputs. `discard` if the current default is already equivalent.
`crash` for an execution failure after permitted retries, `invalid` for input
ambiguity or a frozen-object change, and `quarantine` for any unanticipated
research-result difference.
