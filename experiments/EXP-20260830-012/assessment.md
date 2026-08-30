# Assessment

## Result

The audit reproduces the frozen 84-case historical-only LPM and repairs the
exact alias in the 78-case adjusted design. The legacy adjusted matrix has
nine columns and rank eight because the two platform indicators sum to the
intercept. With district/county platforms as the reference category, the
corrected matrix has eight columns, rank eight, and a condition number of
6.10. The sample, outcome, exposure, and nonredundant regressors are unchanged.

The fixed historical-only models give probability-scale effects of 0.0664 for
the LPM and 0.0555 for the Firth-logit average marginal effect. Their 95 percent
diagnostic intervals are -0.0131 to 0.1459 and -0.0079 to 0.1190,
respectively. Both estimators converge, and the elite-density effect retains
its sign under every case deletion. The leave-one-out ranges are 0.0485 to
0.0825 for the LPM and 0.0434 to 0.0671 for Firth logit. Changshu is the most
influential case under both estimators, with absolute changes of 0.0179 and
0.0122.

The corrected adjusted models give probability-scale effects of 0.0054 for
the LPM and 0.0035 for Firth logit. Their diagnostic intervals are -0.0834 to
0.0943 and -0.0979 to 0.1049. Both estimators converge, but the design has only
1.5 events per independent column. The LPM effect ranges from -0.0095 to
0.0230 and changes sign in 9 of 78 deletions; the Firth effect ranges from
-0.0097 to 0.0184 and changes sign in 11 of 78 deletions. Taizhou is most
influential for the adjusted LPM, while Foshan is most influential for the
adjusted Firth model.

Complete-control selection also remains nonneutral. All six excluded
matched-gold cases are nominal exits, and their mean elite density is -0.726
standard deviations in the matched sample, compared with 0.056 among the 78
included cases. This comparison is descriptive because the excluded group is
small and no missing value is imputed. Province fixed effects are not
estimated: the diagnostic candidate would have 25 independent columns for 12
events, and only 4 of 18 provinces have within-province outcome variation.

## Hard gates

- Frozen outcome, exposure, sample flags, controls, labels, and crosswalk
  inputs unchanged: pass.
- Legacy rank deficiency reproduced and reference-category repair verified:
  pass.
- All four predeclared models and all leave-one-out attempts reported: pass.
- Model-specific sample size, event support, rank, convergence, uncertainty,
  selection, and influence reported in machine-readable form: pass.
- Missing contemporary controls imputed: no.
- Province fixed effects estimated despite insufficient support: no.
- Specification selected by sign or significance: no.
- Central ledgers and existing manuscript prose changed: no.
- Generated table and plot labeled exploratory: pass.

## Status

`keep`. The experiment corrects an implementation defect and supplies a
reproducible sparse-outcome audit while preserving the null and unstable
adjusted evidence. Any change to the reported main specification or manuscript
claim remains `quarantine` pending coordinator and human review.

## Review-gated interpretation

The 84-case historical-only LPM can remain a descriptive associational
baseline because it follows the frozen estimand and uses every matched gold
case. The fixed Firth result can be reported as a rare-outcome sensitivity
diagnostic. Neither estimate supports a causal interpretation, and their
diagnostic intervals include zero.

The corrected adjusted coefficient should not be presented as stable main-text
evidence. This recommendation follows from complete-case selection, 1.5 events
per independent column, and the case-deletion results rather than from the
coefficient's sign or statistical significance. If the coordinator retains
the adjusted results for transparency, they should appear as explicitly
exploratory appendix diagnostics together with the selection and influence
outputs.

## Limitations

Firth-logit uncertainty is based on inverse-information curvature and a
delta-method average marginal effect, so it is diagnostic rather than a
small-sample coverage guarantee. Leave-one-out analysis measures sensitivity
to individual cases but does not address correlated cities, outcome
misclassification, historical crosswalk error, contemporary-control
provenance, or sample representativeness. The audit cannot recover liquidation
cases, distinguish the two substantive exits from the ten functional
transfers in a stable multinomial model, or justify province fixed effects
with the observed event allocation.
