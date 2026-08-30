# Experiment assessment

## Status

`quarantine`

This append-only correction supersedes the generated frame artifacts from
`EXP-20260830-015` without replacing that experiment's directory or ledger row.
It was registered before the deterministic correction run; the preceding Ultra
audit is treated as diagnosis rather than a prospective result.

All 88 inherited geography gaps received a case-level disposition: 86 have a
source-supported unique province-city assignment, two have documented multiple
locations, and none remains unsupported after search. All 98 inherited scope
reviews are resolved, with 53 eligible and 45 ineligible. Across the full
133-unit frame, the audit records 130 unique geographies, two multiple-location
dispositions, one unresolved legal-identity/geography case, 66 eligible units,
66 ineligible units, and one unresolved scope case.

## Source-backed review

The successor source manifest contains 272 records and covers all 133 proposed
issuer units. Each cited decision retains a document identifier, URL, retrieval
date, page or webpage basis, raw-source hash, extracted-text hash, extraction
profile, and excerpt. Compilation verifies 485 cited excerpts against the
available extracted pages. It also verifies that every physical citation page
falls within the page count declared for that hash-matched extraction; this
repairs 27 stale extraction-bound conflicts in the committed predecessor.

The unresolved log contains four failed gates across three units. Shenzhen
International Holdings and Shenzhen Dongyangguang each retain one failed unique
geography gate because their disclosures record more than one location and the
registered rules do not specify a location-precedence rule. The remaining two
failed gates belong to `mv_dd84e076bf32`, 贵阳市交通运营集团有限公司. A
current government source uses 贵阳市公共交通投资运营集团有限公司, and the frozen
packet does not establish that the two names denote the same legal issuer.
Geography and scope therefore remain unresolved for that frozen unit.

## Probability-frame candidate

The candidate contains 66 unique eligible legal issuers and retains all 157
originating disclosure rows in a separate origin map. The eligible issuers
account for 73 originating disclosure rows. The proposal has 23 strata: 57
issuer units are in the nominal screen-positive layer and nine are in the
screen-nonpositive layer. Sixty-five units have moderate source coverage and
one has low source coverage. Historical capacity is matched for 32 units, and
debt-pressure availability is recorded for 39 units.

Every eligible unit has inclusion probability one because no stratum exceeds
its registered target. The proposal is therefore a census of the current
candidate rather than a random subsample. The deterministic seed remains
`20260830015`, but it has no operational effect, and
`random_draw_executed` is `false` throughout.

The strata use only screen status, source coverage, historical capacity,
debt-pressure availability, and administrative level. The builder reads safe
identifier and coverage columns from the surrogate input but does not read its
outcome columns. No working-reference outcome was accessed, assigned, changed,
or exposed, and this model-based audit is not described as independent human
validation.

## Integrity decision

The frame is not ready to freeze. Two units do not have a unique geography
under the registered rules, one frozen name cannot be linked uniquely to a
current legal issuer, three inherited source files are absent from the surviving
temporary cache, and the original extractor version for inherited text files
was not recorded. None of the three absent files is cited by a retained
decision. PI approval and resolution or exclusion of the three open geography
or identity units are required before the frame or sampling design may be
frozen.
