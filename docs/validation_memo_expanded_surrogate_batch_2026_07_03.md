# Expanded Surrogate Validation Batch, July 3 2026

This memo records the first validation pass on the expanded Codex surrogate queue created after the July 3 candidate-pool expansion. Seven issuer packets were promoted from Codex surrogate labels to human gold-standard labels. One repeated Beijing Controls Group packet was marked boundary-reviewed and excluded from the core city-platform LGFV exit frame.

## Promoted Gold-Standard Cases

| Case ID | Issuer | Final label | Key formal-event evidence | Key continued-function evidence |
|---|---|---|---|---|
| `exp_20260703_0008` | 晋中市公用基础设施投资控股(集团)有限公司 | `nominal_exit` | `doc_exp_20260703_0008_007`, lines 984-990 and 1121-1124 | `doc_exp_20260703_0008_007`, lines 993-1002; `doc_exp_20260703_0008_001`, lines 999-1001 |
| `exp2_20260703_0009` | 南京江北新城投资发展有限公司 | `nominal_exit` | `doc_exp2_20260703_0009_007`, lines 1198-1208, 1475-1478, and 5522-5525 | `doc_exp2_20260703_0009_007`, lines 1211-1212; `doc_exp2_20260703_0009_006`, lines 1456-1458 |
| `sch_20260630_0132` | 日照城投集团有限公司 | `nominal_exit` | `doc_sch_20260630_0132_009`, lines 1240-1245 and 1289-1292 | `doc_sch_20260630_0132_002`, lines 163-168 and 505-521 |
| `sch_20260630_0175` | 青岛上合控股发展集团有限公司 | `nominal_exit` | `doc_sch_20260630_0175_001`, lines 1372-1375 | `doc_sch_20260630_0175_001`, lines 216-220, 466-467, and 745-757 |
| `sch_20260630_0073` | 如东县东泰社会发展投资有限责任公司 | `nominal_exit` | `doc_sch_20260630_0073_003`, lines 1138-1145 and 1300-1307 | `doc_sch_20260630_0073_002`, lines 62-66, 3683-3743, and 4997-5004 |
| `exp_20260703_0001` | 蚌埠市城市投资控股有限公司 | `nominal_exit` | `doc_exp_20260703_0001_005`, lines 1277-1280 | `doc_exp_20260703_0001_001`, lines 2044-2063, 2848-2858, and 8352-8359 |
| `exp2_20260703_0001` | 许昌市城投发展集团有限公司 | `nominal_exit` | `doc_exp2_20260703_0001_013`, lines 1216-1222 and 1230-1238 | `doc_exp2_20260703_0001_013`, lines 3912-3975 and 4316-4361 |

The promoted cases share the same coding logic. Each packet contains formal no-government-financing or no-local-government-debt language, usually dated to the post-2015 regulatory regime. Each packet also contains evidence that the issuer or issuer group continued to perform public-development functions after the formal compliance event. These functions include infrastructure investment and construction, land development or land sorting, entrusted construction, fiscal settlement, government-linked receivables, policy project repayment, fiscal subsidies, or delegated project-management roles.

The labels are therefore coded as `nominal_exit`, not because the documents prove illegal borrowing, but because official compliance language does not show that the fiscal function disappeared or moved outside the issuer group. Several cases contain negative compliance evidence, such as denials of BT, PPP repurchase, land-reserve, advance construction, or direct fiscal repayment arrangements. Those denials are retained in the caveats and alternative-label fields because they matter for distinguishing nominal exit from formal fiscal substitution.

## Boundary Decision

`sch_20260630_0129`, 北京控股集团有限公司, was marked `boundary_reviewed`. The packet contains formal no-government-financing language, and a related repeated Beijing Controls Group packet had already been boundary-reviewed. The issuer is a large diversified Beijing municipal SOE with utilities and infrastructure exposure rather than a clean city-platform LGFV. The available continued-function evidence is also too generic for the core exit-type typology. The packet is useful for defining scope conditions, but it should not enter the gold-standard city-platform sample.

## Dataset Effect

After this batch, the human gold-standard label file contains 94 cases. The new cases raise the number of human-validated nominal-exit labels while preserving a separate boundary category for non-core issuers. Rebuilding the seed pool and Codex surrogate files should reduce the non-overlap surrogate queue, keep the usable surrogate sample above the current target range, and improve the DSL validation overlap between surrogate labels and gold-standard labels.
