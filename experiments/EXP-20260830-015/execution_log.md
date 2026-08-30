# Execution log

## Registration and inputs

- Checked the current main commit and registered the next unclaimed identifier,
  `EXP-20260830-015`, before inspecting source-review results.
- Recorded base commit `5a68bf10de84491ab39c47427d585099e2c34b49` and
  fixed-input hashes in `brief.md`.
- Reproduced the inherited baselines: 133 proposed legal-issuer units, 157
  originating disclosure rows, 88 geography gaps, and 98 scope reviews.
- Did not read `data/processed/working_reference_labels.csv` or any exit-type
  outcome field.

## Retrieval and case review

- Re-fetched the 253 records in the Experiment 011 retrieval manifest into an
  uncommitted temporary source directory and verified the recorded hashes.
- Added 13 source records where the inherited packet did not settle identity,
  geography, owner level, or issuer role. These were government, SASAC,
  exchange, or public issuer-disclosure sources.
- Reviewed all 133 proposed units case by case and registered one row per unit
  in `review_decisions.csv` before compiling the successor crosswalk.
- Retained four unresolved units and five failed gates instead of inferring an
  owner level, platform role, or legal-name equivalence.

## Construction

Final compilation and construction commands:

```text
python3 experiments/EXP-20260830-015/compile_source_review.py --source-dir /tmp/lgfv-exp015-sources
python3 scripts/build_probability_validation_frame.py
```

Final construction result:

```text
133 reviewed units; 132 source-supported unique geographies; 1 unresolved geography
54 eligible; 75 ineligible; 4 unresolved scope units; 5 failed gates
54 candidate issuer units; 157 origin rows retained; 19 frozen strata
50 nominal screen-positive; 4 screen-nonpositive; all proposed probabilities > 0
deterministic seed 20260830015; random draw not executed
```

## Validation attempts

The first validator run rejected a geography excerpt whose source page contained
the city but whose retained snippet did not. The compiler was changed to anchor
geography snippets on the city token. The next run rejected a preexisting
resolved row because its supported current legal name was blank; a current CSRC
notice was added for that identity, while the older issuer disclosure continued
to supply the city, owner, and role basis. Both failures were evidence-retention
defects and did not change a geography or scope disposition.

Final checks:

```text
python3 scripts/validate_probability_validation_frame.py
python3 -m unittest tests.test_probability_validation_frame
```

The validator passed with the registered counts. Six unit tests passed.

Repository checks after the experiment-ledger append:

```text
python3 scripts/validate_immutable.py                 # passed
python3 scripts/validate_ledgers.py                   # passed; 15 experiments
python3 scripts/validate_labels.py                    # passed; 94 rows/cases
python3 scripts/validate_master_case_pool.py          # pre-existing baseline failure
git diff --check                                      # passed
```

The master-case-pool validator reports that 94 existing validated rows lack
`reference_label_producer` and emits existing warnings for unavailable local
extracted text. This experiment did not change the master case pool, human-label
file, or document packets. Repairing that provenance field is outside this
registered experiment and would require separate governance because it concerns
the protected label workflow.

## Prohibited actions

- No random sample was drawn.
- No validation accuracy or classifier-performance estimate was calculated.
- No exit-type label was read, assigned, changed, or revealed.
- No raw source document was committed.
- No manuscript result, immutable file, or sampling rule was changed.
