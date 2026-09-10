# Interrupted integration assessment

Status: `crash`. Recorded on 2026-09-10 from the retained 2026-09-02 execution
transcript and worktree. This is an after-execution record, not a new
registration of the interrupted attempts.

The builder produced the expected 67 eligible units, 66 exclusions, 157
origins, and 24 strata. Exactly two crosswalk units changed. Three validation
attempts failed: the first two rejected noncontinuous evidence excerpts, and
the third rejected stale expected counts of 86 unique and two multiple
geographies among the 88 inherited gaps. All three failures remain recorded
in `execution_log.md`.

The run did not pass the integrity gate before interruption. The existing
program allows two mechanical retries, both of which were used. Further repair
is registered separately in `EXP-20260910-001`; no result is promoted from
this interrupted run alone.

The old builder also wrote current counts into Experiment 001's historical
metrics file. That generated change has been undone to preserve the exact
historical artifact. The successor must write versioned metrics, protect the
unchanged 131 units and labels against the registered base, and record a clean
rebuild and its output hashes. No random draw or human confirmation occurred.
