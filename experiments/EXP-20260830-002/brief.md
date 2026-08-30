# EXP-20260830-002 Source reconstruction audit

## Loop

Claim-evidence and reproducibility.

## Hypothesis

The gold-label file contains enough stable identifiers to resolve every cited
document and supplementary source against the tracked inventories, but at least
one case may still lack a complete local evidence packet or a dedicated evidence
memo.

## Success criteria

- Every primary and secondary document identifier resolves uniquely against
  `data/document_inventory.csv`.
- Every supplementary source identifier resolves uniquely against
  `data/source_inventory.csv`.
- Every gold case has at least one recoverable page or download URL.
- Local-file and evidence-memo coverage are reported case by case rather than
  treated as label-validation evidence.

The experiment is kept if it produces a complete case-level audit, including
negative findings. It does not upgrade confidence or change an exit label.

## Allowed changes

- Add one deterministic audit script.
- Add generated diagnostics and a reconstruction protocol.
- Update only the experiment and reviewer ledgers after the run.
- Do not edit gold labels, source inventories, the codebook, or the manuscript.

## Status rules

Keep a reproducible audit. Quarantine any case with an unresolved evidence
identifier. Record absent local files or memos as reconstruction gaps rather
than silently excluding the case.
