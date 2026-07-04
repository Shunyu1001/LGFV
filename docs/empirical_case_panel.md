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

The full-controls regression sample is currently zero by design. The dataset
contains fields for contemporary fiscal capacity, GDP per capita, fiscal
self-sufficiency, debt pressure, land finance dependence, platform
administrative level, capital or sub-provincial city status, province fixed
effects, and bond disclosure quality. Source coverage and city-status fields
are populated systematically. `platform_control_coding_queue.csv` supplies
rule-based platform administrative-level pre-codes for cases where the platform
name or city-prefecture mismatch is informative, but these values remain
pending human review. Debt, land-finance, and fiscal controls are retained as
explicit collection fields rather than imputed.

The next empirical step is to fill the contemporary-control fields from
city-level statistical yearbooks, local final-account reports, bond-market
debt disclosures, and platform source packets. Once those fields are complete,
the paper can report the full alternative-explanations specification rather
than only the current validated-sample association.

The control collection templates are:

- `data/analysis_inputs/contemporary_city_controls.csv`
- `data/analysis_inputs/platform_control_coding_queue.csv`
- `docs/contemporary_controls.md`
