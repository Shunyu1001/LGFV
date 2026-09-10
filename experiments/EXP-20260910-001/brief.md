# Corrective frame integration

Registered: 2026-09-10 before corrective execution.
Base commit: `e9da7bf3dbac04eabcd615997fb026bf1b2b1379`.
Branch: `codex/validation-frame-freeze-execution`.
Loop: measurement_validation.
Corrects: crashed `EXP-20260831-004`, whose provisional outputs are in the base.
Authorization: PI decision dated 2026-09-02, commit `2fe53f1`, and resumption
request dated 2026-09-10. No new research rule is proposed.

## Known result and falsifiable bottleneck

The interrupted builder already produced 67 eligible units and 24 strata.
Those counts are known before this experiment and are not a prospective
scientific finding. The bottleneck is whether the authorized integration can
be reproduced from its original input with verified continuous citations,
unchanged protected records, accurate current validation, and intact historical
experiment artifacts.

## Fixed acceptance criteria

1. Relative to `9977dd752f911bfd07dc4d434301041ef485c9f2`, crosswalk fields
   change only for `mv_940b87861065` and `mv_dd84e076bf32`. All 131 other
   records, including Shenzhen International, remain value-identical and in
   the same order. The two modifications match the approved evidence patches.
2. All protected files listed in EXP-004, immutable files, outcome labels,
   frozen source inventories, source-packet predecessors, and Experiment 001
   metrics remain byte-identical. New metrics are stored under this experiment.
3. All 157 origin identifier/document mappings remain identical. Only the
   Guiyang origin may change scope metadata. All 66 existing candidate records
   and 23 existing stratum allocations remain identical; Guiyang adds one
   candidate and one stratum. Proposed probabilities remain one; no draw,
   coder assignment, confirmation, or realized inclusion is claimed.
4. Rebuilding from the registered input and rerunning on integrated output
   produce identical output hashes. Tampering with an unrelated field, a
   protected label, a scope reason, or a frozen origin must be rejected.
5. Current validation verifies every cited cache against its raw and text
   hashes and checks continuous excerpt containment. Recovery from a recorded
   URL is permitted only if the raw hash agrees; no raw file is overwritten.
6. Historical EXP-002/003 checks use their registered snapshot for mutable
   integration files; their evidence packets and protected objects are still
   checked against current tracked bytes. No old result is rewritten.

## Files and commands

Permitted: this experiment directory; probability-frame builder and validator;
freeze-package validator and targeted tests; existing seven probability-frame
CSV outputs; EXP-004 assessment/execution log as additive corrections;
append-only experiment/reviewer/decision entries; research state; and
CR-20260831-001 implementation status. No manuscript, claim, codebook,
immutable object, prior experiment result, or raw source may change.

Commands: `python3 scripts/build_probability_validation_frame.py --integrate-exp004`;
`python3 scripts/validate_probability_validation_frame.py`;
`python3 scripts/validate_validation_freeze_package.py`;
targeted unittest discovery for both probability-frame and freeze-package
tests; `python3 scripts/validate_immutable.py`;
`python3 scripts/validate_ledgers.py`; `python3 scripts/validate_labels.py`;
`python3 scripts/validate_master_case_pool.py`; and an experiment-local audit
runner that records commands, return codes, field diffs, and output hashes.

Budget: one corrective implementation and two mechanical retries, up to 90
minutes of execution; one read-only parallel AI review. Record failures and
leave the result quarantined if the fixed integrity criteria are not met.
The previous three failures remain in EXP-004. This experiment cannot validate
outcome accuracy or identify national prevalence, recall, or four-class error.
