# Assessment

## Decision

`keep`

The registered hypothesis passed after one invariant-triggered correction.
Generated analysis files and paper tables now distinguish Codex source-packet
working references from Codex LLM surrogate labels. All 94 working-reference
outcomes remain pending independent human confirmation. The five source-packet
boundary reviews carry the same provisional status.

The repair changes no case ID, exit type, confidence score, evidence score,
sample inclusion flag, historical-capacity value, contemporary control,
adjusted quantity, coefficient, or sample composition. The comparison against
the base build reports zero changes in numeric and label fields. The rebuilt
panel still contains 191 rows, including 94 working-reference rows and 97
nonoverlap surrogate rows. The historical diagnostic sample remains 84 and the
full-controls sample remains 78. The paper compiles to 78 pages.

## Failed attempt and correction

The first attempted clean rebuild reran disclosure-level classification in an
isolated worktree. That worktree did not contain the untracked local extracted
source packets, so the builder replaced the 203 active surrogate disclosure
labels with zero. The registered count audit caught the failure before commit.
No result from that attempt was retained.

A subsequent metadata migration changed only role fields in the active label
file, but the validation-freeze audit correctly rejected even that change
because the file is a frozen input. The final implementation restores the
frozen file byte for byte. Builders now interpret its legacy role strings at
read time and emit canonical role strings only in downstream generated
artifacts. Both the role-rebuild audit and the freeze-package audit pass.

## Reproducibility and remaining risk

Two complete downstream rebuilds produced the same generated-artifact diff
hash,
`348d2d49d61eae7f65e6e3e76c59044002c5657ad685169646611c1100be9f88`.
Six targeted tests pass, all 43 audited manuscript quantities match generated
artifacts, and the immutable, ledger, label, master-pool, and freeze-package
validators pass.

Full disclosure-level surrogate classification is still not portable to a
clean worktree because the legally constrained source-text cache is local and
untracked. This experiment makes downstream rebuilding safe but does not solve
that source-cache dependency. The 89 inherited missing-extraction warnings and
the absence of independent human confirmation remain substantive limitations.
