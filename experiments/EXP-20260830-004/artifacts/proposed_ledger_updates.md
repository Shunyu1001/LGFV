# Proposed ledger updates

## Experiments ledger

Append a row for `EXP-20260830-004` with loop `claim_evidence`, base commit
`e178e195704fe6ad6ec353a28081e444995350e7`, status `keep`, artifact path
`experiments/EXP-20260830-004`, and the following result summary:

> A deterministic audit mapped 33 empirical narrative quantities to generated
> outputs. Thirty match; the three `R-001` effect sizes should be corrected
> from 6.3, 17.1, and 13.5 to 6.6, 16.1, and 12.5 percentage points.

Record the two permitted mechanical retries and note that the strict audit
continues to exit 1 until manuscript review and correction. The coordinator
should add the reviewed trial commit.

## Claims ledger

For `C-004`, propose adding `EXP-20260830-004` to `evidence_ids` after the
coordinator applies the numerical correction. The claim wording, scope,
associational status, and limitations do not require expansion.

## Reviewer issue

Keep `R-001` open on this branch. Propose closing it only after the coordinator
applies the numerical correction and reproduces a zero-mismatch strict audit.
Use `experiments/EXP-20260830-004/artifacts/narrative_number_audit.csv` as the
traceable evidence record.
