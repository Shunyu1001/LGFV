# Pilot Evidence Packet: Huangshi Urban Development Investment Group

## Case Summary

- Case ID: `expand_hb_huangshi_chengfa`
- Company: Huangshi Urban Development Investment Group Co., Ltd.
  (`黄石市城市发展投资集团有限公司`)
- Status: human-validated evidence packet
- Final coding: `nominal_exit`
- Confidence: medium
- Main source page: Shanghai Clearing House,
  `黄石市城市发展投资集团有限公司2026年度第八期短期融资券发行文件`,
  2026-06-24
- Source inventory row: `src_hb_huangshi_chengfa_001`

## Why This Case Matters

Huangshi is a useful expansion case because the issuer's own disclosures put
formal debt compliance and continuing development functions next to each other.
The prospectus says the current bond will not increase government or hidden
debt, will not be repaid directly through fiscal funds, and that the company
does not undertake government financing functions. It also says new debt after
January 1, 2015 is not local-government debt.

Yet the same document describes the issuer as responsible for city-designated
infrastructure investment, land development, local railway investment, urban
franchise operations, and cultural-tourism development. Its subsidiaries
continue infrastructure construction, entrusted construction, land整理, public
housing, PPP/BOT participation, and other government-linked development work.
The disclosure also reports heavy fiscal linkages, including large government
fiscal inflows, finance-bureau payables, and government fiscal dependence in
the issuer's cash flow.

## Machine-Readable Documents

The useful local text extractions are:

- `doc_hb_huangshi_chengfa_2026_cp8_001`: 2026 eighth CP prospectus, 304 pages,
  306,262 extracted characters
- `doc_hb_huangshi_chengfa_2026_cp8_003`: issuance plan and issuer commitment,
  12 pages, 5,685 extracted characters
- `doc_hb_huangshi_chengfa_2026_cp8_005`: issuance plan, 9 pages, 4,606
  extracted characters
- `doc_hb_huangshi_chengfa_2026_cp8_008`: issuance plan and bookrunner
  commitment, 11 pages, 5,277 extracted characters

Several audit-report and legal-opinion PDFs in this packet were scanned or
otherwise not machine-readable in the current extraction pass. The prospectus
contains enough direct evidence for a medium-confidence label.

## Evidence Themes

### Formal Compliance Language

The prospectus states that the bond proceeds will not increase government or
hidden debt, will not be used for non-operating assets, will not be transferred
to the government or finance department, and will not be directly repaid by
fiscal funds. It later states that the issuer does not undertake government
financing functions and that new debt after January 1, 2015 is not
local-government debt.

Relevant extracted-text locations:

- `doc_hb_huangshi_chengfa_2026_cp8_001.txt`, lines 1136-1166
- `doc_hb_huangshi_chengfa_2026_cp8_001.txt`, lines 1248-1265

### Continuing Development Mandate

The issuer's registered business scope includes city-designated infrastructure
investment, land development, urban franchise operations, local railway
investment, cultural-tourism development, real estate development, and medical
elder-care investment. The document states that infrastructure construction is
carried out by subsidiaries and includes roads, road expansion, pipe networks,
sewage treatment, and shantytown renovation.

Relevant extracted-text locations:

- `doc_hb_huangshi_chengfa_2026_cp8_001.txt`, lines 1248-1258
- `doc_hb_huangshi_chengfa_2026_cp8_001.txt`, lines 1290-1308

### Fiscal Dependence and Entrusted Construction

The prospectus reports that government fiscal inflows accounted for a large
share of operating cash inflows from 2023 to 2025. It also states that
entrusted-construction projects are funded through self-raised funds, transferred
to the Huangshi municipal government after completion, and repaid through fiscal
funds according to construction agreements. This is classic continuing
quasi-fiscal function evidence.

Relevant extracted-text locations:

- `doc_hb_huangshi_chengfa_2026_cp8_001.txt`, lines 638-676

### Land整理, PPP, and Government-Linked Payables

The prospectus reports that subsidiaries conduct land development and整理 on
behalf of the Huangshi land-reserve center and the development-zone land bureau.
It also describes a PPP/BOT project in which a subsidiary participates as the
government-side representative. Later balance-sheet discussion lists large
payables to the Huangshi Economic and Technological Development Zone Finance
Bureau and the Huangshi Finance Bureau.

Relevant extracted-text locations:

- `doc_hb_huangshi_chengfa_2026_cp8_001.txt`, lines 1290-1332
- `doc_hb_huangshi_chengfa_2026_cp8_001.txt`, lines 12340-12430

## Validation Decision

The case is coded as `nominal_exit` at medium confidence.

It is not substantive exit because infrastructure, land整理, public housing,
entrusted construction, PPP/BOT participation, government fiscal inflows, and
finance-bureau payables remain central to the issuer's disclosed operations. It
is not functional transfer because the public development functions appear to
remain inside the issuer and its subsidiaries rather than being shifted to a
different platform or fully budgeted arrangement.

The alternative label is `functional_transfer`. That label would become more
plausible if later documents show that the relevant project-financing risk was
absorbed outside the issuer group. The current prospectus instead points to a
formal compliance layer over continuing platform-like functions.

Source coverage score: 3. Confidence should rise only after collecting an
independent local-government source or a readable legal opinion that confirms
the issuer's formal platform-exit status.
