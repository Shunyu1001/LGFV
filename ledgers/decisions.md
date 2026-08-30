# Research Decisions

## 2026-08-30: Contribution order

The measurement framework is the primary contribution. Historical state
capacity is a secondary exploratory application. The decision reflects the
current evidence: the typology and source audit are developed, whereas the
adjusted historical-capacity coefficient attenuates and the outcome remains
sparse.

## 2026-08-30: Parallel work

Parallel tasks use separate worktrees and disjoint primary file scopes. The
coordinator is the only writer to `main`, the central ledgers, and Overleaf.
Parallel branches may be pushed to GitHub for review but are not synchronized
to Overleaf until their results pass the fixed evaluation protocol.

## 2026-08-30: Source reconstruction is not validation

Reference resolution, local-file presence, and recovery URLs are treated as
reproducibility properties. They do not raise label confidence or substitute
for independent coding. The manuscript may report these properties only with
that distinction explicit.
