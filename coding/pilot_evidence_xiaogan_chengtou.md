# Pilot Evidence Packet: Xiaogan City Construction Investment

## Case Summary

- Case ID: `expand_hb_xiaogan_chengtou`
- Company: Xiaogan City Construction Investment Company
  (`孝感市城市建设投资公司`)
- Status: human-validated evidence packet
- Final coding: `functional_transfer`
- Confidence: medium
- Main source page: Shanghai Clearing House,
  `孝感市城市建设投资公司2026年度第二期中期票据发行材料`,
  2026-06-22
- Source inventory row: `src_hb_xg_chengtou_001`

## Why This Case Matters

This case adds a central-China prefecture-level city with unusually clear
evidence of fiscal substitution after 2018. The issuer still manages public
construction projects and remains a central city-development platform, but the
prospectus states that project funding shifted away from issuer financing and
advance payment toward fiscal budget appropriations, own funds, and
state-asset operating income.

The final label is `functional_transfer`. Public construction tasks remain, but
the financing role is described as having been stripped from the platform. This
is the kind of case where official exit is not mere disappearance; it is a
change in the channel through which local public investment is organized.

## Machine-Readable Documents

The 2026 Shanghai Clearing disclosure page lists eight downloadable documents.
The most useful local text extractions are:

- `doc_hb_xg_chengtou_2026_mtn2_004`: 2026 second MTN prospectus, 218 pages,
  209,976 extracted characters
- `doc_hb_xg_chengtou_2026_mtn2_001`: legal opinion, 39 pages, 34,694
  extracted characters
- `doc_hb_xg_chengtou_2026_mtn2_003`: 2023 audited financial report, 103 pages,
  73,129 extracted characters
- `doc_hb_xg_chengtou_2026_mtn2_007`: 2024 audited financial report, 104 pages,
  75,414 extracted characters
- `doc_hb_xg_chengtou_2026_mtn2_008`: 2025 audited financial report, 106 pages,
  77,525 extracted characters

The 2026 first-quarter financial statement downloaded successfully but produced
no machine-readable text with the current extractor.

## Evidence Themes

### No Government Financing Function

The prospectus and legal opinion both state that the issuer does not undertake
government financing functions and that debt newly incurred after January 1,
2015 is not local government debt. The prospectus also reports that the Xiaogan
Finance Bureau confirmed the compliance statements and that the issuance will
not add local-government or hidden debt.

Relevant extracted-text locations:

- `doc_hb_xg_chengtou_2026_mtn2_004.txt`, lines 1147-1148
- `doc_hb_xg_chengtou_2026_mtn2_004.txt`, lines 1248-1259
- `doc_hb_xg_chengtou_2026_mtn2_001.txt`, lines 520-531
- `doc_hb_xg_chengtou_2026_mtn2_001.txt`, lines 720-749

### Shift from Financing to Project Management

The prospectus states that after 2018, in response to local-government-debt
management and financing-platform transformation rules, the issuer's project
funding came mainly from fiscal budget special appropriations, own funds, and
state-asset operating income. It states that the issuer no longer undertakes
project financing or advance-payment functions and only performs project
construction management duties. The same section explains that the issuer still
recognizes construction-management revenue because it controls project
initiation, bidding, construction management, quality control, completion
inspection, and settlement.

Relevant extracted-text locations:

- `doc_hb_xg_chengtou_2026_mtn2_004.txt`, lines 2168-2185
- `doc_hb_xg_chengtou_2026_mtn2_004.txt`, lines 2636-2689

### Continuing Platform Function

The issuer is still described as the main construction body for Xiaogan urban
infrastructure and key projects. It manages urban construction funds, carries
out city-development tasks assigned by the municipal government, and remains a
major platform for financing, investment, development, asset operation, city
resources, and construction-fund settlement. Government receivables and
entrusted-construction claims remain large.

Relevant extracted-text locations:

- `doc_hb_xg_chengtou_2026_mtn2_004.txt`, lines 1213-1228
- `doc_hb_xg_chengtou_2026_mtn2_004.txt`, lines 4400-4447
- `doc_hb_xg_chengtou_2026_mtn2_004.txt`, lines 4590-4632
- `doc_hb_xg_chengtou_2026_mtn2_004.txt`, lines 4672-4680

## Validation Decision

The case is coded as `functional_transfer` at medium confidence.

The formal compliance language is clear, and the continued public-development
function is also clear. What makes this case different from a simple nominal
exit is the explicit statement that after 2018 the issuer stopped undertaking
project financing and advance-payment functions, while project funding moved to
fiscal budget appropriations, own funds, and state-asset operating income. The
issuer still manages public projects and recognizes cost-plus construction
management revenue, so the local-development function remains active through a
different fiscal and managerial arrangement.

The main alternative label is `nominal_exit`. The issuer continues to have large
government receivables, government-linked project claims, and a broad
city-development mandate. The final label remains functional transfer because
the prospectus directly documents the post-2018 movement from platform
financing to project management and fiscal-budget channels.

Source coverage score: 4. Confidence should rise only if an independent local
government, SASAC, banking-regulator, or platform-list document confirms the
issuer's formal platform-list status or exit event.
