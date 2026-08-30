# Assessment

## Result

The audit maps 33 empirical quantities in the empirical section to generated
CSV rows or declared formulas. Thirty reported values match their generated
sources at the displayed precision. The three mismatches are the effect sizes
recorded in `R-001`: the manuscript reports 6.3, 17.1, and 13.5 percentage
points, whereas the generated pilot LPM coefficients imply 6.6, 16.1, and
12.5 percentage points.

The strict check exits with status 1 while these discrepancies remain in the
manuscript. This is the intended integrity behavior. Tests verify that the
current audit identifies exactly these three discrepancies and no missing or
ambiguous mappings.

## Hard gates

- Generated source and transformation recorded for each mapped quantity:
  pass.
- Existing manuscript left unchanged: pass.
- Outcome, sample, model, and rounding rules unchanged: pass.
- Significance or sign used to choose a value: no.
- Failed and retried attempts retained: pass.
- Proposed text and ledger changes confined to artifacts: pass.

## Status

`keep`. The experiment converts a critical reporting discrepancy into a
deterministic, machine-checkable audit and supplies a minimal correction for
coordinator review.

## Limitations

The audit covers empirical sample counts, effect sizes, screening-flow counts,
validation rates, and adjusted descriptive counts in
`paper/sections/empirical_strategy.tex`. It does not verify qualitative case
descriptions, citations, mathematical derivations, or quantitative claims in
other manuscript sections. Because this workstream may not edit the paper,
the strict check will continue to exit 1 until the coordinator applies the
reviewed correction.
