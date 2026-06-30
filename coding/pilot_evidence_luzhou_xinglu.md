# Pilot Evidence Packet: Luzhou Xinglu

## Case Summary

- Case ID: `pilot_sc_003`
- Company: Luzhou Xinglu Investment Group Co., Ltd.
  (`泸州市兴泸投资集团有限公司`)
- Status: human-validated evidence packet
- Final coding: `nominal_exit`
- Confidence: medium
- Main source page: Shanghai Clearing House,
  `泸州市兴泸投资集团有限公司2023年度第一期中期票据发行文件`,
  2023-01-09
- Source inventory rows: `src_sc_lz_xinglu_000`, `src_sc_lz_xinglu_001`,
  `src_sc_lz_xinglu_002`, `src_sc_lz_xinglu_003`,
  `src_sc_lz_xinglu_004`, `src_sc_lz_xinglu_005`

## Why This Case Matters

Luzhou is in the low historical-capacity bin in the current candidate list.
It is useful because it adds a western prefecture case outside Guizhou and
outside the most severe debt-resolution examples. The case therefore helps
separate weak-capacity platform persistence from the more extreme Zunyi and
Liupanshui cases.

The case is now treated as a medium-confidence validated label. The source
packet does not contain an independent exit-list notice, but the 2018 and 2023
prospectuses both state that the issuer does not undertake government financing
functions and that post-2015 new debt is not local government debt. These
formal compliance statements coexist with a long record showing that the same
issuer remains the city's infrastructure investment body, uses self-raised and
external financing for government-designated projects, receives fiscal
subsidies and financing-interest subsidies, and carries large project
receivables from entrusted construction. This combination is coded as nominal
exit rather than substantive exit.

## Machine-Readable Documents

The 2023 Shanghai Clearing disclosure page lists eight downloadable documents.
Seven produced machine-readable text:

- `doc_sc_lz_xinglu_2023_mtn1_001`: legal opinion, 28 pages, 24,366
  extracted characters
- `doc_sc_lz_xinglu_2023_mtn1_002`: 2020 audited financial report, 141 pages,
  139,519 extracted characters
- `doc_sc_lz_xinglu_2023_mtn1_003`: 2022 tracking rating report, 28 pages,
  44,197 extracted characters
- `doc_sc_lz_xinglu_2023_mtn1_004`: 2019 audited financial report, 143 pages,
  137,218 extracted characters
- `doc_sc_lz_xinglu_2023_mtn1_005`: 2021 audited financial report, 152 pages,
  6,254 extracted characters
- `doc_sc_lz_xinglu_2023_mtn1_007`: 2023 first MTN prospectus, 243 pages,
  209,608 extracted characters
- `doc_sc_lz_xinglu_2023_mtn1_008`: issuance plan and commitment letter, 26
  pages, 10,682 extracted characters

The 2022 third-quarter financial statement downloaded successfully but produced
no machine-readable text with the current extractor.

The 2018 Shanghai Clearing disclosure page adds an older cross-time source.
Two documents have been downloaded and extracted:

- `doc_sc_lz_xinglu_2018_mtn1_rating`: 2018 first MTN credit rating report,
  35 pages, 52,629 extracted characters
- `doc_sc_lz_xinglu_2018_mtn1_prospectus`: 2018 first MTN prospectus, 198
  pages, 231,723 extracted characters

The 2015 ChinaBond enterprise-bond disclosure page adds an earlier source
close to the post-2014 local-debt reform period:

- `doc_sc_lz_xinglu_2015_bond_prospectus`: 2015 enterprise-bond prospectus,
  117 pages, 84,388 extracted characters
- `doc_sc_lz_xinglu_2015_bond_prospectus_summary`: 2015 enterprise-bond
  prospectus summary, 90 pages, 59,453 extracted characters

The remaining 2015 ChinaBond attachments are recorded in
`data/document_inventory.csv`, but the current coding evidence relies on the
full prospectus and the prospectus summary.

