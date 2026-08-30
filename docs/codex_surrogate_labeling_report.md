# Codex Surrogate Labeling Report

Date: 2026-07-03

This note records the Codex-based surrogate labeling passes for the LGFV exit
project. The output is a screening file, not a working-reference label file.

## Inputs

- Working-reference labels: `data/processed/working_reference_labels.csv`
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
- `data/analysis_inputs/issuer_level_surrogate_empirical_input.csv`
- `data/analysis_inputs/surrogate_empirical_flow.csv`

The expanded surrogate-label file contains 361 rows:

- 94 working-reference labels
- 262 pending candidate disclosures screened by Codex
- 203 Codex surrogate disclosure-level labels
- 59 unresolved candidate disclosures
- 5 source-packet-reviewed boundary packets

The July 3 expanded screening sample converts this into a fuller LLM-coded
screening file. It contains 346 usable screening rows:

- 94 working-reference exit-type labels
- 203 LLM surrogate exit-type labels
- 44 source packets screened as having no direct formal exit or compliance event
- 5 source-packet-reviewed boundary packets
- 15 source-missing rows that remain unusable for screening

The exit-type outcome sample is narrower than the screening sample. It contains
297 rows: the 94 working reference labels plus 203 LLM surrogate exit-type labels. The 44
screened no-formal-event rows are useful for source coverage and measurement
attrition, but they are not treated as nominal, substantive, functional-transfer,
or liquidation outcomes.

After the latest screening pass, the screening file contains 203 surrogate
`nominal_exit` labels. These cases contain direct no-government-financing,
no-new-government-debt, no-hidden-debt, or equivalent formal compliance language
together with continuing urban infrastructure, entrusted construction,
land-development, fiscal-support, or public-project functions. They remain
disclosure-level surrogate evidence and should not be counted as new
working-reference observations until they receive full source-packet review.
Any promoted working label still awaits independent human confirmation.

The 203 surrogate labels correspond to 158 unique issuers because several
Shanghai Clearing rows are repeated bond disclosures for the same platform. Of
these issuers, 61 already match the working-reference file under
another case ID. The remaining 97 non-overlap issuers form the current
validation queue. The analysis file therefore preserves disclosure-level
labels, while the statistical step must aggregate or deduplicate them at the
issuer or city-platform level.

The issuer-level empirical input makes this separation explicit. It contains
252 rows: 94 working-reference outcomes, 61 surrogate overlap checks, and 97
non-overlap surrogate auxiliary rows. A combined 191-row file is retained for
workflow diagnostics, but it is not a human-validated or DSL-adjusted outcome
sample. The overlap rows are retained only for descriptive concordance between
the two Codex procedures.

## Conservative Rule

Codex only produces an exit-type surrogate when the source packet contains direct formal exit, no-government-financing, no-new-government-debt, no-hidden-debt, or market-oriented transformation language. Ordinary historical equity transfers, generic debt-restructuring discussion, subsidiary changes, and Shanghai Clearing disclosure titles do not create a surrogate outcome. Shanghai Clearing rows are classified only after their attached PDF source packets have been downloaded and converted to text, and a surrogate exit-type label still requires continuing-function evidence.

This conservative rule is intentional. The purpose of the first pass is to
separate usable surrogate labels from source-screened non-outcomes and cases
that still need source-packet collection. A model-generated exit-type label is
useful only when the underlying source packet supports the coding decision.

## DSL Interpretation

The current design follows the design-based supervised learning logic in Egami,
Hinck, Stewart, and Wei. The working-reference outcomes are provisional Codex
source-packet decisions awaiting human confirmation. The separate Codex
exit-type labels are imperfect surrogate labels. Source-screened rows without a
direct formal event are usable screening observations, but they are not
exit-type outcomes. Source-missing rows remain missing-label candidates, not
negative outcomes.

The current issuer-level overlap shows 61-of-61 selected concordance between
two Codex procedures. It does not identify positive predictive value because
the overlap was not probability sampled and the reference side is not yet
human confirmed. Jeffreys or Wilson adjustments cannot repair that selection
problem.

## Current Collection Status

The broad Shanghai Clearing source-packet workflow is now functional. The latest
expansion incorporated 361 candidate disclosure rows, downloaded key PDFs for
new source packets, and reran text extraction for pending candidates. Local raw
PDFs and extracted texts are ignored by git. Of the 361 disclosure rows, 346
are usable screening rows and 15 remain source-missing.

The next collection task is no longer broad PDF recovery. It is validation
triage for the 97 non-overlap issuer queue, followed by closer review of the 44
source-screened candidates that have usable source text but no direct formal
exit or compliance event under the frozen codebook.
