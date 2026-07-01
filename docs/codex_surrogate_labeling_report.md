# Codex Surrogate Labeling Report

Date: 2026-07-01

This note records the Codex-based surrogate labeling passes for the LGFV exit
project. The output is a screening file, not a human-validated label file.

## Inputs

- Gold-standard labels: `data/processed/human_validated_labels.csv`
- Candidate seed pool: `data/analysis_inputs/llm_candidate_pool_seed_2026_06_30.csv`
- Source metadata: `data/document_inventory.csv` and `data/source_inventory.csv`
- Frozen coding rules: `coding/codebook.md`
- Prompt template: `coding/llm_labeling_prompt.md`

## Output

- `data/analysis_inputs/codex_surrogate_labels_2026_07_01.csv`
- `data/analysis_inputs/codex_surrogate_issuer_summary_2026_07_01.csv`
- `data/analysis_inputs/surrogate_validation_queue_2026_07_01.csv`

The output contains 247 rows:

- 51 human gold-standard labels
- 196 pending candidate cases screened by Codex
- 48 Codex surrogate labels
- 148 unresolved candidate cases

The first pass produced two medium-confidence `nominal_exit` labels for
Guangzhou Metro and Nanjing Metro. The Shanghai Clearing source-packet passes
added source packets for 56 high- and medium-priority harvest rows. After
promoting Kunming Transportation Investment Group from the review queue into
the gold-standard file, the screening file contains 46 additional
medium-confidence `nominal_exit` surrogate labels from these packets. These cases contain direct
no-government-financing language together with continuing urban infrastructure,
entrusted construction, land-development, fiscal-support, or public-project
functions. They remain surrogate labels and require human validation before
entering the gold-standard label file.

The 48 surrogate labels correspond to 32 unique issuers because several
Shanghai Clearing rows are repeated bond disclosures for the same platform. Of
these 32 issuers, 21 exactly match issuers that already appear in the
gold-standard human-validated label file under different case IDs. This overlap
is useful as a consistency check, but it should not be counted as new sample
expansion. The remaining 11 issuers form the current validation queue. The
analysis file therefore preserves the disclosure-level labels, while the next
statistical step must aggregate or deduplicate them at the issuer or
city-platform level. The issuer-level summary file performs this preliminary
collapse and keeps evidence snippets for later human review.

## Conservative Rule

Codex only produces an exit-type surrogate when the source packet contains
direct formal exit, no-government-financing, or market-oriented transformation
language. Ordinary historical equity transfers, generic debt-restructuring
discussion, subsidiary changes, and Shanghai Clearing disclosure titles do not
create a surrogate outcome. Shanghai Clearing rows are classified only after
their attached PDF source packets have been downloaded and converted to text.

This conservative rule is intentional. The purpose of the first pass is to
separate usable surrogate labels from cases that still need source-packet
collection. A model-generated label is useful only when the underlying source
packet supports the coding decision.

## DSL Interpretation

The current design follows the design-based supervised learning logic in
Egami, Hinck, Stewart, and Wei. Human labels are gold-standard outcomes. Codex
labels are imperfect surrogate labels. Unresolved cases are missing-label
candidates, not negative outcomes.

The next inference stage should use the human-validated sample to estimate
surrogate-label error and then apply a validation-adjusted or doubly robust
estimator to downstream relationships such as historical capacity and
substantive exit.

## Next Step

The high- and medium-priority Shanghai Clearing source-packet workflow is now
functional. It added 56 disclosure pages and 456 attached documents to the
inventory, downloaded the PDF packets, and extracted usable text from all 56
case directories. Across these packets, 323 extracted text files contain at
least 200 characters, with about 28.7 million usable characters. The next
collection task is to review the 11 queued non-overlap issuers and decide
whether to promote them to gold-standard labels, reject them as boundary cases,
or retain them as surrogate-only observations for validation-adjusted
inference.
