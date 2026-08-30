# EXP-20260830-013 Manuscript integration audit

## Loop

Manuscript integration and consistency.

## Falsifiable bottleneck

The manuscript predates the retained measurement, empirical, source,
literature, and mechanism audits. It therefore overstates the validation
design, reports three stale numerical quantities, leaves the historical
application more prominent than the measurement contribution, and does not
yet cite the verified adjacent literature.

## Hypothesis

The retained audit results can be integrated without changing labels, data,
models, or source packets, producing a shorter measurement-first manuscript
whose numerical claims pass the narrative audit and whose inferential limits
are explicit.

## Success criteria

- State that the 94 reference labels were reviewed by the project author and
  were not independently double-coded.
- Describe the 61 overlapping issuers as a selected-overlap consistency check,
  not as probability-sample precision, recall, calibration, or multiclass
  validation.
- Report 94 resolving evidence identifiers, 93 complete local source packets,
  94 recovery-URL packets, and 62 exact evidence memos.
- Correct the three audited historical-association quantities to 6.6, 16.1,
  and 12.5 percentage points.
- Move rank-deficient and sparse adjusted specifications out of the main
  empirical argument and disclose their diagnostics.
- Integrate the verified literature with a bounded novelty claim.
- Pass immutable, ledger, unit-test, citation, numerical-narrative, and LaTeX
  compilation checks.

The experiment is kept only if all factual checks pass and the revised
manuscript does not imply that planned probability validation, independent
coding, or validation-adjusted estimation has already occurred. It is
quarantined if bibliography or compilation checks fail. It is discarded if
the revision changes data, labels, or estimates.

## Permitted files

- `paper/**`
- manuscript-facing table builders and numerical narrative audit scripts
- `experiments/EXP-20260830-013/**`
- central ledgers after the manuscript passes its checks

Data, source packets, codebooks, model inputs, and generated empirical
estimates are out of scope.

## Inputs

- Base commit: `bf1bd7b`
- Retained experiments: EXP-20260830-002 through EXP-20260830-010
- Existing uncommitted introduction, literature, theory, research-design, and
  abstract edits initiated after those retained results were reviewed

## Commands

```text
python3 scripts/audit_empirical_narrative_numbers.py --check
python3 scripts/validate_immutable.py
python3 scripts/validate_ledgers.py
python3 -m unittest discover -s tests -p 'test_*.py'
cd paper && latexmk -g -pdf -interaction=nonstopmode -halt-on-error main.tex
```

## Budget

- One integration pass across the abstract, introduction, literature, theory,
  research design, coding strategy, empirical evidence, conclusion, and
  bibliography.
- No new statistical model, label, source claim, or outcome-dependent choice.

## Registration note

Section-level revision began after the relevant audit results were retained.
This brief freezes the remaining integration checks before compilation and
outcome assessment; it is not represented as a pre-result registration.
