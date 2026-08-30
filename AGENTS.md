# LGFV Research Repository Rules

This repository uses an auditable academic autoresearch workflow. Read the
following files before making substantive changes:

1. `immutable/research_charter.md`
2. `immutable/analysis_plan.md`
3. `immutable/evaluation_protocol.md`
4. `immutable/data_manifest.yaml`
5. `ledgers/research_state.yaml`
6. `program.md`

## Research boundaries

- Treat the measurement framework as the primary contribution.
- Treat the historical-state-capacity analysis as exploratory and
  associational unless a later approved design justifies stronger language.
- Do not change the four exit-type definitions, gold-label inclusion rules,
  main outcome coding, or validation design without a change request.
- Do not reward significance, a preferred sign, or a more persuasive story.
- Preserve null, negative, contradictory, and failed results.
- Never overwrite raw source material. The tracked inventories are manifests,
  not substitutes for the underlying source packets.

## Experiment discipline

- One experiment addresses one falsifiable bottleneck.
- Create `experiments/EXP-YYYYMMDD-NNN/brief.md` before execution.
- Record the base commit, permitted files, success criteria, commands, and
  budget before seeing the result.
- Append every attempt to `ledgers/experiments.tsv`.
- Update `ledgers/claims.csv` before changing a material manuscript claim.
- Use `keep`, `discard`, `quarantine`, `crash`, or `invalid` as defined in
  `program.md`.
- Work on an isolated `codex/` branch or worktree. The coordinator owns merges
  to `main`, the paper build, and Overleaf synchronization.

## Writing

Before editing academic prose, read
`/Users/shunyuhao/Desktop/GAN GSC/SKILL.md` when it is available. In
particular, use plain descriptive section titles, define each term once, keep
one term per concept, remove duplicated claims across sections, and avoid
dramatic fragments, branded phrasing, rhetorical italics, and decorative
metaphors. Use `---` rather than the Unicode em dash in LaTeX. Do not change
numbers, citation keys, labels, references, or mathematical content during a
prose-only pass.

## Required checks

Run the relevant subset of these commands after changes:

```text
python3 scripts/validate_immutable.py
python3 scripts/validate_ledgers.py
python3 scripts/validate_labels.py
python3 scripts/validate_master_case_pool.py
python3 scripts/build_pilot_capacity_summary.py
python3 scripts/build_pilot_empirical_models.py
python3 scripts/build_dsl_surrogate_adjustment.py --issuers data/analysis_inputs/codex_surrogate_issuer_summary_2026_07_03_expanded.csv
python3 scripts/build_surrogate_empirical_core.py
python3 scripts/build_empirical_case_panel.py
python3 scripts/build_controlled_empirical_models.py
latexmk -g -pdf -interaction=nonstopmode -halt-on-error paper/main.tex
```

The DSL adjustment command must use the expanded issuer file until its default
is repaired and independently checked.
