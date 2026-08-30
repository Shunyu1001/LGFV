# Handoff: Measurement validation

## Objective

Determine exactly what the current human and LLM labels validate, then create
the strongest honest validation design that can be implemented without
inventing a second human coder or treating one-sided screening as multiclass
classification.

## Primary reviewer issues

- `R-003`: no independently double-coded subset or agreement statistic.
- `R-004`: surrogate validation identifies positive predictive performance
  only; recall and four-class error remain unknown.

## Required first experiment

Audit `coding/codebook.md`, `paper/sections/coding_strategy.tex`, the gold label
file, the expanded screening file, the expanded issuer summary, and all
validation memos. Produce a measurement estimand map that states which unit,
sampling mechanism, and error quantity each existing table identifies. Do not
change gold labels.

## Permitted primary files

- `coding/`
- new scripts under `scripts/measurement_validation/`
- new outputs under `data/validation/`
- new reports under `docs/measurement_validation/`
- a proposed replacement subsection saved under
  `experiments/<EXP-ID>/artifacts/`

Do not directly edit the central ledgers, `paper/main.tex`, or existing paper
sections. Return proposed ledger rows and manuscript text to the coordinator.

## Success criteria

The work must separate precision, recall, calibration, category error, and
sampling error; define a feasible probability-based validation sample; report
what can be computed from current data; and identify the exact human work still
required. A second-coder statistic may be reported only if an independent
second human actually performs the coding.

Read `AGENTS.md`, `program.md`, the immutable files, and
`/Users/shunyuhao/Desktop/GAN GSC/SKILL.md` before writing prose.
