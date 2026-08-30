# Review-gated decision

## Decision required

The coordinator and human PI should decide whether to authorize two changes
after independent reproduction:

1. Re-encode the full-control platform indicators with one reference category
   and rebuild the existing model outputs. This is a mechanical identification
   correction, but it affects a reported specification and therefore should
   be reviewed before integration.
2. Add conventional-logit and Firth-logit average marginal effects as fixed
   sparse-outcome sensitivity diagnostics. Neither link should replace the
   frozen descriptive LPM based on sign or significance.

## Recommendation

Approve the reference-category repair before any interpretation of the
current full-control table. Keep promotion of the Firth diagnostic and any
stronger adjusted historical-capacity claim review-gated. The current evidence
supports a descriptive associational baseline, not a stable adjusted or causal
claim.

## Evidence

- `design_alias_diagnostics.csv` records the exact dummy-variable alias.
- `sample_outcome_diagnostics.csv` records events and parameters.
- `sample_selection_diagnostics.csv` and
  `excluded_matched_gold_cases.csv` record complete-case selection.
- `functional_form_sensitivity.csv` reports all fixed links.
- `leave_one_out_influence.csv` records every case deletion.
