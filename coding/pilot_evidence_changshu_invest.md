# Pilot Evidence Packet: Changshu Investment Holding Group

## Case Summary

- Case ID: `expand_js_changshu_invest`
- Company: Changshu Investment Holding Group Co., Ltd.
  (`常熟市投资控股集团有限公司`)
- Status: human-validated evidence packet
- Final coding: `functional_transfer`
- Confidence: medium
- Main source page: Shanghai Clearing House,
  `常熟市投资控股集团有限公司2026年度第三期中期票据发行文件`,
  2026-06-25
- Source inventory row: `src_js_changshu_invest_001`

## Why This Case Matters

This case is useful because it is not a simple disappearance story. The issuer
still has public functions. Its business includes affordable housing, market
development, grain procurement, equity investment, and policy-linked services.
It also receives fiscal subsidies and has large receivables from government
agencies, public institutions, and local state-owned enterprises.

At the same time, the documents distinguish these continuing public functions
from classic platform financing. The issuer says it has stripped government
financing functions and become a market-oriented entity. The legal opinion and
prospectus state that the issuer does not conduct land development or land
reserve financing, does not participate in PPP, government investment funds,
BT, repurchase of other entities' projects, government-purchase-service
projects, or advance financing for government projects. This makes the case
closer to functional transfer than to pure nominal exit.

## Machine-Readable Documents

The useful local text extractions are:

- `doc_js_changshu_invest_2026_mtn3_001`: 2026 third MTN prospectus, 216 pages,
  277,577 extracted characters
- `doc_js_changshu_invest_2026_mtn3_002`: legal opinion, 50 pages, 43,873
  extracted characters

## Evidence Themes

### Formal Exit Language and State-Capital Ownership

The prospectus states that the issuer has stripped government financing
functions and transformed into a market-oriented entity that operates and bears
risk independently. The legal opinion shows that, in 2021, the issuer's entire
equity was transferred to Changshu State Capital Investment and Operation Group.
It also records the 2025 name change to Changshu Investment Holding Group.

Relevant extracted-text locations:

- `doc_js_changshu_invest_2026_mtn3_001.txt`, lines 18-21
- `doc_js_changshu_invest_2026_mtn3_002.txt`, lines 363-375
- `doc_js_changshu_invest_2026_mtn3_002.txt`, lines 381-384

### Continuing Public Functions

The issuer still performs policy-linked functions. Its registered business
scope includes investment in transportation, energy, urban infrastructure,
other industrial infrastructure, market development, and market support
services. The prospectus identifies leasing, affordable housing, and grain
procurement as main businesses. Affordable housing is policy-sensitive and
supported by the local government, while grain procurement is a policy-linked
business. The firm also receives fiscal subsidies tied to business and project
conditions.

Relevant extracted-text locations:

- `doc_js_changshu_invest_2026_mtn3_001.txt`, lines 523-532
- `doc_js_changshu_invest_2026_mtn3_001.txt`, lines 549-553
- `doc_js_changshu_invest_2026_mtn3_001.txt`, lines 655-662
- `doc_js_changshu_invest_2026_mtn3_001.txt`, lines 731-732
- `doc_js_changshu_invest_2026_mtn3_001.txt`, lines 1156-1175
- `doc_js_changshu_invest_2026_mtn3_002.txt`, lines 157-160

### Negative Functional List and Fiscal Normalization

The strongest evidence for functional transfer is the unusually explicit
negative list. The issuer and legal opinion state that the company does not
undertake land development or land reserve financing, does not participate in
PPP, government investment funds, BT, project repurchase, government purchase
services, or advance financing for government projects, and does not create
debts requiring fiscal repayment through public-interest projects or land
整理. Government receivables are described as having operating backgrounds and
not increasing government debt.

Relevant extracted-text locations:

- `doc_js_changshu_invest_2026_mtn3_001.txt`, lines 1172-1175
- `doc_js_changshu_invest_2026_mtn3_001.txt`, lines 6509-6528
- `doc_js_changshu_invest_2026_mtn3_002.txt`, lines 1802-1821

### Remaining Government Linkages

The case is not substantive exit. The issuer reports large other receivables,
with debtors mainly government agencies, public institutions, or local SOEs. It
also receives fiscal subsidies for grain procurement, venture investment,
high-tech industrial investment, apparel-market operations, and logistics.
These ties show that public functions remain inside the group, even if the old
financing-platform channel is formally narrowed.

Relevant extracted-text locations:

- `doc_js_changshu_invest_2026_mtn3_001.txt`, lines 464-475
- `doc_js_changshu_invest_2026_mtn3_001.txt`, lines 529-532
- `doc_js_changshu_invest_2026_mtn3_001.txt`, lines 6509-6523

## Validation Decision

The case is coded as `functional_transfer` at medium confidence.

It is not a substantive exit because the issuer still handles public and
policy-linked functions, including affordable housing, grain procurement,
market operations, state-capital investment, and government-linked receivables.
It is also not best read as pure nominal exit because the documents provide
specific evidence that several classic LGFV functions have been excluded or
normalized. Land reserve financing, land development, BT, PPP, government
purchase service, project repurchase, and government-project advance financing
are all explicitly rejected.

The main alternative label is `nominal_exit`. That label would become stronger
if later evidence shows that affordable housing or infrastructure investment is
still financed through the issuer in a way similar to the old platform model.
The current evidence instead points to a rechanneling of public functions
through policy business, state-capital ownership, and operating receivables.

Source coverage score: 3. Confidence should rise only after collecting a rating
report or local government document that independently explains how Changshu
shifted the issuer away from government financing while retaining affordable
housing, grain, market, and investment functions.
