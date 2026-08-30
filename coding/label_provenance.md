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

Their status is `pending_human_confirmation`. They are not independently human
validated and may not be used to claim intercoder reliability, population
accuracy, or an error-free gold standard. A future human review may confirm,
revise, or reject each label. The frozen pre-confirmation label must remain in
the audit trail after that review.

## LLM Surrogate Labels

The Codex/ChatGPT surrogate files contain high-throughput screening labels
produced from candidate disclosures. The current rule is a one-sided nominal
exit screen. These labels are cheaper and narrower than the working reference
labels: they do not require full case-level documentary adjudication and do not
emit all four outcome categories. They may be used to prioritize source review
and, after a valid probability validation design exists, as noisy surrogate
outcomes in design-based supervised learning.

## Human-Confirmed Gold Labels

Human-confirmed gold labels do not yet exist as a completed project artifact.
They require a researcher to inspect the original source packet without seeing
the surrogate label, record an independent decision, and freeze that decision
before adjudication. The project will preserve the working reference label, the
independent human label, disagreement type, adjudicated label, and signatures.

Only this third layer can support claims of human validation and intercoder
agreement. Until it is complete, DSL corrections are design specifications or
provisional sensitivity exercises rather than final validation-adjusted
estimates.
