# Surrogate Expansion Without Gold-Label Promotion, July 3 2026

This note records the follow-up expansion requested after the expanded surrogate validation batch. No new cases were added to `data/processed/human_validated_labels.csv`. The gold-standard file remains fixed at 94 human-validated labels.

The expansion has two parts. First, a third Shanghai Clearing harvest pass added two previously unseen disclosure packets to the candidate pool: Qinghai State-Owned Assets Investment Management and Changzhou Urban Construction Group. The Changzhou packet produced a new Codex surrogate `nominal_exit` label after key PDFs were downloaded and extracted.

Second, the Codex screening rule was extended to cover formal compliance language that states the issue will not increase government debt or hidden debt, will not form government debt, or leaves repayment responsibility outside the local state. This is consistent with the codebook's nominal-exit rule, which treats legal language that new debt is not local-government debt as formal compliance evidence when the same packet also shows continuing public-project functions. The rule still does not assign a final label. It only creates a surrogate label that requires human validation before entering the gold-standard file.

After rebuilding the screening files, the current counts are:

| Quantity | Count |
|---|---:|
| Human gold-standard labels | 94 |
| Candidate disclosure rows | 312 |
| Usable LLM screening rows | 297 |
| LLM surrogate exit-type labels | 163 |
| Source-screened rows with no direct formal event | 35 |
| Human-reviewed boundary packets | 5 |
| Source-missing rows | 15 |
| Usable exit-type rows | 257 |
| Issuer-level surrogate rows | 120 |
| Surrogate issuers overlapping gold labels | 61 |
| Non-overlap surrogate issuers queued for human review | 59 |

The main caution is that the expanded surrogate pool is broader than the gold-standard sample. Some additional surrogate rows are specialized transportation, construction, state-capital, or provincial SOE packets. They are useful for screening and for DSL-style surrogate adjustment, but they should not be treated as final city-platform LGFV labels until the validation protocol checks scope and line-level evidence.
