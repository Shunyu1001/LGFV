# Current measurement estimands

## Scope

This report audits the tracked human labels, disclosure-level screening file,
issuer-level surrogate summary, validation queues, and validation memos. It
does not change a gold label or treat a proposed validation design as completed
evidence. The machine-readable estimand map is stored in
`data/validation/current_measurement_estimands.csv`.

## Current evidence

The tracked files reproduce all declared counts. The gold file contains 94
city-platform cases: 2 substantive exits, 82 nominal exits, 10 functional
transfers, and no liquidation cases. The screening file contains 262 candidate
disclosure rows, of which 203 receive the one-sided nominal-exit surrogate, 44
have usable text but no direct formal event identified by the screen, and 15
have missing source packets. The 203 positive disclosure rows collapse to 158
named issuers. The 44 no-formal-event rows collapse to 36 named issuers. The 15
source-missing rows have blank issuer names and therefore cannot be treated as
one deduplicated issuer.

The current files identify four descriptive quantities. First, they identify
the exit-type distribution within the assembled 94-case gold file. Second,
they identify screening flow and source attrition within the 361 tracked
disclosure rows. Third, they identify the reduction from 203 positive
disclosures to 158 positive issuers. Fourth, they identify nominal-label
concordance in the 61 issuers that appear in both the surrogate-positive and
gold files. All 61 surrogate labels and all 61 corresponding gold labels are
nominal exit.

The last quantity is conditional concordance in a post-hoc overlap rather than
positive predictive value for a defined target population. The overlap was not
drawn with known inclusion probabilities, all 61 cases have the same label,
and all 61 reviewer fields record Codex-assisted review by the same identified
human reviewer. A Jeffreys adjustment or Wilson interval can smooth the
observed boundary value, but it cannot correct the unknown overlap selection
or justify transporting the result to the 97 non-overlap positive issuers.

## Unidentified quantities

Five measurement quantities remain unidentified. First, positive predictive
value among the positive issuers is not identified because the 97 non-overlap
positive issuers lack independent human labels and the 61 overlap inclusion
probabilities are unknown. Second, recall is not identified because none of the
36 named screen-nonpositive issuers overlaps with the gold file. Third,
calibration is not identified because the current output contains categorical
evidence confidence rather than a frozen predicted probability. Fourth,
four-category error is not identified because the surrogate rule emits only
nominal exit and the gold file contains no liquidation case. Fifth,
inter-coder agreement is not identified because no case has labels from two
independent human coders.

The existing `dsl_surrogate_diagnostics.csv` reports `61/61` as raw nominal
precision, and `dsl_augmented_outcome_distribution.csv` transports smoothed
versions of that quantity to the 97 non-overlap issuers. The arithmetic is
reproducible, but the population precision and adjusted outcome counts are not
identified by the current overlap mechanism. They should not support a
measurement-performance claim until an approved probability validation sample
is completed.

## Proposed probability validation design

The current files support a bounded design for the one-sided screen. The fixed
source-available, non-overlap frame contains 133 named issuers: 97 positive
issuers and 36 issuers for which the screen found no direct formal event. After
human approval of the validation design, draw a simple random sample of 60
positive issuers without replacement and review all 36 nonpositive issuers.
The corresponding inclusion probabilities are (60/97) and 1. The 15
source-missing rows remain in a separate coverage and attrition audit until
their issuer identities and source availability are resolved.

The human reviewer must receive the original source packet and frozen codebook
without the surrogate label, model rationale, or existing outcome. For each
selected issuer, the reviewer records eligibility, the formal event, the
post-event function, the four-category label or `unclear`, the alternative
label, source coverage, and the remaining caveat. Design-weighted estimates can
then report positive predictive value, false-negative behavior, and recall
within this fixed 133-issuer candidate frame. These quantities would not be
national prevalence or national classifier-performance estimates.

This design validates the one-sided screen rather than a four-category
classifier. A future multiclass validation study would require four-category
predictions and probability scores frozen before human outcomes are opened,
followed by probability-sampled independent human labels from the same eligible
frame.

## Independent human work

Closing the human-label reliability issue requires a real second human coder.
The strongest current-sample design is for that coder to label all 94 frozen
gold packets without seeing the existing human or LLM labels. The original
reviewer and second coder then adjudicate every disagreement against the source
packet and record whether the disagreement concerns the formal event,
post-event function, related-entity scope, source hierarchy, or an edge-case
rule. The report can then provide raw agreement, category-specific agreement,
Cohen's kappa or an appropriate sparse-category alternative, and adjudication
counts for the assembled sample. Liquidation-specific agreement will remain
unobserved because no gold case has that label.

## Review gate

Changing the validation sampling design is review-gated under `program.md` and
the immutable charter. This experiment defines but does not draw the proposed
sample. Human approval is required for the 133-issuer target frame, the
60-of-97 positive allocation, the census of 36 screen-nonpositive issuers, the
handling of 15 source-missing rows, and the independent recoding of all 94 gold
cases.
