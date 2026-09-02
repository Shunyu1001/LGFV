# Experiment brief: Existing-rule freeze integration

## Registration

- Experiment: `EXP-20260831-004`
- Registered: `2026-08-31T12:40:00+08:00`
- Loop: `measurement_validation`
- Base commit: `4d75edbbf53da5604f0798148d17ac4480d8c3f0`
- Branch: `codex/lgfv-validation-frame-freeze`
- Evidence predecessors: `EXP-20260831-002` and `EXP-20260831-003`
- Status: authorized prospective rebuild; not executed

## Falsifiable bottleneck

The source audits may close three gates under existing frozen rules: the
Dongyangguang geography gate and the Guiyang identity/geography and scope
gates. Those evidence findings are not yet part of the registered frame. A
deterministic rebuild must test whether the findings can be integrated without
changing any rule, label, origin row, unrelated case, or sampling field.

## Hypothesis and success criteria

The rebuild will change only the following registered dispositions:

1. `mv_940b87861065`: geography from `source_supported_multiple` to
   `source_supported_unique`, province `Guangdong`, city `Shenzhen`; scope
   remains `ineligible` with reason `excluded_private`.
2. `mv_dd84e076bf32`: supported legal issuer to
   `贵阳市公共交通投资运营集团有限公司`; geography to
   `source_supported_unique`, province `Guizhou`, city `Guiyang`; owner level
   to `subprovincial_public`; scope to `eligible` under the existing local
   public infrastructure-platform rule.

Success requires exact evidence citations from the two predecessor packets,
zero changes to the other 131 units, zero changes to source or outcome labels,
all 157 origin rows preserved, no random draw, and byte-for-byte preservation
of the registered exit-type, working-reference, and LLM-surrogate label files.
The candidate census may change from 66 to 67 eligible units only because the
Guiyang scope gate closes. The unresolved log must retain only the Shenzhen
International geography gate unless a PI-approved location rule has already
been registered and separately tested.

Any additional unit change, label change, origin loss, rule invention, or
sample draw is a failed integration and must be quarantined.

## Frozen inputs

| Input | SHA-256 |
|---|---|
| `data/validation/probability_validation_geography_scope_crosswalk.csv` | `fc72c263dade64d3404d873fec0b40328429346661710d24988c448fbeb711d2` |
| `data/validation/probability_validation_unresolved_log.csv` | `5c9ede8c97b86add246ab99b2a6a052375f849f9be9fecc02abd4c95f368571c` |
| `data/validation/probability_validation_source_manifest.csv` | `5713057b161939748a334426bb41e5ed1ce59adc4519204ea0b1d31b0bb1d664` |
| `data/validation/probability_validation_frame_candidate.csv` | `a31000f9896b86c6bbd9327716761fb28386ea08a57c7845b8884e1a36be168c` |
| `data/validation/probability_validation_frame_origin_rows.csv` | `2799dda51d7cbe05c1960ae35ae67354dbaedf0495d5315cbcca2038ba2fe2f7` |
| `data/validation/probability_validation_frame_flow.csv` | `57929324912b1ab3db7eb97c72709fdbcf5424783087c64baa433f385a22a423` |
| `data/validation/probability_validation_sampling_design.csv` | `f525276471be1911b125f6e41d4ad870ad49f20b70f8cd09face4e80532c8abd` |

Before execution, replace the evidence-packet placeholders in the run manifest
with the committed hashes of the final `EXP-20260831-002` and
`EXP-20260831-003` assessments, decisions, manifests, and excerpt registers.

## Permitted files

- `experiments/EXP-20260831-004/**`;
- the probability-validation builder and its targeted tests;
- the probability-validation crosswalk, unresolved log, source manifest,
  candidate frame, origin map, flow, and sampling-design outputs;
- append-only experiment and reviewer-issue ledger rows.

No immutable file, codebook, source hierarchy, exit-type label,
working-reference label, LLM-surrogate label, claim, manuscript file, or raw
source packet may change. Do not draw a sample.

## Required checks

Run the freeze-package validator first, rebuild only after independent review
of both evidence packets, then run the relevant repository validators. Record
all output hashes and the exact set of changed unit identifiers. A successful
deterministic build remains a candidate pending PI approval; it does not by
itself approve the frame or a sampling draw.

## Stop rule

Do not execute this experiment in the freeze-decision workstream. Execution is
permitted only after the coordinator accepts the two evidence packets and the
PI decides whether the remaining Shenzhen International gate must be resolved,
excluded, or governed by an approved rule.

## PI authorization amendment

This amendment was registered before execution on `2026-09-02`. The
coordinator accepted the evidence findings in `EXP-20260831-002` and
`EXP-20260831-003`. The PI approved the following three decisions:

1. Integrate the Dongyangguang geography finding under the existing focal-
   entity rule.
2. Integrate the Guiyang identity, geography, ownership, role, and scope
   findings under the existing rules.
3. Adopt Alternative 3 in `CR-20260831-001`: an already ineligible unit need
   not receive a unique city. Shenzhen International must retain the supported
   Bermuda, Hong Kong, and Shenzhen location concepts, remain
   `source_supported_multiple`, and remain outside the city-platform
   probability-validation frame.

Execution is authorized from base commit
`9977dd752f911bfd07dc4d434301041ef485c9f2` on branch
`codex/validation-frame-freeze-execution`. The amendment changes the original
success criterion for the unresolved log: after the two evidence integrations
and the approved scope-contingent geography rule, the log must contain zero
blocking gates. The crosswalk may still report Shenzhen International as
`source_supported_multiple`; that status is nonblocking because the unit is
already ineligible and is not in the candidate frame.

The rebuild must produce 67 eligible city-platform units, preserve all 157
origin rows, preserve the exact scope and geography facts for Shenzhen
International, and make no random draw. Only `mv_940b87861065` and
`mv_dd84e076bf32` may change crosswalk fields relative to the frozen input.
The policy decision for `mv_2547f5fbc2e2` changes gate interpretation, not its
recorded location or scope fields.

For this authorized execution, permitted files additionally include
`change_requests/CR-20260831-001.md`, `ledgers/change_requests.tsv`, and
`ledgers/decisions.md`. No manuscript or claim change is authorized by this
experiment.
