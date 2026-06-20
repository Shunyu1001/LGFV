# Pilot Evidence Packet: Xi'an Hi-tech Holding

## Case

- Case ID: `pilot_sn_xian_hightech`
- Company: Xi'an Hi-tech Holding Co., Ltd. (`西安高新控股有限公司`)
- Status: strong candidate for first LLM-assisted label
- Main source page: Shanghai Clearing House, `西安高新控股有限公司2026年度第六期中期票据发行文件`, 2026-06-11
- Source inventory row: `src_sn_xa_001`

## Why This Case Matters

This case is useful because it separates official platform exit from functional exit. The 2026 prospectus states that the issuer exited the financing-platform list in 2012 and that its bank loans were converted to ordinary corporate loans. The same document and the rating report show that the issuer remains the most important infrastructure investment and construction entity in Xi'an High-tech Zone, continues to use BT and entrusted-construction arrangements, and receives project repurchase funds and fiscal support from the High-tech Zone Management Committee.

This makes the case a likely `nominal_exit` candidate, subject to human validation.

## Machine-Readable Documents

Ten documents have been downloaded locally. Eight produced usable text:

- `doc_sn_xa_hightech_2026_mtn6_001`: joint lead-underwriter issuance plan, 10 pages, 4,965 extracted characters
- `doc_sn_xa_hightech_2026_mtn6_002`: legal opinion, 33 pages, 22,859 extracted characters
- `doc_sn_xa_hightech_2026_mtn6_003`: 2025 issuer rating report, 26 pages, 32,846 extracted characters
- `doc_sn_xa_hightech_2026_mtn6_004`: 2024 audited financial report, 105 pages, 115,678 extracted characters
- `doc_sn_xa_hightech_2026_mtn6_005`: issuer issuance plan and commitment document, 13 pages, 5,239 extracted characters
- `doc_sn_xa_hightech_2026_mtn6_006`: 2026 sixth MTN prospectus, 306 pages, 280,287 extracted characters
- `doc_sn_xa_hightech_2026_mtn6_007`: 2025 audited financial report, 100 pages, 106,823 extracted characters
- `doc_sn_xa_hightech_2026_mtn6_009`: bookrunner issuance plan and commitment document, 12 pages, 5,223 extracted characters

Two documents produced no text through `pypdf`: the 2026 first-quarter financial statements and the 2023 audited financial report.

## Evidence Themes

### Official Exit Language

The prospectus states that the issuer exited the financing-platform list in 2012. It also states that bank loans were converted to ordinary issuer loans. This is the clearest event evidence found so far.

Relevant extracted-text locations:

- `doc_sn_xa_hightech_2026_mtn6_006.txt`, lines 774-783

### Continuing Infrastructure and Financing Role

The prospectus describes the issuer as the most important infrastructure investment and construction entity in Xi'an High-tech Zone. It says the issuer undertakes infrastructure construction and park development functions and that future entrusted-construction income will continue to support operations.

Relevant extracted-text locations:

- `doc_sn_xa_hightech_2026_mtn6_006.txt`, lines 656-663
- `doc_sn_xa_hightech_2026_mtn6_006.txt`, lines 7001-7053

### BT and Entrusted-Construction Arrangements

The prospectus states that the issuer undertakes projects under BT and entrusted-construction models. It describes project repurchase by the High-tech Zone Management Committee and says the repurchase amount covers investment costs and management fees.

Relevant extracted-text locations:

- `doc_sn_xa_hightech_2026_mtn6_006.txt`, lines 724-728
- `doc_sn_xa_hightech_2026_mtn6_006.txt`, lines 3600-3615
- `doc_sn_xa_hightech_2026_mtn6_006.txt`, lines 4398-4416

### Government Support and Repurchase Funds

The prospectus and rating report describe continuing fiscal subsidies, project repurchase funds, and strong government support. The rating report states that the company remains highly important to the High-tech Zone Management Committee and receives continued support in funding and subsidies.

Relevant extracted-text locations:

- `doc_sn_xa_hightech_2026_mtn6_006.txt`, lines 180-183
- `doc_sn_xa_hightech_2026_mtn6_006.txt`, lines 4363-4389
- `doc_sn_xa_hightech_2026_mtn6_003.txt`, lines 21-22
- `doc_sn_xa_hightech_2026_mtn6_003.txt`, lines 129-135

### Compliance and Government-Debt Language

The prospectus contains regulatory language that the current MTN does not add local government debt or hidden debt and that the issuer does not bear a government financing function for new debt after 2015. This language should be coded separately from functional evidence. It is evidence of formal compliance, not necessarily substantive exit.

Relevant extracted-text locations:

- `doc_sn_xa_hightech_2026_mtn6_006.txt`, lines 1435-1479
- `doc_sn_xa_hightech_2026_mtn6_006.txt`, lines 7094-7143

## Preliminary Coding Implication

The likely label is `nominal_exit`.

The logic is:

- Official exit condition: present, because the issuer says it exited the financing-platform list in 2012.
- Substantive disappearance condition: not supported, because the issuer continues to be the zone's key infrastructure investment and construction entity.
- Functional transfer condition: not the best fit from current evidence, because the same issuer still appears to perform the core infrastructure and financing-related role.
- Liquidation condition: not supported.

Before final labeling, the next validation step should check whether there is a more direct official document from the High-tech Zone or finance bureau confirming the 2012 exit, rather than relying only on the issuer prospectus.