The 2017 Shanghai Clearing disclosure page and 2021 tracking-rating disclosure
add two intermediate source points:

- `doc_sc_lz_xinglu_2017_mtn1_prospectus`: 2017 first MTN prospectus, 204
  pages, 231,866 extracted characters
- `doc_sc_lz_xinglu_2017_mtn1_rating`: 2017 first MTN credit rating report,
  37 pages, 54,977 extracted characters
- `doc_sc_lz_xinglu_2021_tracking_rating`: 2021 tracking rating report, 31
  pages, 44,323 extracted characters

## Evidence Themes

### Municipal Infrastructure Role

The 2015 enterprise-bond prospectus states that Xinglu's business included
investment in energy, transportation, infrastructure, pillar industries, and
high-technology industries; investment and financing; and information
consulting and entrusted agency services for development construction and
investment management. It also states that the firm was created by the Luzhou
municipal government, initially funded by the Luzhou Finance Bureau, and later
placed under Luzhou SASAC.

Relevant extracted-text location:

- `doc_sc_lz_xinglu_2015_bond_prospectus.txt`, lines 579-604

The prospectus states that Xinglu was approved by the Luzhou municipal
government, initially funded by the Luzhou Finance Bureau, and later placed
under Luzhou SASAC. It then defines the firm as the Luzhou government's
operating body for urban infrastructure investment and financing, construction
management, and state-asset operation.

Relevant extracted-text location:

- `doc_sc_lz_xinglu_2023_mtn1_007.txt`, lines 858-862

The 2018 prospectus uses the same institutional definition. It states that the
firm was founded by the Luzhou Finance Bureau and became a Luzhou SASAC firm in
2006. It then describes Xinglu as the Luzhou government's operating body for
urban infrastructure investment and financing, construction management, and
state-asset operation.

Relevant extracted-text location:

- `doc_sc_lz_xinglu_2018_mtn1_prospectus.txt`, lines 2888-2906

The tracking rating report uses a similar formulation. It describes Xinglu as
Luzhou's most important urban infrastructure construction and state-asset
management operating body, and it says that the company continued to receive
government support during the tracking period.

Relevant extracted-text locations:

- `doc_sc_lz_xinglu_2023_mtn1_003.txt`, lines 83-110
- `doc_sc_lz_xinglu_2023_mtn1_003.txt`, lines 817-824
- `doc_sc_lz_xinglu_2018_mtn1_rating.txt`, lines 700-735

The 2017 prospectus and rating report show that this institutional role
predates the 2018 no-government-financing language. The 2017 prospectus
describes Xinglu as the Luzhou government's operating body for urban
infrastructure investment and financing, construction management, and
state-asset operation. The 2017 rating report likewise describes the company
as the municipal government's infrastructure investment-financing,
construction-management, and state-asset operating body.

Relevant extracted-text locations:

- `doc_sc_lz_xinglu_2017_mtn1_prospectus.txt`, lines 3776-3795
- `doc_sc_lz_xinglu_2017_mtn1_rating.txt`, lines 742-760

### 2015 Platform-Function Baseline

The 2015 enterprise-bond prospectus gives a clear pre-2018 baseline. It states
that Xinglu was the main investment and financing body and construction body
for Luzhou infrastructure projects. It reports that the company undertook a
large number of urban infrastructure, affordable-housing, and municipal public
facility projects, and that these projects mainly obtained returns through
government subsidies and project operations.

Relevant extracted-text location:

- `doc_sc_lz_xinglu_2015_bond_prospectus.txt`, lines 1503-1508

The same prospectus states that Xinglu pursued a `投、融、建、管` operating
mechanism and should give full play to government investment-financing,
construction-management, and state-asset-management functions.

Relevant extracted-text location:

- `doc_sc_lz_xinglu_2015_bond_prospectus.txt`, lines 1525-1530

