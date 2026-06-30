# Pilot Evidence Packet: Fuzhou City Construction Investment

## Case Summary

- Case ID: `expand_fj_fuzhou_chengtou`
- Company: Fuzhou City Construction Investment Group Co., Ltd.
  (`福州城市建设投资集团有限公司`)
- Status: human-validated evidence packet
- Final coding: `functional_transfer`
- Confidence: medium
- Main source page: Shanghai Clearing House,
  `福州城市建设投资集团有限公司2026年度第二期超短期融资券发行材料`,
  2026-06-22
- Source inventory row: `src_fj_fz_chengtou_001`

## Why This Case Matters

This case adds Fujian to the validated pool and gives the project a clean
example of formal fiscal substitution. The issuer does not disappear from
public development. It remains a major Fuzhou infrastructure, affordable
housing, shantytown-renovation, area-development, PPP, and delegated project
vehicle. The institutional change is that municipal project funding is described
as shifting away from issuer financing with fiscal repayment toward fiscal
appropriation, budgeted management fees, and regulated PPP or government
purchase service arrangements.

The case is treated as medium confidence because the formal event is based on
issuer disclosure rather than an independent regulator or local government
platform-list notice. It is still useful because the same prospectus gives a
rarely explicit before-and-after account of how municipal infrastructure
financing was restructured.

## Machine-Readable Documents

The 2026 Shanghai Clearing disclosure page lists ten downloadable documents.
The most useful local text extractions are:

- `doc_fj_fz_chengtou_2026_scp2_005`: 2026 second SCP prospectus, 341 pages,
  408,134 extracted characters
- `doc_fj_fz_chengtou_2026_scp2_001`: legal opinion, 28 pages, 21,579
  extracted characters
- `doc_fj_fz_chengtou_2026_scp2_009`: long-term issuer rating report, 32 pages,
  45,381 extracted characters
- `doc_fj_fz_chengtou_2026_scp2_003`: 2025 audited financial report, 113 pages,
  128,701 extracted characters
- `doc_fj_fz_chengtou_2026_scp2_002`: 2023 audited financial report, 103 pages,
  109,078 extracted characters

The 2026 first-quarter financial statement and 2024 audited financial report
downloaded successfully but produced no machine-readable text with the current
extractor.

## Evidence Themes

### No Government Financing Function

The prospectus states that the bond proceeds will not add government debt, will
not involve false debt resolution or new hidden debt, will not be transferred to
government or fiscal use, and will not be repaid directly with fiscal funds. The
issuer later states that it does not undertake government financing functions
and that new debt after January 1, 2015 is not local government debt. The same
compliance section says that the issuance will not add local government debt or
hidden debt.

Relevant extracted-text locations:

- `doc_fj_fz_chengtou_2026_scp2_005.txt`, lines 1055-1059
- `doc_fj_fz_chengtou_2026_scp2_005.txt`, lines 1167-1170
- `doc_fj_fz_chengtou_2026_scp2_005.txt`, lines 1218-1220

### Continuing Public Development Functions

The prospectus describes the issuer as Fuzhou SASAC's representative for
affordable housing and infrastructure. Its responsibilities include citywide
affordable-housing construction, infrastructure investment, project preparation,
and asset operations. Its main businesses include urban infrastructure
investment, construction, and operation; area redevelopment; land development;
real-estate development; and industrial-park and hotel operations.

Relevant extracted-text location:

- `doc_fj_fz_chengtou_2026_scp2_005.txt`, lines 1894-1910

### Fiscal Substitution in Municipal Infrastructure Projects

The strongest mechanism evidence is the prospectus's before-and-after account
of municipal project finance. Before 2011, Fuzhou municipal projects were
funded partly by fiscal appropriations and partly by issuer financing; the
financing principal and interest were repaid through fiscal arrangements. After
2011, municipal project funds no longer came through issuer financing and were
instead fully fiscally appropriated. The issuer remained the project owner and
construction manager, paid contractors according to project progress, and
claimed construction funds and management fees from the municipal finance
system.

Relevant extracted-text location:

- `doc_fj_fz_chengtou_2026_scp2_005.txt`, lines 7622-7651

### Delegated Projects and Accounting Treatment

The prospectus reports that Fuzhou government departments continue to assign
construction tasks to subsidiaries, including 33 congestion-relief and bridge
projects. Project work is still organized through government plans and
construction task documents. The accounting treatment records fiscal
appropriations as capital reserve or, after 2024, special payables until project
completion.

Relevant extracted-text location:

- `doc_fj_fz_chengtou_2026_scp2_005.txt`, lines 7663-7692

### Rating Evidence of Continued Fiscal Linkage

The rating report states that the company is an important Fuzhou infrastructure,
area-redevelopment, and affordable-housing body. It also describes continuing
municipal代建 work, area redevelopment, government purchase service projects,
PPP projects, fiscal appropriations, and government receivables. The report
notes that 2022-2024 fiscal payments and redevelopment funds remained important
to the issuer's project cycle.

Relevant extracted-text locations:

- `doc_fj_fz_chengtou_2026_scp2_009.txt`, lines 88-95
- `doc_fj_fz_chengtou_2026_scp2_009.txt`, lines 547-578
- `doc_fj_fz_chengtou_2026_scp2_009.txt`, lines 589-592
- `doc_fj_fz_chengtou_2026_scp2_009.txt`, lines 1155-1163

## Validation Decision

The case is coded as `functional_transfer` at medium confidence.

The formal-event evidence is the issuer's no-government-financing statement and
the post-2015 local-government-debt disclaimer. The continued-function evidence
is too extensive for substantive exit. The issuer remains central to Fuzhou's
public development system. The crucial difference from a simple nominal-exit
case is that the prospectus documents a change in financing and settlement
rules. Municipal infrastructure projects that previously combined fiscal
appropriation with issuer financing and fiscal repayment are now described as
fiscally appropriated projects with management-fee settlement. This is not the
disappearance of the fiscal function; it is its relocation into more formal
budgetary and contractual channels.

The main alternative label is `nominal_exit`. Because the same legal issuer
continues to carry public project tasks, a coder focused only on functional
continuity could label it nominal. The final label is functional transfer
because the evidence shows a clear change in how public-project finance is
organized and recorded.

Source coverage score: 4. Confidence should rise only if an independent local
government, SASAC, banking-regulator, or platform-list document confirms the
issuer's formal platform-list status or exit event. Historical-capacity metrics
for this added target still need to be merged into the candidate-capacity file.
