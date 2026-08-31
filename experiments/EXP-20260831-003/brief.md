# Experiment brief: Guiyang legal-identity and scope linkage

## Registration

- Experiment: `EXP-20260831-003`
- Registered: `2026-08-31T09:59:20+08:00`
- Loop: `measurement_validation`
- Base commit: `5de57d63a70b52cedc5223a7fa6f751bfc70cfe1`
- Branch: `codex/lgfv-validation-frame-freeze`
- Predecessor: `EXP-20260831-001`

## Falsifiable bottleneck

The frozen unit `mv_dd84e076bf32` is named
`贵阳市交通运营集团有限公司`, while the retained current government source
names `贵阳市公共交通投资运营集团有限公司`. The frozen packet does not establish
whether these names denote the same legal issuer, a rename, a successor, a
parent or subsidiary, or unrelated entities. Geography and scope therefore
remain open.

## Hypothesis and decision criteria

Authoritative issuer, government, registration, exchange, rating, and bond
records will either establish or refute a unique legal-identity chain. A
resolved chain under existing rules requires at least one original or
near-original record that states the rename, merger, succession, or ownership
relationship, plus a corroborating identifier or fact such as a unified social
credit code, registration number, bond issuer code, unchanged registered
address, or explicit government reorganization instrument.

Name similarity, shared abbreviation, a search snippet, or a shared city is
insufficient. If the chain is established, separate authoritative evidence
must identify the focal legal issuer's province-city, controlling-owner level,
and issuer-level or consolidated platform role. Contrary evidence is retained.
If the chain or either scope element remains ambiguous, both gates remain open
and the experiment is quarantined.

## Frozen inputs

| Input | SHA-256 |
|---|---|
| `experiments/EXP-20260831-001/brief.md` | `8f35d7e4f73c6f7725a8299c2f894112cd8c432e9b29a43cde491dfbc3db8abc` |
| `experiments/EXP-20260831-001/assessment.md` | `b9cbc6cbe1d004437c9bc2680627d3f07c87969e99720b6b73a459571e5b6bbc` |
| `experiments/EXP-20260831-001/ultra_audit.md` | `be09d57db965ffb0e0824579541959e6712d5f2899f2a2c5b074cf25c6035495` |
| `data/validation/probability_validation_geography_scope_crosswalk.csv` | `fc72c263dade64d3404d873fec0b40328429346661710d24988c448fbeb711d2` |
| `data/validation/probability_validation_unresolved_log.csv` | `5c9ede8c97b86add246ab99b2a6a052375f849f9be9fecc02abd4c95f368571c` |
| `data/validation/probability_validation_source_manifest.csv` | `5713057b161939748a334426bb41e5ed1ce59adc4519204ea0b1d31b0bb1d664` |
| `coding/source_search_protocol.md` | `6c1146dac712b58cb49cd64124f71a91d5e76d1baf76ca46f8e39c57f47d8c8c` |
| `coding/codebook.md` | `877a898bfc125e9bfd35c1f612b5034a00ab30cd3a9f9efaca7f10aab9dc9b66` |

The registered cache for
`web_saac_guiyang_public_transport_current_name` must match the predecessor
manifest before use.

## Search and evidence rules

Use up to three fixed search rounds. First, search exact-name and paired-name
government, SASAC, transport-bureau, public-resource, and registration records.
Second, search bond, exchange, rating, prospectus, and legal-opinion records.
Third, search explicit reorganization, rename, merger, ownership, and unified
social-credit-code combinations. Open and retain no more than twelve
authoritative records in total. Search snippets and commercial registries are
discovery aids unless they reproduce an original registration record.

Each retained source must record the publisher, title, URL, publication and
retrieval dates, raw SHA-256, extraction method and hash, exact page or webpage
locator, exact excerpt, and its identity, geography, owner, or role use.

## Permitted files

- `experiments/EXP-20260831-003/**`;
- one append-only row in `ledgers/experiments.tsv` after assessment;
- a targeted validator and tests for the freeze-decision package;
- a separate prospective rebuild experiment brief if the existing-rule gates
  are resolved; and
- an append-only update to the open validation-frame reviewer issue.

Do not change the prior crosswalk, unresolved log, source manifest, frame,
sampling design, labels, immutable files, codebook, manuscript, or claims. Do
not execute a sample draw or describe this Codex review as human validation.

## Required artifacts and checks

The experiment must produce a source manifest, exact excerpt register,
case-level decision record, run manifest, metrics, assessment, and execution
log. A resolved evidence finding is not integrated into the frozen frame in
this experiment. Any rebuild must be separately preregistered and reviewed.

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

Stop rather than infer if authoritative evidence cannot identify one legal
chain or cannot tie ownership and platform role to that chain. The frame
remains quarantined pending any separately registered rebuild and PI approval.