The 2015 balance-sheet evidence is also important. The prospectus reports that
other receivables were mainly infrastructure entrusted-construction payments
owed by the Luzhou Finance Bureau. It then lists large receivables from the
finance bureau for project principal and interest, district construction
projects, infrastructure development funds, bank-loan principal, policy-bank
loan interest, fiscal temporary borrowing, and treasury-bond on-lending
principal and interest.

Relevant extracted-text location:

- `doc_sc_lz_xinglu_2015_bond_prospectus.txt`, lines 1695-1731

For public-welfare projects, the prospectus states that financing principal,
interest, and investment returns were to be repaid through annual subsidies
from the Luzhou government. For the central-city shantytown redevelopment
project, Xinglu's subsidiary signed a BT agreement with the Luzhou municipal
government using an enterprise-investment and government-repurchase model, with
repurchase payments planned from 2015 through 2024.

Relevant extracted-text locations:

- `doc_sc_lz_xinglu_2015_bond_prospectus.txt`, lines 1899-1904
- `doc_sc_lz_xinglu_2015_bond_prospectus.txt`, lines 2601-2608
- `doc_sc_lz_xinglu_2015_bond_prospectus.txt`, lines 3120-3134

Finally, the 2015 prospectus incorporates a rating conclusion that calls Xinglu
an important Luzhou investment-financing platform that undertook major project
development, construction, operation, and service responsibilities. This is
useful because it gives a market-facing description of the issuer before the
2018 and 2023 compliance-language sources.

Relevant extracted-text location:

- `doc_sc_lz_xinglu_2015_bond_prospectus.txt`, lines 3385-3389

### Compliance Language

The prospectus contains explicit post-2014 compliance language. It states that
the MTN proceeds will not add local government debt, will not involve false
hidden-debt resolution or new hidden debt, will not be transferred to
government or fiscal use, and will not be repaid directly by fiscal funds. It
also excludes uses such as land primary development, affordable housing, and
shantytown redevelopment.

Relevant extracted-text location:

- `doc_sc_lz_xinglu_2023_mtn1_007.txt`, lines 761-790

The same prospectus later states that the issuer does not borrow for local
governments or provide guarantees for them. After consultation with the local
finance department, the document says that the issuer will not increase local
government debt or hidden debt, that the SASAC shareholder has limited
liability, and that the firm does not undertake government financing functions.
It further states that new debt after January 1, 2015 is not local government
debt.

Relevant extracted-text location:

- `doc_sc_lz_xinglu_2023_mtn1_007.txt`, lines 902-908

The 2018 prospectus already used the same post-2015 formulation. It states
that the issuer does not undertake government financing functions, that new
debt after January 1, 2015 is not local government debt, that the debt will not
increase the scale of government debt, and that the government will not repay
the debt directly with fiscal funds.

Relevant extracted-text location:

- `doc_sc_lz_xinglu_2018_mtn1_prospectus.txt`, lines 2770-2817

Keyword search in the extracted 2015 prospectus did not find direct language
that Xinglu had exited a financing-platform list or had been approved to leave
platform management. The 2015 source therefore strengthens the baseline
platform-function evidence but does not by itself solve the formal-exit-event
problem.

### Continuing Project Finance Function

The prospectus states that Xinglu is the investment body for municipal
infrastructure construction. Its infrastructure operation model is government
entrusted construction. The firm serves as project owner for government-
designated infrastructure projects, raises funds through its own resources and
external financing, and is compensated by the government through entrusted-
construction agreements. The compensation covers financing principal and
interest and can also include investment returns or equity-asset transfers.

Relevant extracted-text location:

- `doc_sc_lz_xinglu_2023_mtn1_007.txt`, lines 2384-2403

The same section enumerates three forms of compensation. First, Xinglu can
recognize investment income according to project agreements. Second, it can
receive government subsidies for infrastructure construction, including
subsidies that offset financing expenses. Third, it can receive project
repurchase payments during construction or after final settlement.

