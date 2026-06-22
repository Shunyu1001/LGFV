# Pilot Case Selection

## Purpose

The pilot has two goals. First, it checks whether the four exit-type categories
can be applied consistently to real documents. Second, it identifies which
source materials are most useful for distinguishing substantive exit, nominal
exit, functional transfer, liquidation, and unclear cases.

The pilot should not be treated as the final sample. It is a design stage that
allows the coding rules, source hierarchy, and empirical strategy to be revised
before the project scales up. The candidate city list is not data. It is a
sampling plan that records where source collection should begin.

## Target Size

The first pilot should include 20 to 30 city-platform cases. A case is a major
LGFV or platform-like state-owned enterprise within a prefecture-level city. If
platform-level information is unavailable, the city can be retained in the case
plan but should not receive a final label until a specific company or group
company is identified.

## Selection Logic

The pilot should maximize variation rather than produce a representative
sample. It should include cities that vary along four dimensions.

First, the pilot should include variation in contemporary fiscal and
administrative capacity. Large coastal cities such as Hangzhou, Nanjing,
Suzhou, Guangzhou, and Shenzhen are useful high-capacity comparisons, while
inland cities in Guizhou, Yunnan, and parts of central China are useful for
observing cases where formal fiscal substitution may be more difficult.

Second, the pilot should include within-province variation. Comparing cities
inside the same province helps hold constant provincial implementation style,
regulatory pressure, and document availability. For this reason, the first
candidate list includes several cities from Zhejiang, Jiangsu, Shandong, Hunan,
Guizhou, Yunnan, Sichuan, and Guangdong.

Third, the pilot should include likely variation in exit types. The case list
should not only search for successful market-oriented transformations. It should
also deliberately look for reorganizations, mergers, changes in bond issuers,
new state capital operation companies, deregistration records, and cases where
the company's public project role appears to continue after official exit.

Fourth, the pilot should include variation in document quality. Some cities
will have clear announcements and bond disclosures, while others will have only
short official notices or business registration changes. This variation is
useful because the paper needs explicit rules for ambiguous and low-information
cases.

## Candidate Provinces

The first pilot uses eight provinces. They are not final sample strata; they
are a practical starting point for source collection.

- Zhejiang and Jiangsu: high-capacity coastal provinces with strong city-level
  fiscal variation.
- Guangdong: high-capacity coastal province with distinctive local state and
  state-owned asset structures.
- Shandong: large northern province with a mix of coastal and inland cities.
- Hunan: central province useful for comparing provincial capital and
  non-capital industrial cities.
- Guizhou and Yunnan: inland provinces where local debt pressure may make
  nominal exit or functional transfer easier to observe.
- Sichuan: large western province with a strong provincial capital and
  substantial prefecture-level variation.

The initial candidate list is stored in `data/candidate_city_plan.csv`. Every
row in that file has `evidence_status = candidate_only` until a specific
platform company and source documents have been identified. Candidate-only rows
must not be used in analysis.

## Case Selection Procedure

For each city in the pilot plan, proceed in four steps.

First, identify one major local platform company. Useful search terms include
the city name plus `城投`, `城市建设投资`, `交通投资`, `产业投资`, `国有资本运营`,
`融资平台退出`, `市场化转型`, and `政府融资职能`.

Second, collect at least two source types before assigning a final label. The
preferred combination is one official or company document and one financial
market document, such as a bond prospectus or credit rating report.

Third, record every source in `data/source_inventory_template.csv`. The source
inventory should include the source type, title, date, URL or local path, and a
short note on why the document is useful.

Fourth, apply the LLM labeling prompt only after the source excerpts have been
assembled. The LLM should classify the case using the codebook and should
return textual evidence. The final label should be entered in
`data/labeling_template.csv` only after human review.

## Source Hierarchy

Documents should be interpreted in the following order.

First, use official and company documents when available: local government
announcements, finance bureau notices, state-owned asset supervision documents,
company announcements, and formal transformation notices.

Second, use bond and rating documents: bond prospectuses, credit rating reports,
follow-up rating reports, and annual reports. These documents are often more
informative about continuing government support, public project obligations,
and debt repayment arrangements than short official notices.

Third, use business registration records to identify liquidation,
deregistration, mergers, business scope changes, and legal successor entities.

Fourth, use credible financial news as supplementary evidence. News reports can
help identify events and entities, but they should not be the only basis for a
final label unless no primary or near-primary document is available.

## Minimum Evidence Rule

A high-confidence label requires at least two pieces of evidence that speak to
the post-exit function of the company. A medium-confidence label can be assigned
when one strong source directly addresses the post-exit function. A low-
confidence label should be assigned only when the evidence points in one
direction but remains incomplete. Use `unclear` when available documents do not
show whether the government financing function continued, disappeared, or moved.

## Pilot Outputs

The pilot should produce four outputs.

First, it should produce a filled case plan indicating which city-platform cases
were found, which were dropped, and why. Second, it should produce a source
inventory with stable links or local file references. Third, it should produce
preliminary LLM labels and final human-validated labels. Fourth, it should
produce a memo summarizing the main ambiguities discovered during coding.

## Current Candidate Balance

The first validated cases now cover three exit-type patterns. Xi'an Hi-tech is a
nominal-exit case, Guangzhou City Construction Investment Group is a
substantive-exit case, and Hangzhou City Investment Group is a
functional-transfer case. Chengdu City Construction Investment Management Group
adds a second nominal-exit case with a different source pattern: compliance
language coexists with continuing infrastructure investment, BT, fiscal-payment,
and debt-replacement evidence.

The next useful addition is not simply another high-capacity coastal case. The
pilot needs weak-capacity cases where debt pressure and fiscal dependence make
substantive exit harder to observe. Zunyi Daoqiao is the first such candidate.
Its 2015 ChinaBond documents establish baseline platform function, its 2022
tracking rating report shows continuing entrusted-construction and
land-consolidation functions, and its July 2022 and January 2023 rating
attention notices place the company in a government-financing-platform
debt-resolution and bank-loan restructuring process. Because no direct formal-exit or
no-government-financing source has yet been found, the case should remain a
candidate evidence packet rather than a final label.
