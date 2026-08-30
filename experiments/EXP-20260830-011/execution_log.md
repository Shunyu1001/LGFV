# Execution summary

## Preparation

- Created the experiment brief and run manifest before source retrieval.
- Froze the 128 unresolved units, source hierarchy, two-document ceiling,
  evidence rules, 100-unit hypothesis threshold, and randomization prohibition.
- Recorded SHA-256 hashes for all four tracked inputs.

## Retrieval and extraction

The first execution used serial retrieval and was stopped after four minutes
because the exchange response remained in a long chunked transfer. The first
mechanical retry used concurrent retrieval but full-document Python extraction
was CPU-bound on long prospectuses. The second retry retained the same source
documents and used bundled Poppler extraction for at most the first 120 pages,
where the issuer overview, registration, ownership, and main-business sections
occur in these disclosure formats. That run completed all 128 units.

The completed run attempted 253 fixed-hierarchy documents for 127 units. All
253 public issuer disclosures were retrieved, hashed, and text-extracted. Raw
files were held in temporary storage and were not committed. The remaining
unit had no matching inventoried evidence document.

## Evidence audit

The completed machine extraction initially proposed 87 unique geography
matches and 27 units with apparent conflicts. Inspection showed that permissive
text matches had captured subsidiary, intermediary, predecessor, and generic
regulatory passages. A stricter regeneration of the same source hierarchy was
started but stopped after exchange throttling limited progress to 16 units.
The already recorded snippets were therefore subjected to a deterministic
issuer-linkage audit: only structured issuer address fields, exact controller
relations, and issuer-linked platform-role passages were retained. This audit
reduced supported geography from 87 to 61 and finally to 40. It removed the 27
apparent conflict units because none represented conflicting accepted issuer
evidence. The lower coverage is retained.

## Commands

```text
/Users/shunyuhao/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/measurement_validation/build_validation_geography_scope_packet.py
/Users/shunyuhao/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/measurement_validation/build_validation_geography_scope_packet.py --sanitize-existing
/Users/shunyuhao/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/measurement_validation/validate_validation_geography_scope_packet.py --check-metrics
/Users/shunyuhao/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest scripts.tests.test_validation_geography_scope_packet
```

## Result summary

- Unresolved units processed: 128.
- Source retrieval units: 127.
- Retrieved and extracted documents: 253.
- Legal identities supported: 127.
- Unique province-city pairs supported: 40.
- Controlling-owner levels supported: 61.
- Platform-role excerpts supported: 46.
- Fully supported identity, geography, owner, and role records: 5.
- Provisional scope dispositions: 13 eligible, 17 ineligible, 98 review
  required.
- Accepted conflicting units: 0.
- Random seed or draw: none.
- Gold-label or manuscript change: none.

## Validation

The packet validator and two deterministic unit tests passed. Repository-wide
immutable, ledger, label, and master-case-pool checks are recorded after the
independent-coding packet experiment so that both bounded experiments are
validated against one final branch state.