Relevant extracted-text location:

- `doc_sc_lz_xinglu_2023_mtn1_007.txt`, lines 2404-2414

The 2018 prospectus contains an earlier version of the same project-finance
arrangement. It states that Xinglu is the municipal infrastructure investment
body, that its infrastructure operation model is government entrusted
construction, that it invests in government-designated infrastructure projects
with self-owned and external financing, and that the government compensates
construction financing principal, interest, and investment returns through
entrusted-construction agreements. It further states that project repurchase
payments and project subsidies are used in settlement, and that some entrusted
projects without investment returns receive fiscal subsidies.

Relevant extracted-text location:

- `doc_sc_lz_xinglu_2018_mtn1_prospectus.txt`, lines 9984-10094

The 2017 prospectus provides an even earlier version of the same mechanism.
It records large fiscal and project-linked liabilities and receivables,
including treasury-bond on-lending funds from the Luzhou Finance Bureau,
policy-finance and fund investments in shantytown and infrastructure projects,
and government commitments to arrange fiscal-budget funds for repurchase of
development-fund equity.

Relevant extracted-text locations:

- `doc_sc_lz_xinglu_2017_mtn1_prospectus.txt`, lines 5880-5940
- `doc_sc_lz_xinglu_2017_mtn1_prospectus.txt`, lines 7018-7036

### Entrusted Construction and Receivables

The prospectus states that some entrusted projects are owned by Xinglu and
some are not. For projects not owned by the firm, the document says that
Xinglu is responsible for the financing function, records the project spending
as long-term receivables, and settles project funds through government
repurchase payments or final fiscal settlement. This is important because it
shows that the functional question cannot be answered by the formal compliance
sentence alone.

Relevant extracted-text location:

- `doc_sc_lz_xinglu_2023_mtn1_007.txt`, lines 2420-2494

The tracking rating report makes the same point more directly. It states that
the infrastructure construction business does not recognize revenue, that
project repayments were ordinary rather than strong, and that projects whose
owner is not the company are recorded as long-term receivables. It also states
that, for those projects, the company is responsible only for the financing
function.

Relevant extracted-text location:

- `doc_sc_lz_xinglu_2023_mtn1_003.txt`, lines 900-930

The 2021 tracking rating report confirms that the same accounting and
functional pattern existed between the 2018 and 2023 source sets. It states
that Xinglu's infrastructure construction business used government-entrusted
construction, that projects for which the company was not the owner were
recorded as long-term receivables because the company was responsible for the
financing function, and that completed projects had received only partial
repayment. The report also states that 2020 other receivables mainly consisted
of receivables from government agencies and related parties, and that long-term
receivables mainly reflected infrastructure projects for which the company was
not the owner, relocation-poverty-alleviation projects, and shantytown
redevelopment investment.

Relevant extracted-text locations:

- `doc_sc_lz_xinglu_2021_tracking_rating.txt`, lines 884-928
- `doc_sc_lz_xinglu_2021_tracking_rating.txt`, lines 1332-1382

### Fiscal Dependence and Debt Pressure

The prospectus identifies fiscal support as part of the issuer's repayment
capacity. It states that the Luzhou government provides subsidies for financing
interest, infrastructure construction, and public-utility losses. In 2019,
2020, and 2021, the issuer received RMB 973.8065 million, RMB 755.1387 million,
and RMB 606.9980 million in government subsidies.

Relevant extracted-text location:

- `doc_sc_lz_xinglu_2023_mtn1_007.txt`, lines 814-824

The same prospectus lists several risks that matter for coding. First, the
issuer had twelve main projects under construction or planned as of March 2022,
with RMB 5.257 billion still to be invested. Second, the issuer had RMB
40.357 billion in interest-bearing debt. Third, long-term receivables were
mainly generated by entrusted construction projects and occupied substantial
funds. Fourth, part of the affordable-housing business had a negative gross
margin because price-limited resettlement sales were compensated by fiscal
subsidies.

