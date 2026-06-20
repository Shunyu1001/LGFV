# LGFV Exit Types

This repository contains a research project on local government financing vehicle
(LGFV) exit reform in China. The project studies why some localities achieve
substantive exit from government financing functions while others display nominal
exit, functional transfer, or liquidation.

## Project Structure

- `paper/`: LaTeX paper draft.
- `coding/`: coding protocol and LLM-assisted labeling prompts.
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

