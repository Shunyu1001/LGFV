# LGFV Exit Types

This repository contains a research project on local government financing vehicle
(LGFV) exit reform in China. The project studies why some localities achieve
substantive exit from government financing functions while others display nominal
exit, functional transfer, or liquidation.

## Project Structure

- `paper/`: LaTeX paper draft.
- `coding/`: coding protocol and LLM-assisted labeling prompts.
- `data/candidate_city_plan.csv`: first-stage candidate city list for source
  collection. This is a sampling plan, not an empirical dataset.
- `data/source_inventory_template.csv`: document-level source tracking
  template.
- `data/labeling_template.csv`: case-level LLM and human-validated labels.
- `data/analysis_inputs/`: small tracked intermediate datasets used for
  empirical construction, including the pilot coding matrix.
- `data/diagnostics/`: small tracked reports about downloaded source data,
  schemas, and coverage.
- `data/raw/`: original source materials, such as announcements, bond
  prospectuses, rating reports, and registration records.
- `data/processed/`: coded datasets and cleaned variables, including
  `human_validated_labels.csv`.
- `scripts/`: workflow notes and future scripts for extraction, labeling, and
  validation.
- `docs/`: notes, memos, and project documentation.

## Core Research Design

The central measurement contribution is to disaggregate official LGFV exit into
four institutional types:

1. Substantive exit
2. Nominal exit
3. Functional transfer
4. Liquidation

The coding workflow is designed as LLM-assisted, human-validated coding. Large
language models can generate preliminary labels using a fixed codebook, but final
labels are assigned after human review of the original source documents.

## Current Workflow

The current gold-standard file contains 94 human-reviewed city-platform cases.
The historical-capacity analysis uses 84 matched gold cases. The expanded LLM
screen contains 203 disclosure-level surrogate labels, which collapse to 158
issuer-level rows. These surrogates are a one-sided screen for nominal exit and
are not treated as a validated four-class classifier.

## Autoresearch Quick Start

1. Read `immutable/research_charter.md`, `AGENTS.md`, and `program.md`.
2. Run `python3 scripts/validate_immutable.py`.
3. Inspect `ledgers/research_state.yaml` and open critical issues in
   `ledgers/reviewer_issues.tsv`.
4. Create one pre-result experiment brief under `experiments/`.
5. Run the fixed evaluation command in `AGENTS.md`.
6. Append `ledgers/experiments.tsv` and update affected claims or sources.

The measurement framework is the primary contribution. The historical-state-
capacity results are currently exploratory and associational. Parallel work is
performed in isolated `codex/` worktrees; only reviewed changes are merged to
`main` and synchronized to Overleaf.
