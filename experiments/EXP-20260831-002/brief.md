# Experiment brief: Multiple-location geography rule audit

## Registration

- Experiment: `EXP-20260831-002`
- Registered: `2026-08-31T09:59:20+08:00`
- Loop: `measurement_validation`
- Base commit: `5de57d63a70b52cedc5223a7fa6f751bfc70cfe1`
- Branch: `codex/lgfv-validation-frame-freeze`
- Predecessor: `EXP-20260831-001`

## Falsifiable bottleneck

Two frozen issuer units, `mv_2547f5fbc2e2` and `mv_940b87861065`, have
source-supported multiple locations. The registered geography evidence rule
accepts an issuer's registered address, domicile, office location,
registration authority, controlling owner, or named supervising government,
but it does not rank these location concepts. The frame cannot treat either
unit as having one province-city without determining whether existing frozen
rules reconcile the evidence or a new location-precedence rule is required.

## Hypothesis and decision criteria

Authoritative issuer, government, exchange, rating, registration, and bond
sources will permit one of two auditable conclusions for each unit:

1. the locations can be reconciled under the existing rules because one
   source is obsolete, concerns another legal entity, or is otherwise outside
   the focal issuer and date scope; or
2. the sources continue to support multiple focal-issuer locations, so a
   unique assignment requires a new validation-design rule.

An existing-rule resolution requires exact legal-entity, date, and location
evidence that explains every contradictory location without ranking two valid
focal-issuer locations. A source hierarchy may resolve differences in factual
reliability; it may not create a substantive address-type precedence that is
absent from the frozen protocol. If any valid focal-issuer location remains in
conflict, the gate remains open and the experiment is quarantined.

## Frozen inputs

| Input | SHA-256 |
|---|---|
| `experiments/EXP-20260831-001/brief.md` | `8f35d7e4f73c6f7725a8299c2f894112cd8c432e9b29a43cde491dfbc3db8abc` |
| `experiments/EXP-20260831-001/assessment.md` | `b9cbc6cbe1d004437c9bc2680627d3f07c87969e99720b6b73a459571e5b6bbc` |
| `experiments/EXP-20260831-001/ultra_audit.md` | `be09d57db965ffb0e0824579541959e6712d5f2899f2a2c5b074cf25c6035495` |
| `experiments/EXP-20260831-001/review_decisions.csv` | `b86381191c4373b4049bca1afe942c59b732c14fe368f032f7ca19412b042a8b` |
| `data/validation/probability_validation_geography_scope_crosswalk.csv` | `fc72c263dade64d3404d873fec0b40328429346661710d24988c448fbeb711d2` |
| `data/validation/probability_validation_unresolved_log.csv` | `5c9ede8c97b86add246ab99b2a6a052375f849f9be9fecc02abd4c95f368571c` |
| `data/validation/probability_validation_source_manifest.csv` | `5713057b161939748a334426bb41e5ed1ce59adc4519204ea0b1d31b0bb1d664` |
| `coding/source_search_protocol.md` | `6c1146dac712b58cb49cd64124f71a91d5e76d1baf76ca46f8e39c57f47d8c8c` |
| `coding/codebook.md` | `877a898bfc125e9bfd35c1f612b5034a00ab30cd3a9f9efaca7f10aab9dc9b66` |

The registered temporary caches for
`doc_exp10_20260704_0013_006`, `doc_exp10_20260704_0013_007`,
`doc_sch_20260630_0135_002`, and `doc_sch_20260630_0135_010` must match the
hashes in the predecessor source manifest before use.

## Search and evidence rules

For each unit, inspect the full registered cache before retrieving new
material. New retrieval follows the existing hierarchy: government or
registration records; issuer, exchange, annual-report, prospectus, or legal
records; rating records; and supplementary discovery sources. Search snippets
are not evidence. Each retained source must record the publisher, title, URL,
publication and retrieval dates, raw SHA-256, extraction method and hash, exact
page or webpage locator, and a short exact excerpt. Contradictory evidence is
retained.

The retrieval budget is eight opened authoritative records per unit, excluding
duplicate mirrors and search-result pages. Stop rather than infer after the
budget is exhausted.

## Permitted files

- `experiments/EXP-20260831-002/**`;
- `change_requests/CR-20260831-001.md` if a new rule is necessary;
- one append-only row in `ledgers/change_requests.tsv` for that proposal;
- one append-only row in `ledgers/experiments.tsv` after assessment;
- a targeted validator and tests for the freeze-decision package; and
- an append-only update to the open validation-frame reviewer issue.

Do not change the prior crosswalk, unresolved log, source manifest, frame,
sampling design, labels, immutable files, codebook, source hierarchy,
manuscript, or claims. Do not execute a sample draw.

## Required artifacts and checks

The experiment must produce a source manifest, exact excerpt register,
case-level decision record, run manifest, metrics, assessment, and execution
log. If a new rule is required, the change request must state a prospective
rule, alternatives, consequences, and falsifiable acceptance tests without
implementing it.

```text
python3 scripts/validate_validation_freeze_package.py
python3 -m unittest tests.test_validation_freeze_package
python3 scripts/validate_immutable.py
python3 scripts/validate_ledgers.py
python3 scripts/validate_labels.py
python3 scripts/validate_master_case_pool.py
git diff --check
```

## Stop rule

The frame remains quarantined unless both locations are uniquely resolved
under an already-registered rule and the PI separately approves the freeze.
Drafting a proposed precedence rule does not resolve either gate.
