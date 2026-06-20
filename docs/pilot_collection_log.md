# Pilot Collection Log

## 2026-06-20

The first collection pass searched for platform-level source material for the
initial eight-city pilot. The in-app browser automation interface was not
available, so the search was conducted through web search and direct page
inspection.

The first pass found three usable official sources.

First, Guangzhou has a usable company source. The Guangzhou City Construction
Investment Group website describes the group as a wholly municipal functional
state-owned enterprise engaged in urban infrastructure investment, financing,
construction, operation, and management. This source is useful for identifying
the company as a relevant platform case, but it is not sufficient for assigning
an exit type. The next source should be a bond prospectus or credit rating
report.

Second, Chengdu has a usable company source. The Chengdu City Construction
Investment Management Group website describes the group as a municipal
state-owned enterprise focused on government-related major municipal projects
and market-oriented urban comprehensive development projects, with business
segments including infrastructure construction, urban comprehensive
development, urban operation services, urban industry investment, and smart
city construction. This source is useful for identifying the company and its
pre-exit function. The next source should be a bond prospectus or credit rating
report.

Third, Shenzhen has a usable government source. The Shenzhen SASAC page for
Shenzhen Special Zone Construction and Development Group describes the group as
a municipal comprehensive investment and financing platform company and as an
infrastructure investment, construction, and operation platform. This is a
strong source for platform identification. The next source should be bond or
rating disclosure material that indicates whether the group continues to
perform government financing functions after official exit or transformation.

No final exit labels are assigned in this collection pass. The current output is
source discovery only.

## 2026-06-20, follow-up search

The second search pass tried to move from company identification to bond and
rating documents.

First, the Shanghai Stock Exchange bond announcement page was inspected. Its
public page loads company bond announcements through `query.sse.com.cn` with
`sqlId = BS_ZQ_GGLL`. The relevant announcement categories include `1601` for
rating announcements and `1105` for issuance documents. A test query for
Guangzhou City Construction Investment Group using both the full company name
and the shorter keyword `广州城投` returned no records for 2023-01-01 to
2026-06-20 under the company/corporate bond bulletin categories. This does not
mean that the company has no bonds; it only means that this SSE route did not
find useful documents in this query.

Second, the NAFMII disclosure page was inspected. The page uses JavaScript and
WAF verification before loading the disclosure interface. For this reason, it
is not a good target for command-line collection in the current environment.
The project should use the website manually, use another accessible disclosure
portal, or rely on commercial databases if available.

Third, broad web search for exact company names plus `募集说明书` and
`跟踪评级报告` did not yet produce stable official documents for the three
started cases. The next collection pass should try ChinaBond's bond search,
company websites' disclosure sections, local SASAC pages, and issuer-specific
searches using bond abbreviations rather than only company names.

## 2026-06-20, ChinaBond bond-code search

The third search pass used ChinaBond's public bond query page. The page exposes
a JSON endpoint at `/cbiw/GetBase/bondSimpleQueryForChinese`. The query accepts
`bondCode`, `bondNameAbbr`, `bondFeatureNo`, `issueDate`, `pageSize`, and
`pageNum`.

Queries for `广州城投`, `成都城投`, and `特区建发` returned only the aggregate
row and no bond-level records. Queries for `深圳地铁集团`, `成都轨道`, and
`成都轨交` also returned no bond-level records. These non-hits should not be
interpreted as evidence that the companies have no debt; they only indicate
that these exact bond-abbreviation queries did not find records in ChinaBond.

The query `广州地铁` returned eight bond-level records for Guangzhou Metro Group
or its issuer abbreviation `广州地铁`: `14广州地铁债01` (`1480169`),
`14广州地铁债02` (`1480347`), `14广州地铁债03` (`1480443`),
`16广州地铁可续期债01` (`1680052`), `16广州地铁专项债01` (`1680227`),
`16广州地铁可续期债02` (`1680303`), `16广州地铁可续期债03` (`1680325`), and
`17广州地铁专项债01` (`1780204`). These records are stored in
`data/bond_inventory.csv`.

