# LGFV Exit Types

This repository contains a research project on local government financing vehicle
(LGFV) exit reform in China. The project studies why some localities achieve
substantive exit from government financing functions while others display nominal
exit, functional transfer, or liquidation.

## Project Structure

- `paper/`: LaTeX paper draft.
- `coding/`: coding protocol and LLM-assisted labeling prompts.
- `data/pilot_case_plan.csv`: first-stage pilot city list for source
  collection.
- `data/source_inventory_template.csv`: document-level source tracking
  template.
- `data/labeling_template.csv`: case-level LLM and human-validated labels.
- `data/raw/`: original source materials, such as announcements, bond
  prospectuses, rating reports, and registration records.
- `data/processed/`: coded datasets and cleaned variables.
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

## Pilot Workflow

The first empirical step is a 20-30 case pilot. The pilot starts from
`data/pilot_case_plan.csv`, records documents in
`data/source_inventory_template.csv`, and stores preliminary and final labels in
`data/labeling_template.csv`. The goal is to validate the coding categories and
source hierarchy before scaling the project to a larger sample.
