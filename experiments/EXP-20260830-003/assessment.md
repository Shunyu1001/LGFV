# Assessment

## Result

The default DSL command now selects the authoritative expanded 2026-07-03
issuer file. It reads 158 issuer-level surrogate rows, including 61 issuers
that overlap gold labels and 97 non-overlap issuers. A regression check runs
the default and explicit-authoritative commands in temporary directories and
verifies byte-identical diagnostic CSV, adjusted-distribution CSV, and LaTeX
outputs.

Rebuilding the tracked DSL outputs with both commands produced no research
output diff. The change repairs command provenance without changing the
one-sided screening estimand or any reported result.

## Hard gates

- Frozen inputs and estimand unchanged: pass.
- Default and explicit input identifiers traceable: pass.
- Authoritative counts reproduced: pass.
- Deterministic regression check: pass.
- Result direction or significance used for selection: no.
- Adverse or failed commands omitted: no failures occurred.

## Status

`keep`. The change repairs the reproducibility defect recorded in `R-002`
without changing authoritative outputs.

## Limitations

The regression check establishes input selection and output identity only. It
does not extend the current one-sided precision evidence to recall or
four-class classification performance.
