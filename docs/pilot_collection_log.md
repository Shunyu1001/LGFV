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

## 2026-06-22, Zunyi weak-capacity candidate

The next collection pass returned to the Guizhou weak-capacity side of the
pilot. ChinaBond metadata had already identified two local enterprise bonds for
`遵义道桥建设集团有限公司`: `12遵义道桥债` and `15遵义道桥债`. A follow-up
ChinaBond disclosure search located the 2015 issuance-document page for the
issuer's older name, `遵义市道路桥梁工程有限责任公司`, and a set of rating
files and attention notices under the later group name.

Seven documents were downloaded. Five produced machine-readable text: the 2015
enterprise-bond prospectus, the 2015 initial rating report, the 2022 tracking
rating report, a July 2022 rating attention notice on debt-restructuring news,
and a 2023 rating attention notice on bank-loan restructuring. Two 2017
restructuring documents were downloaded but did not produce text through the
current extraction workflow.

The 2015 prospectus identifies the issuer and its subsidiary as infrastructure,
land-development, and investment-financing bodies for New Pu New Area. The 2022
tracking rating report shows that entrusted construction, land consolidation,
and government support were still central to the company. The July 2022
attention notice is especially useful because it describes Zunyi Daoqiao as one
of Guizhou's city- and county-level government financing platform company
debt-resolution pilot enterprises. The 2023 attention notice then reports a RMB
15.594 billion, or 155.94 yi yuan, bank-loan restructuring with a 20-year
post-restructuring maturity profile and continued reliance on provincial,
municipal, and financial-institution support.

This is not yet a human-validated exit-type case. The current evidence is
strong for baseline platform function, continuing public-project function, and
debt-continuity pressure, but it does not yet contain a direct formal-exit or
no-government-financing statement. The case has therefore been recorded as
`pilot_gz_002` with a separate evidence packet in
`coding/pilot_evidence_zunyi_daoqiao.md`. It should be used as a candidate weak
capacity case and should not be added to
`data/processed/human_validated_labels.csv` until a direct exit or compliance
source is collected.

## 2026-06-22, Liupanshui weak-capacity candidate

The next Guizhou search pass found a second weak-capacity candidate. ChinaBond
metadata returned three local enterprise bonds under `六盘水开投`: `12六盘水开投债`,
`14六盘水开投债`, and `16六盘水开投债`. The issuer is
`六盘水市开发投资有限公司`. ChinaBond disclosure search then located the 2016
issuance-document page, the 2022 tracking rating report, a 2021 attention
notice on enforcement-list inclusion, and a 2023 attention notice that kept the
company on the rating watch list.

Five documents were downloaded. Three produced machine-readable text: the 2016
prospectus, the 2016 initial rating report, and the 2022 tracking rating report.
The two one-page attention notices were downloaded but did not produce text
through the current extraction workflow.

The 2016 prospectus identifies Liupanshui Kaitou as a wholly state-owned
company established by the municipal government, with a business scope covering
project development, project investment and financing, entrusted project
construction, asset management, and land development. It also describes the
company's infrastructure business as an entrusted-construction and repurchase
arrangement with the municipal government. The 2022 tracking rating report
shows that the company still derived most of its revenue from infrastructure
construction, continued to undertake roads, environmental governance, water
projects, sewage-treatment projects, and shantytown redevelopment, and still
received asset injections and fiscal subsidies.

This case is not yet a human-validated exit-type case. Like Zunyi, it is strong
for baseline platform function, continued public-project function, weak fiscal
self-sufficiency, and debt pressure, but it lacks direct formal-exit or
no-government-financing language. The case has therefore been recorded as
`pilot_gz_003` with a separate evidence packet in
`coding/pilot_evidence_liupanshui_kaitou.md`.

## 2026-06-22, historical state-capacity sources

A parallel search identified three historical data sources for the explanatory
variable. CHGIS V6 is the strongest starting point for historical
administrative density because it provides historical administrative units and
time slices for 1820 and 1911. CBDB is the strongest source for historical
elite density because it provides biographical records, including civil-service
degree holders, with downloadable SQLite data. CHGIS also lists a Ming courier
routes and stations shapefile that can be used later as a communication and
transport-infrastructure robustness measure.

The current recommendation is to build the main historical state-capacity
measure from Qing administrative density using CHGIS, then use Ming-Qing
high-degree-holder density from CBDB as an alternative measure. The source memo
is stored in `docs/historical_state_capacity_sources.md`.

## 2026-06-22, CBDB elite-density construction pass

