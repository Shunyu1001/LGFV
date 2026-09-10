# Mechanical retry 2 and coordinator clarification

Attempt 2 passed all 19 collection tests and every preregistered command.
The coordinator then requested that routine research-state and README updates
not invalidate the collection package. The research-state ledger had been
included as a strict current input, although it is only historical audit
context and does not drive packet construction.

Correction: read research_state.yaml from the original base Git object only,
record pin_policy=baseline_snapshot_only, and retain strict current hash guards
for all scientific inputs. Baseline proposal metadata remains distinct from a
future actual-approval overlay. No pending question or coordinator metadata
update becomes a freeze or collection authorization. Add a regression test
that prohibits reading the live coordinator ledger. No candidate IDs, sources,
reference mappings, entry-sheet bytes, outcome coding, or proposal is changed.

This is the second and final mechanical retry. Preserve the earlier generated
input/output hash indexes and package README under this experiment directory
before rebuilding those three machine-generated artifacts. All human-entry
files remain untouched and byte-identical. Execute the same command list as
attempt 3; stop after that attempt, preserving any failure.
