# Pilot Evidence Packet: Guangzhou Metro Group

## Case

- Case ID: `pilot_gd_001_alt_metro`
- Company: Guangzhou Metro Group Co., Ltd. (`广州地铁集团有限公司`)
- Current status: source collection and evidence extraction, not final labeling
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

Reviewed again on 2026-07-01. This case should not be promoted to the
gold-standard label file yet. The packet contains strong evidence of continuing
public infrastructure investment, financing, construction, operation, land
development, fiscal support, and standard no-hidden-debt compliance language.
It still lacks a direct official exit, transfer-out, marketization, or platform
list removal event for Guangzhou Metro. Under the codebook, standard debt
compliance language alone is not enough to define a validated exit case.

For the first LLM-assisted coding pass, this case should be treated as a strong test of the difference between regulatory compliance language and actual functional role. The strongest current interpretation is:

- If an official exit or transformation document is later found for Guangzhou Metro, these sources would be strong evidence against `substantive_exit`.
- The likely alternatives would be `nominal_exit` if the same entity continues the financing and construction function under a compliance narrative, or `functional_transfer` if a formal document shows the financing role moved to a different entity.
- Without an official exit or transformation event, the case should remain `documents_found` rather than labeled.

## Next Collection Need

Search specifically for Guangzhou Metro official exit, platform-list removal, market-oriented transformation, or hidden-debt cleanup documents. Suggested Chinese search terms:

- `广州地铁 融资平台 退出`
- `广州地铁 政府融资职能`
- `广州地铁 隐性债务`
- `广州地铁 市场化转型`
- `广州地铁 融资平台名单`
- `广州地铁 政府债务`
