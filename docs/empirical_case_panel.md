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

The first-pass full-controls regression sample now has 50 rows. This is not a
final journal sample. It comes from twenty-two source-backed city-control units
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
