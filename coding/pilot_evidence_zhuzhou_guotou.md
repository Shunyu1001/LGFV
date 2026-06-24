# Pilot Evidence Packet: Zhuzhou Guotou

## Case Summary

- Case ID: `pilot_hn_002`
- Company: Zhuzhou State-Owned Assets Investment Holding Group Co., Ltd.
  (`株洲市国有资产投资控股集团有限公司`)
- Status: low historical-capacity non-Guizhou industrial-city evidence packet
- Preliminary coding implication:
  `nominal_exit_or_functional_transfer_candidate`
- Confidence: candidate only
- Main source page: Shanghai Clearing House,
  `株洲市国有资产投资控股集团有限公司2026年度第一期超短期融资券发行文件`,
  2026-03-25
- Source inventory rows: `src_hn_zz_001`, `src_hn_zz_002`

## Why This Case Matters

Zhuzhou is in the low historical-capacity bin in the current candidate list.
It is useful because it broadens the weak-capacity evidence beyond Guizhou. The
existing weak-capacity cases, especially Zunyi and Liupanshui, are shaped by
acute debt stress. Zhuzhou adds a central industrial city where the platform
record contains direct exit language, direct no-government-financing language,
and evidence of continuing public project functions.

The current evidence should not yet be treated as a final label. The documents
show that the issuer exited the banking regulator's local government financing
platform list in March 2013 and that it does not currently undertake government
financing functions. They also show that the issuer remains closely connected
to land preparation, major project construction, fiscal settlement, and
municipal industrial-development tasks. This combination makes the case
especially useful for distinguishing a formal list exit from an institutional
exit in which public functions are either retained inside the same firm or
repackaged as marketized business.

## Machine-Readable Documents

The 2026 Shanghai Clearing disclosure page lists six downloadable documents.
Five produced useful machine-readable text:

- `doc_hn_zz_guotou_2026_scp1_002`: 2021-2023 audited consolidated and parent
  financial report, 162 pages, 175,321 extracted characters
- `doc_hn_zz_guotou_2026_scp1_003`: 2026 first SCP prospectus, 334 pages,
  340,492 extracted characters
- `doc_hn_zz_guotou_2026_scp1_004`: 2024 audited consolidated and parent
  financial report, 121 pages, 109,696 extracted characters
- `doc_hn_zz_guotou_2026_scp1_005`: legal opinion, 61 pages, 67,635 extracted
  characters
- `doc_hn_zz_guotou_2026_scp1_006`: issuance plan and commitment letter, 22
  pages, 9,878 extracted characters

The 2025 third-quarter financial statement downloaded successfully but produced
no machine-readable text with the current extractor.

## Evidence Themes

### Formal Exit From Platform List

The prospectus states that the issuer was twice included in financing-platform
lists, in September 2009 and March 2012, because it was government-approved and
had received government asset injections. It then states that the issuer repaid
RMB 265 million in Agricultural Development Bank loans, had cash flow sufficient
to cover bank principal and interest, had market-oriented operating conditions,
and was approved by the Hunan banking regulator to exit the government financing
platform list in March 2013.

Relevant extracted-text location:

- `doc_hn_zz_guotou_2026_scp1_003.txt`, lines 4558-4575

### Debt Identification and Financing-Function Separation

The prospectus reports that, after debt identification under the post-2014
local-government debt framework, all of the issuer's debt was classified as the
enterprise's own debt and was not included in local government debt. It also
states that the Zhuzhou government had organized debt-classification work and
specified separation of the issuer's government financing function. The issuer
states that its bond issuance does not increase government debt and that the
Zhuzhou government will not directly repay the debt with fiscal funds.

Relevant extracted-text location:

- `doc_hn_zz_guotou_2026_scp1_003.txt`, lines 4576-4608

### Current No-Government-Financing Language

The prospectus has a separate subsection on the separation of government
financing functions. It states that the issuer exited local government financing
platform management in March 2013, is no longer on the banking regulator's
platform list, does not undertake government financing functions, and repays
its own debt as an independent legal person. It further states that new debt
after January 1, 2015 is not local government debt.

Relevant extracted-text location:

- `doc_hn_zz_guotou_2026_scp1_003.txt`, lines 4656-4665

### Continuing Land-Preparation and Fiscal-Settlement Functions

The prospectus states that the issuer still conducts land preparation and
development through several project areas, including Shuizhuhu, Rail Technology
City, and Yunlong Demonstration Zone. After Zhuzhou implemented its `151`
debt-resolution mechanism in 2020, the land-preparation model was adjusted:
the government entrusted the issuer with land approval, relocation and
compensation, and land-preparation services; the municipal finance bureau
arranged and paid land-preparation costs; and the issuer settled completed
projects with the finance bureau and received service fees.

Relevant extracted-text location:

- `doc_hn_zz_guotou_2026_scp1_003.txt`, lines 3888-3907

### Public Project Role and Government Support

The prospectus describes the issuer as one of Zhuzhou's important urban
infrastructure investment and construction bodies. It states that the issuer
has undertaken land preparation and major project construction in places such
as Lusong District, and that it has received strong support from Zhuzhou in
policy, funding, and project acquisition. The same prospectus states that the
issuer receives support through equity injections, fiscal subsidies, and tax
preferences. In 2022-2024, fiscal subsidies were RMB 224 million, RMB 475
million, and RMB 503 million.

Relevant extracted-text locations:

- `doc_hn_zz_guotou_2026_scp1_003.txt`, lines 4488-4499
- `doc_hn_zz_guotou_2026_scp1_003.txt`, lines 4677-4688

### Legal Opinion on Government Receivables

The legal opinion states that receivables and prepayments involving government
departments mainly arose from entrusted construction and land-preparation
businesses. It says these receivables had an operating background and did not
constitute financing for government, new government debt, or hidden debt. This
corroborates the prospectus: the issuer frames the same activities as
marketized or service-based functions rather than as government financing.

Relevant extracted-text location:

- `doc_hn_zz_guotou_2026_scp1_005.txt`, lines 1248-1265

## Coding Implication

The case should remain a candidate evidence packet rather than a final
human-validated label.

The strongest current interpretation is
`nominal_exit_or_functional_transfer_candidate`. The case has stronger formal
exit evidence than Qingdao because the prospectus explicitly says the issuer
left the government financing platform list in March 2013. It also has strong
compliance language: the issuer says it does not undertake government financing
functions, that post-2015 new debt is not local government debt, and that the
Zhuzhou government will not directly repay the debt with fiscal funds.

At the same time, the documents do not show disappearance of public functions.
The issuer continues to conduct land preparation, major project construction,
and government-entrusted work with fiscal settlement. It also receives fiscal
subsidies and policy, funding, and project-acquisition support from the city.
The key validation question is therefore whether the issuer's 2013 exit should
be coded as a nominal exit, because the same company retained platform-like
tasks, or as functional transfer/formal fiscal substitution, because the
financing function was separated while land-preparation and project functions
were reframed as service contracts and marketized operations.