The first historical elite-density script has been implemented. The script
`scripts/prepare_cbdb_elite_counts.py` reads the local CBDB SQLite release and
writes a place-level Ming-Qing examination-elite count file to
`data/analysis_inputs/cbdb_mingqing_elite_place_counts.csv`. It also writes
diagnostic files for the release metadata, schema summary, examination entry
codes, and address coverage.

The downloaded Hugging Face zip contains `cbdb_20260620.sqlite3`, with metadata
generated on 2026-06-20. This differs from the GitHub `latest.json` file that
was initially retrieved, which still reported a 2026-03-14 SQLite filename. The
script therefore records the metadata stored inside the downloaded zip and
checks the SQLite SHA-256 hash against that internal metadata.

The first pass uses CBDB entry types `040101` for jinshi and `040102` for
juren, restricts biography dynasties to Ming, Qing, and Southern Ming, and
assigns each person to a preferred address using basic affiliation first,
followed by Ming household address, actual residence, household registration
address, and alternate basic affiliation. The resulting file contains 3,514
historical places with non-missing preferred addresses. Among 98,880
Ming-Qing examination-elite persons, 91,241 have a preferred address and 7,639
do not.

This output is an intermediate input rather than the final treatment variable.
The next step is to join CBDB places to contemporary prefecture-level units,
preferably through CHGIS place identifiers or coordinates. A separate script,
`scripts/inspect_chgis_archives.py`, has been added for CHGIS field inspection,
but the CHGIS 1820 and 1911 time-slice zip files still need to be downloaded
manually because Dataverse blocked automated API access during this run.

## 2026-06-22, CBDB-GADM prefecture match

The first modern-boundary match for the historical elite-density variable has
been implemented in `scripts/match_cbdb_to_gadm_prefectures.py`. The script
uses GADM 4.1 China ADM2 boundaries as a local modern prefecture-level
boundary file. The raw GADM zip is stored under `data/raw/` and is not tracked
because GADM allows academic and other non-commercial use but does not allow
redistribution of raw boundary data.

The script matches CBDB historical places to GADM ADM2 polygons by longitude
and latitude, then aggregates Ming-Qing jinshi and juren counts to the modern
prefecture. It writes a place-to-prefecture crosswalk, a prefecture-level count
and density file, a GADM metadata file, a match-coverage diagnostic, and an
unmatched-place diagnostic. The main output is
`data/analysis_inputs/cbdb_mingqing_elite_gadm_prefecture_counts.csv`.

The first match assigns 3,356 of 3,514 CBDB historical places to GADM ADM2
units. These matched places account for 89,433 of the 91,241 examination-elite
persons with preferred addresses. The unmatched places account for 1,808
persons and are mostly banner categories, broad historical regions, missing
coordinate records, Taiwan, and other places outside the mainland China GADM
polygon set. The resulting prefecture table contains 286 GADM ADM2 units with
at least one matched CBDB historical place.

The pilot-city values are substantively plausible. Hangzhou has 2,716 matched
elite persons, Guangzhou 1,524, Chengdu 861, Xi'an 536, Kunming 437, Zunyi 222,
and Liupanshui 6. After scaling by approximate area, Liupanshui remains very
low, while Hangzhou and Guangzhou remain high. These values should be treated
as an exploratory first pass until the boundary source and area calculations
are finalized.

## 2026-06-22, pilot historical-capacity validation table and figure

The first paper-facing historical-capacity artifact has been added. The script
`scripts/build_pilot_capacity_summary.py` combines the four human-validated
pilot labels with the two Guizhou weak-capacity candidate cases, then matches
them to `data/analysis_inputs/cbdb_mingqing_elite_gadm_prefecture_counts.csv`.
It writes a case-level summary file, an auto-generated LaTeX table, and a PNG
figure:

- `data/analysis_inputs/pilot_case_historical_capacity.csv`
- `paper/tables/pilot_case_historical_capacity.tex`
- `paper/figures/pilot_case_historical_capacity.png`

The figure and table have been included in the empirical-strategy section as a
pilot validation exercise. The text explicitly states that this is not a test
of the main hypothesis because the cases were selected for coding development,
not as a representative sample. The purpose is to check whether the historical
elite-density measure captures meaningful variation across the pilot cases.
The resulting pattern is substantively coherent: Guangzhou and Hangzhou have
high elite density; Chengdu and Xi'an occupy an intermediate position; Zunyi and
Liupanshui are much lower.

## 2026-06-24, candidate historical-capacity screen

