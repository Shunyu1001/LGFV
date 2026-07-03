# Surrogate Validation Queue

Date: 2026-07-02

This note summarizes the current human-review queue generated from the Codex surrogate-labeling pass. After the missing-PDF recovery pass and promotion of the two Priority A cases, the queue contains 27 non-overlap issuers: 9 Priority B rows and 18 Priority C rows. These rows are not gold-standard labels. Each row must be checked against original PDF evidence before promotion.

The queue file is stored in `data/analysis_inputs/surrogate_validation_queue_2026_07_02.csv`. A row should be promoted only if the original source packet supports both the formal event and the post-event functional assessment. Rows should be marked as boundary if the issuer is a specialized industrial, energy, provincial, or otherwise non-core LGFV entity whose inclusion would blur the sampling frame.

| Queue ID | Priority | Issuer | Source row | Docs | Usable text | Surrogate label |
| --- | --- | --- | --- | ---: | ---: | --- |
| `svq_001` | B | 日照城投集团有限公司 | `sch_20260630_0132` | 9 | 6 | nominal_exit |
| `svq_002` | B | 青岛上合控股发展集团有限公司 | `sch_20260630_0175` | 7 | 5 | nominal_exit |
| `svq_003` | B | 乌鲁木齐交通旅游投资(集团)有限公司 | `sch_20260630_0127` | 8 | 4 | nominal_exit |
| `svq_004` | B | 北京控股集团有限公司 | `sch_20260630_0129` | 10 | 4 | nominal_exit |
| `svq_005` | B | 如东县东泰社会发展投资有限责任公司 | `sch_20260630_0073` | 7 | 4 | nominal_exit |
| `svq_006` | B | 扬州建工控股集团有限公司 | `sch_20260630_0149` | 8 | 2 | nominal_exit |
| `svq_007` | B | 新乡投资集团有限公司 | `sch_20260630_0159` | 9 | 2 | nominal_exit |
| `svq_008` | B | 湖北荆门城建集团有限公司 | `sch_20260630_0110` | 9 | 2 | nominal_exit |
| `svq_009` | B | 重庆市江津区珞璜开发建设有限公司 | `sch_20260630_0094` | 9 | 2 | nominal_exit |
| `svq_010` | C | 山西建设投资集团有限公司 | `sch_20260630_0101` | 9 | 6 | nominal_exit |
| `svq_011` | C | 南京江宁科学园发展集团有限公司 | `sch_20260630_0075` | 7 | 5 | nominal_exit |
| `svq_012` | C | 南京高淳国有资产经营控股集团有限公司 | `sch_20260630_0160` | 8 | 5 | nominal_exit |
| `svq_013` | C | 南通城市建设集团有限公司 | `sch_20260630_0089` | 7 | 5 | nominal_exit |
| `svq_014` | C | 天津北辰经济技术开发区集团有限公司 | `sch_20260630_0134` | 10 | 5 | nominal_exit |
| `svq_015` | C | 宜昌城发实业投资有限公司 | `sch_20260630_0071` | 9 | 5 | nominal_exit |
| `svq_016` | C | 扬州新材料投资集团有限公司 | `sch_20260630_0121` | 7 | 5 | nominal_exit |
| `svq_017` | C | 南京江宁交通建设集团有限公司 | `sch_20260630_0144` | 7 | 4 | nominal_exit |
| `svq_018` | C | 温州市工业与能源发展集团有限公司 | `sch_20260630_0095` | 9 | 4 | nominal_exit |
| `svq_019` | C | 重庆市永川区惠通建设发展有限公司 | `sch_20260630_0119` | 7 | 4 | nominal_exit |
| `svq_020` | C | 中煤矿山建设集团有限责任公司 | `sch_20260630_0061` | 8 | 3 | nominal_exit |
| `svq_021` | C | 义乌中国小商品城控股集团有限公司 | `sch_20260630_0078` | 8 | 3 | nominal_exit |
| `svq_022` | C | 合肥北城建设投资(集团)有限公司 | `sch_20260630_0125` | 7 | 3 | nominal_exit |
| `svq_023` | C | 西部(重庆)科学城江津园区开发建设集团有限公司 | `sch_20260630_0168` | 7 | 3 | nominal_exit |
| `svq_024` | C | 南通产业控股集团有限公司 | `sch_20260630_0074` | 7 | 2 | nominal_exit |
| `svq_025` | C | 安徽省宁国建设投资集团有限公司 | `sch_20260630_0173` | 8 | 2 | nominal_exit |
| `svq_026` | C | 重庆市江津区滨江新城开发建设集团有限公司 | `sch_20260630_0167` | 10 | 2 | nominal_exit |
| `svq_027` | C | 青岛胶州湾发展集团有限公司 | `sch_20260630_0145` | 8 | 2 | nominal_exit |

The immediate next validation batch should start with the Priority B rows, especially cases with multiple usable source documents and direct no-government-financing language. Priority C rows are usable but generally have thinner functional evidence or more scope ambiguity.
