# Priority-B Surrogate Queue Validation Memo

Date: 2026-07-02

This memo records the second July 2 review batch from the surrogate validation
queue. The batch reviewed all remaining Priority-B non-overlap issuers. Five
cases were promoted to the human gold-standard label file and two were marked
as boundary-reviewed packets outside the current city-platform LGFV frame.

## Promoted Cases

| Case ID | Issuer | Final label | Source basis |
| --- | --- | --- | --- |
| `sch_20260630_0005` | 河北顺德投资集团有限公司 | nominal_exit | `doc_sch_20260630_0005_005`, lines 1593-1596, 199-208, 210-217, 1572-1583, 1900-1904, 1935-1949, 2052-2061, 2077-2101 |
| `sch_20260630_0048` | 常州市交通产业集团有限公司 | nominal_exit | `doc_sch_20260630_0048_003`, lines 1402-1412; `doc_sch_20260630_0048_007`, lines 1251-1264, 199-211, 1270-1309, 1311-1339, 1549-1568, 1623-1652 |
| `sch_20260630_0046` | 徐州市交通控股集团有限公司 | nominal_exit | `doc_sch_20260630_0046_003`, lines 1264-1270, 485-490, 497-505, 1374-1435, 1517-1535, 1823-1849; `doc_sch_20260630_0046_004`, lines 558-563, 132-143 |
| `sch_20260630_0014` | 河南航空港投资集团有限公司 | nominal_exit | `doc_sch_20260630_0014_009`, lines 1078-1089, 179-192, 1131-1166, 1485-1540; `doc_sch_20260630_0014_001`, lines 929-939 and 551-565 |
| `sch_20260630_0021` | 泰兴市中兴国有资产经营投资集团有限公司 | nominal_exit | `doc_sch_20260630_0021_009`, lines 1114-1129, 491-495, 1207-1229, 1407-1418; `doc_sch_20260630_0021_006`, lines 290-310 and 523-540 |

## Boundary-Reviewed Packets

`sch_20260630_0016`, 北京控股集团有限公司, was marked boundary-reviewed. The
packet contains no-government-financing language and public-utility or
infrastructure exposure, but the issuer is a large diversified Beijing
municipal SOE rather than a clean city-platform LGFV case.

`sch_20260630_0043`, 厦门港务控股集团有限公司, was also marked
boundary-reviewed. The packet contains historical platform-list exit language,
but the issuer is a specialized port group controlled through Fujian Port Group
and is outside the current city-platform gold-standard frame.

## Dataset Effect

The batch raises the human gold-standard file from 68 to 73 cases. The
candidate seed pool now contains 73 gold-standard rows, 180 pending rows, and 4
boundary-reviewed rows. The Codex surrogate file now contains 66
disclosure-level surrogate labels and 114 unresolved rows. The non-overlap
validation queue falls from 21 to 14 issuers.
