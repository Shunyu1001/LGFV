# Validation collection and inference

The 94 original reference labels have author-reported human confirmation.
The new 67-unit collection frame does not have an exact issuer/event match to
those labels. Neither a shared city nor a historical-capacity link supplies
the missing outcome. The checked reference file, new human collection,
surrogate screen, and numerical estimator remain separate records.

## Collection materials

After final frame and collection authorization, give each reviewer only the
unchanged codebook, `blinded_packets.csv`, `blinded_sources.csv`, and that
reviewer's own entry sheet from `data/validation/collection_2026_09_10/`.
Keep coordinator files, screening results, historical/debt covariates, the
other reviewer's decisions, and this diagnostic status out of the blinded
coding packet. The two entry sheets are templates, not completed human data.
Retain received records as new dated files rather than replacing the templates.

For each unit, the reviewer establishes the formal event and post-event
function, records source identifiers and locators, assesses exit-case
eligibility, and then assigns an allowed label when the evidence supports it.
Platform scope alone does not establish an exit case. Missing event evidence
does not mean nominal exit, non-substantive exit, or zero institutional change.
Unresolved evidence and eligibility decisions remain visible. Scores and
review metadata are supplied by the reviewer rather than filled by a model.

## Analysis inputs

The current 24-stratum allocation is a proposal to review all 67 units. Final
authorization, actual selection, received responses, and adjudication must be
recorded separately. A completed census has no label-selection variance, but
its outcomes can still have coding error and it does not represent all Chinese
LGFVs. The original 61/61 selected overlap is not the response set for this
new design.

The default status builder checks exact unit coverage and flags missing or
inconsistent human entries. A filled row is counted as a received entry only,
not authenticated as a human judgment. Source and review-process verification
is the coordinator's responsibility. The estimator contract is in
`experiments/EXP-20260910-005/method.md`; the analysis request must contain the
frozen frame, outcome definition, fixed predictions and covariates, vetted
approval, actual selected IDs, and complete eligible human responses.

The optional analysis dispatcher accepts an explicit request and separate
approval file. It checks consistency against the estimator contract; JSON
statuses and hashes do not prove that a person reviewed a packet or approved a
design. The approval's provenance must be independently verified before use.
Synthetic fixtures remain labeled synthetic. No completed request for the
current 67-unit frame is included in this release.

The status report keeps `collection` and `requested_analysis` as separate
objects. Success on a supplied request never changes the collection's missing
response counts or marks the current frame as estimated. Actual-mode requests
reject explicit synthetic identifiers throughout their provenance, including
reviewer and approval records. This guard still does not authenticate records.

## Current evidence

All four predeclared historical-only and adjusted models have been reproduced.
Their main-text table retains the small adjusted effects and broad uncertainty;
the human-check report does not change their covariates or precision.

The finite-screen bounds retain 97 unknown outcomes among the 158 screened
issuers. The 38.61--100 percent range conditions on the linked reference labels
being correct and applicable to the corresponding issuer/event. Without that
linkage assumption the range is 0--100 percent. These are identified sets,
not confidence intervals or estimated screening performance. The raw and
derived records remain available for source and linkage review.
