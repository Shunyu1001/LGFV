# Evaluation Protocol

## Baseline invariants

The current reproducible baseline is commit
`8c5b4611d96fa1fe76dc77a87f6db816c7672b36`. It contains 94 gold labels, 84
historically matched gold rows, 361 candidate disclosures, 203 disclosure-level
surrogate labels, 158 issuer-level surrogate rows, 61 surrogate-gold overlaps,
97 non-overlap surrogate issuers, 78 first-pass full-control rows, and an
89-page compiled PDF.

## Integrity gate

A run fails the integrity gate if it changes a frozen object without approval,
uses an unverified material source, selects a result by sign or significance,
hides a failure or null result, mixes disclosure and issuer units, overwrites
raw material, or cannot identify its inputs and commands.

## Measurement loop

A measurement change is kept only if it improves a predeclared quantity such
as traceable source coverage, independently assessed agreement, calibration,
category-specific error characterization, or adjudication clarity. More labels
alone are not sufficient. Precision-only evidence cannot be described as full
classifier validation.

## Empirical loop

An empirical change is kept if it reproduces the baseline, corrects an actual
implementation or reporting error, adds a declared diagnostic, or yields a
more credible estimate without changing the estimand post hoc. Null and
attenuated estimates are valid results. Main-text effect sizes must match the
generated output after rounding.

## Literature loop

A source is kept when the original publication or authoritative document has
been opened, its metadata and relevant claim have been verified, and it fills
a defined coverage gap or changes a claim. Search snippets and inaccessible
summaries are discovery aids only.

## Claim and reviewer loops

A material claim must identify supporting artifacts or verified sources, its
scope, and its limitations. Reviewer issues are closed only by reproduced
evidence, a corrected implementation, a narrower claim, or an explicit
limitation. Rhetorical defense does not close an issue.

## Build and visual checks

The paper must compile without errors. Overfull boxes, broken references,
unreadable tables, excessive whitespace, and colored link boxes are recorded
as formatting issues. Before a submission candidate is accepted, representative
pages from the introduction, empirical core, figures, tables, appendix, and
references must be rendered and inspected.