This creates an alternative Guangzhou platform candidate. The original
Guangzhou City Construction Investment Group case remains in the candidate plan
because its official company profile identifies infrastructure investment and
financing functions. However, if no bond or rating documents can be found for
that company, Guangzhou Metro Group may be a more feasible pilot case for
testing the coding workflow.

The same ChinaBond endpoint produced additional useful pilot records. The query
`南京地铁` returned six bond-level records for Nanjing Metro, all local
enterprise bonds with AAA ratings in the ChinaBond metadata. The query
`苏州城投` returned two records: `12苏州城投债` and `G22苏州城投资本01`. The
query `遵义道桥` returned two records: `12遵义道桥债` and `15遵义道桥债`.
These records were added to `data/bond_inventory.csv` and source rows were
added to `data/source_inventory.csv`.

The next step is to use these bond codes and bond abbreviations to locate the
original issuance documents, follow-up rating reports, annual reports, and major
event announcements. Bond metadata alone is not enough to classify exit type,
but it gives stable issuer names, bond abbreviations, and bond codes for source
collection.

## 2026-06-20, Shanghai Clearing document source

The fourth search pass found the first complete issuer document set for the
pilot. Shanghai Clearing House has a disclosure page titled `广州地铁集团有限公司2025年度第一期中期票据发行文件(更新)`,
dated 2025-05-23. The page lists ten
downloadable documents for Guangzhou Metro Group: an updated renewal
prospectus, a base prospectus, two rating reports, three audited annual
financial reports, one quarterly financial statement, one legal opinion, and
one issuance plan or commitment document.

This source set changes the Guangzhou Metro case from bond-metadata discovery
to full-text source collection. The documents are recorded in
`data/document_inventory.csv`. They should be used before any final exit-type
label is assigned. The first documents to read are the prospectuses and rating
reports, because they are most likely to discuss current business functions,
government support, public project obligations, debt use, and whether the
issuer continues to perform quasi-fiscal infrastructure financing functions.

No final exit label is assigned at this stage. The current status is
`documents_found`, not `labeled`.

Local extraction was attempted after downloading the ten PDFs listed in
`data/document_inventory.csv`. Six documents produced usable text: the updated
renewal prospectus, legal opinion, two rating reports, base prospectus, and
issuance plan. Four accounting documents produced no text through `pypdf`: the
2024 audited report, 2023 audited report, 2025 first-quarter statements, and
2022 audited report. Those documents may require OCR if they become important
for balance-sheet evidence. For the first labeling pass, the prospectuses and
rating reports should be treated as the main machine-readable documents.

## 2026-06-20, Xi'an Hi-tech external validation case

The next search pass looked for a case with explicit platform-exit language.
Shanghai Clearing's public disclosure interface returned an issuer record for
`西安高新控股有限公司` and a 2026 sixth MTN disclosure page. The page lists ten
issuer documents, including a prospectus and a 2025 issuer rating report.

This case is useful because the prospectus states that the issuer exited the
financing-platform list in 2012, while the same source and the rating report
show continuing infrastructure construction, BT and entrusted-construction
arrangements, project repurchase by the High-tech Zone Management Committee,
and ongoing fiscal or shareholder support. This is the clearest source pattern
found so far for distinguishing official exit from substantive exit.

The case has been added as `pilot_sn_xian_hightech`, with source row
`src_sn_xa_001`. It is outside the initial eight-province pilot, so it should
be treated as an external validation case rather than part of the initial
province-stratified sample. The preliminary coding implication is
`nominal_exit`, subject to human validation and ideally one additional official
source confirming the 2012 exit event.

All ten PDFs for this disclosure page were downloaded locally. Eight produced
machine-readable text through `pypdf`: the issuance plans, legal opinion, 2025
issuer rating report, 2024 audited report, 2025 audited report, and 2026 sixth
MTN prospectus. Two accounting documents produced no text: the 2026
first-quarter statements and the 2023 audited report. The main coding evidence
comes from the 2026 prospectus and the 2025 rating report.

