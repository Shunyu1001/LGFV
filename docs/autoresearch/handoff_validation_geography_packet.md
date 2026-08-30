# Handoff: validation geography and independent-coding packet

## Objective

Make the proposed probability validation frame reviewable without changing a
gold label or drawing a sample. Resolve issuer geography and city-platform
scope with traceable authoritative evidence, and prepare a blinded instrument
for genuine independent human coding.

## Governing records

Read `AGENTS.md`, `program.md`, every file under `immutable/`,
`ledgers/research_state.yaml`, `ledgers/reviewer_issues.tsv`,
`docs/measurement_validation/current_estimand_map.md`, and Experiments
`EXP-20260830-006` through `EXP-20260830-008`. Read
`/Users/shunyuhao/Desktop/GAN GSC/SKILL.md` before proposing prose.

## Fixed boundaries

- Do not edit `data/processed/working_reference_labels.csv`.
- Do not assign or revise an exit-type label.
- Do not draw the probability sample or choose a random seed.
- Do not edit central ledgers, `paper/main.tex`, or existing manuscript
  sections.
- Do not infer province or city from an issuer name without authoritative
  source evidence.
- Preserve provincial, central, specialized, and ambiguous issuers as explicit
  scope cases.

## First bounded experiment

Create a pre-result experiment brief. For the 128 unresolved issuer units in
`data/validation/proposed_one_sided_validation_frame_enriched.csv`, collect an
authoritative company, government, exchange, registration, or original packet
record that supports province, city, legal issuer identity, controlling owner,
and city-platform eligibility. Record the source URL, title, date, retrieval
date, exact supporting text or page, and any conflicting evidence.

The primary metric is the share of unresolved units receiving a unique,
source-supported province-city pair and an explicit scope decision. A null or
low-coverage result is retained. Do not optimize source selection to reach a
threshold.

## Independent-coding instrument

Prepare, but do not fill, a packet for a second human coder. The instrument must
hide every current label, model prediction, confidence score, rationale, and
screen status. It may expose case IDs, issuer identity, city after verification,
document identifiers, source locations, and blank fields required by the frozen
codebook. Provide a separate adjudication log template.

## Deliverables

- Source-supported geography and scope crosswalk.
- Rights-aware retrieval manifest and conflict log.
- Blinded second-coder packet for the 94 frozen gold cases.
- Blinded probability-validation packet for eligible candidate issuers.
- Deterministic validators and tests.
- Experiment assessment with keep, discard, quarantine, crash, or invalid.
- Proposed ledger and manuscript rows stored only in experiment artifacts.

Commit coherent work on `codex/validation-geography-packet` and push the branch
for coordinator review.
