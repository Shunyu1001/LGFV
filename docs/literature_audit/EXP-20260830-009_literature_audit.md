# Literature and novelty audit

## Result

The current broad novelty claim is not defensible. The formal-substantive
distinction, official-exit outcomes, market-transformation pathways,
function-over-label regulation, and text-label validation all have direct
precedents. The contribution that remains distinctive within the audited
sources is narrower: an auditable LGFV case measure that requires a documented
formal event, traces the financing and project function after that event, and
assigns one of four mutually exclusive institutional fates.

This is a bounded assessment. The search is reproducible, but it is not an
exhaustive proof that no earlier source used the same combination. In
particular, Crossref and OpenAlex incompletely index Chinese-language social
science. The paper should therefore avoid `first`, `new distinction`, and
other universal priority language.

## Search and verification

The predeclared plan contained three exact queries in each of four literatures:
LGFV exit and transformation, local-debt resolution and fiscal
recentralization, organizational compliance and functional substitution, and
text-derived measurement error. Each query was submitted once to Crossref and
OpenAlex for up to 50 records. The run produced 1,200 candidate rows and 1,104
deduplicated works. The raw responses, request times, API URLs, normalized
candidates, and deterministic first-pass decisions are retained under
`experiments/EXP-20260830-009/search_results/`.

The deterministic screen marked 191 works for possible manual review: 73 in
organizational compliance, 52 in debt resolution, 6 in LGFV transformation,
and 60 in text measurement. The 913 other records retain a machine-readable
title-and-abstract exclusion reason. The 24-source full-text budget did not
permit opening all 191. The retained material set prioritizes the closest
construct, design, and mechanism competitors and deliberately includes adverse
and conflicting results. The other manual-review records remain candidates,
not verified exclusions. This is a targeted novelty-boundary audit rather than
a systematic-review prevalence estimate.

Targeted searches then recovered original texts and authoritative records for
the most material candidates, known close competitors, and conflicting work.
The exact supplemental queries and explicit exclusions are in
`artifacts/supplemental_search_log.txt`. The material set was capped at 24
sources, as specified before results were viewed. Each included source has an
opened original text, locations checked, a finding, a limitation, and a claim
mapping in `artifacts/verified_source_matrix.csv`.

Two mechanical retries did not alter the design. The first search process
stopped before making a network request because the local Python lacked a YAML
package; the plan was converted to JSON syntax, which is valid YAML, and the
standard library was used. The first screening process stopped because two
source-only CSV fields were passed to the output writer; the writer was set to
ignore those already-consolidated fields. No query, criterion, source budget,
or selection rule changed.

## LGFV exit and transformation

The closest work already separates formal signals from economic or
organizational consequences. Li, Feng, and Hao treat market transformation as
change in business, management, and financing and warn that asset integration
can be formal without substantive management rights. Liu Hao distinguishes
superficial transformation from function peeling, restructuring, liquidation,
and continuity of public services. Li, He, and Ai operationalize exit through
issuer declarations that the firm no longer performs government financing;
their results show that the signal can change pricing and the distribution of
financing without proving that the total function disappeared. Fang and Lu
show that exit from the supervisory list can coexist with debt growth and
weaker long-term solvency.

Feng, Wu, and Zhang provide the most direct adverse case. Jiaxing Chengtou left
the monitoring list but retained public ownership, government-appointed
management, infrastructure functions, and government-linked repayment, and a
later debt clearance coexisted with regrouping into a larger public group.
This source anticipates the paper's central motivation. It does not, however,
provide a common four-fate codebook applied to a multi-case source packet.

The resulting boundary is precise. The paper did not invent exit pathways,
formal-versus-substantive transformation, or the idea that list exit can be
misleading. Its measurement contribution is to make those concerns auditable
and mutually exclusive at the case level by locating the post-event function.

## Local-debt resolution

