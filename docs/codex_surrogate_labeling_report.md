# Codex Surrogate Labeling Report

Date: 2026-07-03

This note records the Codex-based surrogate labeling passes for the LGFV exit
project. The output is a screening file, not a human-validated label file.

## Inputs

- Gold-standard labels: `data/processed/human_validated_labels.csv`
- Candidate seed pool: `data/analysis_inputs/llm_candidate_pool_seed_2026_06_30.csv`
- Source metadata: `data/document_inventory.csv` and `data/source_inventory.csv`
- Frozen coding rules: `coding/codebook.md`
- Prompt template: `coding/llm_labeling_prompt.md`

## Output

- `data/analysis_inputs/codex_surrogate_labels_2026_07_02.csv`
- `data/analysis_inputs/codex_surrogate_issuer_summary_2026_07_02.csv`
- `data/analysis_inputs/surrogate_validation_queue_2026_07_02.csv`
- `data/analysis_inputs/llm_screening_sample_2026_07_03.csv`
- `data/analysis_inputs/llm_screening_summary_2026_07_03.csv`

The surrogate-label file contains 257 rows:

- 87 human gold-standard labels
- 164 pending candidate disclosures screened by Codex
- 84 Codex surrogate disclosure-level labels
- 80 unresolved candidate disclosures

The July 3 screening sample converts this into a fuller LLM-coded screening
file. It contains 242 usable screening rows:

- 87 gold-standard exit-type labels
- 84 LLM surrogate exit-type labels
- 65 source packets screened as having no direct formal exit or compliance event
- 6 human-reviewed boundary packets
- 15 source-missing rows that remain unusable for screening

The exit-type outcome sample is narrower than the screening sample. It contains
171 rows: the 87 gold labels plus 84 LLM surrogate exit-type labels. The 65
screened no-formal-event rows are useful for source coverage and measurement
attrition, but they are not treated as nominal, substantive, functional-transfer,
or liquidation outcomes.

After the missing-PDF recovery pass, the screening file contains 84 surrogate `nominal_exit` labels. These cases contain direct no-government-financing language together with continuing urban infrastructure, entrusted construction, land-development, fiscal-support, or public-project functions. They remain disclosure-level surrogate evidence and should not be counted as new gold-standard observations until validated against original line references.

The 84 surrogate labels correspond to 64 unique issuers because several Shanghai Clearing rows are repeated bond disclosures for the same platform. Of these issuers, 37 already match the gold-standard human-validated file under another case ID. The remaining 27 non-overlap issuers form the current validation queue. The analysis file therefore preserves disclosure-level labels, while the statistical step must aggregate or deduplicate them at the issuer or city-platform level.

## Conservative Rule

Codex only produces an exit-type surrogate when the source packet contains direct formal exit, no-government-financing, or market-oriented transformation language. Ordinary historical equity transfers, generic debt-restructuring discussion, subsidiary changes, and Shanghai Clearing disclosure titles do not create a surrogate outcome. Shanghai Clearing rows are classified only after their attached PDF source packets have been downloaded and converted to text.

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

The next inference stage should use the human-validated sample to estimate
surrogate-label error and then apply a validation-adjusted or doubly robust
estimator to downstream relationships such as historical capacity and
institutional change.

## Current Collection Status

The broad Shanghai Clearing source-packet workflow is now functional. The latest recovery pass downloaded 338 additional key PDFs and reran text extraction for pending candidates. Local raw PDFs and extracted texts are ignored by git, but the current working collection contains 1,508 downloaded PDFs and 1,396 extracted text files. Among the 164 pending candidate disclosures, 146 now have usable extracted text, 1 has downloaded PDF records without usable extracted text, and 17 have no collected document packet.

The next collection task is no longer broad PDF recovery. It is validation
triage for the 27 non-overlap issuer queue, followed by closer review of the 65
source-screened candidates that have usable source text but no direct formal
exit or compliance event under the frozen codebook.
