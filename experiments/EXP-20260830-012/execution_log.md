# Execution summary

## Preparation

- Created the experiment brief and run manifest at commit `538d99a` before
  building any packet.
- Froze the 94-case gold census, 13-row candidate hypothesis, allowlisted
  identity and source fields, blank coder fields, and randomization
  prohibition.
- Recorded SHA-256 hashes for all seven inputs.

## Packet construction

The deterministic builder joined the 94 gold case IDs to packet document IDs
in the master case pool and to source locations in the document inventory. It
constructed the candidate instrument from the provisionally eligible scope
rows in Experiment 011 and the proposed frame's evidence-document IDs. A
separate adjudication template used only the 94 case IDs.

The first validator run rejected the 13-row candidate output because nine
provisionally eligible scope rows still had unresolved geography. The builder
was corrected to enforce the predeclared verified-geography criterion. The
final candidate packet has four rows, and the failed 13-row hypothesis is
retained in the metrics and assessment.

## Commands

```text
python3 scripts/measurement_validation/build_independent_coding_packets.py
python3 scripts/measurement_validation/build_independent_coding_packets.py --check
python3 scripts/measurement_validation/validate_independent_coding_packets.py --check-metrics
python3 -m unittest scripts.tests.test_independent_coding_packets
```

## Result summary

- Gold second-coder rows: 94.
- Gold rows with document IDs and source locations: 94.
- Candidate rows hypothesized: 13.
- Candidate rows passing geography and provisional scope gates: 4.
- Provisionally eligible rows omitted for unresolved geography: 9.
- Adjudication rows: 94.
- Populated coder-entry cells: 0.
- Populated adjudication-entry cells: 0.
- Coding or adjudication executed: no.
- Random seed or draw: none.
- Gold-label or manuscript change: none.

## Validation

Byte-identical regeneration, packet reconstruction, field allowlist, source
location, blank-cell, unit-set, and output-hash checks passed. Repository-wide
checks are recorded against the final branch state after both experiments.
