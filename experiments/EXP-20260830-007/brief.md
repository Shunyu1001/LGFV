# Experiment brief: Validation-frame integrity

## Experiment identity

- Experiment ID: `EXP-20260830-007`
- Loop: `empirical_simulation`
- Base commit: `fe2c98b9e86d15603804e06cb564c19310cf561d`
- Started at: `2026-08-30T13:10:00+08:00`
- Owner: measurement-validation worktree

## Falsifiable bottleneck

Experiment 002 proposed probability validation within 133 named,
source-available, non-overlap candidate issuers. This experiment tests whether
those issuers can be reconstructed as unique review units with sufficient
packet identifiers and whether a coder-facing instrument can omit every model
prediction and rationale. It does not test or alter labels.

## Hypothesis

The expanded screening file and validation queue support a deterministic
133-issuer frame with 97 one-sided screen-positive issuers and 36 issuers for
which the screen found no direct formal event. Every unit can be assigned a
unique normalized issuer key, source-row identifiers, pool identifiers, and
document identifiers. A separate blinded template can retain those identifiers
while excluding screen status, surrogate label, confidence, model rationale,
and any current human outcome.

## Inputs

- `data/analysis_inputs/llm_screening_sample_2026_07_03_expanded.csv`
- `data/analysis_inputs/surrogate_validation_queue_2026_07_03_expanded.csv`
- `data/analysis_inputs/codex_surrogate_labels_2026_07_03_expanded.csv`
- `data/processed/human_validated_labels.csv`
- `data/validation/validation_design_requirements.csv`

## Permitted files

- New scripts under `scripts/measurement_validation/`
- New outputs under `data/validation/`
- New reports under `docs/measurement_validation/`
- New files under `experiments/EXP-20260830-007/`

The experiment must not modify labels, central ledgers, existing paper files,
or the Experiment 002 outputs.

## Planned change

Add a deterministic frame builder that collapses source-available candidate
rows to named issuer units, excludes all gold overlaps, reconciles the 97
positive issuers against the existing human-review queue, and emits both an
internal design frame and a prediction-free coder template. The script will
not draw a sample or create a selected-case flag.

## Success criteria

1. The internal frame contains exactly 133 unique issuer units, divided into
   97 positive and 36 screen-nonpositive units.
2. Every positive unit matches exactly one row in the existing 97-row queue.
3. No frame unit overlaps the gold file or has a blank issuer, province, city,
   source-row identifier, pool identifier, or evidence-document identifier.
4. The coder template contains every frame unit but no prediction, stratum,
   confidence, rationale, existing label, or selection field.
5. The script makes no random draw and deterministic regeneration is
   byte-identical.
6. Repository integrity, ledger, label, and master-case-pool checks pass.

The experiment is kept if these gates pass. It is quarantined if the frame is
recoverable but has unresolved identifiers, and discarded or invalid according
to `program.md` otherwise.

## Commands

```text
python3 scripts/measurement_validation/build_validation_frame.py
python3 scripts/measurement_validation/build_validation_frame.py --check
python3 scripts/validate_immutable.py
python3 scripts/validate_ledgers.py
python3 scripts/validate_labels.py
python3 scripts/validate_master_case_pool.py
git diff --check
```

## Budget

- One deterministic frame-building script.
- At most two machine-readable frame outputs, one metrics file, one assessment,
  and one proposed ledger artifact.
- At most two minimal mechanical retries.
- No source retrieval, label assignment, sampling draw, or manuscript edit.

## Review gate

Frame construction and validation do not authorize the proposed sampling
design. The PI must approve the target frame and allocation before a random
seed is frozen or a sample is drawn.
