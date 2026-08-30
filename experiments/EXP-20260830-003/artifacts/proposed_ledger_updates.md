# Proposed ledger updates

## Experiments ledger

Append a row for `EXP-20260830-003` with loop `empirical_simulation`, base
commit `e178e195704fe6ad6ec353a28081e444995350e7`, status `keep`, artifact path
`experiments/EXP-20260830-003`, and the following result summary:

> The DSL default now selects the authoritative expanded issuer input and
> reproduces 61 overlap and 97 non-overlap issuers; default and explicit runs
> are byte-identical and leave authoritative outputs unchanged.

Record uncertainty as `not_applicable` and record that result direction was
not used for selection. The coordinator should add the reviewed trial commit.

## Reviewer issue

Propose closing `R-002` after the coordinator reproduces the regression check
on the reviewed commit. Use
`experiments/EXP-20260830-003/command_results.txt` and
`scripts/tests/test_build_dsl_surrogate_adjustment.py` as evidence. Do not
change the scope of `R-004`; this experiment does not identify recall or
multiclass error.
