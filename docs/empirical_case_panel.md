# Empirical Case Panel

`scripts/build_empirical_case_panel.py` builds the current case-level analysis
file:

- `data/analysis_inputs/empirical_case_panel.csv`
- `data/analysis_inputs/empirical_case_panel_coverage.csv`
- `paper/tables/empirical_case_panel_coverage.tex`

The panel has 191 rows. It combines 94 human-validated gold-standard labels
with 97 non-overlap issuer-level Codex surrogate nominal-exit labels. The
surrogate rows are included only for validation-adjusted descriptive analysis.
They are not treated as final human labels.

The current validated model uses the 84 gold-standard rows that can be matched
to the CBDB-GADM historical-capacity crosswalk. These rows support the current
descriptive and linear-probability models that relate historical capacity to
institutional change.

The first-pass full-controls regression sample now has 65 rows. This is not a
final journal sample. It comes from thirty-seven source-backed city-control units
covered by a mix of official statistical communiques, official budget reports,
official budget tables, official final-account reports, and secondary
public-data compilations. Hangzhou, Foshan, Wuxi, Wenzhou, and Taizhou now
bring functional-transfer cases into the first-pass full-controls sample. Hangzhou's
GDP, population, and
GDP-per-capita values come from a municipal statistical-communique reprint,
while its general-budget, debt, and government-fund values come from the
official municipal budget-execution and budget-draft report. Foshan's GDP and
population values come from the 2024 statistical communique published by the
Foshan Statistics Bureau and Foshan survey team in Foshan Daily, while its
general-budget, debt, and government-fund values come from the official 2024
municipal final-account disclosure. Wuxi brings the Yixing functional-transfer
case into the model with prefecture-level controls from a Lianhe Ratings
compilation of public 2024 economic, fiscal, fund-revenue, and debt data.
Wenzhou brings a municipal construction-group functional-transfer case into
the model, with GDP and population from the municipal statistical communique
and general-budget, government-fund, and local-government debt values from the
official municipal budget-execution report.
Taizhou brings the Wenling county-level state-asset platform case into the
model, with GDP and population from the municipal statistical communique and
general-budget, government-fund, and debt values from the official municipal
budget-execution report.
Shaoxing adds a high-capacity development-zone nominal-exit case, with GDP and
population from the municipal statistical communique, general-budget values
from the official general-budget execution report, government-fund revenue
from the official government-fund budget execution report, and debt balance
from the official local-government debt limit and balance table.
Huzhou adds a prefecture-level nominal-exit case in a high-capacity Zhejiang
setting. Its GDP, population, and GDP-per-capita values come from the municipal
statistical communique, while general-budget revenue, government-fund revenue,
and fiscal self-sufficiency come from a public rating-report table sourced to
Huzhou Finance Bureau. The debt balance is cross-checked against a separate
tracking-rating report. General-budget expenditure is calculated from the
reported fiscal self-sufficiency ratio and should be replaced with the official
final-account table before journal submission.
Zhenjiang adds a high-debt Jiangsu nominal-exit case. Its GDP and
GDP-per-capita values come from a Lianhe Ratings report, resident population is
calculated from those two fields, and its general-budget, government-fund, and
debt values come from a tracking-rating table sourced to Zhenjiang Finance
Bureau. The row is useful for the alternative-explanations design because it
adds a case with very high statutory debt pressure but no coded institutional
change.
Bengbu adds an Anhui high-debt nominal-exit case from a lower historical-capacity
setting. GDP, population, GDP per capita, general-budget revenue,
government-fund revenue, fiscal self-sufficiency, and debt balance come from a
Dongfang Jincheng tracking-rating compilation. General-budget expenditure is
calculated from the reported fiscal self-sufficiency ratio and should be
replaced with the official final-account table before journal submission.
Huai'an adds a northern Jiangsu nominal-exit case with lower fiscal
self-sufficiency and substantial government-fund dependence. GDP, GDP per
capita, general-budget revenue, government-fund revenue, fiscal
self-sufficiency, and debt balance come from a Dongfang Jincheng tracking-rating
compilation based on local statistical communiques and fiscal final accounts.
Resident population and general-budget expenditure are calculated from the
reported GDP, per-capita GDP, and fiscal self-sufficiency fields.
Nanning adds a non-eastern provincial-capital nominal-exit case. GDP,
GDP per capita, general-budget revenue, general-budget expenditure,
government-fund revenue, fiscal self-sufficiency, and local-government debt
balance come from a Lianhe Ratings tracking report based on public materials.
Resident population is calculated from the reported GDP and per-capita GDP.
The row also adds a case in which the source packet describes a shift after
2018 toward fiscal funding for project-owner-designated municipal projects.
Linyi adds a Shandong non-capital nominal-exit case. GDP, general-budget
revenue, general-budget expenditure, government-fund revenue, and
local-government debt balance come from a Lianhe Ratings tracking report based
on public materials. Because the report says the 2024 year-end resident
population was not published, the row uses the report's 2023 resident-population
field to calculate a transparent first-pass GDP-per-capita proxy.
Chengdu adds a western provincial-capital nominal-exit case. GDP,
general-budget revenue, general-budget expenditure, government-fund revenue,
and local-government debt balance come from a Lianhe Ratings tracking report.
Resident population and official per-capita GDP come from the municipal
statistical communique. The row adds a high-fiscal-capacity comparison in which
observed exit remains nominal rather than substantive.
Harbin adds a northeastern provincial-capital nominal-exit case with very high
statutory debt pressure. GDP and registered population come from the municipal
statistical communique, while general-budget revenue, general-budget
expenditure, government-fund revenue, and legal debt balance come from the
official municipal budget report and debt disclosure. GDP per capita uses
registered population as a transparent first-pass proxy until a resident
population field is collected.
Luoyang adds a Henan interior-prefecture nominal-exit case. GDP and resident
population come from the municipal statistical communique. General-budget
revenue, general-budget expenditure, government-fund revenue, and year-end
government debt balance come from the official municipal budget report. The row
adds an inland provincial-subcenter comparison with moderate fiscal
self-sufficiency and sizable government-fund dependence.
Hengyang adds a Hunan high-debt nominal-exit case. GDP, resident population,
GDP per capita, general-budget revenue, general-budget expenditure,
government-fund revenue, and local-government debt balance come from a Lianhe
Ratings tracking report based on public materials. The row adds a high-debt
central-province comparison with weak fiscal self-sufficiency and substantial
government-fund dependence.
Xi'an adds a western provincial-capital nominal-exit case centered on a
high-tech-zone platform. GDP, resident population, GDP per capita,
general-budget revenue, and general-budget expenditure come from the municipal
statistical communique. Government-fund revenue and local-government debt
balance come from a CCXI tracking report based on public materials. The row is
useful because it adds a district-level development-zone platform inside a large
western city rather than another ordinary prefecture-level city-investment
group.
Luzhou adds a western prefecture-level nominal-exit case. GDP, GDP per capita,
general-budget revenue, general-budget expenditure, government-fund revenue,
and local-government debt balance come from a Lianhe Ratings tracking report
based on public materials. Resident population is calculated from the reported
GDP and per-capita GDP. The row gives the Sichuan component a non-capital
comparison with weaker fiscal self-sufficiency and sizable debt pressure.
Dezhou adds a Shandong non-capital nominal-exit case. GDP, resident population,
GDP per capita, general-budget revenue, general-budget expenditure, fiscal
self-sufficiency, government-fund revenue, and local-government debt balance
come from a Lianhe Ratings report. The row adds a non-capital Shandong
comparison with weak fiscal self-sufficiency, high statutory debt pressure, and
continuing infrastructure and state-asset functions.
Suzhou, Anhui adds a northern Anhui nominal-exit case. GDP, resident
population, GDP per capita, general-budget revenue, general-budget expenditure,
fiscal self-sufficiency, government-fund revenue, and local-government debt
balance come from a Lianhe Ratings tracking report. The row adds a low
historical-capacity comparison with weak fiscal self-sufficiency, high statutory
debt pressure, and continuing shantytown redevelopment, municipal
infrastructure, land-development, and state-asset functions.
Bozhou adds two nominal-exit cases. Its
general-budget and debt fields come from a CCXI tracking-rating compilation,
its expenditure value is calculated from the reported fiscal balance ratio, and
its government-fund field uses a municipal audit-report figure as a transparent
first-pass proxy because the rating report says full government-fund revenue
was not published for 2022--2024. Qingdao is included from official budget and
statistical-communique sources, and its SCO demonstration-zone platform is
coded as a development-zone platform. Ningbo brings one substantive exit case
and one nominal comparison case into the first-pass full-controls sample. Its
fiscal fields come from local-government bond disclosure and tracking-report
compilations and should be OCR-checked against official final-account tables
before journal submission. Jiaxing is included from official statistical
communique and final-account sources. Xuzhou is included from a public
rating-report compilation of the city's statistical communique and
budget-execution report. Shangrao adds two nominal-exit cases using a
statistical-communique reprint for GDP and population and a Dagong active-rating
report for general-budget, government-fund, and debt values. Huangshi is
included with a transparent city-direct
government-fund proxy for the land-finance measure, while its GDP, population,
general-budget, and debt values come from citywide official sources. The
dataset contains
fields for contemporary fiscal capacity, GDP per capita, fiscal
self-sufficiency, debt pressure, land finance dependence, platform
administrative level, capital or sub-provincial city status, province fixed
effects, and bond disclosure quality. Source coverage and city-status fields
are populated systematically. `platform_control_coding_queue.csv` supplies
rule-based platform administrative-level pre-codes for cases where the platform
name, common municipal platform markers such as city-construction,
investment-holding, and industrial-investment groups, specialized sector, or
city-prefecture mismatch is informative, but these values remain
pending human review. Debt, land-finance, and fiscal controls are retained as
explicit collection fields and are merged only when source-backed values are
available.

The next empirical step is to expand the contemporary-control fields from
city-level statistical yearbooks, local final-account reports, bond-market
debt disclosures, and platform source packets. Once those fields cover a much
larger share of the validated sample, the paper can treat the full
alternative-explanations specification as a main result rather than a
first-pass diagnostic.

The control collection templates are:

- `data/analysis_inputs/contemporary_city_controls.csv`
- `data/analysis_inputs/contemporary_city_controls_source_backed.csv`
- `data/analysis_inputs/platform_control_coding_queue.csv`
- `docs/contemporary_controls.md`