The CBDB-GADM historical elite-density measure has now been attached to the full
candidate city plan. The script
`scripts/build_candidate_capacity_summary.py` combines
`data/candidate_city_plan.csv` with
`data/analysis_inputs/cbdb_mingqing_elite_gadm_prefecture_counts.csv`, applies a
small city-name crosswalk for Xi'an and Honghe Hani and Yi Autonomous
Prefecture, and writes:

- `data/analysis_inputs/candidate_city_historical_capacity.csv`
- `data/diagnostics/candidate_capacity_unmatched.csv`
- `docs/candidate_capacity_prioritization.md`

All 37 candidate platform rows match to a GADM ADM2 unit, covering 33 unique
province-city pairs. The unmatched diagnostic file is empty apart from the
header. The candidate cities divide evenly into 11 high-density, 11
middle-density, and 11 low-density cases when cut by candidate-list terciles.

The collection implication is to keep one high-density search, one low-density
search, and one middle-density search active at the same time. This keeps the
pilot from drifting toward either document-rich coastal cities or debt-stress
inland cases alone. The current high-density completion candidates are Suzhou,
Nanjing, Guiyang, Chengdu, and Ningbo. The low-density follow-ups are Zunyi,
Shenzhen, Zhuzhou, Qujing, and Luzhou. The middle-density pool is Kunming,
Qingdao, Mianyang, Jinhua, and Wenzhou.

## 2026-06-24, Suzhou high-capacity candidate

The next high historical-capacity search completed the source trail for Suzhou
City Construction Investment Development Group. Shanghai Clearing's disclosure
page for
`苏州城市建设投资发展(集团)有限公司2026年度第一期中期票据发行文件`,
published on 2026-03-02, lists eleven downloadable issuer documents. These have
been added to `data/document_inventory.csv`, and the main source has been added
to `data/source_inventory.csv` as `src_js_sz_002`.

The most important readable document is the 2026 first MTN prospectus,
`doc_js_sz_chengtou_2026_mtn1_009`, with 306 pages and 314,243 extracted
characters. The legal opinion and 2023 audited financial report also produced
readable text. The 2022 and 2024 audited financial reports and the 2025
third-quarter financial statement downloaded successfully but did not produce
machine-readable text with the current extractor.

The evidence packet is stored at
`coding/pilot_evidence_suzhou_chengtou.md`. The case should remain a candidate
rather than a final human-validated label. The current interpretation is
`substantive_exit_or_functional_transfer`: the documents contain strong
no-government-financing and no-new-hidden-debt compliance language, but they
also describe a transformation from an earlier investment-financing platform
toward a broader city construction, city operation, industrial development, and
city-investment financial-services group. The key validation question is whether
the delegated project and city-investment financial-service activities are
formal operating businesses or preserve quasi-fiscal financing functions in a
new form.

## 2026-06-24, Nanjing Metro boundary case

The next high historical-capacity pass completed the source trail for the
Nanjing Metro alternative platform case. Shanghai Clearing's disclosure page for
`南京地铁集团有限公司2025年度第二期中期票据发行文件`, published on 2025-06-17,
lists seven downloadable issuer documents. These have been added to
`data/document_inventory.csv`, and the main source has been added to
`data/source_inventory.csv` as `src_js_nj_002`.

The most important readable document is the 2025 second MTN prospectus,
`doc_js_nj_metro_2025_mtn2_004`, with 257 pages and 261,169 extracted
characters. The legal opinion, issuance plan, and 2024 audited financial report
also produced readable text. The 2025 first-quarter statement and 2022 audited
financial report downloaded successfully but did not produce machine-readable
text. The 2023 audited financial report produced only 130 extracted characters
and should be treated as not usable without OCR.

The evidence packet is stored at
`coding/pilot_evidence_nanjing_metro.md`. This case should remain a candidate
rather than a final human-validated label. The current interpretation is
`formal_fiscal_substitution_candidate`: the documents show an ongoing
rail-transit infrastructure SOE with explicit municipal fiscal support, project
capital, subsidies, PPP arrangements, and corporate-debt disclosure, while also
stating that the issuer does not undertake government financing functions and
that new debt after January 1, 2015 is not local government debt. The case is
therefore useful as a boundary case that separates formal fiscal substitution
from a direct LGFV exit-type label.

## 2026-06-24, Qingdao middle-capacity candidate

