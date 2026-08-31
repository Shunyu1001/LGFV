# Experiment brief: Manuscript label-role disclosure

## Registration

- Experiment: `EXP-20260831-092`
- Registered: `2026-08-31T12:28:00+08:00`
- Loop: `prose_claims`
- Base commit: `13c837d16d9ff11daaad72d443ae0a995ebaa21a`
- Branch: `codex/manuscript-label-role-disclosure`

## Falsifiable bottleneck

The manuscript now discloses that the 94 current outcomes are Codex
source-packet working references pending independent human confirmation, but
two sentences still call a current outcome gold or human. Three claims-ledger
scope fields retain the same obsolete terminology. These strings contradict
the canonical role registry even though the surrounding limitations are
correct.

## Hypothesis and success criteria

A narrow prose-only correction can remove the five false current-data role
descriptions while preserving conceptual statements about the independent
human outcomes required by a future design-based supervised-learning analysis.
Success requires:

1. current labels are described only as working-reference labels or outcomes;
2. statements about future independent human coding remain unchanged;
3. no number, citation key, LaTeX label or reference, mathematical expression,
   empirical result, limitation, or section structure changes;
4. all repository validators pass; and
5. the paper compiles to 78 pages.

## Permitted files

- `paper/sections/coding_strategy.tex`
- `paper/sections/empirical_strategy.tex`
- `ledgers/claims.csv`
- `experiments/EXP-20260831-092/**`
- one append-only row in `ledgers/experiments.tsv`

No other manuscript, data, code, figure, table, immutable, validation-frame,
or result file may change.

## Registered execution

```text
rg -ni "human|gold|author-reviewed|working-reference" paper/sections
python3 scripts/validate_immutable.py
python3 scripts/validate_ledgers.py
python3 scripts/audit_empirical_narrative_numbers.py
latexmk -g -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The compile command runs from `paper/`. The budget is five exact terminology
replacements and one coherence read of the surrounding paragraphs.
