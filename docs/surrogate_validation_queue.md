# Surrogate Validation Queue

Date: 2026-07-01

This note summarizes the current human-review queue generated from the Codex surrogate-labeling pass. The queue starts from 40 disclosure-level Codex surrogate labels, collapses them to 26 unique issuers, flags 22 issuers that already overlap with the gold-standard label file, and retains 4 non-overlap issuers for review. Four previously queued packets have been marked `boundary_reviewed` or promoted to the gold-standard label file, so they no longer appear here.

The queue is stored in `data/analysis_inputs/surrogate_validation_queue_2026_07_01.csv`. These rows are not gold-standard labels. Each row identifies one representative source packet for the issuer and should be checked against the original PDFs before any case is promoted to `data/processed/human_validated_labels.csv`.

| Queue ID | Priority | Issuer | Source row | Docs | Usable text docs | Surrogate label |
| --- | --- | --- | --- | ---: | ---: | --- |
| svq_001 | C | 南京市交通建设投资控股(集团)有限责任公司 | sch_20260630_0052 | 9 | 8 | nominal_exit |
| svq_002 | C | 江苏腾海投资控股集团有限公司 | sch_20260630_0019 | 7 | 6 | nominal_exit |
| svq_003 | C | 江苏高淳国际慢城文化旅游产业投资集团有限公司 | sch_20260630_0142 | 7 | 5 | nominal_exit |
| svq_004 | C | 嘉兴市嘉秀发展投资控股集团有限公司 | sch_20260630_0068 | 5 | 4 | nominal_exit |

Priority A rows have repeated disclosures and strong source/function scores. Priority B rows have strong source/function scores but fewer repeated disclosures. Priority C rows have usable source packets but need closer scope review before they should be treated as city-platform LGFV cases.

The review decision for each row should be one of three outcomes. First, promote the case to the gold-standard label file if original PDF evidence supports both the formal event and the continued-function assessment. Second, mark the row as duplicate if it is substantively the same platform as an already validated case. Third, retain or reject it as a boundary case if the issuer is a specialized infrastructure SOE, provincial SOE, transport group, or non-core LGFV whose inclusion would blur the sampling frame.
