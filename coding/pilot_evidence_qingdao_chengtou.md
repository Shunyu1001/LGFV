# Pilot Evidence Packet: Qingdao City Construction Investment

## Case Summary

- Case ID: `pilot_sd_002`
- Company: Qingdao City Construction Investment Group Co., Ltd.
  (`青岛城市建设投资(集团)有限责任公司`)
- Status: human-validated evidence packet
- Final coding: `nominal_exit`
- Confidence: medium
- Main source page: Shanghai Clearing House,
  `青岛城市建设投资(集团)有限责任公司2026年度第二期中期票据发行文件`,
  2026-02-02
- Source inventory rows: `src_sd_qd_001`, `src_sd_qd_002`

## Why This Case Matters

Qingdao is in the middle historical-capacity bin in the current candidate list.
It is therefore useful as a comparison case between high-capacity coastal
platforms such as Guangzhou, Hangzhou, Suzhou, and Nanjing, and weak-capacity
debt-pressure cases in Guizhou. The case is also substantively useful because it
looks like a city-investment group that has been pushed toward marketized
operation and formal debt compliance while continuing to hold public project
functions.

The case is now treated as a medium-confidence validated label. The formal
event is not an independent exit-list notice, but the prospectus contains direct
no-government-financing language and states that new debt after January 1, 2015
is not local government debt. The same document also describes a 2014
market-oriented reform and SOE transformation. The post-event evidence points
away from substantive exit because the same issuer continues land-development,
urban-renewal, infrastructure-construction, delegated project-management,
fiscal-settlement, and policy-loan-administration functions.

## Machine-Readable Documents

The 2026 Shanghai Clearing disclosure page lists seven downloadable documents.
The most useful local text extractions are:

- `doc_sd_qd_chengtou_2026_mtn2_001`: 2026 second MTN prospectus, 356 pages,
  408,048 extracted characters
- `doc_sd_qd_chengtou_2026_mtn2_006`: issuance plan and commitment letter, 35
  pages, 15,616 extracted characters
- `doc_sd_qd_chengtou_2026_mtn2_007`: 2024 audited consolidated and parent
  financial report, 141 pages, 134,130 extracted characters

The 2025 third-quarter financial statement, 2023 audited financial report, 2026
legal opinion, and 2022 audited financial report downloaded successfully but
produced no machine-readable text with the current extractor. They should not be
used for LLM-assisted labeling unless OCR is added later.

## Evidence Themes

### Debt Responsibility and Compliance

The prospectus begins by stating that the issuer is a marketized operating
entity and that local government does not assume responsibility for the
enterprise's debt. In the proceeds-use section, the issuer states that the MTN
proceeds will not increase government debt, will not involve false debt
resolution or new hidden government debt, will not be transferred to government
or fiscal use, and will not be directly repaid with fiscal funds. It also
excludes real-estate development, land reserve, affordable-housing and
shantytown-redevelopment project construction or loan repayment, and similar
uses.

Relevant extracted-text locations:

- `doc_sd_qd_chengtou_2026_mtn2_001.txt`, lines 34-40
- `doc_sd_qd_chengtou_2026_mtn2_001.txt`, lines 1111-1135

### No Government Financing Function

The prospectus states that Qingdao SASAC bears limited liability only up to its
capital contribution, that the issuer repays its own debts as an independent
legal person, that the company does not undertake government financing
functions, and that new debt after January 1, 2015 is not local government debt.
It also states that the company has no PPP projects, government investment
funds, BT business, repurchase of other entities' projects, government
purchase-of-service arrangements, or advance financing for government projects.
The prospectus says that receivables from government have normal business
backgrounds and do not constitute financing for government.

Relevant extracted-text location:

- `doc_sd_qd_chengtou_2026_mtn2_001.txt`, lines 1297-1324

### Market-Oriented Reform and Platform Transformation

The prospectus states that the issuer was established in 2008 and initially
undertook infrastructure construction and primary land-development work. It then
states that, from 2014, the issuer comprehensively began market-oriented reform
and SOE transformation, becoming a municipal state-capital investment and
operation company. This is not by itself evidence of LGFV exit, but it gives a
clear institutional transition point for later validation.

