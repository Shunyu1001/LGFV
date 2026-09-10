# Current validation collection package

- Experiment: EXP-20260910-004; loop: measurement_validation.
- Base commit: 4330c5728dec64ba30c1faec972fad0097622e9d.
- Branch: codex/validation-packets-20260910.
- Worktree: /Users/shunyuhao/.codex/worktrees/lgfv-validation-packets/LGFV.
- Hypothesis: the current 67 eligible issuer units can be handed off with
  deterministic source locators, blank independent human-entry instruments,
  exact reference-case identity auditing, and explicit missing-input states
  without extending HC-20260910-001 or changing the proposed design.

## Scope and budget

Only new files in scripts/build_validation_collection_package.py,
tests/test_validation_collection_package.py,
data/validation/collection_2026_09_10/*, and this experiment directory are allowed.
No historical outputs, source snapshots, human report, sampling design,
manuscript, or global ledger may be edited. The user's explicit global-ledger
restriction overrides the general append requirement for this worker; record
attempts locally for coordinator integration. No remote push, main merge,
source retrieval, frame freeze, random draw, or new label is authorized.

Budget: one conceptual implementation/evaluation loop and at most two minimal
mechanical retries, preserving all failures. Stop after those attempts. This
brief is committed before running the implementation or analyzing overlaps.
Preflight reads are for rules, schemas, and existing builder conventions only.

## Inputs and identity rule

Pin all consumed tracked inputs to the stated base Git objects; report SHA-256
hashes and reject mutated inputs. Use the current candidate and origin rows,
source and document inventories, source manifest, sampling proposal, reference
snapshot and exact confirmation report/register, plus historical coding packet.
Additional tracked row-level origin metadata may be read only when needed for
documented event identity. Do not search for arbitrary issuer aliases.

An authorized historical mapping requires exact issuer identity and an exact
documented event/source-case link to one of the 94 report-covered cases. A city
or historical-capacity match is not a label match. Missing or ambiguous event
evidence must remain unmatched. Even a historical match does not become a new
independent decision or an approved probability-validation outcome. Report
missing human labels and process metadata as missing/null/blank, never as
negative outcomes, zero, or false. Proposed inclusion probability 1 remains
proposed; realized probability is missing until separately authorized.

## Success criteria and exact checks

1. Deterministic coverage of exactly 67 unique current eligible units and all
   their origin-document links; unresolved locators have explicit reasons.
2. Separate blinded source/entry sheets use allowlisted columns and no inherited
   surrogate, status, capacity, debt, existing label, identity, or signature
   values. Coordinator sidecars retain original design metadata as proposed.
3. Machine-readable reference-match audit, historical packet comparison, and
   realized-input readiness distinguish source metadata from recovered files,
   blank templates from decisions, and historical checking from new validation.
4. Input and output hashes, duplicate detection, schema/leakage mutations,
   same-city/wrong-issuer and same-issuer/wrong-event mapping tests pass.
5. No out-of-scope changes; baseline read-only integrity checks pass or their
   pre-existing failures are explicitly retained and explained.

Commands (from this worktree, with PYTHONDONTWRITEBYTECODE=1):

```text
python3 scripts/build_validation_collection_package.py
python3 scripts/build_validation_collection_package.py --check
python3 -m unittest discover -s tests -p test_validation_collection_package.py -v
python3 scripts/build_human_confirmation_register.py --check
python3 scripts/validate_immutable.py
python3 scripts/validate_ledgers.py
python3 scripts/validate_labels.py
python3 scripts/validate_master_case_pool.py
git diff --check
git status --short
```

The builder must refuse overwriting altered human-entry forms. Tests may use
temporary directories for mutation fixtures, not edit historical inputs.
Assessment uses keep only for the collection/audit artifact if hard gates pass;
inference readiness may remain missing and all design approvals remain pending.

## User clarification before evaluation

The current 67 units meet platform scope; 10 have no direct formal-event screen.
Platform scope does not establish codebook exit-case eligibility. Human entry
fields separate exit-case eligibility, formal-event evidence, and post-event
evidence. Without the necessary evidence the exit case stays unresolved or
ineligible, with a missing label/outcome, not institutional-change zero and not
a fifth exit label. Freeze/census authorization remains pending; an unanswered
question is not authorization. This clarifies the original boundaries without
changing the hypothesis, coverage target, or one-loop/two-retry budget.