Relevant extracted-text location:

- `doc_sc_lz_xinglu_2023_mtn1_007.txt`, lines 330-386

The tracking rating report also notes a weak local fiscal environment. It
reports that Luzhou's 2021 fiscal self-sufficiency rate was 42.89 percent and
describes the city's fiscal self-sufficiency as relatively low.

Relevant extracted-text location:

- `doc_sc_lz_xinglu_2023_mtn1_003.txt`, lines 804-815

The 2018 rating report shows that this fiscal linkage was not new in 2023. It
states that Xinglu was Luzhou's largest platform company, that its main
business and revenue depended on the local government, and that it received
support through asset injections and fiscal subsidies. It reports that from
2015 to 2017 the Luzhou government injected RMB 5.998 billion for subsidiaries
and entrusted-construction project subsidies, transferred major assets to the
firm, and provided annual fiscal subsidies including bond issuance-fee and
interest subsidies.

Relevant extracted-text location:

- `doc_sc_lz_xinglu_2018_mtn1_rating.txt`, lines 756-803

## Validation Decision

The case is coded as `nominal_exit` at medium confidence.

The evidence supports three claims. First, Xinglu is a platform-like municipal
entity: both the prospectus and the tracking rating report define it as a key
Luzhou infrastructure and state-asset operating body. Second, the issuer uses
formal compliance language: the 2018 and 2023 prospectuses state that the bond
does not add local government debt or hidden debt and that the company does not
undertake government financing functions after 2015. Third, the same documents
show continuing public-project and project-finance functions: Xinglu raises
funds for government-designated infrastructure projects, receives fiscal
subsidies and financing-interest subsidies, records entrusted-construction
receivables, and participates in shantytown and infrastructure projects.

The 2018 source set strengthens the case because it shows that this combination
of claims predates the 2023 issuance. In 2018, the issuer already stated that it
did not undertake government financing functions after 2015, while the same
source set described Xinglu as the city's largest platform company and as a
government-designated infrastructure investment body supported through asset
injections, project subsidies, and financing-interest subsidies.

The 2017 and 2021 source sets make the cross-time pattern more continuous. In
2017, the issuer was still described as a municipal infrastructure
investment-financing and construction-management body, with fiscal receivables,
project-fund repayment, and government-backed repurchase arrangements. In 2021,
the rating report still described government-entrusted infrastructure
construction, long-term receivables for projects where the issuer performed
the financing function, and continuing government support. Neither source
contains direct `退出融资平台` or `退出平台名单` language.

The 2015 ChinaBond source set pushes the functional baseline further back. The
2015 prospectus identifies Xinglu as Luzhou's infrastructure project
investment-financing and construction body, records infrastructure
entrusted-construction receivables from the Luzhou Finance Bureau, describes
public-welfare project financing as repaid through annual government subsidies,
and documents a shantytown BT project with planned government repurchase
payments. It does not contain direct `退出融资平台` or `退出平台名单` language.

The main alternative label is `substantive_exit`. The issuer repeatedly states
that new debt is not local government debt and that the bond proceeds do not
add hidden debt. The final label remains nominal exit because the same source
packet documents continued project-finance functions after the compliance
point. The 2023 prospectus says that Xinglu serves as project owner for
government-designated infrastructure projects, raises funds through its own
resources and external financing, and receives compensation through entrusted
construction agreements. The rating evidence also states that, for projects
not owned by the firm, Xinglu is responsible for the financing function and
records project spending as long-term receivables.

Source coverage score: 4. The packet contains cross-time prospectuses, rating
reports, and financial reports from 2015, 2017, 2018, 2021, and 2023. Confidence
should rise only if a government or regulator document directly confirms an
exit-list event or a local platform-management decision.
