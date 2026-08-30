# Experiment brief: Authoritative validation geography and scope

## Experiment identity

- Experiment ID: `EXP-20260830-011`
- Loop: `empirical_simulation`
- Base commit: `bf1bd7b99c7dd9261678015c9f050599ae862fe3`
- Started at: `2026-08-30T16:08:39+08:00`
- Owner: validation-geography-packet worktree

## Falsifiable bottleneck

Experiments 007 and 008 left 128 of the 133 proposed validation issuers
without traceable province and city. The proposed frame therefore cannot
establish its city-platform scope or geographic coverage. This experiment
tests whether authoritative original packet records can resolve geography,
legal identity, controlling ownership, and a provisional scope disposition
without reading geography from company names or assigning an exit label.

## Hypothesis

A fixed source hierarchy applied to the 128 unresolved units will provide a
unique, source-supported province-city pair and an explicit provisional scope
disposition for at least 100 units. The result may be lower or null and will
be retained. Source selection will not be changed after observing coverage.

## Inputs

- `data/validation/proposed_one_sided_validation_frame_enriched.csv`
- `data/document_inventory.csv`
- `coding/codebook.md`
- `immutable/data_manifest.yaml`

## Source hierarchy and evidence rules

For each unresolved issuer, use at most two already inventoried original
packet records, selected before retrieval in this order: prospectus, rating
report, legal opinion, audited financial statement, issuance plan, and other
issuer disclosure. Within a type, use the first document identifier in the
frozen frame order. The exchange page and original issuer document are treated
as separate retrieval fields but one source record.

A geography field is supported only by exact text in the opened record that
identifies the issuer's registered address, domicile, office location,
registration authority, controlling owner, or named supervising government.
Company-name tokens alone are not evidence. Legal identity and controlling
ownership must likewise have exact supporting text or remain unresolved.

The provisional scope disposition uses three values:

1. `provisionally_eligible` requires source-supported subprovincial public
   control and evidence of a platform-like public financing or project role.
2. `provisionally_ineligible` requires source-supported central, provincial,
   private, or purely commercial status without a documented city-platform
   role.
3. `review_required` preserves specialized, conflicting, incomplete, or
   otherwise ambiguous cases.

These are proposed scope dispositions, not final eligibility decisions. The
PI must review every disposition before approving a frame or sample.

## Planned change

Create a rights-aware retrieval manifest, a source-supported geography and
scope crosswalk, and a conflict log for all 128 unresolved units. Add a
deterministic validator that rejects blank unit IDs, duplicate units,
unsupported resolved fields, unrecorded conflicts, forbidden label or model
fields, any random-draw flag, and inconsistent summary counts. Raw retrieved
documents will be used only in a temporary directory and will not be committed
or substituted for the underlying source archive.

## Success criteria

1. All 128 unresolved units appear exactly once in the crosswalk.
2. At least 100 units have a unique, source-supported province-city pair and
   one of the three explicit provisional scope dispositions.
3. Every supported identity, geography, owner, and scope field records the
   source URL, document title and date, retrieval date, page or line locator,
   exact supporting text, publisher, access status, rights note, and SHA-256
   hash of the retrieved file.
4. Conflicting evidence is recorded without silently selecting the convenient
   version; unresolved evidence remains blank or `review_required`.
5. No source choice is based on achieved coverage, and no geography is parsed
   from an issuer name.
6. No exit label, model prediction, screen status, confidence, rationale,
   random seed, or selected-case field enters the crosswalk.
7. Deterministic validators and repository integrity checks pass.

Meeting every criterion yields `keep`. A reproducible low-coverage or
ambiguous result is `quarantine`; an access failure is `crash`; hidden
conflicts, name-based inference, post-result source selection, or label
contamination is `invalid`.

## Permitted files

- New scripts under `scripts/measurement_validation/`
- New outputs under `data/validation/`
- New files under `experiments/EXP-20260830-011/`

Do not modify gold labels, raw inventories, central ledgers, manuscript files,
prior experiment outputs, or the proposed sampling design.

## Commands

```text
python3 scripts/measurement_validation/build_validation_geography_scope_packet.py
python3 scripts/measurement_validation/validate_validation_geography_scope_packet.py
python3 scripts/measurement_validation/validate_validation_geography_scope_packet.py --check-metrics
python3 scripts/validate_immutable.py
python3 scripts/validate_ledgers.py
python3 scripts/validate_labels.py
python3 scripts/validate_master_case_pool.py
git diff --check
```

## Budget

- 128 unresolved issuer units.
- At most two fixed-hierarchy original packet records per issuer.
- One retrieval and extraction script, one deterministic validator, three
  machine-readable outputs, one metrics file, one assessment, one execution
  log, and proposed ledger and manuscript rows stored as experiment artifacts.
- At most two minimal mechanical retries without changing the hypothesis,
  source hierarchy, or success criteria.
- No probability sample, random seed, label assignment, model run, central
  ledger edit, or manuscript edit.

## Review gate

All scope dispositions, the 133-issuer target frame, the sampling allocation,
and any exclusion from the probability frame require PI approval. This
experiment supplies an auditable packet and does not exercise that authority.
