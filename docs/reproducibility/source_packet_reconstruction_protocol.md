# Source packet reconstruction protocol

## Scope

This protocol reconstructs the evidence packet cited by each working-reference
LGFV case. It verifies reference integrity and file recovery. It does not
recode outcomes or substitute for independent validation.

## Inputs

The case-level label file identifies primary documents, secondary documents,
and supplementary sources. `data/document_inventory.csv` maps document IDs to
titles, dates, page URLs, download URLs, local paths, and document types.
`data/source_inventory.csv` maps supplementary source IDs to source metadata.
The inventories are append-only research records; corrections require a dated
change record.

## Reconstruction procedure

1. Resolve every primary and secondary document ID against the document
   inventory and every supplementary source ID against the source inventory.
2. Prefer the tracked local copy when it exists. Verify that the inventory path
   points to a readable file and preserve the original filename and extension.
3. If a local copy is absent, use the recorded download URL. If it is blank or
   unavailable, use the recorded document page to recover the disclosed file.
4. Record retrieval date, final URL, file size, and a cryptographic checksum
   before adding a newly recovered public document to the packet.
5. Do not bypass access controls or redistribute restricted material. For a
   document that cannot be stored lawfully, retain bibliographic metadata,
   access notes, and a checksum supplied by an authorized holder when
   available.
6. Run `python3 scripts/audit_source_reconstruction.py --strict`. Unresolved IDs
   block the audit. Missing local copies and missing evidence memos remain
   visible case-level gaps.

## Separation from validation

A resolvable reference shows that a reader can identify or recover the source.
It does not show that the source supports the assigned label. A local file shows
that the project preserves the cited item. It does not show authenticity or
coding accuracy. Label validity requires the separate human-validation and
adjudication protocol.

## Current snapshot

The dated result in `docs/reproducibility/source_reconstruction_audit.md` is
generated from the tracked inventories and gold-label file. The case-level
output is `data/diagnostics/source_reconstruction_audit.csv`.
