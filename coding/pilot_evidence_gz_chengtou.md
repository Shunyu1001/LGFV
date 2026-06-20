# Pilot Evidence Packet: Guangzhou City Construction Investment Group

## Case Summary

- Case ID: `pilot_gd_001`
- Company: Guangzhou City Construction Investment Group Co., Ltd. (`广州市城市建设投资集团有限公司`)
- Status: second human-validated pilot label
- Final label: `substantive_exit`
- Confidence: medium
- Main source page: Shanghai Clearing House, `广州市城市建设投资集团有限公司2026年度第四期中期票据发行文件`, 2026-04-07
- Company profile source: Guangzhou City Construction Investment Group official website
- Source inventory rows: `src_gd_gz_001`, `src_gd_gz_004`, `src_gd_gz_005`, `src_gd_gz_006`, `src_gd_gz_007`

## Why This Case Matters

Guangzhou City Construction Investment Group is a useful contrast to the Xi'an
Hi-tech case. Xi'an Hi-tech is a likely `nominal_exit` case because official
exit language coexists with continuing infrastructure financing and BT or
entrusted-construction functions.

Guangzhou City Construction Investment Group, by contrast, is a candidate for
formal fiscal substitution. The prospectus describes the company's origin in
Guangzhou's city-construction investment and financing reform, but it also says
that since 2014 the company no longer participates in new government-project
investment and financing. Its remaining public-project role is described as
`代建代管`: government agencies commission the company to manage projects,
public-welfare project funding comes from municipal fiscal funds, and the
company receives a capped management fee.

This makes Guangzhou a good candidate for testing whether the codebook can
distinguish continued public-project management from continued government
financing.

## Machine-Readable Documents

Four key documents have been downloaded locally. Three produced usable text:

- `doc_gd_gz_chengtou_2026_mtn4_004`: 2026 fourth MTN prospectus, 342 pages,
  340,331 extracted characters
- `doc_gd_gz_chengtou_2018_tracking_rating`: 2018 tracking rating report, 22
  pages, 30,962 extracted characters
- `doc_gd_gz_chengtou_2018_swap_plan`: 2018 planned debt-replacement
  announcement for `14粤城建MTN001`, 3 pages, 961 extracted characters

One scanned announcement produced no local text:

- `doc_gd_gz_chengtou_2018_swap_special`: 2018 special announcement on local
  government debt replacement for `14粤城建MTN001`

The downloaded PDF and extracted text are stored under ignored local data
directories. The tracked inventory records the source URL and local path.

## Evidence Themes

### Reform Origin

The prospectus states that the Guangzhou municipal government issued the
`城市建设投融资体制改革方案` in 2008 and decided to establish the city construction
investment group.

Relevant extracted-text locations:

- `doc_gd_gz_chengtou_2026_mtn4_004.txt`, lines 939-943
- `doc_gd_gz_chengtou_2026_mtn4_004.txt`, lines 1064-1071

### No Government Financing Function

The prospectus states that the issuer does not undertake government financing
functions, and that new debt after 2015 does not legally constitute local
government debt.

Relevant extracted-text location:

- `doc_gd_gz_chengtou_2026_mtn4_004.txt`, lines 927-931

### Shift from Investment-Financing to Entrusted Management

The prospectus states that since 2014 the company has not participated in new
government-project investment and financing. Instead, it shifted to a
`代建代管` model in which it manages government projects under commission.

Relevant extracted-text location:

- `doc_gd_gz_chengtou_2026_mtn4_004.txt`, lines 6537-6544
- `doc_gd_gz_chengtou_2018_tracking_rating.txt`, lines 657-668

### Fiscal Funding of Public-Welfare Projects

The prospectus says that public-welfare entrusted-management projects are
funded by municipal fiscal funds, with the government responsible for
investment. The company receives a management fee capped by fiscal rules.

Relevant extracted-text locations:

- `doc_gd_gz_chengtou_2026_mtn4_004.txt`, lines 6545-6548
- `doc_gd_gz_chengtou_2026_mtn4_004.txt`, lines 6756-6761
- `doc_gd_gz_chengtou_2018_tracking_rating.txt`, lines 657-668

### Debt Replacement as Fiscal Substitution

The 2018 announcement on the planned partial replacement of the 2014 MTN states
that 1.141 billion yuan of `14粤城建MTN001` was recognized as debt for which the
government bore repayment responsibility and included in the 2018 fiscal budget.
It also cites a Guangzhou Finance Bureau notice requiring replacement of
non-government-bond-form government debt by the end of August 2018.

Relevant extracted-text location:

- `doc_gd_gz_chengtou_2018_swap_plan.txt`, lines 14-27

### Remaining Ambiguities

The case is coded as `substantive_exit` with medium confidence. The reason is
that both 2018 and 2026 documents describe a post-2014 shift away from new
government-project investment and financing toward fiscal-funded project
management, while the 2018 debt-replacement announcement shows that part of an
older 2014 MTN was absorbed into the formal fiscal budget.

The main caveat is that this is not an exit-list case. The company profile still
describes the group as engaged in city infrastructure investment, financing,
construction, and operation. The prospectus also records large public-welfare
assets and ongoing public-project management. The coding claim therefore turns
on the distinction between budgetary project management and off-budget
government financing.

Before raising confidence to high, the next validation step should collect the
original Guangzhou 2008 reform document or additional 2014 issuance materials.
