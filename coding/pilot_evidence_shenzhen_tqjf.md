# Pilot Evidence Packet: Shenzhen Special Zone Development

## Case Summary

- Case ID: `pilot_gd_002`
- Company: Shenzhen Special Zone Development Group Co., Ltd.
  (`深圳市特区建设发展集团有限公司`)
- Status: low historical-capacity but high contemporary-capacity boundary case
- Preliminary coding implication:
  `formal_fiscal_substitution_boundary_candidate`
- Confidence: candidate only
- Main source page: Shanghai Clearing House,
  `深圳市特区建设发展集团有限公司2025年度第四期中期票据发行文件`,
  2025-11-12
- Source inventory rows: `src_gd_sz_001`, `src_gd_sz_002`

## Why This Case Matters

Shenzhen is in the low historical-capacity bin in the current candidate list,
but it is one of the strongest contemporary local fiscal and administrative
environments in China. This makes the case useful for separating historical
capacity from present-day economic and fiscal capacity. If the paper's
mechanism is about historically rooted administrative capacity, Shenzhen should
not be treated as a simple weak-capacity case merely because its Ming-Qing elite
density is low. It is better used as a boundary case that shows how strong
contemporary institutions can support formal fiscal substitution even in a
historically low-density locality.

The evidence should not be treated as a final LGFV exit label. The current
documents do not show that the issuer formally exited an LGFV list. They do
show that the firm is a municipal state-owned platform-like company with
infrastructure, technology-park, transport, marine-development, government
assistance, and PPP-related functions. They also show that the issuer frames
current bond financing as corporate debt rather than local government debt and
distinguishes project financing from direct fiscal repayment.

## Machine-Readable Documents

The 2025 Shanghai Clearing disclosure page lists eight downloadable documents.
Six produced useful machine-readable text:

- `doc_gd_sz_tqjf_2025_mtn4_001`: issuance plan and commitment letter, 32
  pages, 15,337 extracted characters
- `doc_gd_sz_tqjf_2025_mtn4_002`: issuer credit rating report, 29 pages,
  39,523 extracted characters
- `doc_gd_sz_tqjf_2025_mtn4_003`: 2023 audited financial report, 123 pages,
  108,078 extracted characters
- `doc_gd_sz_tqjf_2025_mtn4_004`: 2025 fourth MTN continuation prospectus, 62
  pages, 58,020 extracted characters
- `doc_gd_sz_tqjf_2025_mtn4_005`: 2024 audited financial report, 129 pages,
  106,217 extracted characters
- `doc_gd_sz_tqjf_2025_mtn4_008`: 2022 audited financial report, 130 pages,
  103,004 extracted characters

The 2025 third-quarter financial statement downloaded successfully but produced
no machine-readable text. The 2025 legal opinion downloaded successfully but
extraction produced only 21 characters, so it should not be used for coding
without OCR.

## Evidence Themes

### Municipal Platform Role

The rating report states that the issuer was established with approval from the
Shenzhen municipal government and is wholly owned and controlled by Shenzhen
SASAC. It describes the company as an important technology-park construction
and operation firm in Shenzhen. It also states that the company undertakes local
major infrastructure project investment and construction functions and
government assistance project capital-contribution functions.

Relevant extracted-text locations:

- `doc_gd_sz_tqjf_2025_mtn4_002.txt`, lines 120-131
- `doc_gd_sz_tqjf_2025_mtn4_002.txt`, lines 152-155

### Corporate-Debt and No-Hidden-Debt Commitment

The continuation prospectus states that, if the use of proceeds changes, the
issuer must check whether the change involves false debt resolution or new
hidden local government debt. It then commits that the MTN proceeds comply with
local-government debt-management rules, will not increase government debt or
hidden debt, will not be transferred to government or fiscal use, and will not
be directly repaid by fiscal funds. It also excludes land primary development,
ordinary commercial housing, affordable housing, and shantytown redevelopment
uses.

Relevant extracted-text location:

- `doc_gd_sz_tqjf_2025_mtn4_004.txt`, lines 360-384

### Infrastructure Project Functions

The continuation prospectus describes major infrastructure projects including
urban underground utility tunnels, land reclamation for the marine emerging
industry base, the Shenzhen Outer Ring Expressway, and the Shenzhen-Zhongshan
Link. The issuer's urban tunnel projects have a planned investment of RMB
14.116 billion and receive construction funds through direct fiscal allocation.
The marine project includes land formation and land-maturation work, with a
planned project investment of RMB 42.950 billion and a land-maturation
component of RMB 12.827 billion.

Relevant extracted-text locations:

- `doc_gd_sz_tqjf_2025_mtn4_002.txt`, lines 532-564
- `doc_gd_sz_tqjf_2025_mtn4_002.txt`, lines 565-585
- `doc_gd_sz_tqjf_2025_mtn4_004.txt`, lines 506-539

### Government Funding Channel and PPP Role

The continuation prospectus states that, according to Shenzhen government
arrangements, the issuer established a specialized transport investment company
in 2022 to undertake transport investment, construction, and operation. For the
Shenzhen Outer Ring Expressway, the issuer participated as the municipal
government's funding channel and did not receive future project income. For the
Shenzhen-Zhongshan Link, it contributed project capital as the municipal
government's funding channel, again without project equity or future income.
For Shenzhen Metro Lines 12 and 13, it participated as the government
contributor representative.

Relevant extracted-text location:

- `doc_gd_sz_tqjf_2025_mtn4_004.txt`, lines 972-1002

### Government Assistance and Functional Investment

The rating report states that the issuer participates in government assistance
and industrial cooperation projects in Heyuan, Guang'an, and Harbin on behalf
of the Shenzhen government. The funding for the issuer's capital contribution
is arranged by Shenzhen finance. These projects are formally structured through
project companies and are expected to become marketized over time, but their
origin and financing remain tied to municipal policy assignments.

Relevant extracted-text location:

- `doc_gd_sz_tqjf_2025_mtn4_002.txt`, lines 628-645

### Receivables, Construction Costs, and Subsidies

The rating report states that the issuer's other receivables include RMB 15.582
billion owed by the Shenzhen Finance Commission and other government
departments, mainly municipal engineering project advances. It also states that
the issuer's accounts receivable include investment-financing settlement
payments from the Shenzhen Finance Commission for the International Low-Carbon
City project. The 2023 audit report lists several construction costs as
entrusted-construction or agency-construction projects, including land
reclamation, utility tunnels, assistance hospitals, Jihe Expressway expansion,
and parking projects.

Relevant extracted-text locations:

- `doc_gd_sz_tqjf_2025_mtn4_002.txt`, lines 712-722
- `doc_gd_sz_tqjf_2025_mtn4_003.txt`, lines 2576-2585

## Coding Implication

This case should remain a boundary evidence packet rather than a final
human-validated label.

The strongest current interpretation is
`formal_fiscal_substitution_boundary_candidate`. The issuer looks very
different from distressed weak-capacity platforms. It operates in a strong
fiscal environment, has explicit municipal assignments, and has access to
formal project structures, fiscal allocations, project companies, PPP
arrangements, and state-capital channels. The documents also use clear
corporate-debt and no-hidden-debt language.

At the same time, the company does not represent a simple disappearance of the
platform function. It continues to act as infrastructure investor, fiscal
funding channel, project manager, government contributor representative, and
functional-investment vehicle. The case is therefore useful for the paper's
theory because it separates two dimensions that are easy to conflate: weak
historical capacity and weak contemporary fiscal capacity. Shenzhen is
historically low-density in the current CBDB-GADM measure, but its current
institutional and fiscal environment supports a more formalized version of
platform functions.
