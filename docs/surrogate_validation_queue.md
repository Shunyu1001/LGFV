# Surrogate Validation Queue

Date: 2026-07-02

This note summarizes the current human-review queue generated from the Codex surrogate-labeling pass. The queue starts from 79 disclosure-level Codex surrogate labels, collapses them to 56 unique issuers, flags 29 issuers that already overlap with the gold-standard label file, and retains 27 non-overlap issuers for review.

The queue is stored in `data/analysis_inputs/surrogate_validation_queue_2026_07_02.csv`. These rows are not gold-standard labels. Each row identifies one representative source packet for the issuer and should be checked against the original PDFs before any case is promoted to `data/processed/human_validated_labels.csv`.

| Queue ID | Priority | Issuer | Source row | Docs | Usable text docs | Surrogate label |
| --- | --- | --- | --- | ---: | ---: | --- |
| svq_001 | A | 嘉善县高新科技园区建设投资有限公司 | sch_20260630_0035 | 7 | 4 | nominal_exit |
| svq_002 | A | 徐州经济技术开发区国有资产经营有限责任公司 | sch_20260630_0015 | 8 | 3 | nominal_exit |
| svq_003 | B | 北京未来科学城发展集团有限公司 | sch_20260630_0051 | 8 | 5 | nominal_exit |
| svq_004 | B | 常州市交通产业集团有限公司 | sch_20260630_0048 | 7 | 5 | nominal_exit |
| svq_005 | B | 江阴高新区投资开发有限公司 | sch_20260630_0029 | 9 | 5 | nominal_exit |
| svq_006 | B | 河北顺德投资集团有限公司 | sch_20260630_0005 | 8 | 5 | nominal_exit |
| svq_007 | B | 溧阳市城市建设发展集团有限公司 | sch_20260630_0047 | 7 | 5 | nominal_exit |
| svq_008 | B | 北京控股集团有限公司 | sch_20260630_0016 | 7 | 4 | nominal_exit |
| svq_009 | B | 徐州市交通控股集团有限公司 | sch_20260630_0046 | 7 | 4 | nominal_exit |
| svq_010 | B | 厦门港务控股集团有限公司 | sch_20260630_0043 | 8 | 3 | nominal_exit |
| svq_011 | B | 新疆城建(集团)股份有限公司 | sch_20260630_0056 | 7 | 2 | nominal_exit |
| svq_012 | B | 河南航空港投资集团有限公司 | sch_20260630_0014 | 10 | 2 | nominal_exit |
| svq_013 | B | 泰兴市中兴国有资产经营投资集团有限公司 | sch_20260630_0021 | 9 | 2 | nominal_exit |
| svq_014 | C | 丹阳投资集团有限公司 | sch_20260630_0044 | 9 | 5 | nominal_exit |
| svq_015 | C | 济南高新控股集团有限公司 | sch_20260630_0006 | 10 | 5 | nominal_exit |
| svq_016 | C | 苏州吴中国太发展有限公司 | sch_20260630_0007 | 9 | 5 | nominal_exit |
| svq_017 | C | 亳州城建发展控股集团有限公司 | sch_20260630_0032 | 9 | 4 | nominal_exit |
| svq_018 | C | 常州天宁建设发展集团有限公司 | sch_20260630_0057 | 7 | 4 | nominal_exit |
| svq_019 | C | 绍兴滨海新区控股集团有限公司 | sch_20260630_0033 | 8 | 4 | nominal_exit |
| svq_020 | C | 黄石市东楚投资集团有限公司 | sch_20260630_0054 | 9 | 4 | nominal_exit |
| svq_021 | C | 寿光市金旭产业发展集团有限公司 | sch_20260630_0028 | 9 | 3 | nominal_exit |
| svq_022 | C | 浙江安吉国控建设发展集团有限公司 | sch_20260630_0017 | 5 | 3 | nominal_exit |
| svq_023 | C | 温州市工业与能源发展集团有限公司 | sch_20260630_0031 | 8 | 3 | nominal_exit |
| svq_024 | C | 西宁城市发展有限公司 | sch_20260630_0041 | 8 | 3 | nominal_exit |
| svq_025 | C | 嘉兴科技城投资发展集团有限公司 | sch_20260630_0013 | 9 | 2 | nominal_exit |
| svq_026 | C | 知识城(广州)投资集团有限公司 | sch_20260630_0025 | 9 | 2 | nominal_exit |
| svq_027 | D | 湖州莫干山国有资本控股集团有限公司 | sch_20260630_0008 | 11 | 1 | nominal_exit |

Priority A rows have repeated disclosures and strong source/function scores. Priority B rows have strong source/function scores but fewer repeated disclosures. Priority C rows have usable source packets but need closer scope review before they should be treated as city-platform LGFV cases.

The review decision for each row should be one of three outcomes. First, promote the case to the gold-standard label file if original PDF evidence supports both the formal event and the continued-function assessment. Second, mark the row as duplicate if it is substantively the same platform as an already validated case. Third, retain or reject it as a boundary case if the issuer is a specialized infrastructure SOE, provincial SOE, transport group, or non-core LGFV whose inclusion would blur the sampling frame.
