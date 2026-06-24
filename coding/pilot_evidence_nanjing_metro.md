# Pilot Evidence Packet: Nanjing Metro

## Case Summary

- Case ID: `pilot_js_001_alt_metro`
- Company: Nanjing Metro Group Co., Ltd. (`南京地铁集团有限公司`)
- Status: high historical-capacity alternative platform evidence packet
- Preliminary coding implication: `formal_fiscal_substitution_candidate`
- Confidence: candidate only
- Main source page: Shanghai Clearing House,
  `南京地铁集团有限公司2025年度第二期中期票据发行文件`, 2025-06-17
- Source inventory rows: `src_js_nj_001`, `src_js_nj_002`

## Why This Case Matters

Nanjing is one of the highest historical elite-density cities in the current
candidate pool. The original Nanjing row has not yet been tied to a core city
investment platform, but the ChinaBond and Shanghai Clearing searches identify
Nanjing Metro as a feasible alternative municipal infrastructure SOE. The case
therefore helps test whether the coding scheme can separate an LGFV exit type
from a broader process of formal fiscal substitution.

The current documents do not show that Nanjing Metro exited from a local
government financing vehicle list, and they do not make the company a final
exit-type label. They do, however, show a public infrastructure SOE that
continues to build and operate urban rail transit while its bond disclosures
make explicit legal and fiscal distinctions from local government debt. This is
useful because the paper needs to distinguish three related objects. First,
official LGFV exit is an administrative status. Second, substantive exit refers
to the disappearance of quasi-fiscal financing functions from the platform.
Third, formal fiscal substitution refers to the movement of public-project
support into more explicit budgetary, capital-injection, subsidy, PPP, or
regulated corporate-financing arrangements.

## Machine-Readable Documents

The 2025 Shanghai Clearing disclosure page lists seven downloadable documents.
The most useful local text extractions are:

- `doc_js_nj_metro_2025_mtn2_004`: 2025 second MTN prospectus, 257 pages,
  261,169 extracted characters
- `doc_js_nj_metro_2025_mtn2_002`: legal opinion, 21 pages, 17,399 extracted
  characters
- `doc_js_nj_metro_2025_mtn2_003`: issuance plan and commitment letter, 36
  pages, 14,095 extracted characters
- `doc_js_nj_metro_2025_mtn2_001`: 2024 audited consolidated and parent
  financial report, 127 pages, 13,603 extracted characters

The 2025 first-quarter financial statement and the 2022 audited financial report
downloaded successfully but produced no machine-readable text. The 2023 audited
financial report produced only 130 extracted characters and should be treated as
not usable without OCR.

## Evidence Themes

### Rail-Transit Public Function

The prospectus describes Nanjing Metro as a government-approved group that
integrates metro construction, operation, and resource development. It also
states that the projects have a public-welfare character as government
investment projects. The issuer's business is therefore not a disappearing
platform function but an ongoing urban public-infrastructure function.

Relevant extracted-text locations:

- `doc_js_nj_metro_2025_mtn2_004.txt`, lines 496-517
- `doc_js_nj_metro_2025_mtn2_004.txt`, lines 10992-10998

### Budgetary Support and Capital Injection

The same prospectus states that the municipal government allocates fiscal
subsidies each year according to metro construction progress and operating
conditions. It also states that the municipal budget provides construction
capital, operating subsidies, and other special funds. The prospectus reports
government subsidies of 50.06, 50.59, and 58.12 yi yuan in 2022, 2023, and 2024,
respectively, and later reports other income from comprehensive subsidies,
operating-loss subsidies, and security-check subsidies.

Relevant extracted-text locations:

- `doc_js_nj_metro_2025_mtn2_004.txt`, lines 501-517
- `doc_js_nj_metro_2025_mtn2_004.txt`, lines 11015-11020

### No Government Financing Function

The prospectus states that the Nanjing SASAC bears limited liability only up to
its capital contribution, that the relevant debts are repaid by the local SOE as
an independent legal person, that the company does not undertake government
financing functions, and that new debt after January 1, 2015 is not local
government debt.

Relevant extracted-text location:

- `doc_js_nj_metro_2025_mtn2_004.txt`, lines 1103-1110

### No New Government or Hidden Debt

The 2025 MTN proceeds are used to repay an existing debt-financing instrument,
not to finance a new non-operating public-welfare project. The prospectus
states that the issue will not increase government debt, will not involve false
debt resolution or new hidden local government debt, will not be transferred to
government or fiscal use, and will not be directly repaid with fiscal funds.
The legal opinion repeats this compliance position and concludes that the MTN is
the issuer's own repayment responsibility and will not increase government debt
or hidden debt.

Relevant extracted-text locations:

- `doc_js_nj_metro_2025_mtn2_004.txt`, lines 904-990
- `doc_js_nj_metro_2025_mtn2_002.txt`, lines 64-64
- `doc_js_nj_metro_2025_mtn2_002.txt`, lines 113-118

### Regulated Project Structure

The prospectus states that Nanjing Metro Line 5 uses a concession-right PPP
model and that the project was entered into the National Development and Reform
Commission's national major construction project database. It also says that,
apart from self-built projects, the remaining projects are financed and built by
PPP project companies established by the issuer and social capital, and that
these project-company debts do not constitute the issuer's own debt or appear in
the issuer's consolidated financial statements. The text further states that the
issuer has no government investment fund, BT, repurchase-of-other-entities'
projects, government-purchase-of-service, or government advance-financing
arrangements.

Relevant extracted-text locations:

- `doc_js_nj_metro_2025_mtn2_004.txt`, lines 1116-1131
- `doc_js_nj_metro_2025_mtn2_002.txt`, lines 98-98

### Continuing Financing Need

The prospectus still describes large ongoing capital needs. In-progress rail
projects have project capital mainly from city- and district-level fiscal funds
and demolition funds, with subsequent financing mainly from syndicated loans and
similar financing. The document also reports that ongoing metro projects
increase the company's financing needs and that shareholder capital injections
help keep the asset-liability ratio stable.

Relevant extracted-text locations:

- `doc_js_nj_metro_2025_mtn2_004.txt`, lines 2917-2919
- `doc_js_nj_metro_2025_mtn2_004.txt`, lines 10855-10891

## Coding Implication

The case should remain a candidate evidence packet rather than a final label.

The strongest current interpretation is that Nanjing Metro is a
formal-fiscal-substitution boundary case. It provides strong evidence that
public infrastructure financing can continue through a formal SOE, explicit
budgetary support, project capital, subsidies, PPP structures, and regulated
corporate debt while the issuer denies government financing functions and
local-government debt responsibility. It does not yet provide direct evidence
that a named LGFV officially exited or that a former LGFV's functions were
substantively removed.

For the paper, the case is useful as a guardrail. It should prevent the coding
scheme from classifying every subsidized infrastructure SOE as a failed LGFV
exit. The relevant validation question is narrower: whether a city uses formal
budgetary and SOE instruments to replace informal platform financing after LGFV
exit, and whether this replacement is attached to the same platform or to a
separate specialized infrastructure SOE.