## 2026-06-20, Xi'an Hi-tech validation source

A follow-up search found an older Shanghai Clearing disclosure page for
`西安高新控股有限公司2020年度第一期中期票据发行披露材料`, dated 2020-03-18.
The 2020 prospectus repeats the key official-exit language: the issuer had
exited the financing-platform list in 2012 and its bank loans were converted to
ordinary issuer loans. This gives the case a second disclosure source across
time, rather than relying only on the 2026 prospectus.

The 2020 rating report also reinforces the functional evidence. It describes
the company as the key infrastructure construction body in Xi'an High-tech Zone
and states that the Management Committee authorized the company as the
financing, investment, and construction body for infrastructure projects under
BT arrangements, with project repurchase payments by the Management Committee.

A 2018 New Beijing News report, reposted by Sina, was recorded as a
supplementary source. It describes the company's infrastructure role, BT
zero-cost repurchase arrangement, government subsidies, and dependence on
public backing. Because it is a media source, it should not replace disclosure
documents for final coding, but it is useful external corroboration of the
functional interpretation.

The Xi'an Hi-tech case is now strong enough to use as the first human-validated
`nominal_exit` pilot, while recording that the official exit event is supported
by issuer disclosures and still lacks a directly retrieved government exit-list
document.

## 2026-06-20, Guangzhou City Investment second-case search

A second pilot search compared Chengdu City Investment, Hangzhou City
Investment, and Guangzhou City Construction Investment Group. Chengdu has rich
disclosure materials but appears to combine compliance language with legacy
government代建/BT evidence. Hangzhou has strong reorganization evidence,
including the integration of Qiantou Group and the creation of Hangzhou Anju
Group, making it a future functional-transfer/consolidation candidate.

Guangzhou City Construction Investment Group is the strongest immediate second
case candidate because the 2026 fourth MTN prospectus directly states that the
issuer does not undertake government financing functions and that since 2014 it
has not participated in new government-project investment and financing. The
same document describes the remaining role as fiscal-funded `代建代管`, with
public-welfare project funds coming from municipal fiscal funds and the company
receiving capped project-management fees.

Follow-up collection located three older documents: a 2018 tracking rating
report, a July 2018 planned partial debt-replacement announcement for
`14粤城建MTN001`, and an August 2018 special announcement on local government
debt replacement. The 2018 rating report already states that since 2014 the
company no longer participated in new government-project investment and
financing and instead shifted to fiscal-funded `代建代管`. The July 2018
announcement states that 1.141 billion yuan of the 2014 MTN was recognized as
government-repayment-responsibility debt and included in the 2018 fiscal budget
for replacement.

Based on these old and current sources, Guangzhou City Construction Investment
Group has been entered into `data/processed/human_validated_labels.csv` as a
medium-confidence `substantive_exit` case. It is especially useful as a contrast
with Xi'an Hi-tech because it tests whether the codebook can distinguish
continuing budgetary public-project management from continuing off-budget
government financing.

## 2026-06-20, Hangzhou functional-transfer case

The third pilot case focuses on Hangzhou City Investment Group. Shanghai
Clearing materials for the 2024 first MTN include a prospectus and issuer rating
report. The prospectus records the 2022 municipal decision to integrate
Hangzhou City Investment and Qiantou Group into a new city-investment group and
to form a `1+4+X` structure with water, bus, energy, Anju, and other specialized
groups.

The key transfer evidence is threefold. First, Hangzhou SASAC transferred 90
percent of Qiantou Group equity to Hangzhou City Investment as government
capital contribution. Second, Hangzhou City Investment succeeded Qiantou
Group's existing corporate bonds, enterprise bonds, and private-placement
instruments. Third, Hangzhou Anju Group was created as the citywide
housing-security investment, construction, and operation platform.

This case has been entered into `data/processed/human_validated_labels.csv` as a
medium-confidence `functional_transfer` case. More precisely, it is a
functional-consolidation case within the functional-transfer family: the
public-project and debt functions did not disappear, but were reorganized into a
larger and more specialized municipal platform system.