The next collection pass moved to the middle historical-capacity pool. ChinaBond
metadata returned two local enterprise bonds under `青岛城投`: `12青岛城投债01`
and `12青岛城投债02`. Shanghai Clearing then returned issuer records for
`青岛城市建设投资(集团)有限责任公司` and a disclosure page for
`青岛城市建设投资(集团)有限责任公司2026年度第二期中期票据发行文件`, published on
2026-02-02. The page lists seven downloadable documents, including a prospectus,
legal opinion, issuance plan, 2025 third-quarter financial statement, and
2022-2024 audited financial reports.

All seven PDFs downloaded successfully. Three produced useful machine-readable
text: the 2026 second MTN prospectus, with 356 pages and 408,048 extracted
characters; the issuance plan and commitment letter, with 15,616 extracted
characters; and the 2024 audited financial report, with 134,130 extracted
characters. The 2025 third-quarter statement, 2023 audited financial report,
legal opinion, and 2022 audited financial report did not produce text with the
current extractor.

The evidence packet is stored at
`coding/pilot_evidence_qingdao_chengtou.md`. This case should remain a candidate
rather than a final human-validated label. The current interpretation is
`formal_fiscal_substitution_or_functional_transfer_candidate`: the prospectus
states that the issuer does not undertake government financing functions and
that new debt after January 1, 2015 is not local government debt, but it also
documents continuing land-development, urban-renewal, infrastructure, delegated
project-management, fiscal-settlement, and policy-loan channels. The key
validation question is whether the issuer's 2014 market-oriented reform
corresponds to a formal LGFV exit event or only to a broader SOE transformation.

## 2026-06-24, Zhuzhou low-capacity non-Guizhou candidate

The next collection pass moved to the low historical-capacity pool outside
Guizhou. ChinaBond metadata returned three local enterprise bonds and one
offshore bond under `株洲国投`, issued by `株洲市国有资产投资`. Shanghai
Clearing then returned issuer records for `株洲市国有资产投资控股集团有限公司`
and a disclosure page for
`株洲市国有资产投资控股集团有限公司2026年度第一期超短期融资券发行文件`,
published on 2026-03-25. The page lists six downloadable documents, including a
prospectus, legal opinion, issuance plan, 2025 third-quarter financial
statement, and 2021-2024 audited financial reports.

All six PDFs downloaded successfully. Five produced useful machine-readable
text: the 2026 first SCP prospectus, with 334 pages and 340,492 extracted
characters; the 2021-2023 audited financial report, with 175,321 extracted
characters; the 2024 audited financial report, with 109,696 extracted
characters; the legal opinion, with 67,635 extracted characters; and the
issuance plan and commitment letter, with 9,878 extracted characters. The 2025
third-quarter financial statement did not produce text with the current
extractor.

The evidence packet is stored at
`coding/pilot_evidence_zhuzhou_guotou.md`. This case should remain a candidate
rather than a final human-validated label. The current interpretation is
`nominal_exit_or_functional_transfer_candidate`: the prospectus explicitly says
the issuer exited the government financing platform list in March 2013 and
does not currently undertake government financing functions, but it also
documents continuing land-preparation, major-project, government-entrusted, and
fiscal-settlement functions. The key validation question is whether the formal
exit is mostly nominal or whether the post-2020 service-contract and fiscal
settlement arrangement represents functional transfer with formal fiscal
substitution.

## 2026-06-24, Shenzhen low-historical high-contemporary boundary case

The next collection pass completed the source trail for the Shenzhen Special
Zone Development case. Shenzhen is in the low historical-capacity bin, but it
has very strong contemporary fiscal and administrative capacity. This makes the
case useful as a boundary case rather than a standard weak-capacity case.

ChinaBond did not return bond metadata for `深圳特区建发`, `特区建发`, or
`深圳市特区建设发展`. Shanghai Clearing returned issuer records for
`深圳市特区建设发展集团有限公司` and a long disclosure history from 2014 to 2025.
The main source selected for the current packet is
`深圳市特区建设发展集团有限公司2025年度第四期中期票据发行文件`, published on
2025-11-12. The page lists eight downloadable documents, including a
continuation prospectus, issuer rating report, issuance plan, legal opinion,
2025 third-quarter statement, and 2022-2024 audited financial reports.

All eight PDFs downloaded successfully. Six produced useful machine-readable
text: the continuation prospectus, with 62 pages and 58,020 extracted
characters; the issuer rating report, with 39,523 extracted characters; the
2022, 2023, and 2024 audited financial reports, with more than 100,000
characters each; and the issuance plan and commitment letter, with 15,337
characters. The 2025 third-quarter financial statement did not produce text, and
the legal opinion produced only 21 characters.

