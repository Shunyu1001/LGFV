# Experiment brief: Correct the geography-scope probability frame

## Registration

- Experiment: `EXP-20260831-001`
- Registered: `2026-08-31T05:13:03+08:00`
- Loop: `empirical_simulation`
- Base commit: `7dfa332c6d4c965605abe3337cf0bfd536f068cf`
- Corrects: `EXP-20260830-015`
- Branch: `codex/geography-scope-probability-frame-ultra`
- Identifier check: the current `main` branch ends at
  `5a68bf10de84491ab39c47427d585099e2c34b49` and contains no
  `EXP-20260831-*` identifier; the current worktree branch contains experiments
  through `EXP-20260830-015`.

This is a registered corrective reproduction after a read-only Ultra audit of
the committed Experiment 015 artifacts. It is not a prospective discovery
claim. Exploratory audit runs performed before this brief are diagnostic only;
the registered result is the deterministic run performed after this brief.

## Falsifiable bottleneck

Experiment 015's committed candidate cannot be relied on because the audit
identified nonunique geographies coerced to unique assignments, source
locators that do not identify the focal issuer, scope false negatives, five
corrupted source-row-to-pool-ID pairs, incomplete historical and contemporary
control joins, and a validator that could reproduce several builder defects.

## Corrective hypothesis and success criteria

A source-backed corrective rebuild will:

1. adjudicate the 88 inherited geography cases as 86 unique, two multiple, and
   zero unsupported after search;
2. resolve the 98 inherited scope cases as 53 eligible and 45 ineligible, with
   zero unresolved;
3. retain honest full-frame counts of 130 unique, two multiple, and one
   unresolved geography, and 66 eligible, 66 ineligible, and one unresolved
   scope disposition;
4. retain all 157 originating disclosure rows with the exact source-row and
   pool-ID pairing independently reconstructed from safe surrogate columns;
5. construct 66 unique eligible issuers, 73 eligible originating disclosure
   rows, and 23 strata using only the registered pre-outcome variables;
6. verify every retained evidence excerpt against a hash-verified extracted
   page and retain one unresolved-log row for each failed gate;
7. assign every eligible issuer a strictly positive proposed inclusion
   probability while keeping `random_draw_executed=false`; and
8. avoid reading, assigning, changing, or revealing any working-reference
   exit-type outcome and avoid describing model review as human validation.

Failure of any criterion leaves the correction quarantined or invalid. Even if
all mechanical criteria pass, the frame remains quarantined until the two
nonunique locations, the legal-identity conflict, and PI approval are resolved.

## Frozen corrective inputs

The committed Experiment 015 outputs at the base commit are the correction
baseline:

| Input | SHA-256 at base commit |
|---|---|
| `experiments/EXP-20260830-015/review_decisions.csv` | `7841c82ed83ef48291356a8c655d4f94ce2a5865d3537cecc834b40513881b37` |
| `data/validation/probability_validation_geography_scope_crosswalk.csv` | `4908a98226766cd8d067c4086248f4d72ec8bcde60740f76efe1798374d815a1` |
| `data/validation/probability_validation_unresolved_log.csv` | `c8b6312d1dc2ba9bb7729d7b5e74f0bf62f419dff4c09f6303f6382c9b882f30` |
| `data/validation/probability_validation_source_manifest.csv` | `159d37282110e551c55f7bd3754c60bbd623b1f9652199a4ea1aef72f5906eb7` |
| `data/validation/probability_validation_frame_candidate.csv` | `05a1e83451986eee55074bd23caff64d6966fee32bae10ed42c4aec29838f60d` |
| `data/validation/probability_validation_frame_origin_rows.csv` | `c4582058c055f90d13b175fa4ea2215a6b9a2f35471cb3536e009418970f0790` |
| `data/validation/probability_validation_frame_flow.csv` | `f98c50a346d7c1c4a1cef522d73777102ded85b39ff0dc52b9308120ec581107` |
| `data/validation/probability_validation_sampling_design.csv` | `0b34131d4d17dce0826030e82f318b665bc9bee16be38b0ba145d18acc56086e` |
| `experiments/EXP-20260830-015/metrics.json` | `ee0d50b824de690458ddadb31c06b647fbc91dc595c070c0b2da3fd2edf226e5` |

The audit-derived case register is frozen for the registered reproduction as
`experiments/EXP-20260831-001/review_decisions.csv`, SHA-256
`b86381191c4373b4049bca1afe942c59b732c14fe368f032f7ca19412b042a8b`.
The original source inputs retain the hashes registered in Experiment 015. Two
previously undeclared direct builder inputs are now explicit:

| Input | SHA-256 |
|---|---|
| `data/analysis_inputs/candidate_city_historical_capacity.csv` | `eed33784ec5e1b9c3afee2eef8d8e993f503e8ddd066134236ed7c44a0e9493f` |
| `data/analysis_inputs/contemporary_city_controls.csv` | `3c5f03040ad9e1b881a7ee6b700e021d06a22713997fa4c7711e2f066c704fe4` |

The immutable analysis plan's contemporary-prefecture exposure rule is
implemented for county-level Taicang and Rugao. This operational correction is
registered here rather than represented as part of Experiment 015's design.

## Permitted files

- the seven `data/validation/probability_validation_*` successor outputs;
- `scripts/build_probability_validation_frame.py`;
- `scripts/validate_probability_validation_frame.py`;
- `tests/test_probability_validation_frame.py`;
- `experiments/EXP-20260831-001/**`;
- one append-only correction row in `ledgers/experiments.tsv`.

Experiment 015's committed directory and ledger row must remain unchanged. No
immutable file, raw source, working-reference label, exit-type definition,
manuscript result, claim, or approved sampling rule may be changed.

## Registered execution

```text
python3 experiments/EXP-20260831-001/compile_source_review.py --source-dir /tmp/lgfv-exp015-sources
python3 scripts/build_probability_validation_frame.py
python3 scripts/validate_probability_validation_frame.py
python3 -m unittest tests.test_probability_validation_frame
python3 scripts/validate_immutable.py
python3 scripts/validate_ledgers.py
python3 scripts/validate_labels.py
python3 scripts/validate_master_case_pool.py
git diff --check
```

The source-cache limit is the surviving temporary packet. Stop rather than
infer if a cited source, legal identity, geography, controller, or platform
role cannot be verified. Do not execute a sample draw or calculate validation
accuracy.
