# Experiment brief: Geography, scope, and probability frame

## Registration

- Experiment: `EXP-20260830-015`
- Registered: `2026-08-30T22:20:00+08:00`
- Loop: `measurement_validation`
- Base commit: `5a68bf10de84491ab39c47427d585099e2c34b49`
- Branch: `codex/geography-scope-probability-frame-ultra`
- Prior result: `EXP-20260830-011` left 88 geography assignments unresolved and 98 issuer-scope decisions under review in a 133-issuer proposed frame.

## Falsifiable bottleneck

The 133-issuer candidate frame cannot support a probability validation design unless legal issuers are identifiable, geography and scope decisions follow the fixed source hierarchy, duplicates remain traceable to their originating disclosure rows, strata are frozen without outcome information, and every eligible unit has a positive planned inclusion probability.

## Hypothesis and success criteria

The fixed-hierarchy review and deterministic frame builder will produce an auditable candidate frame in which:

1. all 88 baseline geography gaps and all 98 baseline scope reviews receive a case-level disposition, including `unresolved_after_search` when authoritative evidence is insufficient;
2. every resolved geography and scope decision cites an issuer-linked source with a document identifier, URL, retrieval date, and page or line basis where available;
3. every failed geography or scope gate appears once in the conflict and unresolved-case log;
4. legal-issuer unit identifiers are unique while every originating disclosure row remains recoverable;
5. the frozen strata use only screen status, source coverage, historical-capacity bin, debt-pressure availability, and administrative level;
6. both screen-positive and screen-nonpositive eligible strata are represented, and every eligible unit has a strictly positive proposed inclusion probability; and
7. no random sample is drawn and no exit-type label is accessed, assigned, revised, or exposed.

The integrity gate fails if evidence is inferred from an ambiguous company name, a source cannot be traced to the issuer, a conflict is coerced into a unique match, any outcome label enters a stratum, an originating disclosure row is lost, or the sampling draw is executed.

## Fixed inputs

| Input | SHA-256 |
|---|---|
| `data/validation/proposed_one_sided_validation_frame_enriched.csv` | `9cc5822b69f548b4d6673d895b38f7c2c5a3196a87f41c29edbd49107d1bce26` |
| `data/validation/source_supported_validation_geography_scope_crosswalk.csv` | `50b1f286805aa6a745551aff0172885b53296db18d6fe41a5e9907bef602720a` |
| `data/validation/validation_geography_conflict_log.csv` | `56a7b77429b24ce42fdb378a21faef942faee4a278d33e7c89c82955870f5134` |
| `data/validation/validation_geography_retrieval_manifest.csv` | `669f8c7d7f9294760ecebdb1c1d8f32a1168737274b1730cc34801dd65b4d8bc` |
| `data/analysis_inputs/codex_surrogate_labels_2026_07_03_expanded.csv` | `cfced00afd193fa68d95db10888d05069fab27e7c957832d29bf6260ac44dfbe` |
| `data/document_inventory.csv` | `8d5f13810f31a91b293ccc917153cf2e21f252445719de5a174604151dbd6d27` |
| `data/source_inventory.csv` | `a83c47e7a8c1f8989d9d8e4289b16548c058b4b567ed4725e56310cb41dd8c8c` |
| `coding/source_search_protocol.md` | `6c1146dac712b58cb49cd64124f71a91d5e76d1baf76ca46f8e39c57f47d8c8c` |
| `coding/codebook.md` | `877a898bfc125e9bfd35c1f612b5034a00ab30cd3a9f9efaca7f10aab9dc9b66` |
| `coding/label_provenance.md` | `fde96643b2038e571ef7f604af9d26cf08c142b7086f644696da825e5922e55f` |
| `data/validation/label_role_registry.csv` | `48b2610cc26c8f411d04fdabd692b9706fa3846a266b2f1509bfabcbc71b099b` |

## Permitted files

- `data/validation/source_supported_validation_geography_scope_crosswalk.csv`
- `data/validation/validation_geography_conflict_log.csv`
- `data/validation/validation_geography_retrieval_manifest.csv`
- `data/validation/probability_validation_geography_scope_crosswalk.csv`
- `data/validation/probability_validation_unresolved_log.csv`
- `data/validation/probability_validation_source_manifest.csv`
- `data/validation/probability_validation_frame_candidate.csv`
- `data/validation/probability_validation_frame_origin_rows.csv`
- `data/validation/probability_validation_frame_flow.csv`
- `data/validation/probability_validation_sampling_design.csv`
- `scripts/build_probability_validation_frame.py`
- `scripts/validate_probability_validation_frame.py`
- `tests/test_probability_validation_frame.py`
- `experiments/EXP-20260830-015/**`
- one append-only proposal row in `ledgers/experiments.tsv`

No immutable file, exit-type label, manuscript result, claim, or sampling-design rule may be changed. The sampling file is a proposal for later human approval, not an executed design.

The three `validation_geography_*` files are retained as the quarantined
`EXP-20260830-011` inputs. The completed review is written to new
`probability_validation_*` successors so that the earlier experiment remains
reproducible rather than being overwritten.

## Execution plan and commands

1. Audit all fixed inputs and reproduce the 88 geography and 98 scope baselines.
2. Review each open issuer under the fixed source hierarchy and record exact evidence or an unresolved disposition.
3. Build the legal-issuer frame, origin-row map, flow table, and sampling-design proposal deterministically.
4. Run:

```text
python3 scripts/build_probability_validation_frame.py
python3 scripts/validate_probability_validation_frame.py
python3 -m unittest tests.test_probability_validation_frame
python3 scripts/validate_immutable.py
python3 scripts/validate_ledgers.py
python3 scripts/validate_labels.py
```

## Budget and stop rules

- Review budget: all 98 scope-review issuers and all 88 unresolved-geography issuers.
- Retrieval budget: at most three fixed-hierarchy search rounds per unresolved issuer, prioritizing exchange-hosted, government, SASAC, registration, prospectus, legal-opinion, and rating-report evidence.
- Mechanical retry budget: two retries per failed retrieval or parsing step without changing the hypothesis or success criteria.
- Stop rather than infer when the issuer, geography, controlling-owner level, or platform-like role cannot be tied to authoritative evidence.
- Do not draw the sample, calculate validation accuracy, or inspect working-reference exit-type labels.
