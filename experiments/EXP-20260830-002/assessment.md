# Experiment assessment

## Status

`keep`

The experiment passes the integrity gate and materially improves traceability
by separating a reproducible selected-overlap concordance from population
precision, recall, calibration, four-category error, inter-coder agreement,
and sampling error. The proposed validation draw remains review-gated and was
not executed.

## Results

All declared baseline counts were reproduced. The current positive surrogate
evidence consists of 203 disclosure rows collapsed to 158 issuers. Sixty-one
positive issuers overlap the gold file, and all 61 have nominal surrogate and
nominal gold labels. This quantity is descriptive concordance among the
observed overlap issuers. It does not identify positive predictive value for
the 158 positive issuers because overlap inclusion probabilities are unknown
and the 97 non-overlap positives have no independent human labels.

The source-available candidate screen also contains 36 named issuers for which
no direct formal event was identified. None overlaps the gold file, so recall
and false-negative behavior cannot be computed. The 15 source-missing rows
have blank issuer names and cannot yet be collapsed to issuer units. The
current output also lacks predicted probabilities and surrogate predictions
for substantive exit, functional transfer, and liquidation. Calibration and
four-category error are therefore not identified.

No independent double coding is documented. Ninety of the 94 gold rows record
Codex-assisted review by Shunyu Hao, including all 61 overlap rows. An LLM is
not an independent second human coder, so raw agreement, category-specific
agreement, kappa, and adjudication counts cannot be reported.

## Proposed next design

Subject to human approval, validate the one-sided screen in the 133 named,
source-available, non-overlap issuers. Draw 60 of 97 positive issuers by simple
random sampling without replacement and review all 36 screen-nonpositive
issuers. Record inclusion probabilities of (60/97) and 1, blind the human
reviewers to screen outputs, and use design weights for precision and recall
within this fixed candidate frame. Resolve the 15 source-missing rows
separately.

Separately, a second human should independently code all 94 frozen gold packets
and adjudicate every disagreement with the original reviewer. Because the gold
file contains no liquidation cases, the study cannot report observed
liquidation-specific agreement.

## Adverse and null findings preserved

- The existing `61/61` result does not identify target-population precision.
- Recall, calibration, multiclass error, and sampling error are not identified.
- Existing smoothed and Wilson calculations do not correct validation-sample
  selection.
- No independent inter-coder statistic can be computed.
- The current data cannot validate the four-category classifier described in
  prospective manuscript language.

## Gate decision

Keep the estimand map and reproducible audit. Quarantine the proposed sampling
allocation and any manuscript or ledger change until the human PI approves the
validation design. Do not update the gold labels, central ledgers, or paper on
the basis of this experiment alone.
