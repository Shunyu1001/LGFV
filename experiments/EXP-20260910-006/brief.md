# Deterministic identification bounds

## Registration

- Experiment: EXP-20260910-006.
- Base commit: 4330c5728dec64ba30c1faec972fad0097622e9d.
- Branch: codex/validation-bounds-20260910.
- Worktree: /Users/shunyuhao/.codex/worktrees/lgfv-validation-bounds/LGFV.
- Loop: claim_evidence; bounded worker, coordinator owns integration.
- Budget: one deterministic implementation, at most two minimal mechanical
  retries per execution failure, up to 75 minutes of local work; no network,
  sampling, model fitting, source acquisition, or human coding.
- This brief is committed before input-count audits or bound computation.

## Bottleneck and hypothesis

The exact source-supported reference/surrogate overlap, conditional on the
author's existing human-check report and retained original labels, identifies
nontrivial deterministic bounds in the finite expanded issuer screen without
assuming representative missingness. This is falsified if confirmation hashes,
issuer collapse, case links, source identifiers, or outcome consistency fail.
Reported baseline counts (94 references, 158 issuers, 61 selected overlap,
67 current candidates) are hypotheses to verify, not inputs to arithmetic.

## Inputs and scope

Read the frozen reference and original label snapshots, the human-confirmation
report and register, expanded disclosure labels and issuer summary, existing
source inventories and overlap diagnostics, and current validation candidate,
origin, sampling proposal, and readiness records. Capture input SHA-256 hashes
before computation; require the report's exact reference-snapshot hash and
case-level label agreement. Use existing exact identifiers and the established
compact-name rule only to check links; no fuzzy matching or new source claims.

The primary population is the finite expanded issuer screen. A screen label is
not a reference outcome. All unconfirmed issuer outcomes remain unknown.
For an event indicator, report lower = known positive / N and upper =
(known positive + unknown) / N, with confirmed negatives reducing the upper
bound. Retain selected-overlap concordance as a separate descriptive quantity.
Positive-label correctness uses only issuers actually predicted nominal.

Class-specific bounds are permitted only with explicit unit and eligibility
conditions. A no-direct-event screen is never a known nonnominal exit. Do not
force four-class exhaustiveness on units without established exit eligibility.
The putative 191-unit city-platform union may be reported only separately and
conditionally if exact one-to-one case/issuer links and unit/eligibility
assumptions can be stated. Otherwise withhold it and record why. Current
candidate readiness is separate from outcome identification and human review.

## Falsifiable checks and success criteria

1. Reconstruct all selected disclosure groups and exact source-row/pool links;
   compare every issuer count, screen label, overlap flag, case ID, and retained
   outcome. Empty names, duplicate issuer rows, inconsistent links, duplicate
   source identifiers, and unexplained reference-name collisions fail closed.
2. Enumerate every reference case per compact issuer, including cases outside
   the screen. Conflicting outcomes fail; same-label multiple cases are also
   explicit ambiguity, never silently overwritten. Require unique case IDs and
   preserve all identifiers in a generated audit.
3. Check original labels against the author-confirmed snapshot and register.
   Human-report coverage cannot expand beyond the report. Provenance hash
   mismatch or inconsistent confirmation fields fails before output writing.
4. Recompute denominator, known positive, known negative, and unknown counts;
   enforce their sum and endpoint inequalities. Complete labels yield exact
   fractions; no labels yield [0,1]; empty populations have undefined shares.
5. Reconcile candidate units and both screen strata with origin rows and the
   proposal without interpreting no-event flags as outcomes or a proposal as
   completed coding. Report missingness and population differences.
6. Tests cover complete/no-label inputs, inconsistent links, conflicting
   reference labels, duplicate issuer/case names, empty inputs, provenance hash
   mismatch, and byte-identical repeated outputs. Run applicable read-only
   repository validators. Standalone table compilation is allowed within the
   experiment directory; the coordinator retains the full paper build.
7. Keep requires all integrity gates plus improved traceability or narrower
   defensible claims. Preserve failures and adverse findings. Unresolved
   scientific ambiguity is quarantined or invalid, not a convenient exclusion.

## Allowed paths

- scripts/build_validation_identification_bounds.py
- tests/test_validation_identification_bounds.py
- data/analysis_inputs/validation_identification_bounds.csv
- paper/tables/validation_identification_bounds.tex
- experiments/EXP-20260910-006/*

No manuscript, global ledger, frozen input, human report, remote, or main-branch
edits. This worker-specific restriction supersedes generic ledger-writing
instructions: retain attempt records and proposed coordinator ledger/claim
rows under this experiment and leave actual insertion to the coordinator.

## Commands

Run from the isolated worktree:

```text
python3 scripts/build_validation_identification_bounds.py
python3 -m unittest discover -s tests -p test_validation_identification_bounds.py -v
python3 scripts/validate_immutable.py
python3 scripts/validate_ledgers.py
python3 scripts/validate_labels.py
python3 scripts/validate_master_case_pool.py
git diff --check
```

The builder will write generated counts, bounds, identifiers, input/output
hashes, and sober interpretation notes only to allowed paths. A second builder
run must reproduce every generated artifact byte for byte. Record actual
commands, output, status, and any additional read-only checks in the local
attempt log. No DSL, empirical-model, or manuscript rebuild is needed because
their outputs are outside this worker's scope.
