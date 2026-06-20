# Labeling Workflow

## Step 1: Build the Case List

Create one row per platform company or city-platform case in
`data/labeling_template.csv`.

Minimum fields:

- Province
- City
- Company name
- Official exit year
- Source documents

## Step 2: Collect Source Documents

For each case, collect documents in `data/raw/` or store stable URLs:

- Government announcements
- Company announcements
- Bond prospectuses
- Credit rating reports
- Business registration records

## Step 3: Run LLM-Assisted Preliminary Coding

Use the same prompt in `coding/llm_labeling_prompt.md` for each model. Recommended
setup:

- Model 1: Claude
- Model 2: ChatGPT

Record both outputs in the template. Keep the raw model outputs if possible.

## Step 4: Compare Model Labels

If the two models agree and provide strong textual evidence, mark
`model_agreement = yes`. If they disagree, mark `model_agreement = no` and send
the case to manual review.

## Step 5: Human Validation

Review all cases with:

- Model disagreement
- Low confidence
- Missing or weak evidence
- Ambiguous distinction between nominal exit and functional transfer

The final label should be assigned by the researcher after reviewing the
original documents.

## Step 6: Reliability Checks

For a writing sample, report at least one reliability check:

- Share of model agreement
- Accuracy of LLM preliminary labels in a human-reviewed sample
- Intercoder agreement if a second human coder is available
- Sensitivity analysis excluding `unclear` and low-confidence cases

## Step 7: Analysis Dataset

After final labels are validated, export a cleaned dataset to
`data/processed/lgfv_exit_types.csv`.

