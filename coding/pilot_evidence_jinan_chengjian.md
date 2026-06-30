# Pilot Evidence Packet: Jinan City Construction Group

## Case Summary

- Case ID: `expand_sd_jinan_chengjian`
- Company: Jinan City Construction Group Co., Ltd.
  (`济南城市建设集团有限公司`)
- Status: human-validated evidence packet
- Final coding: `nominal_exit`
- Confidence: medium
- Main source page: Shanghai Clearing House,
  `济南城市建设集团有限公司2026年度第四期超短期融资券发行文件`,
  2026-06-26
- Source inventory row: `src_sd_jn_chengjian_001`

## Why This Case Matters

This case adds a second Jinan platform to the validated pool. The existing Jinan
case covers `济南城市投资集团有限公司`; this packet covers `济南城市建设集团有限公司`.
The same-city comparison is useful because it keeps historical and municipal
conditions partly fixed while allowing platform-level institutional functions
to vary.

The case is treated as a medium-confidence validated label. The formal event is
based on issuer compliance language rather than an independent regulator or
local government exit-list document. The continued-function evidence is strong:
the issuer still reports engineering construction, land preparation, delegated
infrastructure construction, government receivables, and project settlement
with public-sector counterparties.

## Machine-Readable Documents

The 2026 Shanghai Clearing disclosure page lists nine downloadable documents.
The most useful local text extractions are:

- `doc_sd_jn_chengjian_2026_scp4_007`: 2026 fourth SCP prospectus, 331 pages,
  332,283 extracted characters
- `doc_sd_jn_chengjian_2026_scp4_004`: legal opinion, 22 pages, 17,535
  extracted characters
- `doc_sd_jn_chengjian_2026_scp4_003`: 2025 audited financial report, 115
  pages, 114,425 extracted characters
- `doc_sd_jn_chengjian_2026_scp4_006`: 2024 audited financial report, 133
  pages, 113,959 extracted characters

The 2026 first-quarter financial statement and 2023 audited financial report
downloaded successfully but produced no machine-readable text with the current
extractor.

## Evidence Themes

### No Government Financing Function

The prospectus states that the proceeds will not add local government debt, will
not involve false debt resolution or new hidden debt, will not be transferred to
government or fiscal use, and will not be repaid directly with fiscal funds. It
then states that the issuer does not undertake government financing functions
and that the Jinan municipal government only bears limited shareholder
liability. Later, the issuer states that it does not undertake government
financing functions and that new debt after January 1, 2015 is not local
government debt. The passage says this statement was confirmed with the Jinan
Finance Bureau.

Relevant extracted-text locations:

- `doc_sd_jn_chengjian_2026_scp4_007.txt`, lines 954-960
- `doc_sd_jn_chengjian_2026_scp4_007.txt`, lines 1062-1068

### Hidden-Debt Cleanup and Residual Public Functions

The prospectus describes a 2014 cooperation arrangement involving subsidiaries
and private investment entities. It states that the project was placed under
hidden-debt management according to audit and Ministry of Finance standards,
that a resolution plan was formulated, and that the investment had been settled
by the prospectus date. This supports a coding of formal debt cleanup, but it
also shows the issuer's historical involvement in public-project finance.

Relevant extracted-text location:

- `doc_sd_jn_chengjian_2026_scp4_007.txt`, lines 1078-1088

### BT, Entrusted Construction, Government Receivables, and Land Injection

The prospectus states that the issuer has PPP business and BT or entrusted
construction business. For the Xiaoqing River project, the issuer's subsidiary
transfers project-use rights to the Jinan municipal government after completion,
and the government obtains ownership after paying the BT repurchase funds. The
same compliance section states that the issuer has receivables from government
entities and that public authorities injected land into the group through
earlier restructuring.

Relevant extracted-text location:

- `doc_sd_jn_chengjian_2026_scp4_007.txt`, lines 1094-1117

### Engineering Construction, Land Preparation, and Delegated Projects

The issuer reports that it is an important engineering-construction body in
Jinan. Its main revenue comes from engineering construction and land
preparation. The prospectus reports that land preparation is an important
business line in Jinan Binhe New City and the West Railway Station area, and
that the company conducts land preparation according to Jinan's citywide
planning. Engineering-construction income includes delegated-construction
business. The delegated-construction section describes current projects in the
Jinan Start-up Area, where a subsidiary invests in and builds infrastructure
under entrusted-construction agreements and later settles with the entrusted
party.

Relevant extracted-text locations:

- `doc_sd_jn_chengjian_2026_scp4_007.txt`, lines 2719-2725
- `doc_sd_jn_chengjian_2026_scp4_007.txt`, lines 2761-2788
- `doc_sd_jn_chengjian_2026_scp4_007.txt`, lines 2813-2821
- `doc_sd_jn_chengjian_2026_scp4_007.txt`, lines 2966-2986
- `doc_sd_jn_chengjian_2026_scp4_007.txt`, lines 4140-4169
- `doc_sd_jn_chengjian_2026_scp4_007.txt`, lines 4170-4183

## Validation Decision

The case is coded as `nominal_exit` at medium confidence.

The formal-event evidence is the issuer's direct statement that it does not
undertake government financing functions and that post-2015 debt is not local
government debt. The continued-function evidence is too strong for substantive
exit. The same issuer remains active in land preparation, engineering
construction, entrusted infrastructure construction, and public-project
settlement. It also reports a historical hidden-debt cleanup episode and
government receivables.

The main alternative label is `functional_transfer`. Many of the continued
functions are presented as legal fiscal-settlement or marketized construction
businesses rather than direct off-budget financing. The final label remains
`nominal_exit` because the same legal issuer continues to carry public-project
functions after the formal compliance point.

Source coverage score: 4. Confidence should rise only if an independent local
government, SASAC, banking-regulator, or platform-list document confirms the
issuer's list status or formal exit event.
