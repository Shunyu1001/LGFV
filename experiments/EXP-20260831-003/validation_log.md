# Validation log

## Package checks

Run on 2026-08-31 from branch `codex/lgfv-validation-frame-freeze`:

| Check | Result |
|---|---|
| Freeze-package validator with both temporary cache directories | pass; all raw hashes, byte sizes, exact PDF-page text hashes, combined extraction hashes, four gate decisions, frozen files, ledgers, and no-draw flags verified |
| `python3 -m unittest tests.test_validation_freeze_package` | pass; 6 tests |
| `python3 scripts/validate_immutable.py` | pass; 4 immutable files |
| `python3 scripts/validate_ledgers.py` | pass; 1 change request, 9 claims, 18 executed experiments, 29 literature rows, and 11 reviewer issues |
| `python3 scripts/validate_labels.py` | pass; 94 rows and 94 cases, with 89 inherited missing-local-extraction warnings |
| `python3 scripts/validate_master_case_pool.py` | fail on 94 pre-existing rows missing `reference_label_producer` |
| `git diff --check` | pass |

The master-case-pool failure is outside this workstream's permitted files. No
master-pool, label, or producer field changed in this branch, and the targeted
validator confirms the frozen working-reference and LLM-surrogate file hashes.
The failure is preserved rather than repaired opportunistically.

The source caches used for the stronger package check were temporary and are
not part of the commit. The default package validator also passes without
those caches by checking the committed manifests, exact record sets, registered
hashes, decisions, governance files, and frame state.

## Counts verified

- Evidence layer: 4 reviewed gates; 3 resolved under existing rules; 1 requires
  a PI-approved rule or explicit exclusion; 0 integrated.
- Registered frame: 4 open gates across 3 units; unchanged.
- Random draws: 0.
- Raw source documents committed: 0.
- Exit-type, working-reference, and LLM-surrogate label changes: 0.
