# Pilot Evidence Packet: Chengdu City Construction Investment Management Group

## Case Summary

- Case ID: `pilot_sc_001`
- Company: Chengdu City Construction Investment Management Group Co., Ltd. (`成都城建投资管理集团有限责任公司`)
- Status: fourth human-validated pilot label
- Final label: `nominal_exit`
- Confidence: medium
- Main source page: Shanghai Clearing House, `成都城建投资管理集团有限责任公司2023年度第三期中期票据发行文件`, 2023-10-30
- Source inventory rows: `src_sc_cd_001`, `src_sc_cd_002`

## Why This Case Matters

Chengdu City Construction Investment Management Group is useful because it sits
between the Xi'an Hi-tech and Guangzhou City Construction Investment cases. Like
Guangzhou, the prospectus contains formal compliance language stating that the
issuer does not undertake government financing functions and that new debt after
2015 does not legally constitute local government debt. Unlike Guangzhou, the
same document continues to describe a city-infrastructure role in which the
issuer undertakes public facilities and infrastructure construction, uses
self-raised funds and financing in project construction, receives fiscal
payments during construction, and carries government-bond pass-through debt
linked to earlier local debt replacement.

The coding claim is therefore not that every public project function equals
nominal exit. The claim is narrower: when formal no-government-financing
language coexists with continuing evidence that the same platform remains a
municipal infrastructure investor and project-financing vehicle, the case is
best treated as nominal exit unless later evidence shows a cleaner transfer to
budgetary channels or another state entity.

## Machine-Readable Documents

One key document has been downloaded locally and produced usable text:

- `doc_sc_cd_chengtou_2023_mtn3_prospectus`: 2023 third MTN prospectus,
  304 pages, readable extracted text

The downloaded PDF and extracted text are stored under ignored local data
directories. The tracked inventory records the source URL and local path.

## Evidence Themes

### Formal No-Government-Financing Language

The prospectus states that Chengdu SASAC bears limited liability as shareholder,
that issuer debt is repaid by the issuer as an independent legal person, and
that the company does not undertake government financing functions. It also
states that new debt after January 1, 2015 does not legally constitute local
government debt.

Relevant extracted-text location:

- `doc_sc_cd_chengtou_2023_mtn3_prospectus.txt`, lines 1662-1670

### Continuing Infrastructure Investment and Financing Function

The prospectus describes the company's original purpose as accelerating reform
of the city-construction investment and financing system. It states that the
company was responsible for operating transferred state assets, preserving and
increasing their value, undertaking investment tasks for urban infrastructure
and public facilities, and raising funds through multiple channels.

Relevant extracted-text locations:

- `doc_sc_cd_chengtou_2023_mtn3_prospectus.txt`, lines 1716-1734
- `doc_sc_cd_chengtou_2023_mtn3_prospectus.txt`, lines 1757-1759

### BT Legacy and No New BT Contract After 2012

The document records that the Chengdu municipal government and the issuer signed
a 2012 BT cooperation agreement for bond-funded infrastructure projects. The
issuer was responsible for financing, investment, and construction, and the
municipal government repurchased the completed projects. The prospectus also
states that no new BT contract was signed after that agreement.

Relevant extracted-text location:

- `doc_sc_cd_chengtou_2023_mtn3_prospectus.txt`, lines 1681-1696

### Current Infrastructure Construction Model

The issuer continues to undertake public-facility construction and renovation
projects in Chengdu. The prospectus describes infrastructure projects approved
by the municipal development and reform commission, with the issuer serving as
project owner. Project funds come first from the issuer's own funds and
financing, while fiscal funds are arranged over ten years and paid during
construction. The document states that the issuer generally does not need to
advance project funds for a long period, but it still places the issuer inside
the financing and implementation chain for public infrastructure.

Relevant extracted-text locations:

- `doc_sc_cd_chengtou_2023_mtn3_prospectus.txt`, lines 4884-4892
- `doc_sc_cd_chengtou_2023_mtn3_prospectus.txt`, lines 4902-4916

### Government-Bond Pass-Through Debt

The prospectus describes the replacement of earlier China Development Bank
loans with local government bond pass-through funds beginning in 2015. It also
records specific debt-replacement and transfer arrangements with Chengdu fiscal
authorities.

Relevant extracted-text location:

- `doc_sc_cd_chengtou_2023_mtn3_prospectus.txt`, lines 8909-8942

### Remaining Ambiguities

The case is coded as `nominal_exit` with medium confidence. The main ambiguity
is that the available source does not contain a direct government exit-list
document. The official event is therefore a compliance and transformation claim
inside the issuer prospectus rather than an independently retrieved exit-list
announcement.

The main alternative label is `substantive_exit`. The strongest argument for
that label is the document's repeated assertion that the issuer does not
undertake government financing functions and does not create new hidden debt.
The reason for not using that label is that the same document continues to show
the issuer inside the infrastructure investment, financing, fiscal-payment, and
local-debt-replacement chain.
