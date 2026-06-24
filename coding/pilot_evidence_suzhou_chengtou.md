# Pilot Evidence Packet: Suzhou City Construction Investment

## Case Summary

- Case ID: `pilot_js_002`
- Company: Suzhou City Construction Investment Development Group Co., Ltd.
  (`苏州城市建设投资发展（集团）有限公司`)
- Status: high historical-capacity candidate evidence packet
- Preliminary coding implication: `substantive_exit_or_functional_transfer`
- Confidence: candidate only
- Main source page: Shanghai Clearing House,
  `苏州城市建设投资发展(集团)有限公司2026年度第一期中期票据发行文件`,
  2026-03-02
- Source inventory rows: `src_js_sz_001`, `src_js_sz_002`

## Why This Case Matters

Suzhou is the highest historical elite-density city in the current candidate
pool. It is therefore useful as a high historical-capacity comparison for the
weak-capacity Guizhou cases and for the already validated Guangzhou and
Hangzhou cases.

The source trail suggests a high-capacity transformation case rather than a
simple disappearance of public functions. The 2026 prospectus contains strong
compliance language: the company says it does not undertake government financing
functions, that new debt after January 1, 2015 is not local government debt, and
that this MTN will not add government debt or hidden debt. At the same time, the
same document describes Suzhou City Investment as having previously performed
investment-platform and urban-infrastructure construction functions, and as
having transformed toward an operating entity with city construction, city
operations, industrial development, and city-investment financial services.

This makes Suzhou useful for distinguishing two high-capacity outcomes:
substantive exit from government financing, and functional transfer into a more
marketized or operating-oriented municipal state-owned group.

## Machine-Readable Documents

The 2026 Shanghai Clearing disclosure page lists eleven downloadable documents.
The most important local text extractions are:

- `doc_js_sz_chengtou_2026_mtn1_009`: 2026 first MTN prospectus, 306 pages,
  314,243 extracted characters
- `doc_js_sz_chengtou_2026_mtn1_007`: legal opinion, 30 pages, 28,419
  extracted characters
- `doc_js_sz_chengtou_2026_mtn1_006`: 2023 audited consolidated and parent
  financial report, 168 pages, 140,149 extracted characters
- `doc_js_sz_chengtou_2026_mtn1_004`, `008`, and `010`: issuance plans with
  readable text

The 2022 and 2024 annual financial reports and the 2025 third-quarter financial
statement downloaded successfully but produced no local text with the current
extractor.

## Evidence Themes

### No Government Financing Function

The prospectus states that the issuer's debts are the responsibility of the
issuer as an independent legal person, that the company does not undertake
government financing functions, and that new debt after January 1, 2015 is not
local government debt.

Relevant extracted-text location:

- `doc_js_sz_chengtou_2026_mtn1_009.txt`, lines 916-919

### No New Hidden Debt from the MTN

The prospectus says the MTN proceeds will not increase government debt, will not
involve false debt resolution or new local hidden debt, will not be transferred
to government or fiscal use, and will not be directly repaid with fiscal funds.
It also excludes BT projects, non-operating public-welfare projects mainly
repaid by fiscal funds, land primary development, ordinary commercial housing,
and affordable-housing project construction or repayment.

Relevant extracted-text location:

- `doc_js_sz_chengtou_2026_mtn1_009.txt`, lines 868-886

### Legal Opinion on Compliance

The legal opinion repeats the compliance position. It says the issuer does not
have illegal guarantees, public-deposit taking, illegal financing, land-reserve
functions, or misleading publicity linked to government credit. It also says the
issuer does not have PPP projects, government investment funds, BT projects,
repurchase of other entities' projects, government purchase-of-service
arrangements, or advance financing for government projects.

Relevant extracted-text location:

- `doc_js_sz_chengtou_2026_mtn1_007.txt`, lines 667-699

### Transformation from Platform to Operating Entity

The prospectus states that Suzhou City Investment was established in 2001 and
previously mainly performed investment-platform and urban-infrastructure
construction functions. With the post-2010 regulation of financing platforms and
hidden debt, the group began shifting from an investment-financing platform to
an operating entity. The document describes later strategy around city
construction, city operations, industrial development, and city-investment
financial services.

Relevant extracted-text location:

- `doc_js_sz_chengtou_2026_mtn1_009.txt`, lines 4792-4820

### Continuing Public-Project and City-Operation Functions

The same prospectus continues to describe the issuer as Suzhou's main urban
infrastructure and public-utility investment, construction, and operation body.
It says the company is responsible for funding and debt repayment related to
urban infrastructure construction projects and has a leading position in roads,
railway station construction, urban renewal, gas, water, and other public
utility fields.

Relevant extracted-text locations:

- `doc_js_sz_chengtou_2026_mtn1_009.txt`, lines 5002-5018
- `doc_js_sz_chengtou_2026_mtn1_009.txt`, lines 6504-6532

### Delegated Project Accounts and Fiscal Linkages

The prospectus and 2023 financial report show delegated project-management
assets and fiscal linkages. Some subsidiaries conduct project agency management
and maintain independent project accounts under entrusted construction or
management agreements. The prospectus also reports other non-current assets
mainly composed of delegated projects and some SOE equity investments, with
delegated projects rising in 2025. The 2023 financial report contains the same
delegated-project account explanation and reports fiscal subsidies and fiscal
special funds.

Relevant extracted-text locations:

- `doc_js_sz_chengtou_2026_mtn1_009.txt`, lines 5931-5958
- `doc_js_sz_chengtou_2026_mtn1_009.txt`, lines 6504-6532
- `doc_js_sz_chengtou_2026_mtn1_006.txt`, lines 2252-2258
- `doc_js_sz_chengtou_2026_mtn1_006.txt`, lines 3671-3691

## Coding Implication

The case should remain a candidate evidence packet rather than a final label.

The strongest current interpretation is that Suzhou is a high-capacity
transformation case. It has stronger substantive-exit evidence than Xi'an
because the 2026 documents contain repeated no-government-financing,
no-hidden-debt, no-BT, and no-government-project-advance-financing language. Yet
the case should not be treated as pure disappearance of public functions. The
issuer continues to hold city construction, city operation, public utility,
delegated project, and city-investment financial functions.

For now, code this as `substantive_exit_or_functional_transfer` pending manual
validation. The key validation question is whether the delegated project and
city-investment financial-service activities are mainly formal operating
businesses under marketized or fiscal-management rules, or whether they preserve
quasi-fiscal financing functions in a new form.
