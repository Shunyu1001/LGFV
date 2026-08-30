# Surrogate Expansion Without Gold-Label Promotion, July 3 2026

This note records the follow-up expansion requested after the expanded surrogate validation batch. No new cases were added to `data/processed/working_reference_labels.csv`. The working-reference file remains fixed at 94 working-reference labels.

The expansion has two parts. First, a third Shanghai Clearing harvest pass added two previously unseen disclosure packets to the candidate pool: Qinghai State-Owned Assets Investment Management and Changzhou Urban Construction Group. The Changzhou packet produced a new Codex surrogate `nominal_exit` label after key PDFs were downloaded and extracted.

Second, the Codex screening rule was extended to cover formal compliance language that states the issue will not increase government debt or hidden debt, will not form government debt, or leaves repayment responsibility outside the local state. This is consistent with the codebook's nominal-exit rule, which treats legal language that new debt is not local-government debt as formal compliance evidence when the same packet also shows continuing public-project functions. The rule still does not assign a working reference label. Promotion requires full source-packet review, and any promoted label remains pending independent human confirmation.

After rebuilding the screening files, the current counts are:

| Quantity | Count |
|---|---:|
| Working-reference labels | 94 |
| Candidate disclosure rows | 361 |
| Usable LLM screening rows | 346 |
| LLM surrogate exit-type labels | 203 |
| Source-screened rows with no direct formal event | 44 |
| Source-packet-reviewed boundary packets | 5 |
| Source-missing rows | 15 |
| Usable exit-type rows | 297 |
| Issuer-level surrogate rows | 158 |
| Surrogate issuers overlapping working references | 61 |
| Non-overlap surrogate issuers queued for human review | 97 |
| Working reference plus non-overlap diagnostic file | 191 |

The main caution is that the expanded surrogate pool is broader than the working-reference sample. Some additional surrogate rows are specialized transportation, construction, state-capital, or provincial SOE packets. They are useful for screening and for DSL-style surrogate adjustment, but they should not be treated as final city-platform LGFV labels until the validation protocol checks scope and line-level evidence.

The issuer-level empirical input has 252 rows: 94 working-reference outcomes, 61
surrogate overlap checks, and 97 non-overlap surrogate auxiliary rows. Only the
working-reference rows and non-overlap surrogate rows are marked for the
a combined diagnostic file. The overlap checks measure selected concordance,
not population precision, and they are not counted as new observations.
