# Surrogate Validation Queue

Date: 2026-07-01

This note summarizes the current human-review queue generated from the Codex
surrogate-labeling pass. The queue starts from 47 disclosure-level Codex
surrogate labels, collapses them to 32 unique issuers, flags 22 issuers that
already overlap with the gold-standard label file, and retains 10 non-overlap
issuers for review.

The queue is stored in
`data/analysis_inputs/surrogate_validation_queue_2026_07_01.csv`. These rows
are not gold-standard labels. Each row identifies one representative source
packet for the issuer and should be checked against the original PDFs before
any case is promoted to `data/processed/human_validated_labels.csv`.

| Queue ID | Priority | Issuer | Source row | Docs | Usable text docs | Surrogate label |
| --- | --- | --- | --- | ---: | ---: | --- |
| svq_001 | B | 建安投资控股集团有限公司 | sch_20260630_0027 | 9 | 7 | nominal_exit |
| svq_002 | B | 上饶创新发展产业投资集团有限公司 | sch_20260630_0055 | 7 | 6 | nominal_exit |
| svq_003 | B | 广州地铁集团有限公司 | pilot_gd_001_alt_metro | 10 | 6 | nominal_exit |
| svq_004 | B | 南京地铁集团有限公司 | pilot_js_001_alt_metro | 7 | 5 | nominal_exit |
| svq_005 | B | 石家庄市交通投资开发有限公司 | sch_20260630_0151 | 7 | 3 | nominal_exit |
| svq_006 | C | 浙江省交通投资集团有限公司 | sch_20260630_0083 | 10 | 9 | nominal_exit |
| svq_007 | C | 南京市交通建设投资控股(集团)有限责任公司 | sch_20260630_0052 | 9 | 8 | nominal_exit |
| svq_008 | C | 江苏腾海投资控股集团有限公司 | sch_20260630_0019 | 7 | 6 | nominal_exit |
| svq_009 | C | 江苏高淳国际慢城文化旅游产业投资集团有限公司 | sch_20260630_0142 | 7 | 5 | nominal_exit |
| svq_010 | C | 嘉兴市嘉秀发展投资控股集团有限公司 | sch_20260630_0068 | 5 | 4 | nominal_exit |

Priority A rows have repeated disclosures and strong source/function scores.
Priority B rows have strong source/function scores but fewer repeated
disclosures. Priority C rows have usable source packets but need closer scope
review before they should be treated as city-platform LGFV cases.

The review decision for each row should be one of three outcomes. First,
promote the case to the gold-standard label file if original PDF evidence
supports both the formal event and the continued-function assessment. Second,
mark the row as duplicate if it is substantively the same platform as an
already validated case. Third, retain or reject it as a boundary case if the
issuer is a specialized infrastructure SOE, provincial SOE, transport group, or
non-core LGFV whose inclusion would blur the sampling frame.
