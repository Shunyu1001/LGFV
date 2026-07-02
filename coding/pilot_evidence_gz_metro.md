# Pilot Evidence Packet: Guangzhou Metro Group

## Case

- Case ID: `pilot_gd_001_alt_metro`
- Company: Guangzhou Metro Group Co., Ltd. (`广州地铁集团有限公司`)
- Current status: human-validated gold label
- Final label: `nominal_exit`
- Confidence: medium
- Main source page: Shanghai Clearing House, `广州地铁集团有限公司2025年度第一期中期票据发行文件(更新)`, 2025-05-23
- Source inventory row: `src_gd_gz_003`

## Machine-Readable Documents

Six downloaded documents produced usable text through `scripts/extract_pdf_text.py`.

- `doc_gd_gz_metro_2025_mtn_001`: updated renewal prospectus, 22 pages, 13,720 extracted characters
- `doc_gd_gz_metro_2025_mtn_004`: legal opinion, 30 pages, 20,092 extracted characters
- `doc_gd_gz_metro_2025_mtn_006`: MTN rating report, 23 pages, 29,253 extracted characters
- `doc_gd_gz_metro_2025_mtn_008`: issuer rating report, 25 pages, 32,707 extracted characters
- `doc_gd_gz_metro_2025_mtn_009`: base prospectus, 239 pages, 255,436 extracted characters
- `doc_gd_gz_metro_2025_mtn_010`: issuance plan and commitment document, 34 pages, 15,079 extracted characters

Four financial reports were downloaded but did not produce machine-readable text with `pypdf`; they may require OCR if needed.

## Initial Evidence Themes

The current evidence points to continuing public infrastructure and financing functions rather than disappearance of the platform. This is not yet a final exit label, because the project still needs an official exit or transformation event for this company.

### Continuing Public Function

The rating reports describe Guangzhou Metro as Guangzhou's only urban rail transit construction and operation entity. They also describe the company as highly important to the municipal government and closely linked to the government. This evidence is directly relevant to distinguishing `substantive_exit` from `nominal_exit` or `functional_transfer`.

Relevant extracted-text locations:

- `doc_gd_gz_metro_2025_mtn_006.txt`, lines 65-68
- `doc_gd_gz_metro_2025_mtn_006.txt`, lines 120-123
- `doc_gd_gz_metro_2025_mtn_008.txt`, lines 61-64
- `doc_gd_gz_metro_2025_mtn_008.txt`, lines 161-164

### Financing and Construction Role

The rating reports state that the company is responsible for rail transit investment, financing, construction, and operation. They also state that construction funds come from municipal and district fiscal contributions plus company debt financing. This is especially important for identifying whether the company still performs a quasi-fiscal financing role.

Relevant extracted-text locations:

- `doc_gd_gz_metro_2025_mtn_006.txt`, lines 329-337
- `doc_gd_gz_metro_2025_mtn_008.txt`, lines 423-437

### Government Support and Fiscal Linkage

The documents describe fiscal support, operating subsidies, capital injections, and government funding for rail projects. This supports a coding memo focused on continued public-sector backing and dependence, but it does not by itself prove official exit status.

Relevant extracted-text locations:

- `doc_gd_gz_metro_2025_mtn_001.txt`, lines 354-367
- `doc_gd_gz_metro_2025_mtn_006.txt`, lines 676-697
- `doc_gd_gz_metro_2025_mtn_008.txt`, lines 774-789

### Compliance Language on Local Government Debt

The prospectuses include standard regulatory language that the MTN proceeds will not add local government debt, will not create hidden debt, and will not be transferred to government or fiscal departments. This language is important but should not be mistaken for substantive exit. It may coexist with continuing public infrastructure functions.

Relevant extracted-text locations:

- `doc_gd_gz_metro_2025_mtn_001.txt`, lines 318-324
- `doc_gd_gz_metro_2025_mtn_009.txt`, lines 839-867

## Coding Implication

Reviewed again on 2026-07-02 after the surrogate validation queue flagged the
case for human review. The base prospectus contains direct compliance language:
after consultation with the Guangzhou Finance Bureau, it states that the
issuance will not create hidden local-government debt and that the company does
not undertake government financing functions after January 1, 2015. This is
sufficient for a gold-standard coding event under the current protocol, although
the event is still issuer-disclosed rather than a separately collected
platform-list transfer-out notice.

The final label is `nominal_exit`. The same issuer remains Guangzhou's sole
urban rail construction and operation body, undertakes rail transit investment,
financing, construction, and operation, receives municipal and district fiscal
capital contributions, and continues to rely on government support, operating
subsidies, land-reserve proceeds, and debt financing for rail construction.
Official compliance therefore does not imply functional disappearance of the
specialized rail-infrastructure finance role.

The most plausible alternative label is `substantive_exit` if one focuses on
the negative legal-opinion evidence that the issuer has no land-preparation,
affordable-housing, BT, government-purchase-service, government-guarantee, or
project-advance-financing functions. I keep the nominal-exit label because the
same entity still houses the municipal rail investment-financing and
construction role.

## Next Collection Need

Search specifically for Guangzhou Metro platform-list removal, market-oriented
transformation, or hidden-debt cleanup documents. Suggested Chinese search
terms:

- `广州地铁 融资平台 退出`
- `广州地铁 政府融资职能`
- `广州地铁 隐性债务`
- `广州地铁 市场化转型`
- `广州地铁 融资平台名单`
- `广州地铁 政府债务`
