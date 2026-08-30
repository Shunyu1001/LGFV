# Execution summary

## Preparation

- Created the experiment brief before running the frame builder.
- Recorded the base commit and hashes for every input in `run_manifest.yaml`.
- Set `random_draw: false` and left the random seed null.

## Commands

```text
python3 scripts/measurement_validation/build_validation_frame.py
python3 scripts/measurement_validation/build_validation_frame.py --check
```

The first execution stopped when the predeclared completeness check found that
province and city were absent for most frame units. The same script was changed
mechanically to serialize the incomplete frame and failure metrics rather than
printing every affected issuer. The hypothesis and success criteria were not
changed. The retry wrote the quarantined outputs, and the check command
confirmed byte-identical regeneration.

## Result summary

- Frame rows: 133.
- Unique validation-unit identifiers: 133.
- Positive stratum: 97.
- Screen-nonpositive stratum: 36.
- Positive queue mismatches: 0.
- Gold overlaps: 0.
- Missing province fields: 128.
- Missing city fields: 128.
- Missing source-row, pool, or evidence-document fields: 0.
- Forbidden model or selection fields in blinded template: 0.
- Pre-populated coder-entry cells: 0.
- Random draw executed: no.
