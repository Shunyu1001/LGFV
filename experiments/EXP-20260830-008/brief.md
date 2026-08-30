# Experiment brief: Validation-frame geography

## Experiment identity

- Experiment ID: `EXP-20260830-008`
- Loop: `empirical_simulation`
- Base commit: `45714fa884580f4a6c77e7fbce30d3c46f41e2c9`
- Started at: `2026-08-30T13:35:00+08:00`
- Owner: measurement-validation worktree

## Falsifiable bottleneck

Experiment 003 reconstructed the 133 proposed issuer units but found province
and city missing for 128 units. This experiment tests whether existing tracked
inventories contain source-keyed geography that can be joined without
inferring location from an issuer's name.

## Hypothesis

Exact joins on tracked source-row, pool, document, or issuer identifiers can
resolve both province and city for at least 90 percent of the 128 incomplete
units without conflicting matches. The join will preserve its source file and
key for every resolved field and will leave unmatched or conflicting units
blank.

## Source hierarchy

Use only exact identifier matches, in this order:

1. `data/analysis_inputs/master_case_pool.csv` by source-row or pool identifier.
2. `data/analysis_inputs/llm_candidate_pool_seed_2026_07_03_expanded.csv` by
   source-row or pool identifier.
3. `data/source_inventory.csv` by source identifier.
4. `data/document_inventory.csv` by document identifier.

An issuer-name join may be used only when a tracked file has the exact
normalized issuer name and a single nonconflicting province-city pair. The
script must not parse a location from Chinese company-name text or use external
lookup.

## Inputs

- `data/validation/proposed_one_sided_validation_frame.csv`
- `data/analysis_inputs/master_case_pool.csv`
- `data/analysis_inputs/llm_candidate_pool_seed_2026_07_03_expanded.csv`
- `data/source_inventory.csv`
- `data/document_inventory.csv`

## Permitted files

- New scripts under `scripts/measurement_validation/`
- New outputs under `data/validation/`
- New files under `experiments/EXP-20260830-008/`

The experiment must not modify labels, central ledgers, paper files, or prior
experiment outputs.

## Planned change

Create a deterministic geography-audit script that inventories the available
keys and geography fields, applies the frozen exact-match hierarchy, records
the source and key of each proposed match, and emits a separate enriched frame.
Conflicts and unresolved units remain explicit.

## Success criteria

1. At least 116 of the 128 incomplete units receive both province and city,
   meeting the predeclared 90 percent threshold after rounding up.
2. Every resolved geography has one recorded source file and exact join key.
3. No unit receives conflicting geography, and no company-name parsing or
   external lookup is used.
4. The original Experiment 003 frame remains unchanged.
5. The enriched frame remains explicitly proposed and no sample is drawn.
6. Deterministic regeneration and repository validation checks pass.

The experiment is kept only if every criterion passes. A reproducible partial
join is quarantined; a join that hides conflicts or infers geography from names
is invalid.

## Commands

```text
python3 scripts/measurement_validation/enrich_validation_geography.py
python3 scripts/measurement_validation/enrich_validation_geography.py --check
python3 scripts/validate_immutable.py
python3 scripts/validate_ledgers.py
python3 scripts/validate_labels.py
python3 scripts/validate_master_case_pool.py
git diff --check
```

## Budget

- One deterministic geography-audit script.
- At most two machine-readable outputs, one metrics file, one assessment, and
  one proposed ledger artifact.
- At most two minimal mechanical retries.
- No source retrieval, manual geography imputation, label change, sample draw,
  or manuscript edit.

## Review gate

Even a complete geography join does not establish city-platform eligibility.
The PI must review provincial, central, specialized, and other boundary issuers
and approve the validation frame before sampling.
