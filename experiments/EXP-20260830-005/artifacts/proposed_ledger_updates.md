# Proposed ledger updates

## Experiments ledger

Append a row for `EXP-20260830-005` with loop `empirical_simulation`, base
commit `e178e195704fe6ad6ec353a28081e444995350e7`, status `keep`, artifact path
`experiments/EXP-20260830-005`, and the following result summary:

> The frozen 84-row historical-only model reproduces and retains its LPM sign
> under all case deletions. The 78-row complete-control subset retains all 12
> events and excludes six low-capacity nominal exits. The current full-control
> design is rank deficient, has 1.33 events per observed column, and changes
> the elite-effect sign in 9 leave-one-out runs.

Record the fixed model set, null and unstable adjusted results, and that no
specification was selected by sign or significance. The coordinator should
add the reviewed trial commit.

## Claims ledger

- For `C-004`, propose adding `EXP-20260830-005` to `evidence_ids` and adding
  the limitation that the outcome has 12 events and the sample is
  nonrepresentative. The simple associational wording may remain.
- Keep `C-005` as `contradicted`. Add `EXP-20260830-005` to `evidence_ids` and
  add that the current full-control encoding is rank deficient and highly
  deletion-sensitive.

## Reviewer issues

Keep `R-006` open and add `EXP-20260830-005` as evidence. Its proposed
resolution should require reference-category reparameterization, independent
reproduction, explicit complete-case selection reporting, and continued
exploratory language.

Propose a new critical reproducibility issue:

> The current full-control design includes an intercept with two exhaustive
> platform-category dummies. The nine-column matrix has rank eight because the
> two dummies sum to the intercept for all 78 rows. Use one platform category
> as the reference, reproduce the model, and keep the adjusted specification
> exploratory given 12 events.

Use `experiments/EXP-20260830-005/artifacts/design_alias_diagnostics.csv` as
evidence. The coordinator should assign the next available reviewer issue ID.
