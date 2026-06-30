# Labeling Workflow

This workflow describes how to expand the validated sample from the current
pilot to a 50-case human-validated dataset. The authoritative coding rules are
in `coding/codebook.md`. The source-search procedure is in
`coding/source_search_protocol.md`. The LLM prompt for preliminary coding is in
`coding/llm_labeling_prompt.md`.

## Step 1: Build the candidate queue

Start from `data/analysis_inputs/validation_expansion_targets.csv`. This file
is a search queue, not a validated dataset. It gives each candidate a target
city, a likely platform or a platform-search instruction, a sampling stratum,
and the next search terms.

The queue should keep variation across three dimensions: historical capacity,
debt pressure, and region. It should also oversample low-capacity and high-debt
cities because these cases are theoretically important and empirically harder
to validate.

## Step 2: Identify the legal entity

For each city, identify a specific platform company before collecting
classification evidence. A city-level reform document is not enough. The case
must be tied to one legal entity or to a clearly described reorganization among
legal entities.

Useful first searches are:

```text
城市名 城投
城市名 城市建设投资
城市名 交通投资
城市名 国资委 平台公司
城市名 基础设施 投融资 平台
```

If the target platform in the queue is marked `needs_confirmation`, confirm the
legal name through a prospectus, company website, SASAC document, or business
registration source before continuing.

## Step 3: Build the source packet

For each case, collect evidence in the order specified in
`coding/source_search_protocol.md`.

The minimum packet contains a formal-event source, a post-event function source,
and an evidence table with document IDs and line references when available.
Cases with only one strong prospectus may enter the validated sample at medium
confidence if the same document contains direct formal-event language and
detailed post-event function evidence.

Record source metadata in the source inventory. Keep downloaded PDFs, extracted
text, and notes under stable document IDs so that every label can be traced back
to source text.

## Step 4: Run LLM-assisted preliminary coding

Use `coding/llm_labeling_prompt.md` only after the source packet is assembled.
The model should not search the web, fill missing facts, or decide final
validation status.

Recommended setup:

```text
Model 1: Claude
Model 2: ChatGPT
```

Record the output fields needed for review: formal event, continued-function
evidence, exit type, confidence, source coverage score, continued-function
evidence score, alternative label, and missing information.

## Step 5: Human validation

Human validation is a document review, not an agreement check. The reviewer
should inspect the original or near-original sources and decide whether the
case satisfies the minimum packet. If it does, enter the final label in
`data/processed/human_validated_labels.csv`. If it does not, keep the case in
`data/analysis_inputs/master_case_pool.csv` as `not_validated`,
`source_started`, or `llm_candidate_ready`.

After editing the label file, run:

```bash
python3 scripts/validate_labels.py
```

The validator checks category names, confidence levels, case uniqueness,
evidence document IDs, supplementary source IDs, and evidence-line syntax.

## Step 6: Reliability checks

For the paper, report several checks once the sample reaches at least 50
human-validated cases:

1. model agreement before human review;
2. accuracy of LLM preliminary labels in a human-reviewed random sample;
3. inter-coder agreement when a second human coder is available;
4. sensitivity to excluding low-confidence cases;
5. sensitivity to source coverage score; and
6. stratified validation results for low-capacity and high-debt cities.

## Step 7: Analysis dataset

After enough final labels are validated, derive the analysis dataset from
`data/processed/human_validated_labels.csv` and merge it with historical
capacity, debt pressure, land finance dependence, province fixed effects, and
other covariates from `data/analysis_inputs/master_case_pool.csv`.
