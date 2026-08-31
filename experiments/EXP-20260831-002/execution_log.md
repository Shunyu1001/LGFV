# Execution log

## Registered sequence

1. The brief was registered against commit
   `5de57d63a70b52cedc5223a7fa6f751bfc70cfe1` before source retrieval.
2. All four inherited raw and text caches named in the brief were found in the
   registered temporary cache and matched the Experiment 001 manifest hashes.
3. Relevant inherited PDF pages were re-extracted with `pdfplumber` and
   visually checked after rendering representative pages.
4. A current HKEX-filed Shenzhen International interim report and a
   ChinaMoney-filed Dongyangguang legal opinion were retrieved. Raw SHA-256,
   byte size, page count, exact page locator, and normalized page-text hash were
   recorded.
5. Each location was classified by both focal legal entity and field type.
6. The two case decisions, change request, and prospective rebuild brief were
   written without changing the registered frame.

## Commands and extraction profile

Cache verification used `shasum -a 256`. PDF metadata and page counts used
Poppler `pdfinfo`. Text extraction used bundled `pdfplumber`; for each retained
page, line endings were normalized to LF, trailing whitespace was removed from
each line, outer whitespace was stripped, and one final LF was added before
hashing. Relevant pages were also rendered with Poppler and visually inspected.

The package validator and repository validators are recorded in the final
validation log. No command generated a random draw.
