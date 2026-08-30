# Review-gated recommendation

## Recommended disposition

First, close reviewer issue `R-009` after independent review of the generated
rank diagnostic and regression test. The mechanical reference-category repair
restores full rank without changing the frozen sample, outcome, exposure, or
nonredundant controls.

Second, keep reviewer issue `R-006` open. The corrected adjusted design has 12
events across eight independent columns, excludes six low-capacity nominal
exits, and changes the elite-density effect's sign in 9 of 78 LPM deletions and
11 of 78 Firth-logit deletions. These limitations remain after the rank defect
is removed.

Third, retain the 84-case historical-only LPM only as an exploratory,
descriptive associational baseline, and report the fixed Firth-logit average
marginal effect as a rare-outcome sensitivity diagnostic if space permits. Do
not estimate province fixed effects with the current event allocation.

Fourth, remove the adjusted historical-capacity coefficient from the main text
as evidence of a stable association. If the adjusted models are retained for
transparency, move the complete fixed set, sample-selection comparison, and
influence diagnostics to an appendix. This recommendation is based on sample
support and deletion stability rather than coefficient direction or
statistical significance.

## Review requirements

The coordinator should verify the input checksums, rerun the audit and its
test, and review the Firth implementation before accepting the results. The
human PI retains authority over the main specification, claim wording, and
placement of the exploratory table and figure.
