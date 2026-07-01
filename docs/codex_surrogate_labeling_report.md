# Codex Surrogate Labeling Report

Date: 2026-07-01

This note records the first Codex-based surrogate labeling pass for the LGFV
exit project. The output is a screening file, not a human-validated label file.

## Inputs

- Gold-standard labels: `data/processed/human_validated_labels.csv`
- Candidate seed pool: `data/analysis_inputs/llm_candidate_pool_seed_2026_06_30.csv`
- Source metadata: `data/document_inventory.csv` and `data/source_inventory.csv`
- Frozen coding rules: `coding/codebook.md`
- Prompt template: `coding/llm_labeling_prompt.md`

## Output

- `data/analysis_inputs/codex_surrogate_labels_2026_07_01.csv`

The output contains 247 rows:

- 50 human gold-standard labels
- 197 pending candidate cases screened by Codex
- 2 Codex surrogate labels
- 195 unresolved candidate cases

The two Codex surrogate labels are medium-confidence `nominal_exit` labels for
Guangzhou Metro and Nanjing Metro. In both cases, the source packets contain
direct no-government-financing language together with continuing urban
infrastructure functions. These remain surrogate labels and require human
validation before entering the gold-standard label file.

## Conservative Rule

Codex only produces an exit-type surrogate when the source packet contains
direct formal exit, no-government-financing, or market-oriented transformation
language. Ordinary historical equity transfers, generic debt-restructuring
discussion, subsidiary changes, and Shanghai Clearing disclosure titles do not
create a surrogate outcome.

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

The main bottleneck is source-packet construction for the 175 Shanghai
Clearing harvest rows. Each row currently has a disclosure-page title and URL,
but most do not yet have downloaded and extracted prospectuses, rating reports,
legal opinions, or financial statements. The next collection task is to
download and extract source packets for high-priority harvest rows before
running a second Codex labeling pass.
