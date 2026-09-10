# Validation and inference integration

Registered before integration or analysis execution on 10 September 2026.
Base commit: 4330c5728dec64ba30c1faec972fad0097622e9d.
Branch: codex/validation-inference-20260910.

## Bottleneck and hypothesis

The manuscript still describes an obsolete four-unit candidate packet even
though the accepted source audit has produced 67 eligible issuer units. Its
DSL discussion does not specify an executable estimator or distinguish missing
validation outcomes from a completed census. A current-data adapter, tested
finite-frame estimators, and explicit identification bounds can make the
empirical evidence and remaining data requirements reproducible without
inventing human observations or changing a main estimand.

The author's human-check report is limited to its exact 94-case snapshot.
Neither geographic proximity nor AI review extends that report. The current
request authorizes implementation and parallel work, but explicit final frame
freeze approval is being sought separately. The existing design proposal,
outcome definitions, source hierarchy, and all raw inputs remain unchanged.

## Permitted changes

- Integrate separately registered EXP-20260910-004, 005, and 006 after review.
- New scripts/build_validation_inference_status.py and its targeted test.
- New data/validation/inference_2026_09_10 outputs, documentation, and this
  experiment's artifacts, logs, metrics, and assessment.
- Manuscript measurement, empirical, research-design, introduction, conclusion,
  and appendix passages needed to report the accepted evidence and formulas.
- Main-text placement of the existing four-specification sparse-outcome table;
  no change to the models or their numerical results.
- Append claims, experiment attempts, decisions, and reviewer follow-ups;
  update current research state and README after reproducing results.
- If explicit PI approval arrives, record it and create a versioned freeze
  overlay with the unchanged candidate IDs and census allocation. Do not
  overwrite proposal snapshots or label any field as a realized human outcome.

## Pre-result criteria

1. Every included human outcome must match the confirmation report and exact
   issuer/event unit, or a new independently supplied human record.
2. Missing outcomes must remain missing. No actual estimate may be reported
   without its declared frame, selection probabilities, realized responses,
   covariates, and fixed-prediction assumptions.
3. All parallel numerical claims and inputs must reproduce. Bounds are
   identified sets conditional on accepted reference labels, not confidence
   intervals or national performance estimates.
4. Census selection variance must not be described as zero measurement error,
   model uncertainty, or uncertainty about Chinese LGFVs generally.
5. All original outcomes, controls, historical crosswalks, and empirical
   estimates retain their baseline values. Existing limitations remain.
6. The manuscript must report current counts once in their owning sections,
   compile without undefined references, and have visually legible changed
   pages. GitHub and Overleaf completion requires direct remote verification.

## Commands and budget

One integration loop, one independent review of estimator and linkage risks,
and at most two mechanical corrections for a failed command. No significance
search, outcome relabeling, or unrestricted source expansion. The initial
critical-path work is local manuscript/design reconciliation while three
bounded workers handle collection materials, estimator implementation, and
identification bounds.

Run each worker's registered builder and test commands after cherry-picking.
Then run:

```text
python3 scripts/build_validation_inference_status.py
python3 -m unittest discover -s tests -p test_validation_inference_status.py
python3 scripts/validate_immutable.py
python3 scripts/validate_ledgers.py
python3 scripts/build_human_confirmation_register.py --check
python3 scripts/validate_probability_validation_frame.py --source-dir /Users/shunyuhao/Documents/LGFV/data/raw/probability_validation_sources
python3 scripts/validate_label_role_rebuild.py
python3 scripts/build_sparse_outcome_model_audit.py --help
latexmk -g -pdf -interaction=nonstopmode -halt-on-error paper/main.tex
git diff --check
```

The sparse-outcome audit's documented output-directory option will be used to
reproduce its fixed model set in this experiment, not overwrite past results.
Record actual commands and results in the run log. Source-derived DSL claims
must be checked against the original NeurIPS paper; finite-population special
cases are explicitly derived here rather than attributed as a new method.
