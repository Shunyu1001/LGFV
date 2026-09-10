# Independent inference review

Date: 2026-09-10. Bounded, read-only sidecar within EXP-20260910-007.
Disposition: two P2 findings for coordinator correction before relying on
actual-mode integration status. No P0/P1 issue or mathematical estimator bug
was found in this pass. This is not approval of actual data or human decisions.

## Findings

### P2: Actual mode accepts explicitly synthetic provenance

Location: [design_based_validation.py:334](/Users/shunyuhao/.codex/worktrees/lgfv-design-estimator/LGFV/scripts/design_based_validation.py:334),
lines 334-350; related response checks at lines 322-328.
The existing [actual-path test:386](/Users/shunyuhao/.codex/worktrees/lgfv-design-estimator/LGFV/tests/test_design_based_validation.py:386)
demonstrates the accepted input pattern at lines 386-404.

The actual/synthetic namespace guard checks only frame, design, selection, and
unit IDs. It does not check outcome/protocol identifiers, the provenance record
identifiers, reviewer identity, or the supplied approval's author and record
identifier. The existing artificial actual-path fixture changes the core IDs
and label-origin field but leaves explicitly synthetic evidence and approval
identifiers. A matching content hash is sufficient for that fixture to produce
an actual-mode result. The independent in-memory reproduction returned:

```text
estimate.mode       = actual
estimate.outcome_id = synthetic:binary-outcome
approval_record_id  = synthetic:approval-record
approved_by         = synthetic:approver
reviewer_id         = synthetic:reviewer
review_record_id    = synthetic:review-record-synthetic:u000
label_origin        = human_coded
```

This is narrower than the unavoidable inability to authenticate arbitrary
metadata: these records explicitly identify themselves as synthetic, yet the
result is marked actual and the adapter would select
`explicit_request_estimated`. It creates an avoidable route for partially
converted test fixtures to be reported as actual analyses.

Concrete fix: for actual mode, reject the reserved `synthetic:` namespace in
all provenance-bearing identifiers, including the outcome and specification
records, eligibility and probability records, selection verification records,
reviewer/review records, and approval author/record. Preserve the separate
requirement for external documentary verification; namespace rejection cannot
authenticate real approval. Update the artificial actual-contract fixture to
use consistently artificial, non-synthetic contract identifiers, and add a
negative test that injects each synthetic provenance field into an otherwise
valid actual request. No change to either estimating equation is needed.

### P2: Collection status is overwritten by an unrelated request's status

Location: [build_validation_inference_status.py:131](/Users/shunyuhao/.codex/worktrees/lgfv-validation-inference/LGFV/scripts/build_validation_inference_status.py:131),
lines 131-140; the retained collection fields and blocking reasons originate
at lines 63-80.

`main()` first builds a status object for the current collection, then inserts
a separately supplied request's result and replaces the top-level `status`.
It leaves `frame_units`, response counts, `blocking_reasons`, and
`actual_selection_probabilities` describing the collection. An in-memory
adapter-only probe with a successful actual request for a different frame and
an untouched one-unit collection produced:

```text
status                         = explicit_request_estimated
frame_units                    = 1
untouched_human_entries         = 1
actual_selection_probabilities = null
numerical_estimate.frame_id     = actual:different_frame
blocking_reasons includes:
  no_explicit_approved_analysis_request_and_realized_selection_supplied
  missing_or_unresolved_human_outcomes
```

The explanatory `estimate_scope` sentence acknowledges the distinct frames,
but the machine-readable status and collection fields still describe different
objects. The command's final summary also prints the request's success beside
the collection's frame and missingness counts. A consumer following the
top-level success status can mistake the untouched collection for an estimated
frame; a consumer following the blockers can reject the supplied request as
missing even after it succeeded. The synthetic branch has the same scope
mixing, although it correctly labels the nested estimate as synthetic.

Concrete fix: keep collection status/counts/blockers together and unchanged,
and place the explicit request's status, mode, frame ID, and numerical result
in a separate analysis object. Do not clear genuine collection blockers simply
because another request succeeds. Include request/approval input identifiers
and hashes with that analysis rather than leaving `source_hashes` to identify
only collection files. Add `main()` tests for successful actual and synthetic
requests against an untouched, different collection; the current adapter tests
exercise `assess_collection()` and `run_approved_analysis()` separately and do
not check this composition. This is a status/provenance correction, not a new
estimation method.

## Mathematical checks

No correction to the implemented mean, projection, or stratified variance
formula is recommended in this pass.

- The mean uses fixed full-frame predictions plus inverse-selection-probability
  residual totals, with complete response coverage required for the realized
  selected roster.
