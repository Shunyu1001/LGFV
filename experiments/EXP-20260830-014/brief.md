# Experiment brief: Blinded independent-coding instruments

## Experiment identity

- Experiment ID: `EXP-20260830-014`
- Loop: `empirical_simulation`
- Base commit: `538d99ac0424e0814c88dab2b00b6ce7257ab6b8`
- Started at: `2026-08-30T16:41:42+08:00`
- Owner: validation-geography-packet worktree

## Falsifiable bottleneck

Reviewer issue R-003 cannot be closed without a genuine second human coder,
and the proposed probability-validation design has no circulation-ready
prediction-free instrument. This experiment tests whether the tracked source
inventories can produce blinded, source-located coding instruments without
copying any current outcome, model output, confidence, rationale, screen
status, reviewer identity, or sample-selection field.

## Hypothesis

The frozen files support a 94-row second-coder packet for all gold cases, a
separate packet for all 13 provisionally eligible candidate issuers from
Experiment 011, and a 94-row adjudication template. Every packet row will have
a unique identifier, issuer identity, verified geography, at least one source
document identifier and location, and blank coder-entry fields. The candidate
packet will remain review-gated and will not imply an approved frame.

## Inputs

- `data/processed/human_validated_labels.csv`
- `data/analysis_inputs/master_case_pool.csv`
- `data/document_inventory.csv`
- `data/validation/proposed_one_sided_validation_frame_enriched.csv`
- `data/validation/source_supported_validation_geography_scope_crosswalk.csv`
- `data/validation/validation_geography_retrieval_manifest.csv`
- `coding/codebook.md`

## Planned change

Use explicit allowlists to construct three files:

1. A blinded packet for independent recoding of all 94 frozen gold cases.
2. A blinded candidate packet limited to the 13 provisionally eligible,
   source-supported issuers from Experiment 011.
3. A separate adjudication log template keyed to the 94 gold cases.

The gold packet will obtain packet document identifiers from the tracked
master case pool and source locations from the document inventory. The
candidate packet will obtain packet identifiers from the proposed frame and
source locations from the rights-aware retrieval manifest. Neither builder nor
validator will expose any outcome or design-stratum column.

## Coder fields

The coder-facing packets include blank fields for coder identity and date,
case eligibility, formal event, baseline platform function, post-event
function, final and alternative labels, confidence, source coverage,
continued-function evidence, source references, ambiguity, remaining caveat,
and coder signature. The adjudication log includes blank fields for both coder
labels, disagreement domain, adjudicated label and rationale, source
references, and signatures. It is stored separately and is not part of the
second coder's blinded packet.

## Success criteria

1. The gold packet contains exactly 94 unique frozen case IDs.
2. The candidate packet contains exactly the 13 provisionally eligible issuer
   IDs from Experiment 011 and no other proposed-frame unit.
3. The adjudication template contains exactly 94 unique frozen case IDs.
4. Every coder-entry and adjudication-entry cell is blank.
5. Every coder-facing packet row has nonblank issuer identity, verified
   province and city, document identifiers, and at least one source location.
6. No current label, model prediction, confidence value, rationale, screen
   status, design stratum, inclusion probability, random seed, sample flag,
   reviewer identity, or validation date is copied into an output.
7. No probability sample is drawn and no coder or adjudicator entry is filled.
8. Deterministic regeneration, packet validators, repository integrity,
   ledger, label, and master-case-pool checks pass.

The experiment is `keep` only if every structural and blinding gate passes.
It is `quarantine` if a packet is structurally correct but source coverage or
scope approval remains incomplete, and `invalid` if any forbidden information
or pre-populated coding entry appears.

## Permitted files

- New scripts under `scripts/measurement_validation/`
- New packet outputs under `data/validation/independent_coding/`
- New files under `experiments/EXP-20260830-014/`

Do not modify gold labels, raw source inventories, central ledgers, manuscript
files, prior experiment outputs, or the proposed sampling design.

## Commands

```text
python3 scripts/measurement_validation/build_independent_coding_packets.py
python3 scripts/measurement_validation/build_independent_coding_packets.py --check
python3 scripts/measurement_validation/validate_independent_coding_packets.py
python3 scripts/measurement_validation/validate_independent_coding_packets.py --check-metrics
python3 -m unittest scripts.tests.test_independent_coding_packets
python3 scripts/validate_immutable.py
python3 scripts/validate_ledgers.py
python3 scripts/validate_labels.py
python3 scripts/validate_master_case_pool.py
git diff --check
```

## Budget

- One deterministic packet builder, one validator, three coder-facing or
  adjudication CSVs, one instruction file, one metrics file, one assessment,
  one execution log, and proposed ledger and manuscript rows stored only as
  experiment artifacts.
- At most two minimal mechanical retries.
- No label assignment, coding simulation, coder impersonation, probability
  sample, random seed, central ledger edit, or manuscript edit.

## Review gate

The PI must approve the second-human workflow, adjudication procedure,
candidate-frame scope decisions, and probability design before circulation.
Producing blank instruments does not close R-003 or R-010 and does not create
independent labels.
