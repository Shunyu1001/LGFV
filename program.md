# Academic Autoresearch Program

## Mission

The project develops a measurement framework for distinguishing formal LGFV
exit from functional fiscal change and uses that measure to study variation in
institutional fate. The objective is to improve validity, coverage,
reproducibility, traceability, and clarity. The project does not optimize for
smaller p-values, a preferred coefficient sign, more citations, more confident
prose, or a positive conclusion.

The current stage is `revision-exploratory`. The measurement contribution is
the primary object under development. Historical state capacity is a secondary
associational application. Any causal upgrade is review-gated.

## Authority and roles

The human PI owns research design, data rights, interpretation, material
claims, authorship, and submission decisions. The coordinating task maintains
the research state, reviews parallel work, merges accepted changes, and syncs
`main` to GitHub and Overleaf. Parallel tasks implement bounded experiments in
isolated worktrees and do not merge their own changes to `main`.

Read authoritative files in this order:

1. `immutable/research_charter.md`
2. `immutable/analysis_plan.md`
3. `immutable/evaluation_protocol.md`
4. `immutable/data_manifest.yaml`
5. `AGENTS.md`
6. `ledgers/research_state.yaml`
7. `ledgers/claims.csv`
8. `ledgers/experiments.tsv`
9. `ledgers/literature.csv`
10. this file

Conflicts require a recorded reviewer issue or change request. Do not choose
the convenient interpretation silently.

## Object boundaries

The following objects are immutable during one experiment: the four exit-type
definitions, the distinction between gold and surrogate labels, the current
gold-label file, the documented source hierarchy, the historical-capacity
crosswalk used by the baseline, the outcome family declared in the analysis
plan, and all prior ledger rows. The underlying raw documents and inventories
are never overwritten.

Mutable objects include implementation code, diagnostics, approved robustness
checks, source-search queries, tables, figures, appendix organization, claim
wording, and manuscript structure. Prose changes must follow the evidence
state and the writing rules in `AGENTS.md`.

Human approval is required before changing an exit definition, gold-label
inclusion rule, primary measurement claim, validation sampling design,
historical-capacity operationalization used as the principal exposure,
estimand, outcome, sample rule, missing-data treatment, fixed-effect structure,
or causal language. Create `change_requests/CR-YYYYMMDD-NNN.md` before making
such a change.

## Ledgers and experiment artifacts

Maintain the following audit files:

- `ledgers/research_state.yaml`
- `ledgers/experiments.tsv`
- `ledgers/claims.csv`
- `ledgers/literature.csv`
- `ledgers/reviewer_issues.tsv`
- `ledgers/change_requests.tsv`
- `ledgers/decisions.md`

Each experiment directory contains a pre-result brief, run manifest, metrics,
assessment, logs or a stable summary, and any generated artifacts. Earlier
ledger rows are append-only. Corrections receive a new row that identifies the
record being corrected.

## Shared experiment loop

For each experiment:

1. Read the current research state and open critical reviewer issues.
2. Select one high-value bottleneck within the authorized file scope.
3. Write a falsifiable hypothesis and success criteria before execution.
4. Record the base commit, input identifiers, permitted files, budget, and
   exact validation command.
5. Reproduce the relevant baseline.
6. Make one focused conceptual change.
7. Run deterministic checks and inspect the resulting artifacts.
8. Apply integrity and validity gates before interpreting the direction.
9. Assign a status and append the experiment ledger.
10. Update claims, literature, reviewer issues, and the research state when
    affected.

## Five loops

`literature` reduces a documented coverage gap for a specific novelty,
measurement, or identification claim. Material claims require an opened and
verified original source; search snippets and generated citations are not
evidence.

`theory_identification` clarifies assumptions, derives a falsifiable
prediction, identifies a boundary condition, or develops a diagnostic that
distinguishes the proposed mechanism from an alternative explanation.

`empirical_simulation` improves reproducibility, measurement validation,
diagnostics, or estimation under the declared design. It reports all specified
outcomes and failures and never selects a version because its coefficient is
larger or more significant.

`claim_evidence` audits one material claim against original sources and
experiment artifacts. The minimum credible action is to add evidence, narrow
the wording, state a limitation, or retire the claim.

`reviewer` identifies one concrete, evidenced issue that could change an
editorial judgment. A problem is closed only by a reproduced fix, a narrower
claim, an explicit limitation, or evidence that the criticism does not apply.

## Status rules

`keep` requires all hard gates to pass and a material improvement in validity,
coverage, reproducibility, traceability, or clarity. A credible null result or
falsification can be kept.

`discard` records a valid experiment that does not improve the current best or
whose cost exceeds its benefit. Its scientific implication remains in the
audit record.

`quarantine` records a potentially useful exploratory result, source or
evaluator uncertainty, or any proposed review-gated change.

`crash` records an execution, resource, or access failure. At most two minimal
mechanical retries are allowed without changing the hypothesis or criteria.

`invalid` records evaluation contamination, inconsistent inputs,
post-result criteria changes, leakage, or missing audit information.

## Hard gates

No change may be kept if it changes a frozen object without approval, modifies
success criteria after seeing results, omits specified outcomes or failures,
uses an unverified material citation, violates data rights, lacks input and
command traceability, cannot be reproduced, presents exploration as
confirmation, selects a specification by significance or sign, overstates a
claim, or deletes adverse evidence or audit history.

## Batch checkpoints

After five experiments or one substantive merge, the coordinator reports the
current best commit, statuses of all runs, material claim support, unresolved
critical issues, pending human decisions, and the next bottleneck. Stable
changes are pushed to GitHub. Only reviewed changes merged into `main` are
pulled into Overleaf and recompiled.
