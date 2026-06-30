# Pilot Evidence Packet: Suzhou City Construction Investment Group

## Case Summary

- Case ID: `expand_ah_suzhou_chengtou`
- Company: Suzhou City Construction Investment Group Holding Co., Ltd.
  (`宿州市城市建设投资集团(控股)有限公司`)
- Status: human-validated evidence packet
- Final coding: `nominal_exit`
- Confidence: medium
- Main source page: Shanghai Clearing House,
  `宿州市城市建设投资集团(控股)有限公司2026年度第三期中期票据发行披露文件`,
  2026-06-17
- Source inventory row: `src_ah_suzhou_chengtou_001`

## Why This Case Matters

This case is a clean example of formal compliance without institutional exit.
The issuer uses standard post-2014 debt-compliance language: the company says it
does not undertake government financing functions, that post-2015 new debt is
not local-government debt, that the current bond will not increase government
or hidden debt, and that the issuer does not conduct BT or PPP project
financing.

The same prospectus, however, repeatedly identifies the issuer as Suzhou's main
urban infrastructure investment, construction, and operation body. Its main
business is still municipal infrastructure and land leveling, it has
government-backed entrusted construction and repurchase-payment arrangements,
and it expects continued government support because it will keep undertaking
local infrastructure and land整理 tasks. That combination is stronger evidence
of nominal exit than of substantive exit.

## Machine-Readable Documents

The useful local text extractions are:

- `doc_ah_suzhou_chengtou_2026_mtn3_005`: 2026 third MTN prospectus, 238 pages,
  248,358 extracted characters
- `doc_ah_suzhou_chengtou_2026_mtn3_002`: 2025 audit report, 108 pages,
  87,023 extracted characters
- `doc_ah_suzhou_chengtou_2026_mtn3_007`: 2024 audit report, 107 pages,
  90,489 extracted characters

## Evidence Themes

### Formal Debt-Compliance Language

The prospectus states that the issue will not increase government debt or
hidden debt and will not be repaid directly by fiscal funds. It also states
that the company does not undertake government financing functions and that new
debt after January 1, 2015 is not local-government debt. A later compliance
section says the issuer has rectified and standardized the stripping of
government financing functions and does not undertake land-reserve functions.

Relevant extracted-text locations:

- `doc_ah_suzhou_chengtou_2026_mtn3_005.txt`, lines 803-816
- `doc_ah_suzhou_chengtou_2026_mtn3_005.txt`, lines 4506-4523

### Continuing Infrastructure and Fiscal Functions

The same prospectus describes Suzhou Chengtou as the city's most important
urban infrastructure investment, construction, and operation body. It says the
issuer undertakes project financing, construction, and management tasks and
relies on operating income, financing channels, and government support for debt
service. The issuer's business scope includes urban infrastructure, public
utility construction and operation, state-asset operation, land整理 and
development, real estate development, standardized factories, and affordable
housing.

Relevant extracted-text locations:

- `doc_ah_suzhou_chengtou_2026_mtn3_005.txt`, lines 860-878
- `doc_ah_suzhou_chengtou_2026_mtn3_005.txt`, lines 4555-4564

### Entrusted Construction and Repurchase Payments

The prospectus reports that infrastructure and affordable-housing projects are
mainly carried out through an entrusted-construction model. Government payment
is tied to project review and settlement by the finance bureau. The document
also identifies a 2015 infrastructure-project repurchase agreement with the
Suzhou municipal government. This is the core evidence that local development
functions remain inside the issuer after formal debt-compliance language.

Relevant extracted-text locations:

- `doc_ah_suzhou_chengtou_2026_mtn3_005.txt`, lines 4558-4593
- `doc_ah_suzhou_chengtou_2026_mtn3_005.txt`, lines 8024-8038

### Government Subsidy and Future Function Continuity

The prospectus states that revenue mainly comes from municipal infrastructure
and land-leveling business and that government subsidies include shantytown
renovation subsidies and infrastructure-budget investment funds. It further
states that the issuer will continue to undertake Suzhou's infrastructure
construction and land整理 tasks and is expected to continue receiving local
government support.

Relevant extracted-text locations:

- `doc_ah_suzhou_chengtou_2026_mtn3_005.txt`, lines 8834-8865

## Validation Decision

The case is coded as `nominal_exit` at medium confidence.

It is not substantive exit because the company's public infrastructure, land,
affordable-housing, entrusted-construction, fiscal-settlement, and government
support ties remain central to the issuer's business. It is also not best read
as functional transfer because the documents do not show a clear relocation of
quasi-fiscal functions to another entity or to a fully budgetary channel.
Instead, formal debt-compliance language coexists with continuing public
development functions inside the same issuer.

The alternative label is `functional_transfer`. That label would become more
plausible if later evidence shows that post-2015 project financing risk was
absorbed by the fiscal budget or by a different state-owned platform. The
current packet instead points to a nominal institutional change.

Source coverage score: 4. Confidence should rise only after collecting an
independent local government or regulator source on the issuer's platform-list
status.
