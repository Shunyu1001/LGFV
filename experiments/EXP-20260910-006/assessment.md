# Assessment

Status: `keep` for the conditional identification calculation and audit
artifacts, subject to coordinator review. This status does not certify
reference correctness, event alignment, independent pairing, performance
validation, or a wider population claim.

## Result

Conditional on each retained linked-reference outcome being correct and valid
for the corresponding documentary-screen issuer and event, the nominal-label
membership and positive-label-correctness bounds in the 158-issuer screening
universe are **61/158 to 158/158 (38.61% to 100%)**. Counts are 61 positive,
zero negative, and 97 unknown. The separate selected overlap description is
61/61. No extrapolated precision, accuracy interval, or p-value is computed.

The 94 reference cases represent 94 distinct issuer names, without a duplicate
case ambiguity. Their retained outcomes are 82 nominal exits, two substantive
exits, ten functional transfers, and zero liquidations. The issuer screen is
reconstructed exactly from 203 selected disclosure rows. All 61 linked issuer
names match exactly; 41 have shared reference document and source-case anchors,
while 20 do not. Neither group establishes independent same-event pairing or
event-time alignment. Without assuming that the linked reference outcomes
apply to the screen issuer/events, bounds for the 158 screen units are 0% to 100%.

The current candidate has 67 issuers and 74 originating rows: 57 positive
screens and ten no-direct-event screens. None inherits a reference outcome.
All candidate nominal-membership bounds remain 0% to 100%, and candidate
positive-label correctness uses the 57 positive predictions only. Current
scope records exclude 40 of the 97 nonoverlap positives; no exclusion is
recoded as a negative reference outcome. The arithmetic 191-identity union is
not a verified city-platform case population, so no union bounds are supplied.

## Integrity and verification

- Pre-execution brief commit: `7ed12c2`; base:
  `4330c5728dec64ba30c1faec972fad0097622e9d`.
- Fourteen input snapshots are checked byte-for-byte against the base commit;
  the author report also verifies its exact reference hash and the full
  case-level confirmation register.
- Every selected source/pool pair is checked, and duplicate issuer rows,
  repeated case IDs, ambiguous reference issuers, conflicting labels, and
  inconsistent links fail before output writing.
- The current source manifest resolves scope sources for both inherited origin
  rows with empty legacy document-ID fields; both rows remain in the audit.
- Eleven output rows are independently recomputed using exact rational
  arithmetic, and repeated builds reproduce all ten generated artifacts byte
  for byte. The manifest records input and output hashes and producer code.
- Final targeted suite: 31 tests. The existing human-confirmation suite adds
  seven passing tests. Immutable, ledger, label, and master-case-pool validators
  pass; the label validator reports 89 missing local extracted-text warnings.
- All 542 files from the base commit remain byte-identical. No manuscript,
  frozen input, shared ledger, human report, or other existing file is changed.
- The standalone table compiles without overfull or underfull box warnings and
  its rendered page was visually inspected: headers, values, notes, and margins
  are readable without clipping. No full manuscript build was performed.

## Attempts

Attempt 1: `crash` at the candidate-origin source-link guard, before any result
outputs were written. The guard initially assumed the old document inventory
covered every origin. The two alternate Guiyang origins use the separate
current scope-source manifest. The correction preserves both records and
checks their source links without assigning outcomes.

Attempt 2: all eight registered commands and 29 tests pass. Attempt 3: the
same commands and tests pass after strengthening the first-paragraph and table
conditionality language. Attempt 4 adds two regression tests ensuring source
anchors do not imply same-event pairing and scope exclusions remain unknown.
Each attempt has its own retained log. Preparation-only mechanical failures
are recorded separately in `preparation_log.md`.

## Coordinator use

Use `notes.md`, the standalone table, and the exact-fraction results CSV only
with their issuer/event applicability condition. `issuer_audit.csv` identifies
every overlap and unknown issuer and its event/source anchors;
`reference_audit.csv` retains all 94 cases;
`disclosure_audit.csv` preserves all 203 selected source/pool pairs;
`candidate_audit.csv` retains all 133 origin units and their dispositions.
`document_links.csv` records inventory URLs and expected paths, not new source
retrieval. The candidate's four inherited blank packet rows match only three
current candidates; this worker has not changed that separate packet task.

The proposed ledger rows are local handoff artifacts only. The coordinator
owns ledger insertion, any material claim registration, manuscript use, merges,
and the full paper build. No remote operation or main-branch merge occurred.
