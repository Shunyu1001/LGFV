# Data Sources

## Overview

The project should use four kinds of data. The first kind is source text for
coding LGFV exit types. The second kind is platform and bond data for measuring
pre- and post-exit functions. The third kind is city-level fiscal and economic
data for controls and mechanisms. The fourth kind is historical state capacity
data for the main explanatory variable.

The most important rule is that the dependent variable should come from
documents, not from a pre-existing city list. Official exit status is only the
starting point. The paper's measurement contribution is to classify what
official exit means in practice.

## Core Coding Data

The core coding data are documents that reveal the post-exit function of a
platform company.

Use the following sources first:

- Local government announcements, finance bureau notices, NDRC notices, and
  state-owned asset supervision documents.
- Platform company announcements and annual reports.
- Bond prospectuses, follow-up credit rating reports, and bond information
  disclosure documents.
- Business registration records, including changes in business scope,
  deregistration, merger, liquidation, and legal successor information.

Recommended public portals include:

- ChinaBond (`www.chinabond.com.cn`) for bond disclosure documents and local
  government bond information.
- NAFMII (`www.nafmii.org.cn`) for debt financing instrument disclosures,
  including issuance disclosures, credit ratings, financial reports, and major
  event disclosures.
- ChinaMoney (`www.chinamoney.com.cn`) for interbank market bond information
  and disclosure search.
- Shanghai Clearing House (`www.shclearing.com.cn`) for interbank market
  issuance disclosures, rating reports, financial reports, and downloadable
  issuer documents.
- Shanghai Stock Exchange bond announcements (`www.sse.com.cn`) for exchange
  bond disclosures.
- Shenzhen Stock Exchange bond announcements (`www.szse.cn`) for exchange bond
  disclosures.
- National Enterprise Credit Information Publicity System (`www.gsxt.gov.cn`)
  for business registration and deregistration evidence.
- China Local Government Bond Information Disclosure Platform
  (`www.celma.org.cn`) for local government bond documents.

At this stage, the project should not assume that a complete public national
list of LGFV exit types exists. Public sources are more likely to reveal
official exit events, market-oriented transformation language, bond issuer
behavior, and post-exit functions. The dependent variable should therefore be
constructed from documents rather than downloaded as a finished variable.

Commercial databases can be used if available:

- Wind, Choice, CSMAR, and iFinD for platform identifiers, bond issuance,
  issuer characteristics, financial statements, and credit ratings.
- Qichacha, Tianyancha, or Qixinbao for enterprise registration histories and
  ownership links. These should be cross-checked against official registration
  records when the classification turns on legal status.

## Dependent Variable

The main dependent variable is `exit_type`.

The final coding categories are:

- `substantive_exit`
- `nominal_exit`
- `functional_transfer`
- `liquidation`
- `unclear`

The preferred unit is a platform company. If the paper later aggregates to the
city level, the city-level label should be derived from company-level evidence,
not assigned directly from city characteristics.

## Treatment and Event Data

Official exit timing should be coded from the earliest reliable document showing
that a platform company was removed from the financing-platform list, completed
market-oriented transformation, withdrew from government financing functions, or
was liquidated.

Potential sources include:

- Local government or finance bureau announcements.
- Company announcements.
- Bond prospectuses and rating reports that describe transformation or exit.
- Business registration changes.
- Market reports only as supplementary evidence.

## Mechanism Data

Mechanism variables should measure whether former platform functions were
absorbed by formal fiscal instruments or moved elsewhere.

Recommended variables include:

- Special-purpose bond issuance by city or project category.
- On-budget infrastructure and urban construction expenditure.
- Changes in platform and non-platform local SOE debt.
- New local SOE establishment after official exit.
- Changes in bond issuer identity for local infrastructure and public project
  financing.
- Project-level evidence of special-purpose bond substitution.

Data sources include local government bond platforms, Ministry of Finance
documents, ChinaBond, exchange bond disclosures, Wind/Choice/CSMAR/iFinD, local
budget final accounts, and city statistical yearbooks.

## Control Variables

City-level controls should cover current fiscal, economic, and political
conditions.

Recommended variables include:

- GDP per capita and GDP growth.
- Fiscal self-sufficiency.
- General public budget revenue and expenditure.
- Land transfer revenue or land finance dependence.
- Explicit local government debt and debt burden.
- Industrial structure.
- Population size and urbanization.
- Fixed asset investment and infrastructure investment where available.
- Local officials' tenure and turnover.

Data sources include the National Bureau of Statistics, China City Statistical
Yearbook, China Urban Construction Statistical Yearbook, provincial and city
statistical yearbooks, city budget reports, Ministry of Finance local debt
disclosures, and CSMAR/Wind/CEIC if available.

## Historical State Capacity Data

Historical state capacity should be measured separately from contemporary
development.

Candidate measures include:

- Qing county and prefecture density.
- Distance to historical administrative centers.
- Imperial examination degree-holder density.
- Historical tax capacity or land tax records where available.
- Historical transportation access, courier stations, or river/canal networks.
- Historical administrative stability or conflict frequency.

These variables should be assembled from historical GIS datasets, published
historical atlases, China Historical GIS, county gazetteers, examination-degree
datasets, and existing historical political economy datasets where available.

## Data Priority

The first priority is source-text data for exit-type coding. Without that
variable, the paper does not have its main contribution.

The second priority is mechanism evidence, especially special-purpose bond
substitution and post-exit local SOE debt or issuer changes.

The third priority is historical state capacity. A simple primary historical
measure can be used first, with alternative measures added later for robustness.

The fourth priority is full city-year controls. These matter for the empirical
analysis, but they should not delay the first pilot classification.

## Recommended Collection Sequence

The first round of collection should proceed case by case.

First, identify the main platform company in a city using bond issuer lists,
city SOE websites, local SASAC pages, and commercial databases if available.
Second, search ChinaBond, NAFMII, ChinaMoney, SSE, and SZSE for the company's
bond prospectuses, rating reports, annual reports, and major event
announcements. Third, search local government, finance bureau, NDRC, and SASAC
websites for official exit or transformation language. Fourth, check business
registration records for mergers, deregistration, business scope changes, and
legal successor entities. Finally, enter the documents into the source
inventory before running any LLM classification.
