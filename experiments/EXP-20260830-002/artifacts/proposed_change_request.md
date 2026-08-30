# Proposed change request: Validation sampling design

## Decision requested

Approve or revise the target frame and allocation for the next one-sided
screen-validation stage. The proposal targets the 133 named,
source-available, non-overlap candidate issuers, samples 60 of the 97 positive
issuers by simple random sampling without replacement, and reviews all 36
screen-nonpositive issuers.

## Reason for review

The immutable charter and `program.md` require human approval before changing
the validation sampling design. The current 61-issuer overlap has no recorded
probability inclusion mechanism and contains no screen-nonpositive units, so
it cannot identify target-frame precision or recall.

## Proposed design

- Unit: issuer.
- Target: 133 named, source-available, non-overlap candidate issuers.
- Positive stratum: 97 issuers; sample 60 without replacement.
- Screen-nonpositive stratum: 36 issuers; review all 36.
- Inclusion probabilities: (60/97) and 1.
- Missing-source rows: retain 15 rows in a separate coverage audit until
  issuer identity and source availability are resolved.
- Blinding: human reviewers receive original packets and the frozen codebook,
  but not the surrogate label, rationale, or current outcome.
- Reporting: design-weighted positive predictive value, false-negative
  behavior, and recall within the fixed candidate frame; no national
  generalization.

## Separate human-reliability decision

Approve independent recoding of all 94 frozen gold packets by a real second
human coder. Record raw agreement, category-specific agreement, Cohen's kappa
or an appropriate sparse-category alternative, disagreement type, and
adjudication count. Liquidation-specific agreement cannot be observed because
the gold file contains no liquidation case.

## Alternatives for the PI

The PI may approve the proposed allocation, choose a different probability
allocation with recorded inclusion probabilities, or require a smaller pilot.
Any alternative must be frozen before cases or model outputs are opened and
must preserve the screen-nonpositive stratum needed to estimate recall.
