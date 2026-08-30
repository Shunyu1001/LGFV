# Execution summary

## Preparation

- Created the experiment brief before inspecting the candidate join fields.
- Recorded the base commit and SHA-256 hashes for all five inputs.
- Froze the exact-key source hierarchy and the 116-of-128 success threshold.
- Set the random-draw flag to false and left the random seed null.

## Commands

```text
python3 scripts/measurement_validation/enrich_validation_geography.py
python3 scripts/measurement_validation/enrich_validation_geography.py --check
```

Both commands completed successfully. The second confirmed byte-identical
regeneration.

## Result summary

- Initial incomplete units: 128.
- Required resolutions: 116.
- Exact-key resolutions: 0.
- Remaining unresolved units: 128.
- Conflicting units: 0.
- Company-name parsing used: no.
- External lookup used: no.
- Random draw executed: no.
- Experiment gate passed: no.

## Validation commands

```text
python3 -m py_compile scripts/measurement_validation/enrich_validation_geography.py
python3 scripts/validate_immutable.py
python3 scripts/validate_ledgers.py
python3 scripts/validate_labels.py
python3 scripts/validate_master_case_pool.py
git diff --check
```

All commands exited successfully. The label validator confirmed 94 rows and 94
cases. The master-case-pool validator confirmed 114 rows and 114 cases and
repeated the existing missing-extracted-text warnings without suppressing them.
