# Source Search Protocol

This protocol governs the expansion from the pilot validated sample to a
50-case human-validated sample. The goal is not to collect every document on a
city platform. The goal is to build a source packet that can support one
case-level classification under the fixed codebook.

## Case definition

A case is a city-platform pair. The platform should be a municipal or
district-level financing vehicle, city-investment group, development group,
transport group, land-development company, public utility investment company,
or reorganized local SOE that plausibly performed local public project or
financing functions.

A candidate city can appear more than once when there are multiple plausible
platforms. A candidate becomes a validated case only after a specific legal
entity is identified and the source packet contains enough evidence to classify
its exit type.

## Source hierarchy

Searches should prioritize original or near-original documents. The preferred
order is:

1. Government, regulator, SASAC, finance-bureau, NDRC, or audit-office
   documents.
2. Company announcements, annual reports, bond prospectuses, offering circulars,
   and legal opinions.
3. Credit-rating reports, rating follow-up reports, and rating attention
   notices.
4. Business-registration records, merger notices, bankruptcy or liquidation
   records, court documents, and exchange disclosures.
5. News reports and data-provider summaries. These can identify leads, but they
   should not carry the final label unless no stronger document is available
   and the case is kept at low confidence.

## Search sequence

For each city-platform pair, search in four stages.

First, identify the platform. Use city-level searches and local government
language before relying on generic company lists:

```text
城市名 城投
城市名 城市建设投资
城市名 交通投资
城市名 国有资本 投资运营
城市名 基础设施 投融资 平台
城市名 国资委 平台公司
```

Second, search for a formal event. The search should include both direct exit
language and market-oriented transformation language:

```text
公司名 退出融资平台
公司名 退出政府融资平台
公司名 退出平台名单
公司名 退出银监会平台名单
公司名 不承担政府融资职能
公司名 不属于地方政府融资平台
公司名 政府融资职能
公司名 市场化转型
公司名 转型为市场化主体
公司名 隐性债务
公司名 政府性债务
公司名 债务置换
公司名 资产重组
公司名 注销 清算 破产
```

Third, search for post-event functions. The search should use prospectuses and
rating reports because they usually describe business segments, fiscal payment
arrangements, receivables, subsidies, and public-project responsibilities:

```text
公司名 募集说明书
公司名 跟踪评级报告
公司名 评级报告
公司名 委托代建
公司名 土地整理
公司名 基础设施建设
公司名 棚户区改造
公司名 政府购买服务
公司名 BT 项目
公司名 PPP 项目
公司名 财政补贴
公司名 财政资金
公司名 应收政府
公司名 项目回购
公司名 政策性贷款
```

Fourth, search for transfer or liquidation evidence when the first three stages
show exit or restructuring:

```text
公司名 划转
公司名 合并
公司名 重组
公司名 整合
公司名 新设 集团
公司名 股权无偿划转
公司名 资产划转
公司名 债务承继
公司名 工商注销
公司名 清算组
公司名 破产重整
```

## Minimum packet

A case should normally meet all three conditions before it enters the validated
sample.

First, it should have one formal-event source. Acceptable evidence includes
direct list-exit language, no-government-financing language, non-platform-list
language, regulator-transfer language, formal market-oriented transformation
language tied to financing-platform status, reorganization documents, or
liquidation and deregistration records.

Second, it should have one post-event function source. The source should show
whether the same company or a successor entity continued public project,
financing, land, debt, utility, or fiscal-support functions after the formal
event.

Third, it should have an evidence table with document IDs, source types, dates,
line references when available, a short paraphrase of each fact, and the coding
role of that fact.

Cases may enter the sample with only one strong prospectus when the prospectus
contains both direct formal-event language and detailed post-event function
evidence. These cases should usually be coded at medium confidence unless an
independent source later confirms the event.

## Exclusion rules

Exclude a candidate from the validated sample when:

1. the platform cannot be identified as a legal entity;
2. the only evidence is a generic city reform document with no company-level
   information;
3. the source packet lacks a formal-event source;
4. the source packet contains only pre-event business information;
5. the event is ordinary commercial restructuring with no relation to platform
   status, government financing, debt, or public project functions; or
6. the case is a central SOE, private company, or purely provincial entity whose
   function cannot be tied to a local government.

## Edge cases

Some cases will sit near category boundaries. The following rules should keep
the classifications consistent.

If a prospectus says the company no longer undertakes government financing
functions but also describes entrusted construction, land preparation, fiscal
settlement, or large government receivables, the case should normally be
nominal exit unless the evidence shows that these functions were converted into
ordinary budget-funded services without financing or debt exposure.

If the same public function moves from the old platform to a new city-investment
group, transport group, development group, or public-utility company, the case
should be functional transfer even when the old company also reports formal
exit.

If a company is deregistered, liquidated, or bankrupt, the case should be
liquidation only when the source packet does not show a successor entity
continuing the same public function.

If a company never entered a platform list but later reports that it does not
undertake government financing functions, the case can still be useful as a
boundary case, but it should not be treated as a clean exit-list case unless
the packet shows earlier platform-like functions.

## Validation record

Each validated case should leave four records:

1. a row in `data/processed/human_validated_labels.csv`;
2. a row in `data/analysis_inputs/master_case_pool.csv`;
3. a case evidence note in `coding/pilot_evidence_<case>.md` or a successor
   `coding/validated_evidence_<case>.md` file; and
4. a source inventory entry with document IDs, source type, source URL or local
   path, source date, and retrieval date.

The evidence note should state why the case is not merely an LLM label. It
should identify the formal event, the post-event function evidence, the final
classification, the alternative classification, and the source limitation that
would most affect confidence.
