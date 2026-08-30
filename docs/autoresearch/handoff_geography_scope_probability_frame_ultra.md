# Ultra Handoff: Geography, Scope, and Probability Validation Frame

## Objective

Turn the quarantined 133-issuer candidate frame into a source-supported,
deduplicated probability validation frame. Resolve the 88 currently unresolved
province-city assignments and the 98 scope decisions marked for review. Do not
draw the validation sample until all frame gates and reproducibility checks pass.

## Label Roles

Read `coding/label_provenance.md` and
`data/validation/label_role_registry.csv` first.

- `data/processed/working_reference_labels.csv` contains 94 Codex
  source-packet-reviewed working labels. They are provisional gold outcomes for
  workflow development and await independent human confirmation.
- The Codex/ChatGPT screening files contain LLM surrogate labels. They are
  one-sided screening predictions, not final outcomes.
- Do not describe either layer as independently human validated.
- Do not assign, revise, or reveal a working-reference exit-type label in this
  task.

## Required Inputs

- `data/validation/proposed_one_sided_validation_frame_enriched.csv`
- `data/validation/source_supported_validation_geography_scope_crosswalk.csv`
- `data/validation/validation_geography_conflict_log.csv`
- `data/validation/validation_geography_retrieval_manifest.csv`
- `data/analysis_inputs/codex_surrogate_labels_2026_07_03_expanded.csv`
- `data/document_inventory.csv`
- `data/source_inventory.csv`
- `coding/source_search_protocol.md`
- `coding/codebook.md`

## Geography Gate

For every unresolved issuer, identify a unique province-city pair from an
authoritative source. Preferred evidence is an exchange-hosted original
disclosure, government or SASAC page, issuer registration disclosure, bond
prospectus, legal opinion, or rating report. Record the exact document ID, URL,
page or line basis, retrieval date, and any name conflict. Do not infer geography
from an issuer name alone when multiple cities or administrative levels are
plausible.

Allowed dispositions are `source_supported_unique`, `source_supported_multiple`,
and `unresolved_after_search`. Never coerce a conflict into a unique match.

## Scope Gate

For every issuer under review, determine whether it belongs in the target frame:
a city, district, county, development-zone, or municipal-level state-owned entity
with evidence of an LGFV or platform-like public financing or project role.

Record controlling-owner level and platform role separately. Exclude central
SOEs, purely provincial entities without a city-platform role, commercial SOEs
without a platform-like function, duplicate legal entities, and rows without an
identifiable issuer. Preserve difficult boundary cases with a reason rather than
forcing eligibility.

Allowed scope dispositions are `eligible`, `ineligible`, and
`unresolved_after_search`. Each decision needs a source-supported reason code and
an audit note.

## Probability Frame

After geography and scope decisions are complete:

1. Deduplicate at the legal-issuer level while retaining every originating
   disclosure row.
2. Include both surrogate-positive and screen-nonpositive strata.
3. Freeze pre-outcome strata using screen status, source coverage, historical
   capacity bin, debt-pressure availability, and administrative level only.
4. Produce stable unit IDs, stratum sizes, explicit eligibility flags, and
   source-backed geography.
5. Propose inclusion probabilities and a deterministic random seed, but do not
   execute the draw.
6. Demonstrate that every eligible unit has a nonzero planned inclusion
   probability.

## Required Outputs

- A completed source-supported geography and scope crosswalk.
- A conflict and unresolved-case log with one row per failed gate.
- A deduplicated frozen probability-frame candidate file.
- A frame-flow table from 133 proposed issuers to eligible, ineligible, and
  unresolved units.
- A sampling-design proposal with strata, target counts, and planned inclusion
  probabilities.
- Reproducible scripts and tests for identity uniqueness, source traceability,
  stratum coverage, and nonzero inclusion probability.
- A new preregistered experiment directory and ledger proposal. Use the next
  unclaimed experiment identifier after checking the main branch.
- A concise assessment stating exactly how many of the 88 geography and 98 scope
  gaps were resolved and whether the frame is ready to freeze.

## Stop Conditions

Stop and report rather than inventing evidence when an issuer cannot be resolved
from authoritative sources. Do not execute a random draw, calculate validation
accuracy, change exit-type labels, or edit manuscript results. Commit all work on
the isolated worktree branch with a clear message and report the commit hash to
the coordinator.
