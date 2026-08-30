# Empirical identification validation

## Repository state

- Branch: `codex/empirical-identification`.
- Starting commit: `e178e195704fe6ad6ec353a28081e444995350e7`.
- Fetched `origin/main` at the same commit before branch creation.
- Frozen files, gold labels, codebook definitions, historical crosswalk inputs,
  central ledgers, and existing manuscript prose were not changed.

## Validation commands and results

```text
python3 scripts/validate_immutable.py
```

Exit 0: four immutable files validated.

```text
python3 scripts/validate_ledgers.py
```

Exit 0: the unchanged central ledgers validated with 8 claims, 1 experiment,
5 literature rows, and 8 reviewer issues.

```text
python3 scripts/validate_labels.py
```

Exit 0: 94 rows and 94 cases validated. The command emitted 89 warnings for
source documents whose extracted text is not present in the repository. This
is consistent with the tracked data-manifest limitation and is not resolved by
this workstream.

```text
python3 scripts/validate_master_case_pool.py
```

Exit 0: 114 rows and 114 cases validated.

```text
python3 scripts/build_pilot_capacity_summary.py
python3 scripts/build_pilot_empirical_models.py
```

Both exited 0. The first command retained the recorded warnings for 10
capacity-unmatched gold cases. The model command reproduced 84 rows.

```text
python3 scripts/build_dsl_surrogate_adjustment.py --issuers data/analysis_inputs/codex_surrogate_issuer_summary_2026_07_03_expanded.csv
```

Exit 0: 94 gold labels, 61 overlap issuers, and 97 non-overlap issuers. Raw,
Jeffreys-smoothed, and Wilson-lower precision values reproduced as 1.000,
0.992, and 0.941.

```text
python3 scripts/build_surrogate_empirical_core.py
```

Exit 0: 361 candidate rows, 346 usable screening rows, 203 disclosure-level
surrogates, 158 issuer-level surrogates, 61 overlaps, 97 non-overlaps, and a
191-row adjusted descriptive sample.

```text
python3 scripts/build_empirical_case_panel.py
```

Exit 0: 191 panel rows, including 94 gold rows, 84 historically matched model
rows, and 78 full-control rows.

```text
python3 scripts/build_controlled_empirical_models.py
```

Exit 0. The command reproduced the tracked available-control, full-control,
and control-readiness outputs. The new diagnostics separately show that the
current full-control design matrix is rank deficient.

```text
python3 scripts/audit_empirical_narrative_numbers.py --output experiments/EXP-20260830-004/artifacts/narrative_number_audit.csv --summary experiments/EXP-20260830-004/artifacts/narrative_number_audit.json
```

Exit 0: 33 quantities audited, with 30 matches and 3 traceable mismatches.

```text
python3 scripts/audit_empirical_narrative_numbers.py --check
```

Exit 1 as expected: the unchanged manuscript still reports 6.3, 17.1, and
13.5 percentage points rather than the generated 6.6, 16.1, and 12.5. The
strict check is intended to pass only after coordinator review and correction.

```text
python3 scripts/build_empirical_identification_diagnostics.py --output-dir experiments/EXP-20260830-005/artifacts
```

Exit 0: the 84-row, 12-event baseline and the 78-row, 12-event
complete-control subset reproduced. The diagnostic LPM matches the pilot
coefficient at its displayed precision.

```text
python3 -m unittest discover -s scripts/tests -p 'test_*.py'
```

Exit 0: all five tests passed. The tests cover the DSL authoritative default,
the narrative mismatch map, deterministic diagnostic artifacts, frozen sample
counts, and the exact full-control dummy alias.

```text
latexmk -g -pdf -interaction=nonstopmode -halt-on-error paper/main.tex
```

Exit 12 when run from the repository root because the manuscript resolves
`sections/` relative to its working directory. No manuscript defect caused
this failure.

```text
cd paper
latexmk -g -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Exit 0: the paper compiled to 89 pages with no undefined references in the
final log. Existing layout warnings remain: 6 overfull boxes, 12 underfull
boxes, and 47 longtable infinite-glue warnings.

```text
python3 -m py_compile scripts/build_dsl_surrogate_adjustment.py scripts/audit_empirical_narrative_numbers.py scripts/build_empirical_identification_diagnostics.py scripts/tests/test_build_dsl_surrogate_adjustment.py scripts/tests/test_audit_empirical_narrative_numbers.py scripts/tests/test_empirical_identification_diagnostics.py
git diff --check
```

Both exited 0.

## Remaining limitations

First, the repository lacks extracted text for 89 label rows and does not
contain the raw source packet archive. Second, 10 gold cases remain unmatched
to historical capacity, and the capacity-bin field is missing for 58 of the
84 matched panel rows even though continuous elite density is present. Third,
the outcome has only 12 events, including 2 substantive exits, and no
liquidation cases. Fourth, the complete-control subset excludes six
low-capacity nominal exits and retains every event. Fifth, the current
full-control design uses an intercept and two exhaustive platform dummies, so
its nine columns have rank eight. Sixth, the paper retains known layout
warnings and the three intentionally unedited narrative discrepancies.

## Review-gated decisions

The coordinator and human PI should review the proposed narrative corrections,
the reference-category repair for the full-control model, and whether fixed
conventional-logit and Firth-logit average marginal effects should appear as
sparse-outcome sensitivity diagnostics. No specification is recommended or
rejected because of coefficient sign or statistical significance.
