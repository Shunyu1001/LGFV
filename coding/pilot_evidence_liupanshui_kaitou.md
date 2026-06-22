# Pilot Evidence Packet: Liupanshui Kaitou

## Case

- Case ID: `pilot_gz_003`
- Province: Guizhou
- City: Liupanshui
- Company: 六盘水市开发投资有限公司
- Current coding status: candidate evidence packet, not yet human-validated
- Provisional interpretation: weak-capacity debt-continuity case, pending a direct formal exit or no-government-financing source

## Why This Case Matters

Liupanshui Kaitou extends the Guizhou weak-capacity evidence beyond Zunyi. The case is useful because the available documents show a municipal platform whose public-project role continued over time while the surrounding fiscal and credit environment weakened. This makes the case valuable for the paper even before a final exit-type label is assigned.

The current evidence does not yet contain direct formal exit language. For this reason, the case should not be entered into `data/processed/human_validated_labels.csv`. It should instead be used to test whether the codebook can handle cases where the documentary record emphasizes infrastructure obligations, fiscal dependence, rating pressure, and debt rollover stress rather than clean exit or transformation language.

## Source Set

The first ChinaBond source is the 2016 enterprise-bond issuance disclosure page for `2016年六盘水市开发投资有限公司公司债券`. It lists the prospectus, initial rating report, financial statements, guarantee documents, legal opinion, and NDRC approval. The relevant source row is `src_gz_lps_002`.

The second ChinaBond source is the rating-disclosure set for Liupanshui Kaitou. It includes the 2022 tracking rating report, a 2021 attention notice on enforcement-list inclusion, and a 2023 notice that kept the company on the rating watch list. The relevant source row is `src_gz_lps_003`.

Five PDFs have been downloaded. Three produced machine-readable text:

- `doc_gz_lps_kaitou_2016_bond_prospectus`
- `doc_gz_lps_kaitou_2016_bond_rating`
- `doc_gz_lps_kaitou_2022_tracking_rating`
- `doc_gz_lps_kaitou_2021_enforcement_notice`
- `doc_gz_lps_kaitou_2023_rating_watch_notice`

The two one-page attention notices did not produce machine-readable text through the current `pypdf` workflow. They are retained in the inventory as source records, but the main textual evidence currently comes from the prospectus, initial rating report, and 2022 tracking rating report.

## Baseline Platform Function

The 2016 prospectus identifies Liupanshui Kaitou as a wholly state-owned company established by the Liupanshui municipal government. Its business scope included project development, project investment and financing, project management and construction, entrusted project construction, asset management, and land development and consolidation. The extracted text appears in `doc_gz_lps_kaitou_2016_bond_prospectus.txt`, lines 585-586.

The same prospectus states that since its establishment the company had been one of the main operating bodies for urban infrastructure construction and comprehensive development in Liupanshui. This appears at lines 592-593.

The prospectus describes the company's infrastructure construction business as authorized by the Liupanshui municipal government. It states that the company signed an infrastructure investment, construction, management, and repurchase agreement with the municipal government in 2012, and that its infrastructure projects were mainly implemented through entrusted construction. Under this arrangement, the company constructed projects, the municipal finance bureau repurchased them after transfer to the government, and the company recognized project management fee income. This evidence appears at lines 893-920.

The prospectus also states that company revenue came mainly from entrusted infrastructure construction, gas sales, and installation-management fees, and that the company had a monopolistic position in local infrastructure construction and gas supply. It lists completed or ongoing projects including schools, hospitals, road projects, water-river governance, affordable housing construction, shantytown redevelopment, and other municipal projects. This appears at lines 1131-1143.

## Continued Public-Project Function

The 2022 tracking rating report states that Liupanshui Kaitou remained an important infrastructure construction body in Liupanshui and continued to receive support from its shareholder and related parties through asset injections and government subsidies. This appears in `doc_gz_lps_kaitou_2022_tracking_rating.txt`, lines 126-128.

The report further states that the company's operating revenue still mainly came from infrastructure construction. In 2021, infrastructure construction accounted for 87.04 percent of operating revenue. This evidence appears at lines 329-355.

The same report states that the company continued to undertake roads, ecological-environment governance, water-conservancy projects, sewage-treatment projects, and shantytown redevelopment. It says that the business model had not changed and remained mainly entrusted construction. This appears at lines 355-368.

The report lists a substantial stock of ongoing and planned projects. As of the end of March 2022, the company still needed to invest RMB 3.269 billion, or 32.69 yi yuan, in projects under construction and RMB 4.214 billion, or 42.14 yi yuan, in planned projects. The listed projects include railway-station-area shantytown redevelopment, Minghu urban-complex shantytown redevelopment, central-city shantytown projects, relocation housing, and tourism-complex development. This appears at lines 372-386.

## Fiscal And Credit Stress

The 2022 tracking rating report shows that the local fiscal environment was constrained. It reports that Liupanshui's 2021 local fiscal self-sufficiency rate was 31.54 percent and explicitly says that fiscal self-sufficiency remained weak. The same section reports a 2021 local government debt balance of RMB 72.443 billion, or 724.43 yi yuan. This evidence appears at lines 291-326.

The report places the company on a rating watch list. It says that the company faced large ongoing and planned project investment needs, weak asset liquidity, rising short-term interest-bearing debt, guarantee risk, one special-mention loan, enforcement-list inclusion, and a deteriorated own-credit condition. These concerns appear at lines 131-136.

The report also states that the company continued to receive asset injections and government subsidies. In 2021, the company received RMB 416 million, or 4.16 yi yuan, in capital reserve increases through land-use-right transfer and cash capital injection, and RMB 151 million, or 1.51 yi yuan, in government subsidies. It adds that the company was expected to continue receiving support because it would continue to play an important role in local infrastructure construction. This appears at lines 416-421.

Finally, the report records debt and liquidity pressure. By the end of March 2022, short-term interest-bearing debt had increased to RMB 4.028 billion, or 40.28 yi yuan, and accounted for 40.75 percent of interest-bearing debt. The company also had RMB 5.807 billion, or 58.07 yi yuan, in external guarantees, with some guaranteed entities already having enforcement or dishonest-enforcement records. Its 2021 fiscal subsidy-to-profit ratio reached 108.10 percent, and the report states that profit dependence on fiscal subsidies had increased. These passages appear at lines 552-588 and 598-644.

## Coding Implication

The case should not yet receive a final exit-type label. The evidence supports three claims.

First, Liupanshui Kaitou was clearly a platform-like municipal entity before the current reform period. Its formal scope and actual project portfolio combined infrastructure construction, entrusted construction, project investment and financing, land development, and public housing or shantytown redevelopment.

Second, by 2022, the public-project function had not disappeared. The company still derived most of its revenue from infrastructure construction, continued to implement entrusted construction and shantytown projects, and expected continued public-sector support.

Third, the case fits the weak-capacity mechanism. Low local fiscal self-sufficiency, heavy local government debt, dependence on fiscal subsidies, weak liquidity, large short-term debt, and rating-watch status suggest a setting in which formal exit is likely to be difficult without debt restructuring, fiscal support, or continued platform operation.

The remaining missing source is a direct formal-exit or no-government-financing document. The next search should look for `六盘水开投 退出融资平台`, `六盘水市开发投资有限公司 政府融资职能`, `六盘水市开发投资有限公司 不承担政府融资职能`, `六盘水市开发投资有限公司 市场化转型`, and `六盘水开投 隐性债务 化解`.
