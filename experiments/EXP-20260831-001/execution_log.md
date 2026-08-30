# Execution log

## Registration and correction boundary

- Audited the committed Experiment 015 result at base commit
  `7dfa332c6d4c965605abe3337cf0bfd536f068cf` and preserved its directory and
  append-only ledger row unchanged.
- Checked the current `main` branch and the worktree branch. No
  `EXP-20260831-*` identifier existed, so `EXP-20260831-001` was registered.
- Committed the correction brief and frozen audit-derived decision register in
  registration commit `27767834a8a63ad810ffedf5c0fb90b4794d5259` before
  the registered deterministic execution.
- Diagnostic builds run during the read-only Ultra audit are not treated as the
  registered result. The registered result is the post-brief execution recorded
  below.
- Did not read `data/processed/working_reference_labels.csv` or any exit-type
  outcome field.

## Source and case review

- The surviving temporary cache contains raw and extracted text for 250 of the
  253 inherited Experiment 011 records. Their raw SHA-256 values match the
  inherited manifest. Three uncited inherited records are absent and remain
  disclosed as unavailable.
- Added 19 source-manifest records from inventoried disclosures, government or
  SASAC pages, exchange publications, and public issuer or parent disclosures.
  The successor manifest contains 272 records.
- Reviewed all 88 inherited geography gaps and all 98 inherited scope cases.
  A second boundary pass reviewed all 31 commercial exclusions; overlapping
  checks covered 113 distinct units, all 54 original eligible units, and all
  four original unresolved units.
- Corrected three geography dispositions: two issuers retain documented
  multiple locations rather than coerced unique locations, and Aier Medical is
  assigned to Lhasa rather than an intermediary's Changsha address. Thirty-four
  other inherited geography locators were replaced with direct issuer pages.
  A final structured-address pass registers 50 explicit geography locators in
  total and independently locks 14 repaired rows to direct document, page,
  city, and anchor combinations; court-venue boilerplate and intermediary-only
  addresses are rejected.
- Changed 13 scope dispositions after issuer, consolidated-group, or
  controlling-parent evidence was checked. The inherited 98 finish at 53
  eligible and 45 ineligible. The full frame finishes at 66 eligible, 66
  ineligible, and one unresolved legal-identity case.
- Replaced defective controller locators or extracted names with 26 explicit
  focal-source overrides and registered 28 explicit issuer-role locators.
- The audit found 27 citations whose physical page exceeded Experiment 015's
  stale declared extraction bound even though the exact cited text was present
  in the hash-matched cache. The correction derives each cached page count from
  the form-feed-delimited extraction, removes the terminal marker from the
  count, and rejects any citation beyond the manifest bound. All 485 retained
  citations are now both in bounds and exact after canonical whitespace
  normalization.

## Construction correction

- Reconstructed every `source_row_id` and `pool_id` pair from safe surrogate
  identifier columns. This repairs five false pairs while retaining all 157
  disclosure rows in stable order.
- Reconstructed origin document identifiers from the document inventory and
  removed invalid prose fragments from evidence-ID fields.
- Replaced the partial control map with the declared city-control input. The
  fixed join includes Taizhou directly and applies the registered
  prefecture-level exposure rule from Taicang to Suzhou and Rugao to Nantong for
  historical capacity and debt-pressure availability.
- The candidate has 66 issuer units and 73 eligible originating rows in 23
  strata: 57 nominal screen-positive and nine screen-nonpositive units; 65
  moderate-coverage and one low-coverage unit; 32 historical-capacity matches;
  and 39 units with debt-pressure data.
- Every proposed inclusion probability is one. The design is a census proposal,
  not an executed random draw.

## Registered execution and validation

```text
python3 experiments/EXP-20260831-001/compile_source_review.py --source-dir /tmp/lgfv-exp015-sources
python3 scripts/build_probability_validation_frame.py
python3 scripts/validate_probability_validation_frame.py
python3 -m unittest tests.test_probability_validation_frame
```

Compilation wrote 133 crosswalk rows, four failed gates, and 272 source rows,
and verified 485 cited excerpts. The independent validator passed with the
registered counts, page bounds, source-cache hashes, and excerpt containment.
Twenty unit tests passed.

Repository checks:

```text
python3 scripts/validate_immutable.py
python3 scripts/validate_ledgers.py
python3 scripts/validate_labels.py
python3 scripts/validate_master_case_pool.py
git diff --check
```

The immutable, ledger, label, and whitespace checks passed. The
master-case-pool validator retains the pre-existing baseline failure that 94
validated rows lack `reference_label_producer`, together with existing warnings
for unavailable local extracted text. This correction does not change the
protected master case pool, label files, or document packets.

## Limitations and prohibited actions

- Three uncited inherited source caches are absent, and the inherited extractor
  version was not recorded. Every retained citation has a present hash-verified
  cache, so these are disclosed reproducibility limitations rather than active
  retained-decision blockers.
- No random sample was drawn, and no validation accuracy or classifier metric
  was calculated.
- No exit-type label was read, assigned, changed, or revealed.
- No raw source document, immutable file, manuscript result, claim, or approved
  sampling rule was changed.
- The audit was model-based and is not described as independent human
  validation.
