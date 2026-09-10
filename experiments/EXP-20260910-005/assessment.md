# Assessment

Disposition: keep the future-input implementation; actual-data use remains
quarantined pending separately verified approval, design, outcome eligibility,
selection, and complete human responses. This disposition does not approve a
frame, sampling design, outcome recoding, manuscript claim, or current DSL result.

## Results

The 29 implementation tests pass. Exhaustive enumeration covers all 32 binary
populations on a five-unit frame and all six positive allocations across strata
of sizes three and two, including each legitimate sample: 672 sample/population
combinations. Four additional enumeration exercises contribute 45 combinations,
for 717 total and 1,434 mean/projection evaluations within the enumeration helper.
Other direct checks cover additional fixtures and guard failures. Mean and
coefficient expectations match full-frame targets within 1e-10; whenever
estimable, average covariance estimates match exact enumeration covariance
within 1e-10, including coefficient cross-covariances. No Monte Carlo draws are
used and no test depends on favorable signs or statistical significance.

The checks include unequal sampling fractions, mixed census/SRSWOR designs,
singleton census and noncensus strata, inaccurate/negative/perfect predictions,
the zero-prediction Horvitz-Thompson case, constant residuals, no implicit
intercept, row-order invariance, sampled-X rank deficiency with full-frame rank,
nonfinite and missing inputs, duplicate IDs, incomplete responses, approval
mismatches, unknown/censored labels, AI-only provenance, unapproved pi, and
numeric error propagation. Points outside [0,1] are retained. Singleton
noncensus variance is unavailable rather than zero. The cross-fitting
counterexample yields a synthetic mean of 1.5 for a true mean of 1, demonstrating
why the exact fixed-design argument does not follow from cross-fitting alone.

The real-current-data regression check reads the unchanged 67-unit proposal and
24 proposed strata, verifies that all draw flags are false, and rejects numeric
estimation without inventing labels, X, predictions, approved IDs, or selection.
The ten no-direct-formal-event screen records are not converted into binary
zeroes. All actual-path positive contract checks use artificial fixtures rather
than LGFV records.

## Preserved failures

The first targeted run had 28 passing tests and one failing numerical-error
check. Constant auxiliary predictions of size 1e308 did not overflow in the
original implementation; they erased binary residual differences. The failure
prompted an explicit NumericalError when noncensus predictions cannot represent
the distinction between zero and one in residual arithmetic. The second run
passed all 29 tests. Census computation bypasses predictions and continues to
return the actual observed functional, including for extreme finite predictions.
The original failure log is retained; criteria and mathematical targets were not
changed after the result.

The full tests/ discovery run has 77 tests: 76 pass and one inherited historical
freeze-package check fails. That validator retains outdated protected hashes for
coding/codebook.md, coding/label_provenance.md, and
data/validation/label_role_registry.csv. Read-only git-object comparisons prove
that the validator and those three files are unchanged from the specified base
commit and that all three mismatches already exist there. They are not repaired
under this worker's scope. The full output and base comparisons are retained.

The immutable, global-ledger, label, master-case-pool, and current probability-
frame validators all exit zero. Label validation retains 89 existing warnings
about absent extracted source text. This work does not recover source archives.
The five checks also passed before implementation; the final full outputs are
in repository_checks.log. The paper was not built and empirical outputs were
not regenerated directly, because no analysis or prose changes were authorized.

## Equation review

The coordinator's finite-frame mean, SRSWOR finite-population correction, and
fixed-X projection match the implementation. One definitional clarification is
recorded in paper_review.md: each census variance contribution is zero by the
design, even when the within-stratum sample variance is undefined for a
singleton; an all-strata display must state that convention. The review also
notes that the analytical city-platform frame must map one-to-one to engine
issuer IDs. No paper was edited.

## Limitations and handoff

The API and mathematical derivation are in method.md. Documentary authenticity
and timing are external responsibilities, not established by string statuses
or SHA-256 hashes. No actual approval registry ships with the module. The
adapter must validate PI records, issuer identity, downstream outcome
eligibility, sampling execution, and human review before passing trusted
approvals. Missing response is never silently treated as nonselection. The
engine does not estimate a random subdomain, ratio target, nonresponse model,
cross-fitted model, national quantity, or causal effect, and reports no p-values
or confidence intervals. Actual validation inference remains unavailable.

Per explicit worker scope, no global ledger was edited. attempts.tsv preserves
local attempts and coordinator_ledger_row.tsv supplies an append-ready experiment
summary for coordinator review. The coordinator owns integration, the actual-data
adapter, manuscript changes, any ledger updates, merges, and synchronization.