The evidence packet is stored at
`coding/pilot_evidence_shenzhen_tqjf.md`. This case should remain a boundary
case rather than a final human-validated label. The current interpretation is
`formal_fiscal_substitution_boundary_candidate`: the issuer operates as a
municipal state-owned platform-like company with infrastructure, technology
park, transport, marine-development, PPP, government assistance, and fiscal
funding-channel functions, while the bond documents frame current financing as
corporate debt and deny new government or hidden debt. The case helps separate
historically low administrative density from contemporary fiscal strength.

## 2026-06-25, Luzhou Xinglu low-capacity western prefecture case

The next collection pass added a western prefecture case outside Guizhou.
The candidate-capacity table places Luzhou in the low historical-capacity bin,
but the city is less dominated by the acute debt-resolution setting that shapes
Zunyi and Liupanshui. This makes it a useful comparison case for assessing
whether weak historical capacity is associated with formal compliance language
coexisting with continuing platform functions.

Shanghai Clearing's disclosure interface returned a 2023 first MTN issuance
page for `泸州市兴泸投资集团有限公司`, dated 2023-01-09. The page lists eight
downloadable documents: the prospectus, tracking rating report, legal opinion,
issuance plan, three audited financial reports, and a 2022 third-quarter
financial statement. All eight PDFs were downloaded. Seven produced
machine-readable text through the local extractor; the 2022 third-quarter
financial statement produced no text and may require OCR if it becomes
important.

The strongest current source is the 2023 MTN prospectus. It identifies Xinglu
as the Luzhou government's operating body for urban infrastructure investment
and financing, construction management, and state-asset operation. The same
document states that the issuer does not undertake government financing
functions and that new debt after January 1, 2015 is not local government debt.
It also describes continuing entrusted-construction arrangements: the company
serves as project owner for government-designated infrastructure projects,
raises funds through self-owned and external financing, and is compensated by
government payments that cover financing principal, interest, investment
returns, subsidies, or project repurchase.

The 2022 tracking rating report corroborates this interpretation. It describes
Xinglu as Luzhou's most important urban infrastructure construction and
state-asset management operating body, notes continuing government support,
and states that projects not owned by the company are recorded as long-term
receivables because the company is responsible for the financing function.
The rating report also records a relatively low fiscal self-sufficiency rate
for Luzhou, while the prospectus reports fiscal subsidies, financing-interest
subsidies, large interest-bearing debt, and entrusted-construction receivables.

The case has been added as `pilot_sc_003`, with source row
`src_sc_lz_xinglu_001` and evidence packet
`coding/pilot_evidence_luzhou_xinglu.md`. No final exit label is assigned.
The preliminary interpretation is
`nominal_exit_or_functional_persistence_candidate`, pending a direct formal
exit-list source or another local debt-resolution source.

## 2026-06-25, Luzhou Xinglu cross-time validation

A follow-up search tried to find a direct formal exit-list source for Xinglu.
General web search did not return a reliable official `退出融资平台` document.
The collection therefore shifted to cross-time disclosure validation.

ChinaBond's public bond metadata endpoint returned four historical Xinglu
bonds: `08兴泸债`, `11兴泸债`, `12兴泸集MTN1`, and `15兴泸债`. These records
show that Xinglu had been a recurring bond-market financing entity before the
2023 source set. They were added to `data/bond_inventory.csv` and recorded as
source row `src_sc_lz_xinglu_000`.

Shanghai Clearing's 2018 first MTN disclosure page for Xinglu was then added
as source row `src_sc_lz_xinglu_002`. Two documents were downloaded and
extracted: the 2018 first MTN prospectus, with 198 pages and 231,723 extracted
characters, and the 2018 first MTN credit rating report, with 35 pages and
52,629 extracted characters.

The 2018 documents strengthen the Luzhou evidence packet. The prospectus
already states that Xinglu does not undertake government financing functions
and that new debt after January 1, 2015 is not local government debt. At the
same time, the same prospectus describes Xinglu as the Luzhou government's
urban infrastructure investment-financing, construction-management, and
state-asset operation body. It also describes government-entrusted
construction, self-owned and external financing for government-designated
projects, and compensation through fiscal payments, project repurchase, and
project subsidies. The 2018 rating report further calls Xinglu Luzhou's largest
platform company and records support through asset injections and fiscal
subsidies.

This does not convert the case into a final human-validated label, because no
direct exit-list source has been found. It does make the preliminary
interpretation stronger: the formal no-government-financing language and the
continuing platform-like project-finance role coexist across time, not only in
the 2023 prospectus.
