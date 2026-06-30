# Pilot Evidence Packet: Wenling State-Owned Assets Investment

## Case Summary

- Case ID: `expand_zj_wenling_guotou`
- Company: Wenling State-Owned Assets Investment Group Co., Ltd.
  (`温岭市国有资产投资集团有限公司`)
- Status: human-validated evidence packet
- Final coding: `functional_transfer`
- Confidence: medium
- Main source page: Shanghai Clearing House,
  `温岭市国有资产投资集团有限公司2026年度第二期中期票据发行文件`,
  2026-06-30
- Source inventory row: `src_zj_wl_guotou_001`

## Why This Case Matters

This case adds a Zhejiang county-level city platform with unusually clear
evidence of fiscal substitution. The issuer states that it does not undertake
government financing functions and that new debt after 2015 is not local
government debt. At the same time, the documents show that local infrastructure
projects continue through fiscal appropriations, PPP equity participation, and
project-specific public funding rather than through classic BT, project
repurchase, or government-purchase-service arrangements.

The final label is `functional_transfer`. Public investment functions continue,
but the financing channel is described as having moved into formal fiscal
appropriations, project funds, PPP capital contributions, and accounting through
long-term payables or non-current assets rather than ordinary platform
financing.

## Machine-Readable Documents

The 2026 Shanghai Clearing disclosure page lists six downloadable documents.
The useful local text extractions are:

- `doc_zj_wl_guotou_2026_mtn2_005`: 2026 second MTN prospectus, 193 pages,
  252,111 extracted characters
- `doc_zj_wl_guotou_2026_mtn2_003`: legal opinion, 30 pages, 22,078 extracted
  characters

## Evidence Themes

### Formal Separation from Government Financing

The prospectus states that Wenling Finance Bureau acts only as shareholder
within its capital contribution and that the issuer does not undertake
government financing functions. New debt after January 1, 2015 is described as
not local government debt. The legal opinion also states that the issuer has no
government investment fund, BT, project repurchase, government-purchase-service,
or advance-financing arrangement for government projects.

Relevant extracted-text locations:

- `doc_zj_wl_guotou_2026_mtn2_005.txt`, lines 985-987
- `doc_zj_wl_guotou_2026_mtn2_005.txt`, lines 999-1019
- `doc_zj_wl_guotou_2026_mtn2_003.txt`, lines 323-342

### Continuing Public-Project Function Through Fiscal Channels

The prospectus shows that public infrastructure activity continues. The issuer
undertakes municipal supporting works entrusted by Wenling municipal
authorities. The Wenling government entrusts the finance bureau to arrange
project-construction funds, and the issuer records fiscal construction funds as
long-term payables rather than ordinary operating revenue in some projects.

Relevant extracted-text locations:

- `doc_zj_wl_guotou_2026_mtn2_005.txt`, lines 497-501
- `doc_zj_wl_guotou_2026_mtn2_005.txt`, lines 584-588
- `doc_zj_wl_guotou_2026_mtn2_005.txt`, lines 2381-2388
- `doc_zj_wl_guotou_2026_mtn2_005.txt`, lines 2427-2430

### PPP and State-Asset Reorganization

The issuer does not itself undertake PPP construction projects, but it invests
capital on behalf of the government-side investor in two PPP project companies.
The prospectus also records recent state-asset reallocations and continued
municipal infrastructure, land-development, and housing-related business
functions.

Relevant extracted-text locations:

- `doc_zj_wl_guotou_2026_mtn2_005.txt`, lines 202-216
- `doc_zj_wl_guotou_2026_mtn2_005.txt`, lines 1003-1010
- `doc_zj_wl_guotou_2026_mtn2_005.txt`, lines 1163-1163

## Validation Decision

The case is coded as `functional_transfer` at medium confidence.

The documents do not show disappearance of the public-investment function. The
issuer still sits inside Wenling's infrastructure and state-asset system, but
its public-project role is described through formal channels: fiscal project
funds, PPP capital contributions, special construction funds, and balance-sheet
treatment that separates these flows from ordinary platform financing. This is
closer to functional transfer than to substantive exit.

The main alternative label is `nominal_exit`. The same issuer continues to hold
large public-project responsibilities and government-linked funding flows, so a
narrower reading could treat the compliance language as formal relabeling. The
final label remains functional transfer because the prospectus provides concrete
evidence that project finance is organized through fiscal appropriations and
formal project-fund channels rather than classic off-budget repurchase or BT
arrangements.

Source coverage score: 3. Confidence should rise only after collecting a rating
report or local government document that independently confirms the fiscal
substitution arrangement.
