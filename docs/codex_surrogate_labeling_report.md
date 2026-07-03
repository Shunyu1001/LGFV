# Codex Surrogate Labeling Report

Date: 2026-07-03

This note records the Codex-based surrogate labeling passes for the LGFV exit
project. The output is a screening file, not a human-validated label file.

## Inputs

- Gold-standard labels: `data/processed/human_validated_labels.csv`
- Candidate seed pool: `data/analysis_inputs/llm_candidate_pool_seed_2026_07_03_expanded.csv`
- Source metadata: `data/document_inventory.csv` and `data/source_inventory.csv`
- Frozen coding rules: `coding/codebook.md`
- Prompt template: `coding/llm_labeling_prompt.md`

## Output

- `data/analysis_inputs/codex_surrogate_labels_2026_07_03_expanded.csv`
- `data/analysis_inputs/codex_surrogate_issuer_summary_2026_07_03_expanded.csv`
- `data/analysis_inputs/surrogate_validation_queue_2026_07_03_expanded.csv`
- `data/analysis_inputs/llm_screening_sample_2026_07_03_expanded.csv`
- `data/analysis_inputs/llm_screening_summary_2026_07_03_expanded.csv`

The expanded surrogate-label file contains 312 rows:

- 94 human gold-standard labels
- 213 pending candidate disclosures screened by Codex
- 163 Codex surrogate disclosure-level labels
- 50 unresolved candidate disclosures
- 5 human-reviewed boundary packets

The July 3 expanded screening sample converts this into a fuller LLM-coded
screening file. It contains 297 usable screening rows:

- 94 gold-standard exit-type labels
- 163 LLM surrogate exit-type labels
- 35 source packets screened as having no direct formal exit or compliance event
- 5 human-reviewed boundary packets
- 15 source-missing rows that remain unusable for screening

The exit-type outcome sample is narrower than the screening sample. It contains
257 rows: the 94 gold labels plus 163 LLM surrogate exit-type labels. The 35
screened no-formal-event rows are useful for source coverage and measurement
attrition, but they are not treated as nominal, substantive, functional-transfer,
or liquidation outcomes.

After the July 3 validation pass, the screening file contains 163 surrogate
`nominal_exit` labels. These cases contain direct no-government-financing,
no-new-government-debt, no-hidden-debt, or equivalent formal compliance language
together with continuing urban infrastructure, entrusted construction,
land-development, fiscal-support, or public-project functions. They remain
disclosure-level surrogate evidence and should not be counted as new
gold-standard observations until validated against original line references.

The 163 surrogate labels correspond to 120 unique issuers because several
Shanghai Clearing rows are repeated bond disclosures for the same platform. Of
these issuers, 61 already match the gold-standard human-validated file under
another case ID. The remaining 59 non-overlap issuers form the current
validation queue. The analysis file therefore preserves disclosure-level
labels, while the statistical step must aggregate or deduplicate them at the
issuer or city-platform level.

## Conservative Rule

Codex only produces an exit-type surrogate when the source packet contains direct formal exit, no-government-financing, no-new-government-debt, no-hidden-debt, or market-oriented transformation language. Ordinary historical equity transfers, generic debt-restructuring discussion, subsidiary changes, and Shanghai Clearing disclosure titles do not create a surrogate outcome. Shanghai Clearing rows are classified only after their attached PDF source packets have been downloaded and converted to text, and a surrogate exit-type label still requires continuing-function evidence.

This conservative rule is intentional. The purpose of the first pass is to
separate usable surrogate labels from source-screened non-outcomes and cases
that still need source-packet collection. A model-generated exit-type label is
useful only when the underlying source packet supports the coding decision.

## DSL Interpretation

The current design follows the design-based supervised learning logic in Egami,
Hinck, Stewart, and Wei. Human labels are gold-standard outcomes. Codex
exit-type labels are imperfect surrogate labels. Source-screened rows without a
direct formal event are usable screening observations, but they are not
exit-type outcomes. Source-missing rows remain missing-label candidates, not
negative outcomes.

The current issuer-level overlap implies a raw positive predictive value of
1.000 for the conservative surrogate nominal-exit rule. The paper reports this
with Jeffreys-smoothed and Wilson lower-bound adjustments rather than treating
the finite overlap sample as literal certainty.

## Current Collection Status

The broad Shanghai Clearing source-packet workflow is now functional. The July
3 expansion added three additional harvest files, incorporated new source packets,
downloaded key PDFs, and reran text extraction for pending candidates. Local raw
PDFs and extracted texts are ignored by git. Among the 218 pending or boundary
candidate disclosures in the expanded file, 203 are usable screening rows and
15 remain source-missing.

The next collection task is no longer broad PDF recovery. It is validation
triage for the 59 non-overlap issuer queue, followed by closer review of the 35
source-screened candidates that have usable source text but no direct formal
exit or compliance event under the frozen codebook.
