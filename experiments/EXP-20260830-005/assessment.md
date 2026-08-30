# Assessment

## Result

The diagnostic reproduces the 84-row matched-gold sample, its 12
institutional-change cases, and the pilot elite-density LPM coefficient at the
reported precision. The 12 events consist of 2 substantive exits and 10
functional transfers.

Three findings limit the adjusted historical-capacity claim. First, the
78-row complete-control subset retains all 12 events, while the 6 excluded
matched-gold cases are all nominal exits. The excluded cases also have lower
elite density: their matched-sample standardized mean is -0.726, compared
with 0.056 in the complete-control subset. The excluded group is too small for
a reliable selection model, but complete-case analysis is not neutral with
respect to the outcome or exposure.

Second, the simple historical-only association is similar across the fixed
links and retains its sign under every case deletion. In the 84-row sample,
the LPM probability effect is 0.0664, and the conventional and Firth logit
average marginal effects are 0.0538 and 0.0555. The LPM leave-one-out range is
0.0485 to 0.0825. Restricting the same historical-only model to the 78
complete-control rows gives corresponding effects of 0.0618, 0.0521, and
0.0538, with an LPM leave-one-out range of 0.0433 to 0.0782. These fixed
comparisons are sensitivity diagnostics, not a basis for selecting a link.

Third, the current full available-control design is rank deficient. Its nine
columns have rank eight because every complete-control row is in exactly one
of two platform categories, so the intercept equals the district/county dummy
plus the prefecture/municipal dummy. The design also has only 1.33 events per
observed column. The elite-density probability-scale estimates are near zero
under the LPM, conventional logit, and Firth logit, but the current
parameterization must be corrected before coefficient interpretation. The
full-control LPM leave-one-out effect ranges from -0.0095 to 0.0230 and changes
sign in 9 of 78 deletions.

## Hard gates

- Frozen outcome, exposure, sample flags, and inputs unchanged: pass.
- Missing contemporary controls imputed: no.
- All predeclared links and model samples reported: pass.
- Convergence failures suppressed: none occurred.
- Rank deficiency and adverse influence results retained: pass.
- Specification chosen by sign or significance: no.
- Existing model outputs and manuscript left unchanged: pass.

## Status

`keep` for the diagnostics. They add reproducible information about sparsity,
complete-case selection, rank, and influence. The proposed correction to the
full-control encoding and any promotion of a bias-reduced model remain
`quarantine` pending review because this workstream may not change the main
specification.

## Current defensible analysis

Retain the 84-row matched-gold historical-only model as a descriptive
associational baseline because it follows the frozen estimand and uses every
matched gold case. Report the fixed logit and Firth comparisons as sensitivity
diagnostics if the coordinator approves them. This recommendation is based on
estimand alignment, observed-input coverage, matrix rank, and influence rather
than on coefficient sign or significance.

Do not interpret the current full-control coefficient until one platform
category is encoded as the reference and the corrected model is reproduced.
Even after that mechanical repair, the adjusted model remains an exploratory
diagnostic because 12 events cannot support a stable eight-column adjusted
claim in this nonrepresentative sample.

## Limitations

The diagnostics do not make the assembled sample representative, validate the
historical crosswalk, improve contemporary-control provenance, or identify a
causal effect. Firth standard errors in the artifact are curvature-based and
are included only to characterize the fixed sensitivity run. The
complete-control exclusion comparison is descriptive because only six cases
are excluded. The capacity-bin field is missing for 58 of the 84 matched panel
rows, so the recorded bin-composition comparison is incomplete even though
the continuous elite-density exposure is observed for all model rows. No
analysis can recover the absent liquidation outcome or
resolve the distinction between the two substantive-exit cases and the ten
functional-transfer cases within a stable multinomial model.
