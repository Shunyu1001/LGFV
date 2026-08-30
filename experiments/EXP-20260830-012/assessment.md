# Experiment assessment

## Status

`quarantine`

The gold-case instrument and adjudication template pass every structural and
blinding check, but the candidate-packet hypothesis does not. Thirteen issuers
have a provisionally eligible scope disposition in Experiment 011, while only
four also have source-supported geography. The coder-facing candidate packet
therefore contains four rows rather than copying unresolved locations into the
remaining nine. No packet should be circulated until the PI approves the
workflow and scope decisions.

## Gold packet

The second-coder packet contains exactly 94 unique frozen gold case IDs. All 94
rows have issuer identity, province, city, packet document identifiers, and at
least one recorded source location. Every one of the 1,504 coder-entry cells is
blank. The packet contains no current outcome, confidence value, rationale,
reviewer identity, validation date, LLM output, screen status, design stratum,
selection field, or randomization field.

The source locations reproduce the tracked inventory; they do not establish
that the underlying raw source archive is complete. In particular, the known
source-reconstruction limitations in R-007 remain open. The source steward
must verify rights and availability before giving the packet to a second human
coder.

## Candidate packet

The packet contains the following four geography-verified, provisionally
eligible issuers:

1. `mv_83fa1cb2dc9e`, 温州市交通运输集团有限公司, 浙江省温州市.
2. `mv_a48e56f0f316`, 福州市城乡建总集团有限公司, 福建省福州市.
3. `mv_c683a307d980`, 合肥北城建设投资(集团)有限公司, 安徽省合肥市.
4. `mv_c9485f13755e`, 江苏龙城国有控股集团有限公司, 江苏省常州市.

All four rows have document identifiers and source locations, and every coder
entry is blank. The other nine provisionally eligible scope cases are omitted
because their province-city pair remains unresolved. The four rows are not a
probability sample, do not include a selection flag, and do not represent an
approved target frame.

## Adjudication template

The separate adjudication template contains exactly the 94 frozen gold case
IDs and 1,222 blank adjudication-entry cells. It exposes no original or second
coder label. It should be opened only after a real second coder freezes the
completed gold packet.

## Integrity decision

Deterministic regeneration is byte-identical for all three CSVs. The validator
reconstructs every allowed identity and source field from the declared inputs,
checks all coder and adjudication cells, compares the gold and candidate unit
sets to the frozen inputs, and verifies output hashes. No coding, adjudication,
sample draw, random seed, label change, central ledger edit, or manuscript edit
occurred.

## Review gates

The PI must approve the independent second-human workflow, coder access to the
rights-approved source archive, disagreement domains and adjudication
procedure, the candidate scope decisions, and the probability design. R-003
remains open until a genuine second human independently codes the cases and
agreement and adjudication statistics are produced. R-010 remains open because
the candidate instrument covers four proposed issuers rather than an approved
133-issuer frame.
