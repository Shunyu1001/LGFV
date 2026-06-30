# Pilot Evidence Packet: Yuyao City Construction Investment

## Case Summary

- Case ID: `expand_zj_yuyao_chengtou`
- Company: Yuyao City Construction Investment Development Co., Ltd.
  (`余姚市城市建设投资发展有限公司`)
- Status: human-validated evidence packet
- Final coding: `nominal_exit`
- Confidence: medium
- Main source page: Shanghai Clearing House,
  `余姚市城市建设投资发展有限公司2026年度第一期中期票据发行披露文件`,
  2026-06-30
- Source inventory row: `src_zj_yy_chengtou_001`

## Why This Case Matters

This case adds a county-level coastal city in Zhejiang. It is useful because the
issuer's formal compliance language is unusually clear, while its business
description and rating report still place it at the center of local public
development. The case therefore helps separate formal legal exit from the
continued use of a platform company for infrastructure, land development, and
budget-linked public services.

The label is medium confidence. The formal-event evidence comes from issuer
disclosure and finance-bureau confirmation language in the prospectus rather
than from a directly retrieved platform-list document. The continued-function
evidence is strong and appears both in the prospectus and in the credit rating
report.

## Machine-Readable Documents

The 2026 Shanghai Clearing disclosure page lists nine downloadable documents.
The most useful local text extractions are:

- `doc_zj_yuyao_chengtou_2026_mtn1_001`: 2026 first MTN prospectus, 232 pages,
  232,201 extracted characters
- `doc_zj_yuyao_chengtou_2026_mtn1_004`: 2026 credit rating report, 27 pages,
  31,313 extracted characters
- `doc_zj_yuyao_chengtou_2026_mtn1_006`: legal opinion, 22 pages, 19,940
  extracted characters
- `doc_zj_yuyao_chengtou_2026_mtn1_005`: 2024 annual report, 132 pages, 12,881
  extracted characters
- `doc_zj_yuyao_chengtou_2026_mtn1_008`: 2025 annual report, 131 pages, 13,602
  extracted characters
- `doc_zj_yuyao_chengtou_2026_mtn1_009`: 2023 annual report, 113 pages, 12,795
  extracted characters

The 2026 first-quarter financial statement and accounting opinion downloaded
successfully but produced no machine-readable text with the current extractor.

## Evidence Themes

### No Government Financing Function

The prospectus states that the issuer is responsible for its own debt as an
independent legal person. It then states that the company does not undertake
government financing functions and that debt newly incurred after January 1,
2015 is not local government debt. The same compliance section says the issuer
has no debt directly repaid by fiscal funds, no government guarantee or
repayment commitment, and no new local-government or hidden debt from the
issuance.

Relevant extracted-text locations:

- `doc_zj_yuyao_chengtou_2026_mtn1_001.txt`, lines 1162-1168
- `doc_zj_yuyao_chengtou_2026_mtn1_001.txt`, lines 1179-1196
- `doc_zj_yuyao_chengtou_2026_mtn1_001.txt`, lines 4005-4020

### Continued Platform Position

The credit rating report describes the company as an important land-development
and housing-construction body in Yuyao, with an important platform position and
strong local-government support through asset injections and subsidies. The
prospectus also describes the issuer as the main local state-owned body for
water, gas, resettlement housing, and public project construction.

Relevant extracted-text locations:

- `doc_zj_yuyao_chengtou_2026_mtn1_004.txt`, lines 89-100
- `doc_zj_yuyao_chengtou_2026_mtn1_004.txt`, lines 160-179
- `doc_zj_yuyao_chengtou_2026_mtn1_001.txt`, lines 1158-1165

### Fiscal Support and Public-Project Revenue

The prospectus shows that public-project revenue did not disappear. For
municipal infrastructure projects, the issuer obtained road-maintenance,
green-maintenance, parking, advertising, water, and wastewater operating
rights. It also received a municipal infrastructure supporting-fee subsidy that
was approved by the finance bureau and included in the annual people's congress
budget. Other subsidies are tied to infrastructure construction and land
development.

Relevant extracted-text locations:

- `doc_zj_yuyao_chengtou_2026_mtn1_001.txt`, lines 5764-5811
- `doc_zj_yuyao_chengtou_2026_mtn1_001.txt`, lines 6371-6440
- `doc_zj_yuyao_chengtou_2026_mtn1_004.txt`, lines 342-369

## Validation Decision

The case is coded as `nominal_exit` at medium confidence.

The formal-event evidence is clear, but the same legal issuer remains a core
local platform for land development, resettlement housing, public utilities,
and municipal infrastructure. The rating report emphasizes local-government
support, while the prospectus links public-project revenue to budgeted subsidies
and local-government-authorized operating rights. This is not a case where the
function disappears. It is a case where official compliance language coexists
with continuing platform use.

The main alternative label is `substantive_exit`. The prospectus states that the
issuer has no PPP, government-purchase-service, BT, or government-project
advance-financing arrangements, and several revenue channels are presented as
budgeted or operating-right based. The final label remains nominal exit because
the company still performs central public-development functions and remains
financially connected to fiscal subsidies and local-government authorizations.

Source coverage score: 4. Confidence should rise only if an independent local
government, SASAC, banking-regulator, or platform-list document confirms the
issuer's formal exit or platform-list status.
