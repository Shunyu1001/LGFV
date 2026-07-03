# Surrogate Validation Queue
Date: 2026-07-02
This note summarizes the current human-review queue generated from the Codex surrogate-labeling pass. The queue starts from 59 disclosure-level Codex surrogate labels, collapses them to 38 unique issuers, flags 31 issuers that already overlap with the gold-standard label file, and retains 7 non-overlap issuers for review.
The queue is stored in `data/analysis_inputs/surrogate_validation_queue_2026_07_02.csv`. These rows are not gold-standard labels. Each row identifies one representative source packet for the issuer and should be checked against the original PDFs before any case is promoted to `data/processed/human_validated_labels.csv`.
| Queue ID | Priority | Issuer | Source row | Docs | Usable text docs | Surrogate label |
| --- | --- | --- | --- | ---: | ---: | --- |
| svq_001 | C | 寿光市金旭产业发展集团有限公司 | sch_20260630_0028 | 9 | 3 | nominal_exit |
| svq_002 | C | 浙江安吉国控建设发展集团有限公司 | sch_20260630_0017 | 5 | 3 | nominal_exit |
| svq_003 | C | 温州市工业与能源发展集团有限公司 | sch_20260630_0031 | 8 | 3 | nominal_exit |
| svq_004 | C | 西宁城市发展有限公司 | sch_20260630_0041 | 8 | 3 | nominal_exit |
| svq_005 | C | 嘉兴科技城投资发展集团有限公司 | sch_20260630_0013 | 9 | 2 | nominal_exit |
| svq_006 | C | 知识城(广州)投资集团有限公司 | sch_20260630_0025 | 9 | 2 | nominal_exit |
| svq_007 | D | 湖州莫干山国有资本控股集团有限公司 | sch_20260630_0008 | 11 | 1 | nominal_exit |

Priority A would indicate repeated disclosures and strong source/function scores. After the July 2 promotion batches, no Priority A or Priority B non-overlap issuer remains in the queue. The remaining Priority C and Priority D rows have thinner source packets or harder scope questions, so they should receive closer review before they are treated as city-platform LGFV cases.
The review decision for each row should be one of three outcomes. First, promote the case to the gold-standard label file if original PDF evidence supports both the formal event and the continued-function assessment. Second, mark the row as duplicate if it is substantively the same platform as an already validated case. Third, retain or reject it as a boundary case if the issuer is a specialized infrastructure SOE, provincial SOE, transport group, or non-core LGFV whose inclusion would blur the sampling frame.
