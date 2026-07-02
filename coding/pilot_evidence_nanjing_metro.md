# Pilot Evidence Packet: Nanjing Metro

## Case Summary

- Case ID: `pilot_js_001_alt_metro`
- Company: Nanjing Metro Group Co., Ltd. (`南京地铁集团有限公司`)
- Current status: human-validated gold label
- Final label: `nominal_exit`
- Confidence: medium
- Main source page: Shanghai Clearing House,
  `南京地铁集团有限公司2025年度第二期中期票据发行文件`, 2025-06-17
- Source inventory rows: `src_js_nj_001`, `src_js_nj_002`

## Why This Case Matters

Nanjing is one of the highest historical elite-density cities in the current
candidate pool. Nanjing Metro is a specialized municipal rail infrastructure
SOE rather than a generic city-investment platform, but the source packet gives
direct evidence on both sides of the paper's coding rule. The issuer states
that it does not undertake government financing functions and that post-2015
debt is not local-government debt. At the same time, the same disclosure packet
shows that the company continues to house the city's urban rail investment,
construction, operation, resource-development, fiscal-support, and debt-finance
functions.

The case therefore helps discipline the boundary between substantive exit and
nominal exit. A narrow legal reading would treat the compliance language as
evidence that the issuer is no longer a government financing vehicle. The
paper's measurement framework asks a different question: whether the public
infrastructure finance function disappears, moves, or remains in the same
issuer group. On that criterion, Nanjing Metro is coded as nominal exit.

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

### Formal No-Government-Financing Language

The prospectus states that Nanjing SASAC bears limited shareholder liability,
that the relevant debt is repaid by the local SOE as an independent legal
person, that the company does not undertake government financing functions, and
that new debt after January 1, 2015 is not local-government debt.

Relevant extracted-text location:

- `doc_js_nj_metro_2025_mtn2_004.txt`, lines 1103-1110

The prospectus also states that the 2025 MTN proceeds are used to repay an
existing debt-financing instrument. The proceeds are not to be transferred to
government or fiscal use, and the government will not repay the instrument
directly with fiscal funds. The legal opinion repeats the same compliance
position and concludes that the issue will not increase government debt or
hidden debt.

Relevant extracted-text locations:

- `doc_js_nj_metro_2025_mtn2_004.txt`, lines 904-990
- `doc_js_nj_metro_2025_mtn2_002.txt`, lines 64-64
- `doc_js_nj_metro_2025_mtn2_002.txt`, lines 113-118

### Continued Rail-Infrastructure Function

The prospectus describes the issuer as a government-approved company that
integrates metro construction, operation, and resource development. It also
states that the projects are government investment projects with a public
welfare character. Later sections describe the issuer as the leading enterprise
for Nanjing urban rail transit projects and as holding a monopoly position in
urban rail construction, operation, and management.

Relevant extracted-text locations:

- `doc_js_nj_metro_2025_mtn2_004.txt`, lines 496-517
- `doc_js_nj_metro_2025_mtn2_004.txt`, lines 10992-10998
- `doc_js_nj_metro_2025_mtn2_002.txt`, lines 69-69

### Fiscal Absorption and Subsidy Support

The same prospectus states that the municipal government allocates fiscal
subsidies each year according to metro construction progress and operating
conditions. It reports government subsidies of 50.06, 50.59, and 58.12 yi yuan
in 2022, 2023, and 2024. It also states that the annual fiscal budget provides
construction capital, operating subsidies, and other special funds. Other-income
items include comprehensive subsidies, operating-loss subsidies, and
security-check subsidies.

Relevant extracted-text locations:

- `doc_js_nj_metro_2025_mtn2_004.txt`, lines 501-517
- `doc_js_nj_metro_2025_mtn2_004.txt`, lines 11015-11020

### Project Finance and Debt-Finance Continuity

In-progress rail projects have project capital mainly from city- and
district-level fiscal funds and demolition funds, while later project financing
comes mainly from syndicated loans and similar debt financing. The prospectus
also reports that ongoing metro construction increases the company's financing
needs, that financing cash inflows mainly reflect fiscal funds and bank
borrowing, and that shareholder capital injections help keep leverage stable.

Relevant extracted-text locations:

- `doc_js_nj_metro_2025_mtn2_004.txt`, lines 2917-2919
- `doc_js_nj_metro_2025_mtn2_004.txt`, lines 10852-10864
- `doc_js_nj_metro_2025_mtn2_004.txt`, lines 10888-10891
- `doc_js_nj_metro_2025_mtn2_002.txt`, lines 103-103

### Regulated Project Structure

The prospectus and legal opinion provide negative evidence that matters for the
alternative label. Nanjing Metro Line 5 uses a concession-right PPP model and
was entered into the National Development and Reform Commission's major
construction project database. The source packet states that the issuer has no
BT, government-purchase-service, government-investment-fund, project repurchase,
or government advance-financing arrangements. It also states that government
receivables have normal business backgrounds and that the Nanjing Finance
Bureau was consulted on these compliance statements.

Relevant extracted-text locations:

- `doc_js_nj_metro_2025_mtn2_004.txt`, lines 1114-1131
- `doc_js_nj_metro_2025_mtn2_002.txt`, lines 98-118

## Coding Implication

The final label is `nominal_exit`.

The formal event is strong enough for the gold-standard file because the
prospectus contains direct post-2015 no-government-financing and
no-local-government-debt language, and the legal opinion confirms that the
current debt instrument does not create new government or hidden debt. The
continued-function evidence is also strong. The same issuer remains the city's
main rail-transit investment, construction, operation, and resource-development
company. Project capital comes from city and district fiscal funds and
demolition funds. Follow-on financing depends on syndicated loans and other
debt financing. The issuer receives large fiscal subsidies and shareholder
capital support.

The most plausible alternative label is `substantive_exit`. That reading would
emphasize the legal evidence that the issuer has no BT, government purchase
service, government project advance-financing, illegal guarantee, fiscal direct
repayment, land-reserve financing, or hidden-debt arrangement. The final label
remains nominal because the same issuer still contains the specialized municipal
rail infrastructure finance function. This case should be read alongside
Guangzhou Metro as evidence that high-capacity cities can formalize rail
finance without making the infrastructure-finance function disappear.

The case carries a medium confidence score because it is a specialized metro
platform rather than a generic city-investment company, and because the formal
event is based on prospectus and legal-opinion compliance language rather than
an independently retrieved platform-list exit notice.
