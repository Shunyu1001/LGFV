# Surrogate Validation Queue

Date: 2026-07-02

This note summarizes the current human-review queue generated from the Codex surrogate-labeling pass. The queue starts from 66 disclosure-level Codex surrogate labels, collapses them to 45 unique issuers, flags 31 issuers that already overlap with the gold-standard label file, and retains 14 non-overlap issuers for review.

The queue is stored in `data/analysis_inputs/surrogate_validation_queue_2026_07_02.csv`. These rows are not gold-standard labels. Each row identifies one representative source packet for the issuer and should be checked against the original PDFs before any case is promoted to `data/processed/human_validated_labels.csv`.

| Queue ID | Priority | Issuer | Source row | Docs | Usable text docs | Surrogate label |
| --- | --- | --- | --- | ---: | ---: | --- |
| svq_001 | C | 丹阳投资集团有限公司 | sch_20260630_0044 | 9 | 5 | nominal_exit |
| svq_002 | C | 济南高新控股集团有限公司 | sch_20260630_0006 | 10 | 5 | nominal_exit |
| svq_003 | C | 苏州吴中国太发展有限公司 | sch_20260630_0007 | 9 | 5 | nominal_exit |
| svq_004 | C | 亳州城建发展控股集团有限公司 | sch_20260630_0032 | 9 | 4 | nominal_exit |
| svq_005 | C | 常州天宁建设发展集团有限公司 | sch_20260630_0057 | 7 | 4 | nominal_exit |
| svq_006 | C | 绍兴滨海新区控股集团有限公司 | sch_20260630_0033 | 8 | 4 | nominal_exit |
| svq_007 | C | 黄石市东楚投资集团有限公司 | sch_20260630_0054 | 9 | 4 | nominal_exit |
| svq_008 | C | 寿光市金旭产业发展集团有限公司 | sch_20260630_0028 | 9 | 3 | nominal_exit |
| svq_009 | C | 浙江安吉国控建设发展集团有限公司 | sch_20260630_0017 | 5 | 3 | nominal_exit |
| svq_010 | C | 温州市工业与能源发展集团有限公司 | sch_20260630_0031 | 8 | 3 | nominal_exit |
| svq_011 | C | 西宁城市发展有限公司 | sch_20260630_0041 | 8 | 3 | nominal_exit |
| svq_012 | C | 嘉兴科技城投资发展集团有限公司 | sch_20260630_0013 | 9 | 2 | nominal_exit |
| svq_013 | C | 知识城(广州)投资集团有限公司 | sch_20260630_0025 | 9 | 2 | nominal_exit |
| svq_014 | D | 湖州莫干山国有资本控股集团有限公司 | sch_20260630_0008 | 11 | 1 | nominal_exit |

Priority A would indicate repeated disclosures and strong source/function scores. After the July 2 promotion batches, no Priority A or Priority B non-overlap issuer remains in the queue. Priority C rows have usable source packets but need closer scope review before they should be treated as city-platform LGFV cases.

The review decision for each row should be one of three outcomes. First, promote the case to the gold-standard label file if original PDF evidence supports both the formal event and the continued-function assessment. Second, mark the row as duplicate if it is substantively the same platform as an already validated case. Third, retain or reject it as a boundary case if the issuer is a specialized infrastructure SOE, provincial SOE, transport group, or non-core LGFV whose inclusion would blur the sampling frame.
