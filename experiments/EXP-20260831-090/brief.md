# Experiment brief: Synchronize working-reference provenance

## Registration

- Experiment: `EXP-20260831-090`
- Registered: `2026-08-31T10:03:06+08:00`
- Loop: `measurement_validation`
- Base commit: `5de57d63a70b52cedc5223a7fa6f751bfc70cfe1`
- Branch: `codex/reference-label-producer-provenance`

## Falsifiable bottleneck

The master case pool has 94 rows marked `human_validated`, but it omits the
`reference_label_producer` column that the validator requires for those rows.
The canonical working-reference file already records the producer and states
that the labels await independent human confirmation. The missing field leaves
the integrated pool unable to preserve that distinction and causes 94
validation errors.

## Hypothesis and success criteria

A deterministic case-ID join from the canonical working-reference file can add
the missing producer metadata without changing a label or any existing master
pool field. Success requires all of the following:

1. the 94 master-pool rows with `validation_status=human_validated` map one to
   one to the 94 working-reference rows;
2. every mapped row receives the canonical nonempty
   `reference_label_producer` value;
3. all non-reference rows retain a blank producer value;
4. row order, row count, column values already present at the base commit, case
   IDs, exit types, confidence values, reviewer fields, and dates remain
   unchanged;
5. the synchronization is idempotent and rejects conflicting existing values;
6. `validate_master_case_pool.py`, `validate_labels.py`, and the immutable and
   ledger validators pass; and
7. no output describes these records as independently human confirmed.

Failure of any criterion makes the experiment invalid. Passing this experiment
does not approve the legacy status names `human_validated` or `gold_standard`;
those semantic names require a separate governed change.

## Frozen inputs

| Input | SHA-256 at base commit |
|---|---|
| `data/analysis_inputs/master_case_pool.csv` | `1583819a1bcc099598bb925d3dbff23297ce0cea690d0adaf5b2e823c7fe9bf6` |
| `data/processed/working_reference_labels.csv` | `c1e6bd66b7f498a6100422b9f4a66a61374eb47f65fc7fe5f0446f503e2afd18` |
| `scripts/validate_master_case_pool.py` | `014f843a3154c05d22c79c0519a8c1185129022d7bfde784d3bead9698cf4dae` |

## Permitted files

- `data/analysis_inputs/master_case_pool.csv`;
- `scripts/sync_master_case_pool_label_provenance.py`;
- `scripts/validate_master_case_pool.py`;
- `tests/test_sync_master_case_pool_label_provenance.py`;
- `experiments/EXP-20260831-090/**`; and
- one append-only row in `ledgers/experiments.tsv`.

No working-reference row, source packet, outcome, confidence score, immutable
file, manuscript result, or sampling rule may change.

## Registered execution

```text
python3 scripts/sync_master_case_pool_label_provenance.py
python3 scripts/sync_master_case_pool_label_provenance.py --check
python3 -m unittest tests.test_sync_master_case_pool_label_provenance
python3 scripts/validate_immutable.py
python3 scripts/validate_ledgers.py
python3 scripts/validate_labels.py
python3 scripts/validate_master_case_pool.py
git diff --check
```

The execution budget is one deterministic transformation, one idempotence
check, and one repair attempt if a registered invariant fails. There is no
source search, relabeling, model selection, or manuscript editing.
