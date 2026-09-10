# Label Provenance and Analytical Roles

The project separates labels by analytical role and provenance. The distinction
is about how a label was produced and what it may identify. It is not a claim
that one Codex run becomes an independent human coder by using a different
prompt.

## Working Reference Labels

`data/processed/working_reference_labels.csv` contains 94 source-packet labels.
Codex reviewed the retained documents case by case on behalf of the project
author and applied the frozen codebook. These labels are the project's working
reference outcomes and may be used as provisional gold labels for workflow
development, descriptive analysis, and model diagnostics.

The file is preserved as the pre-confirmation snapshot, including its historical
`pending_human_confirmation` metadata. Current status comes from the dated
confirmation register below rather than from overwriting that snapshot.

## LLM Surrogate Labels

The Codex/ChatGPT surrogate files contain high-throughput screening labels
produced from candidate disclosures. The current rule is a one-sided nominal
exit screen. These labels are cheaper and narrower than the working reference
labels: they do not require full case-level documentary adjudication and do not
emit all four outcome categories. They may be used to prioritize source review
and, after a valid probability validation design exists, as noisy surrogate
outcomes in design-based supervised learning.

## Human Check Confirmation

On 10 September 2026, Shunyu Hao reported that all 94 existing gold labels had
been checked by a human and no problems were found. The current reference
outcomes are therefore human-checked without revision, based on the author's
report. `data/validation/human_confirmation_report_2026_09_10.json` records
that statement and the exact snapshot hash. The derived
`data/validation/human_confirmation_register.csv` lists each covered case,
unchanged label, original producer, and report identifier.

The report date is not the actual review date. Reviewer identity, review date,
blinding, signatures, and independent pre-adjudication responses were not
provided and are not inferred. The blank independent-coding and adjudication
templates remain blank. The existing protocol for independent human decisions
and adjudication is unchanged. The author's confirmation records completion
of human checking; it does not establish an independent intercoder statistic,
error-free labels, or probability-sample accuracy.

The confirmation covers only these 94 outcome labels. Surrogate labels,
boundary cases, control variables, mechanism codes, and the separate 67-unit
probability-frame candidate do not inherit it. Final DSL correction still
requires an appropriate realized validation design and its outcome records.
