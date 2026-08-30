# Execution summary

## Preparation

- Read `AGENTS.md`, `program.md`, all files under `immutable/`,
  `ledgers/research_state.yaml`, `ledgers/reviewer_issues.tsv`, the central
  claim, experiment, and literature ledgers, the measurement handoff, the full
  codebook and coding-strategy section, all validation memos, and the required
  prose guidance.
- Created `codex/measurement-validation` from
  `e178e195704fe6ad6ec353a28081e444995350e7`.
- Recorded input hashes in `run_manifest.yaml` before running the audit.

## Mechanical retry

The first hash command used `sha256sum`, which is not installed in this macOS
environment. The unchanged hash task was retried once with `shasum -a 256` and
succeeded.

## Analysis commands

```text
python3 scripts/measurement_validation/audit_measurement_estimands.py
python3 scripts/measurement_validation/audit_measurement_estimands.py --check
```

The first command reproduced the declared counts and wrote the estimand map,
count audit, design requirements, and metrics. The second command confirmed
that deterministic regeneration is byte-identical.

## Result summary

- Declared-count discrepancies: none.
- Selected-overlap nominal concordance: 61/61.
- Target-population positive predictive value: not identified.
- Recall, calibration, four-category error, sampling error, and independent
  inter-coder agreement: not identified.
- Proposed probability frame: 133 named, source-available, non-overlap
  issuers, with a 60-of-97 positive sample and a census of 36 nonpositive
  issuers.
- Validation draw executed: no; human approval is required.

## Validation commands

```text
python3 -m py_compile scripts/measurement_validation/audit_measurement_estimands.py
python3 scripts/validate_immutable.py
python3 scripts/validate_ledgers.py
python3 scripts/validate_labels.py
python3 scripts/validate_master_case_pool.py
git diff --check
```

All commands exited successfully. The label validator confirmed 94 rows and 94
cases. The master-case-pool validator confirmed 114 rows and 114 cases while
repeating the repository's existing warnings that extracted source text is not
tracked locally for many gold rows. No warning was suppressed or treated as a
successful source-packet check.
