# Execution log

## Registered sequence

1. The brief was registered against commit
   `5de57d63a70b52cedc5223a7fa6f751bfc70cfe1` before source retrieval.
2. The inherited National Archives Administration cache matched the
   Experiment 001 raw hash.
3. The tracked ChinaBond origin row was traced through bond code `1580264` to
   current issuer and bond-agent reports.
4. Three fixed search rounds covered paired names, bond identifiers, explicit
   former-name evidence, unified social credit code, ownership, geography, and
   public-project role. Six records were retained, within the twelve-record
   budget.
5. Relevant PDF pages were extracted with `pdfplumber`, hashed, rendered where
   layout mattered, and visually inspected.
6. The name variants, unique identifier, ownership, geography, and role were
   assessed separately. Contrary name evidence was retained.
7. A prospective integration experiment was registered; the existing frame
   was not rebuilt.

## Retrieval limitations

An official Ministry of Justice webpage reproduces a Guiyang regulation that
replaces references to the former rail entities with the current public-
transport issuer. Command-line retrieval entered a redirect loop, so the page
was logged as discovery corroboration and excluded from the hashed retained
packet. A 198-page SSE-hosted related-issuer document was inspected but not
retained because it concerned a different focal issuer and added no necessary
identity fact. Search snippets and commercial registry pages were not treated
as evidence.

## Extraction profile

Raw hashes used `shasum -a 256`; page counts used Poppler `pdfinfo`. Bundled
`pdfplumber` extracted the registered pages. Line endings were normalized to
LF, trailing whitespace was removed from each line, outer whitespace was
stripped, and one final LF was added. Multi-page extraction hashes prefix each
page with `=== PDF PAGE N ===` and concatenate pages in ascending order.

The package validator and repository validators are recorded in the final
validation log. No command generated a random draw.
