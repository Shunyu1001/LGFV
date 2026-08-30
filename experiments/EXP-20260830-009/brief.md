# EXP-20260830-009 Novelty-boundary literature audit

## Loop

Literature and claim evidence.

## Falsifiable bottleneck

Claim C-007 is not auditable because the project has no reproducible search
record establishing whether prior work already distinguishes formal LGFV exit
from the post-event location of local fiscal functions.

## Hypothesis

A reproducible search of four adjacent literatures will find work on LGFV
transformation, local-debt resolution, formal-versus-substantive compliance,
and text-label error, but no verified source that combines (1) a documented
formal exit event, (2) post-event tracing of the financing function across
organizations, and (3) a case-level multi-category outcome for LGFVs.

## Success criteria

- Run every predeclared query in `search_plan.yaml` against both Crossref and
  OpenAlex and retain the raw responses, normalized candidates, timestamps,
  API URLs, and software version.
- Apply the predeclared inclusion and exclusion rules without using a source's
  agreement with C-007 or C-008 as a selection criterion.
- Open an original publication, author manuscript, working-paper repository,
  or authoritative institutional document for every material source.
- Include adjacent and conflicting work, including any source that anticipates
  part or all of the proposed measurement framework.
- Produce a source-to-claim matrix that states what each source supports, what
  it does not establish, and whether C-007 should be retained, narrowed, or
  retired.

The experiment is kept if it makes the novelty boundary auditable, including
if it falsifies the hypothesis. It is quarantined if material sources cannot
be opened or their metadata cannot be reconciled. It is invalid if snippets or
generated citations are treated as evidence, exclusions are changed after
results are viewed, or adverse sources are omitted.

## Permitted files

- `literature/run_primary_searches.py`
- `literature/screen_search_results.py`
- `experiments/EXP-20260830-009/**`
- new audit memos under `docs/literature_audit/`

The central manuscript, bibliography, and ledgers are out of scope. Proposed
BibTeX, prose, and append-only ledger rows will be artifacts of this experiment.

## Inputs

- Base commit: `e178e195704fe6ad6ec353a28081e444995350e7`
- Existing bibliography: `paper/references.bib`
- Claims: C-007 and C-008 in `ledgers/claims.csv`
- Literature baseline: `ledgers/literature.csv`
- Search plan: `experiments/EXP-20260830-009/search_plan.yaml`

## Commands

```text
python3 literature/run_primary_searches.py --plan experiments/EXP-20260830-009/search_plan.yaml --output experiments/EXP-20260830-009/search_results
python3 scripts/validate_immutable.py
python3 scripts/validate_ledgers.py
```

Original texts will be opened from DOI landing pages, publisher pages, author
repositories, preprint servers, or authoritative government sites. Retrieval
URLs and verification notes will be recorded in the source audit.

## Budget

- Twelve query families, each run once against Crossref and OpenAlex.
- Up to 50 metadata results per database-query pair.
- Title-and-abstract screening of all deduplicated results.
- Full-text verification of at most 24 material sources, with no target number
  of supportive citations.
- One mechanical retry for an API failure; no query revision after execution.

## Amendment record

`literature/screen_search_results.py` was added to the permitted files after
database retrieval and before the metadata screen. It implements the
predeclared title-and-abstract relevance rules, retains every decision, and
does not change a query, inclusion rule, exclusion rule, or source budget.
