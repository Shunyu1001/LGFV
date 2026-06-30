# Pilot Evidence Packet: Harbin City Construction Investment

## Case Summary

- Case ID: `expand_hlj_harbin_chengtou`
- Company: Harbin City Construction Investment Group Co., Ltd.
  (`哈尔滨市城市建设投资集团有限公司`)
- Status: human-validated evidence packet
- Final coding: `nominal_exit`
- Confidence: high
- Main source page: Shanghai Clearing House,
  `哈尔滨市城市建设投资集团有限公司2026年度第一期中期票据发行文件`,
  2026-06-18
- Source inventory row: `src_hlj_hrb_chengtou_001`

## Why This Case Matters

This case adds a northeastern provincial-capital platform and has stronger
formal-event evidence than most pilot cases. The prospectus states that the
issuer was in the CBIRC financing-platform list at the end of 2018 and was
changed to the exit category in early 2019. That direct list-status evidence
makes the case especially useful for validating the coding scheme.

The final label is `nominal_exit`. The exit event is clear, but the issuer
continues to carry large public-project assets, government receivables,
entrusted-construction projects, affordable-housing projects, and PPP-related
functions. Official exit therefore did not mean the disappearance of the
public-development function from the same legal issuer.

## Machine-Readable Documents

The 2026 Shanghai Clearing disclosure page lists seven downloadable documents.
The most useful local text extractions are:

- `doc_hlj_hrb_chengtou_2026_mtn1_003`: 2026 first MTN prospectus, 225 pages,
  224,853 extracted characters
- `doc_hlj_hrb_chengtou_2026_mtn1_006`: issuance plan and commitment, 25 pages,
  14,436 extracted characters
- `doc_hlj_hrb_chengtou_2026_mtn1_007`: 2025 audited financial report, 104
  pages, 103,940 extracted characters

The 2023 and 2024 audited financial reports, the 2026 first-quarter statement,
and the legal opinion downloaded successfully but produced no machine-readable
text with the current extractor.

## Evidence Themes

### Direct Exit-List Evidence

The prospectus states that the issuer appeared in the CBIRC full-caliber
financing-platform statistics at the end of the fourth quarter of 2018. It then
states that on January 2, 2019, the Heilongjiang CBIRC office issued an
explanation and changed the issuer's platform category from still-managed-as-a
platform to exit category after considering creditor-bank and Harbin Finance
Bureau opinions.

Relevant extracted-text locations:

- `doc_hlj_hrb_chengtou_2026_mtn1_003.txt`, lines 4156-4162
- `doc_hlj_hrb_chengtou_2026_mtn1_003.txt`, lines 4165-4178
- `doc_hlj_hrb_chengtou_2026_mtn1_003.txt`, lines 4191-4195

### No Government Financing Function

The prospectus states that the issuer does not undertake government financing
functions and that debt newly incurred after January 1, 2015 is not local
government debt. It also says the issuance will not add government or hidden
debt and will not be repaid directly by fiscal funds.

Relevant extracted-text locations:

- `doc_hlj_hrb_chengtou_2026_mtn1_003.txt`, lines 938-941
- `doc_hlj_hrb_chengtou_2026_mtn1_003.txt`, lines 975-981
- `doc_hlj_hrb_chengtou_2026_mtn1_003.txt`, lines 4165-4174

### Continuing Public-Development Function

The same prospectus describes continuing infrastructure, affordable-housing,
PPP, and government-receivable functions. It says infrastructure projects are
entrusted by municipal departments and governed by entrusted-construction
agreements with the municipal government. It also documents a PPP bridge
project in the Ministry of Finance PPP project-management database, government
receivables, and large stocks of project-development costs from infrastructure
and affordable-housing projects.

Relevant extracted-text locations:

- `doc_hlj_hrb_chengtou_2026_mtn1_003.txt`, lines 944-971
- `doc_hlj_hrb_chengtou_2026_mtn1_003.txt`, lines 5544-5565
- `doc_hlj_hrb_chengtou_2026_mtn1_003.txt`, lines 5571-5574
- `doc_hlj_hrb_chengtou_2026_mtn1_003.txt`, lines 5764-5792

## Validation Decision

The case is coded as `nominal_exit` at high confidence.

The formal exit is unusually well documented. The prospectus reports both prior
financing-platform-list inclusion and a later adjustment to exit category. Yet
the same issuer retains a large body of public-development assets and
government-linked project claims. It remains tied to municipal infrastructure,
affordable-housing, PPP, entrusted construction, and government-coordinated
receivables. This pattern fits nominal exit: the official category changed, but
the public-development function continued inside the same corporate shell.

The main alternative label is `functional_transfer`. The prospectus also states
that the issuer has moved toward industrialized and market-oriented operations
and that future investment and financing will be based on its own operations.
The final label remains nominal exit because the document shows extensive
continuity of legacy and current public-project functions rather than a clean
transfer of those functions to another organization.

Source coverage score: 4. The label could become even stronger if the original
2019 CBIRC explanation document is collected directly rather than cited through
the prospectus.
