# Validation-frame freeze decision memo

## Decision

Do not freeze or sample the current frame.

The source-first audit reviewed three issuer units and four predecessor gates.
At the evidence-decision layer, three gates resolve under existing rules and
one requires a new rule or an explicit exclusion decision. At the registered-
frame layer, all four gates remain open because no rebuild has been executed
and no change request has been approved.

| Unit | Gate | Evidence decision | Registered frame |
|---|---|---|---|
| `mv_2547f5fbc2e2` | geography | unresolved; new location rule or exclusion required | open |
| `mv_940b87861065` | geography | resolved to Guangdong, Shenzhen under existing focal-entity rule | open pending prospective rebuild |
| `mv_dd84e076bf32` | identity/geography | resolved to current legal issuer in Guizhou, Guiyang under existing exact-evidence rule | open pending prospective rebuild |
| `mv_dd84e076bf32` | scope | resolved as city-public and eligible under existing platform rule | open pending prospective rebuild |

## Case findings

Shenzhen International remains a genuine multiple-location case. Authoritative
issuer records concurrently report Bermuda registration, a Hong Kong principal
place, a Shenzhen office, and Shenzhen city control. The source hierarchy
cannot create a location-concept precedence. `CR-20260831-001` is therefore
necessary if the PI wants a unique mainland analysis city.

Dongyangguang is not a genuine multiple-issuer-location case on the retained
record. Shenzhen is the legal domicile, registration authority, registered
address, and issuer address for the focal entity. Dongguan is labeled as the
information-disclosure officer's contact address. Resolving the issuer to
Shenzhen applies the existing focal-entity rule and preserves the Dongguan
contact as contrary operational evidence.

The Guiyang frozen string came from bond metadata using issuer abbreviation
`贵阳市交通运营集团`, then added a legal suffix. The unique bond code links to
the current legal issuer `贵阳市公共交通投资运营集团有限公司`. Issuer and
bond-agent reports, an explicit former-name statement, unified social credit
code `915201006884072115`, and the Guiyang address establish the chain. The same
issuer is controlled by Guiyang SASAC and directly finances, invests in,
constructs, and operates rail-transit infrastructure. The two Guiyang gates
therefore resolve under existing rules.

## Exact counts

- Frozen frame: 133 units; 4 open gates across 3 units; unchanged.
- Evidence audit: 4 gates reviewed; 3 resolved under existing rules; 1 requires
  a new rule or explicit exclusion; 0 integrated.
- Prospective existing-rule integration: if independently reviewed and passed,
  the tracked evidence would leave 1 open gate across 1 unit and increase the
  eligible candidate census from 66 to 67. These are preregistered expected
  counts, not current-frame counts.
- Random draws: 0.
- Exit-type, working-reference, and LLM-surrogate label changes: 0.
- Immutable-file, manuscript-claim, and raw-source changes: 0.

## Exact PI decisions required

1. For Shenzhen International, approve one policy in
   `CR-20260831-001`: the proposed structured fallback, strict legal domicile,
   principal place, an explicit nonunique-geography relaxation for ineligible
   units, or continued nonuniqueness with exclusion. Authorize a prospective
   133-unit acceptance test for the selected policy.
2. Accept or reject the three existing-rule evidence determinations. If
   accepted, authorize execution of `EXP-20260831-004`; this does not authorize
   a sample draw.
3. After the selected rule or exclusion and the deterministic rebuild pass all
   checks, separately approve or reject the final frame freeze and any later
   sampling experiment.

Codex review supplies an auditable source assessment. It is not independent
human validation and does not close the separate human-confirmation issue.