Relevant extracted-text location:

- `doc_sd_qd_chengtou_2026_mtn2_001.txt`, lines 2187-2194

### Land Development and Fiscal Settlement

The issuer's urban-renewal business includes low-efficiency-area redevelopment,
primary land development, and land preparation. The prospectus describes the
issuer or its subsidiaries as the front-end operator or implementation body for
several land-development projects, including Huanle Binhecheng, Hongdao, and
Qinggang. In the Huanle Binhecheng project, the issuer advanced land
compensation funds, recorded early land-development expenses as other
receivables from the municipal finance bureau, and offset those receivables when
government repayment funds were received.

Relevant extracted-text locations:

- `doc_sd_qd_chengtou_2026_mtn2_001.txt`, lines 2203-2225
- `doc_sd_qd_chengtou_2026_mtn2_001.txt`, lines 2226-2269
- `doc_sd_qd_chengtou_2026_mtn2_001.txt`, lines 2270-2282

### Infrastructure Construction and Delegated Management

The prospectus describes the issuer as Qingdao's urban infrastructure
investment and operation body. It has implemented more than 50 municipal roads,
water-supply and drainage networks, and other major infrastructure and public
service projects. The current business model is mainly delegated project
management and construction-operation. Under delegated management, government
departments select the issuer as a professional project-management unit through
bidding, sign entrusted-management contracts, and pay project-management fees.
The issuer states that it does not undertake the investment-financing function
for these projects, and that construction and installation costs and other
project costs are paid directly by fiscal funds to construction units.

Relevant extracted-text location:

- `doc_sd_qd_chengtou_2026_mtn2_001.txt`, lines 2645-2691

### Residual Financing and Policy-Loan Channels

The prospectus also contains evidence that the boundary between formal
substitution and residual quasi-fiscal finance remains empirically important.
It states that some infrastructure projects are self-funded or financed through
financial institutions, while denying government guarantees or hidden-debt
creation. The 2024 financial report states that the issuer applies for policy
loans from China Development Bank for municipal infrastructure projects and that
Qingdao finance allocates funds quarterly to repay principal and interest, so
the company records these loans under special payables.

Relevant extracted-text locations:

- `doc_sd_qd_chengtou_2026_mtn2_001.txt`, lines 2973-2984
- `doc_sd_qd_chengtou_2026_mtn2_001.txt`, lines 6898-6922
- `doc_sd_qd_chengtou_2026_mtn2_001.txt`, lines 7065-7073
- `doc_sd_qd_chengtou_2026_mtn2_001.txt`, lines 10216-10220

## Validation Decision

The case is coded as `nominal_exit` at medium confidence.

The formal-event evidence comes from the 2026 prospectus. It states that the
issuer does not undertake government financing functions and that new debt after
January 1, 2015 is not local government debt. It also states that the issuer was
initially responsible for infrastructure construction and primary land
development and began market-oriented reform and SOE transformation in 2014.

The continued-function evidence is extensive. The same prospectus describes the
issuer as the front-end operator or implementation body for land-development
projects, including Huanle Binhecheng, Hongdao, and Qinggang. It also describes
the issuer as Qingdao's urban infrastructure investment and operation body and
as the project-management unit for major municipal roads and public service
projects. The policy-loan passage shows that, for some municipal infrastructure
projects, the issuer applies for China Development Bank loans and Qingdao
finance allocates funds quarterly to repay principal and interest.

The main alternative label is `substantive_exit`. The case has strong formal
compliance language: the prospectus says that delegated project management is
fiscal-funded rather than platform-financed, that the issuer has no PPP, BT,
project repurchase, government purchase service, or advance financing for
government projects, and that government receivables have operating backgrounds.
The final label remains nominal exit because the same issuer continues to carry
core public development functions after the formal compliance point.

Source coverage score: 4. The packet contains a prospectus, financial report,
and issuance documents from the Shanghai Clearing disclosure page. Confidence
should rise only if an independent government, regulator, or SASAC document
confirms the platform-list status or the 2014 transformation event.