- For fixed-X projection, QR computes the fixed coefficient weights
  A = (X'X)^(-1) X'. The residual covariance is computed for a_i times e_i,
  rather than incorrectly applying a scalar residual variance to every slope.
  Its stratum multiplier N_h(N_h - n_h)/n_h is the correct total-variance
  multiplier for those weighted residuals under stratified SRSWOR.
- A census stratum contributes its observed weighted outcomes directly and
  zero label-selection covariance. A noncensus singleton leaves covariance
  unavailable; it is not assigned zero variance or pooled with another stratum.
- Unknown/no-event/censored outcomes are rejected rather than mapped to zero.
  Full-frame analytical eligibility is required separately from platform scope.
- Completed template entries are explicitly counted as pending source/process
  verification; `assess_collection()` does not turn them into authenticated
  human outcomes or invoke the estimator. The prior confirmation count does
  not supply outcomes to new validation IDs.
- The reviewed Design-based estimation subsection agrees with the formulas and
  limits claims to the assembled admissible frame. In the closing snapshot,
  [empirical_strategy.tex:208](/Users/shunyuhao/.codex/worktrees/lgfv-validation-inference/LGFV/paper/sections/empirical_strategy.tex:208)
  also explicitly distinguishes census singletons from noncensus singletons.
  It does not claim completed validation-adjusted estimates or treat no event
  as institutional-change zero. No prose change is requested here.

## Execution and limits

One careful pass covered the two requested modules, their two test files, and
the Design-based estimation subsection. A `python3 -B -c` in-memory harness
loaded the specified estimator and adapter together, with no code edits.
The human-confirmation import was replaced by a sentinel so no unrequested
project confirmation file was read. The single estimator test that reads
current candidate/design CSVs was excluded to respect the read-file scope:
`test_actual_current_67_proposal_rejected_without_inventing_labels`.
The adapter tests' disposable JSON fixtures were synthetic and temporary.

The initial combined run executed 36 tests and found one failure at the former
adapter-test line 94: QR returned 0.4999999999999999 and the test required exact
tuple equality with 0.5. This was a test assertion defect, not an estimator
error. That file changed concurrently; its current lines 94-95 use a length
check and `assertAlmostEqual(..., places=12)`. A closing scoped rerun passed all
36 tests. The resolved test issue is not an open finding.

Two in-memory reproductions support the findings. The first uses the existing
explicitly artificial actual-contract fixture, not LGFV records. The second
stubs a successful estimator return to isolate the adapter's status composition;
collection reads and output writes are mocked, so it is not an actual-data
analysis or evidence of valid approval. No external approval, source packet,
current collection, or human review process was authenticated. No manuscript
build, global ledger update, remote operation, or code rewrite was performed.

## Read-file hashes

SHA-256 was recorded after initial inspection and checked again at closing.
The estimator, its tests, and the adapter module did not change. Concurrent
changes to adapter tests and the manuscript file were rechecked only at the
affected test and requested subsection; their initial and closing hashes are
both retained below. Findings refer to the unchanged module snapshots. The
closing subsection occupies lines 173-233; its initial position was 151-209.

1. `/Users/shunyuhao/.codex/worktrees/lgfv-design-estimator/LGFV/scripts/design_based_validation.py`
   Initial and closing: `20aa49aa1fbf3a5135fc839107d07ddbdcd71af4828292734c4d8c751a1c5c78`
2. `/Users/shunyuhao/.codex/worktrees/lgfv-design-estimator/LGFV/tests/test_design_based_validation.py`
   Initial and closing: `bf8197a98f2abae68e14b68343cb24359c764651ee2a413f10822b2e56d0a9fe`
3. `/Users/shunyuhao/.codex/worktrees/lgfv-validation-inference/LGFV/scripts/build_validation_inference_status.py`
   Initial and closing: `48a080d212f9053586075d60647053d6763efa7a447af96a98535ad70b3aa171`
4. `/Users/shunyuhao/.codex/worktrees/lgfv-validation-inference/LGFV/tests/test_validation_inference_status.py`
   Initial: `966d4a046b62d691b9c2b6d74e65624583710123b1f57112ed02d5a12c9864f2`
   Closing: `32a15cfa620d5ce4efe2e93a436c45dd699bbfaf455e1405dfcf675995606e32`
5. `/Users/shunyuhao/.codex/worktrees/lgfv-validation-inference/LGFV/paper/sections/empirical_strategy.tex`
   Initial: `59b78e4d17cc9f9386669348aa32dca4f87dd41ee9d3145c0bc4d061ec0f11be`
   Closing: `41f6a3e78d2e607edb95342f44aa9fd048574567c67ca2f73490fd943e25c7dc`

Only this review report is written and committed in the reviewer's worktree.
The coordinator owns fixes and any subsequent integration or acceptance check.
