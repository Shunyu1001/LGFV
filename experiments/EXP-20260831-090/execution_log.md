# Execution log

## Registered transformation

The experiment ran the registered deterministic case-ID synchronization from
`data/processed/working_reference_labels.csv` into
`data/analysis_inputs/master_case_pool.csv`. The synchronization found 94
working-reference rows and exactly 94 master-pool rows carrying the legacy
`human_validated` status. It added `reference_label_producer` before the
existing `human_reviewer` field.

The resulting value on all 94 matched rows is:

```text
Codex source-packet review on behalf of Shunyu Hao
```

The other 20 master-pool rows retain a blank producer field. No record is
marked independently human confirmed by this transformation.

## Protected-field audit

A base-commit comparison parsed the old and new CSV files and verified:

```text
rows=114
working_reference_rows=94
unchanged_existing_columns=54
protected_field_audit=ok
```

Row order and case IDs are unchanged. Every value in the 54 preexisting
columns is unchanged, including exit type, confidence, reviewer, and validation
date. The full-file diff necessarily touches each CSV row because a column was
inserted; the parsed-value audit distinguishes that structural insertion from
a substantive row change.

## Checks

```text
python3 scripts/sync_master_case_pool_label_provenance.py        # 114 rows; 94 references
python3 scripts/sync_master_case_pool_label_provenance.py --check # passed
python3 -m unittest tests.test_sync_master_case_pool_label_provenance # 3 passed
python3 scripts/validate_immutable.py                            # passed
python3 scripts/validate_ledgers.py                              # passed before append
python3 scripts/validate_labels.py                               # passed; 94 rows
python3 scripts/validate_master_case_pool.py                     # passed; 114 rows
git diff --check                                                 # passed
```

`validate_labels.py` continues to emit the preexisting warnings that locally
extracted primary-evidence text is unavailable for many working-reference
records. This experiment does not resolve those source-packet availability
warnings and does not change their interpretation.

## Result boundary

The repair closes a metadata-integrity failure. It does not convert the 94
working reference labels into human-confirmed gold labels, validate a
classifier, estimate measurement error, approve a probability sample, or
change the four-category coding framework. The legacy master-pool values
`human_validated` and `gold_standard` remain a separate semantic-governance
problem.
