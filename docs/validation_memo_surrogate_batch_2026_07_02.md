# Surrogate Queue Validation Memo

Date: 2026-07-02

This memo records the first promotion batch from the Codex surrogate validation
queue into the human gold-standard label file. The review rule was conservative:
a case was promoted only when the source packet contained both formal
no-government-financing or exit language and post-event evidence that public
project, land-development, infrastructure, fiscal-support, or state-asset
functions remained institutionally present.

## Promoted Cases

| Case ID | Issuer | Final label | Source basis |
| --- | --- | --- | --- |
| `sch_20260630_0035` | 嘉善县高新科技园区建设投资有限公司 | nominal_exit | `doc_sch_20260630_0035_005`, lines 1248-1251, 493-498, 523-566, 573-577; `doc_sch_20260630_0035_002`, lines 382-389, 811-814, 416-418, 769-805 |
| `sch_20260630_0015` | 徐州经济技术开发区国有资产经营有限责任公司 | nominal_exit | `doc_sch_20260630_0015_007`, lines 1457-1460, 153-155, 570-577, 597-600, 645-675; `doc_sch_20260630_0015_008`, lines 375-386, 434-441, 564-565 |
| `sch_20260630_0029` | 江阴高新区投资开发有限公司 | nominal_exit | `doc_sch_20260630_0029_002`, lines 1286-1288, 483-509, 549-568, 577-588; `doc_sch_20260630_0029_004`, lines 376-382, 434-436, 475-477 |
| `sch_20260630_0047` | 溧阳市城市建设发展集团有限公司 | nominal_exit | `doc_sch_20260630_0047_006`, lines 1355-1356, 492-505, 522-534, 603-605; `doc_sch_20260630_0047_003`, lines 752-755, 777, 921-926 |
| `sch_20260630_0051` | 北京未来科学城发展集团有限公司 | nominal_exit | `doc_sch_20260630_0051_003`, lines 1582, 3176, 226-264, 699-700; `doc_sch_20260630_0051_005`, lines 111-114, 263-286, 737-741; `doc_sch_20260630_0051_001`, lines 681-690, 1278-1279 |
| `sch_20260630_0056` | 新疆城建(集团)股份有限公司 | nominal_exit | `doc_sch_20260630_0056_005`, lines 1238-1241, 767-792, 832-833, 1246-1248; `doc_sch_20260630_0056_003`, lines 1081-1082, 234, 403-405, 1066-1074 |

## Retained for Later Review

`sch_20260630_0021`, 泰兴市中兴国有资产经营投资集团有限公司, was not promoted in
this batch. The available legal-opinion packet contains compliance language,
but one reviewed document also states that the issuer had not recently engaged
in land development or infrastructure construction. The case remains in the
queue until another source packet establishes continued public function with
greater confidence.

## Dataset Effect

The batch raises the human gold-standard file from 62 to 68 cases. All six
promoted rows are coded as `nominal_exit`. The candidate seed pool now contains
68 gold-standard rows, 187 pending rows, and 2 boundary-reviewed rows. The
surrogate validation queue falls from 27 to 21 non-overlap issuers.
