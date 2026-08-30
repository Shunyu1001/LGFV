# Assessment

## Result

The gold-label, historical-match, expanded-surrogate, full-control, and PDF
counts reproduce. The authoritative rebuild leaves no tracked diff. The DSL
adjustment script does not reproduce the current manuscript when run with its
default input because that default points to the 2026-07-02 issuer summary.
Passing the expanded 2026-07-03 issuer summary reproduces 61 overlap and 97
non-overlap issuers.

## Hard gates

- Frozen inputs identified: pass.
- Baseline result direction ignored: pass.
- All failed and successful commands recorded in the task history: pass.
- Tracked output restored after the unintended old-input build: pass.
- Authoritative build reproducible: pass.

## Status

`keep`. The run reproduces the current baseline and identifies a concrete
pipeline-default defect. The defect becomes the first empirical worktree
experiment; it does not change a research result.
