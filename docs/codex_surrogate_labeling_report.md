# Codex Surrogate Labeling Report

Date: 2026-07-02

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

The output contains 257 rows:

- 62 human gold-standard labels
- 193 pending candidate disclosures screened by Codex
- 62 Codex surrogate disclosure-level labels
- 131 unresolved candidate disclosures

The first pass produced two medium-confidence `nominal_exit` labels for
Guangzhou Metro and Nanjing Metro. Later source-packet review showed that both
metro packets are better treated as boundary evidence than as gold-standard
city-platform exit cases. The Shanghai Clearing source-packet passes added
source packets for the full priority range in the harvest file. After promoting
validated packets into the gold-standard file and marking boundary packets as
out of frame, the screening file contains 62 surrogate `nominal_exit` labels.
These cases contain direct no-government-financing language together with
continuing urban infrastructure, entrusted construction, land-development,
fiscal-support, or public-project functions. They remain surrogate labels and
require human validation before entering the gold-standard label file.

The 62 surrogate labels correspond to 46 unique issuers because several
Shanghai Clearing rows are repeated bond disclosures for the same platform. Of
these 46 issuers, 29 exactly match issuers that already appear in the
gold-standard human-validated label file under different case IDs. This overlap
is useful as a consistency check, but it should not be counted as new sample
expansion. The remaining 17 issuers form the current validation queue. The
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

The broad Shanghai Clearing source-packet workflow is now functional. The
latest inventory expansion added 119 disclosure pages and 996 attached
documents to the tracked source and document inventories. Local raw PDFs and
extracted texts are ignored by git, but the current working collection contains
1,070 downloaded PDFs and 958 extracted text files. Among the 193 pending
candidate disclosures, 87 now have usable extracted text, 88 have document
records but still need PDF downloads, 17 have no collected document packet, and
1 has a downloaded PDF without usable text. The next collection task is to
review the 17 queued non-overlap issuers and to continue a resumable download
and extraction pass for the 88 document-record cases that still lack PDFs.
