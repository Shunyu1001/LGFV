# Labeling Workflow

## Step 1: Build the Pilot Case Plan

Start from `data/pilot_case_plan.csv`. The first case plan is intentionally
designed for variation rather than representativeness. It includes high-capacity
coastal cities, inland debt-pressure cases, provincial capitals, and non-capital
prefecture-level cities.

For each city, identify one major platform company or platform-like local SOE.
Useful search terms include:

- `城市名 + 城投`
- `城市名 + 城市建设投资`
- `城市名 + 融资平台退出`
- `城市名 + 市场化转型`
- `公司名 + 政府融资职能`
- `公司名 + 募集说明书`
- `公司名 + 跟踪评级报告`

## Step 2: Build the Source Inventory

Record each document in `data/source_inventory_template.csv`. The preferred
source types are:

- Government announcements
- Company announcements
- Bond prospectuses
- Credit rating reports
- Business registration records

For each case, try to collect at least one official or company document and one
financial-market document before labeling.

## Step 3: Run LLM-Assisted Preliminary Coding

Use the same prompt in `coding/llm_labeling_prompt.md` for each model. Recommended
setup:

- Model 1: Claude
- Model 2: ChatGPT

Record both outputs in `data/labeling_template.csv`. Keep the raw model outputs
as separate text files when possible.

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

For the paper, report at least one reliability check:

- Share of model agreement
- Accuracy of LLM preliminary labels in a human-reviewed sample
- Intercoder agreement if a second human coder is available
- Sensitivity analysis excluding `unclear` and low-confidence cases

## Step 7: Analysis Dataset

After final labels are validated, export a cleaned dataset to
`data/processed/lgfv_exit_types.csv`.
