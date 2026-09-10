# Human confirmation update

- Loop: claim_evidence
- Base commit: `1669bd809b932106a697de3e0467b5393ccf52be`
- Branch: `codex/human-confirmation-20260910`
- Registered: 2026-09-10, before implementation
- Budget: one provenance update, one reproducibility pass, two mechanical
  corrections if needed; no source search, outcome assignment, or model selection.

## Authorization and hypothesis

Shunyu Hao reports in the current task that all gold labels have been checked
by a human and that no problems were found, and requests GitHub and Overleaf
updates. In context, this covers the 94 existing reference cases, not the 203
surrogate disclosures, 67 probability-frame candidates, controls, or mechanism
codes. The hypothesis is that this human-check confirmation can be recorded
and propagated without changing labels, sources, model values, or validation
design, and without claiming undocumented blind double coding.

## Permitted changes

Add a dated author-report record and a derived case-level confirmation register
under `data/validation/`; add a builder/validator and focused tests; update
`scripts/label_roles.py` and notices in affected label/table builders; update
current provenance documentation, README, claims, research state, and relevant
manuscript paragraphs and generated table notes. Append decision, reviewer, and
experiment follow-up records. Keep earlier experiment artifacts and ledger rows.

The working-reference CSV, all surrogate snapshots, original source inventories,
validation-frame data, immutable files, and historical model outcomes remain
unchanged. Record missing reviewer identity, review date, blinding, signatures,
and independent pre-adjudication decisions as unreported, not as completed.

## Success criteria

1. Exactly 94 unique existing cases have a confirmation record linked to the
   unchanged reference snapshot and labels. A changed snapshot fails closed.
2. The date is explicitly the author's report date, not an invented review date.
3. Current paper and table notes no longer say the 94 labels await any human
   check. They retain the unknown blinding and probability-validation limits.
4. Labels remain 2 substantive, 82 nominal, 10 transfers, 0 liquidations;
   surrogate counts, sample membership, numerical outputs and frame data do not
   change. No reliability statistic or DSL estimate is introduced.
5. Relevant checks and the paper build pass; edited pages are inspected.

## Commands

Run `python3 scripts/build_human_confirmation_register.py`, its `--check`
mode, `python3 -m unittest discover -s tests -p 'test_human_confirmation.py'`,
and `python3 -m unittest discover -s tests -p 'test_label_role_builders.py'`.
Run immutable, ledger, label, and master-pool validators. Rebuild pilot capacity,
pilot empirical models, DSL diagnostics using the explicit expanded issuer
file, surrogate empirical core, empirical panel, and controlled models. Run
`scripts/validate_label_role_rebuild.py` for unchanged numerical results.
Record all commands and outcomes in the execution log. Build with
`latexmk -g -pdf -interaction=nonstopmode -halt-on-error paper/main.tex`.
Only after acceptance may the coordinator merge, push, pull into Overleaf,
and recompile there.