Jin and Rial state that regulation should follow the fiscal function regardless
of legal label and should prevent mere relabeling. Wingender shows why moving
liabilities to government bonds can coexist with new off-budget channels.
Chen, He, and Liu document migration from bank loans toward municipal corporate
bonds and shadow-banking instruments. Liu, Oi, and Zhang locate backdoor local
finance within the central-local fiscal and political bargain. The Ministry of
Finance describes project identification, multi-level review, statutory-debt
conversion, monitoring, data sharing, and budget discipline as current policy
tasks.

These sources establish two limits. First, debt conversion is not itself proof
that a financing or project function ended. Second, an exit outcome can reflect
national fiscal arrangements and contemporary policy implementation rather
than a persistent local institutional trait.

## Organizational compliance

Bromley and Powell distinguish a policy-practice gap from a means-ends gap.
De Bree and Stoopendaal decompose the chain further into regulatory goal,
management system, daily practice, and real outcome. Short and Toffel show that
sustained organizational and field surveillance can make a formal commitment
more consequential. Zhelyazkova, Kaya, and Schrama empirically separate legal
from practical compliance. Haack and Schoeneborn warn that the two types of
decoupling should not be merged and that formal change can precede later
practice.

The paper should use this literature to clarify, not claim, conceptual novelty.
A formal-event/practice gap occurs when the same entity retains the financing
or entrusted-project function. A practice/outcome gap occurs when operations
change but fiscal-risk or market-discipline objectives do not follow.
Functional substitution is different: the original entity may genuinely exit
while the function moves to another organization. Repeated dated observations
are necessary to distinguish persistent nominal exit from delayed change.

## Text-derived measurement

The text-as-data literature prevents novelty claims based on using an LLM, a
codebook, human review, or a general validation workflow. Grimmer and Stewart
require application-specific held-out validation and class-specific metrics.
Halterman and Keith show that a model can follow familiar label semantics
rather than the project's operational definition and recommend staged
codebook and error tests. Egami and coauthors show that high predictive
accuracy need not yield valid downstream regression. Knox, Lucas, and Cho and
TeBlunthuis, Hase, and Chan explain how learned-proxy contamination and
misclassification can distort substantive inference.

Gilardi, Alizadeh, and Kubli provide an important conflicting result: a 2023
LLM outperformed crowd workers on several common annotation tasks. That result
supports feasibility, not novelty or downstream validity. It is consistent
with retaining LLMs for discovery while requiring human-reviewed case packets
for the estimand used in the paper.

## Claim C-007

The current claim should be replaced with the proposed row in
`artifacts/proposed_claim_updates.csv`. The central sentence should say that
the paper adapts established concerns about decoupling and LGFV transformation
to an auditable case-level framework. The distinctive components are their
joint use: formal-event verification, post-event function tracing, a
four-category fate, and retained source packets that permit review.

The paper should not claim novelty for any component in isolation. It should
also not infer completeness from the absence of an exact predecessor in this
search. The correct evidentiary phrase is `within the audited sources`, not
`for the first time`.

## Claim C-008

The historical claim is too strong. Chen, Kung, and Ma show that essentially
the same examination-elite proxy predicts modern education, cultural
transmission, and social capital and does not show Communist-era political
elite continuity. Zhou shows that coordination can produce evasion rather than
implementation. Choi and coauthors show that political connections can lower
financing costs without demonstrating administrative reorganization. These
are not minor controls; they are competing interpretations.

The historical association should therefore be separated from the three
contemporary processes. The current evidence can say that observed cases are
consistent with fiscal absorption, bureaucratic coordination, and project or
state-asset governance. It cannot say that historical capacity operates
through them, that the historical proxy measures administrative capacity, or
that these processes mediate the association.

## Coordinator handoff

The experiment artifacts contain proposed claim rows, literature rows, and
BibTeX. They are proposals for independent verification, not direct ledger or
bibliography changes. The coordinator should retain the adverse sources when
deciding what to merge. If a later manuscript revision uses mechanism
language, it should follow the separate diagnostics in EXP-20260830-010.
