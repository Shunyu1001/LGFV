# Ultra correction audit record

## Audit scope

On 2026-08-31, three parallel Codex workstreams independently reviewed the
geography evidence, scope evidence, and probability-frame construction. This
was a model-based audit, not independent human validation. None of the
workstreams inspected or changed a working-reference exit-type label, and no
sampling draw was executed.

The geography workstream reviewed all 88 inherited geography gaps. The scope
workstream reviewed all 98 inherited scope cases and then checked the remaining
full-frame boundary cases. The construction workstream independently rebuilt
the 133-unit frame, checked all 157 originating disclosure rows, and audited
the historical-capacity and contemporary-control joins.

## Geography corrections

The 88 inherited cases now have 86 source-supported unique assignments and two
source-supported multiple-location dispositions. None remains unsupported
after search. The two nonunique cases are Shenzhen International Holdings,
whose disclosure records Bermuda registration, a Hong Kong principal place of
business, and a Shenzhen office, and Shenzhen Dongyangguang, whose disclosure
records a Shenzhen legal domicile and a Dongguan contact address. The review
does not impose an unregistered location-precedence rule.

The registered location for Aier Medical Investment Group was corrected from
Changsha to Lhasa. The prior Changsha locator referred to a law firm rather
than the issuer. In addition, 34 inherited geography locators that pointed to
a subsidiary, intermediary, affiliate, owner, or another entity were replaced
with direct issuer pages. The compiler now registers 36 explicit geography
locators from the initial audit, including the two multiple-location cases.
The final structured-address pass brings the explicit total to 50 and adds
independent document, page, city, and anchor checks for 14 repaired rows. Both
the compiler and standalone validator reject court-venue boilerplate and
intermediary-only addresses.

## Scope corrections

Thirteen scope dispositions changed after direct issuer, consolidated-group,
or controlling-parent evidence was reviewed. Zhangzhou Jiulongjiang Group and
Ji'an Jinluling Economic Development moved from unresolved to eligible.
Guiyang Urban Development Investment Group moved from unresolved to ineligible
because an authoritative parent prospectus establishes provincial rather than
municipal ultimate control. Ten units moved from ineligible to eligible:
Nanjing Niushoushan Cultural Tourism Group, Xining Urban Development, Wuhan
Optics Valley Financial Holding, Nantong Industry Holding, Chengdu Industry
Investment, Guangzhou Industry Investment Holding, Beijing Municipal
Construction, Shandong Quanhui Industry Development, Wenzhou Industry and
Energy Development, and Beijing Enterprises Water Group. Their evidence
documents issuer-level or consolidated public-project financing,
government-commissioned construction, infrastructure funds, or concession
investment rather than ordinary commercial activity alone.

The 98 inherited scope cases now have 53 eligible and 45 ineligible
dispositions, with none unresolved. Across the full 133-unit frame, the final
scope counts are 66 eligible, 66 ineligible, and one unresolved legal-identity
case. The compiler registers 26 explicit owner-evidence overrides, including
24 defective prior locators and two newly resolved owner cases. It also uses 28
explicit role locators to replace nonprobative or misleading pages and retain
the material scope evidence.

## Construction corrections

The original builder independently split and zipped source-row and pool-ID
lists. This produced five false pairs even though no individual identifier was
lost. The revised builder obtains each pair from safe identifier columns in
the declared surrogate input, and the validator reconstructs the pairs
independently.

The control join now uses the declared city-control table rather than a partial
hard-coded map. It adds the direct Taizhou match and implements the registered
prefecture-level exposure rule by rolling Taicang to Suzhou and Rugao to
Nantong. Origin evidence fields now contain only document identifiers that join to the
document inventory. The 66-unit candidate retains 73 originating disclosure
rows, forms 23 strata, and assigns every unit inclusion probability one. The
proposal is therefore a census of the current eligible candidate rather than
an executed random sample.

## Traceability and limitations

Compilation verifies all 485 retained evidence excerpts against their cited
extracted pages after one whitespace normalization and verifies that no cited
page exceeds the extraction bound declared in the manifest. The successor source
manifest contains 272 rows and records a raw-source SHA-256, an extracted-text
SHA-256 when the text cache is present, and an extraction-profile field. Three
uncited documents inherited from Experiment 011 are absent from the surviving
temporary source cache: `doc_exp9_20260704_0193_008`,
`doc_sch_20260630_0172_006`, and `doc_exp2_20260703_0018_003`. Their absence
does not affect a retained disposition, but the original extractor version for
inherited text files was not recorded.

The frame remains quarantined. Two issuers lack a unique geography under the
registered rules, and one frozen name cannot be linked uniquely to the current
legal issuer. These three units account for four failed gates. PI approval is
also required before the frame or any sampling design can be frozen.
