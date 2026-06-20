# Pilot Collection Log

## 2026-06-20

The first collection pass searched for platform-level source material for the
initial eight-city pilot. The in-app browser automation interface was not
available, so the search was conducted through web search and direct page
inspection.

The first pass found three usable official sources.

First, Guangzhou has a usable company source. The Guangzhou City Construction
Investment Group website describes the group as a wholly municipal functional
state-owned enterprise engaged in urban infrastructure investment, financing,
construction, operation, and management. This source is useful for identifying
the company as a relevant platform case, but it is not sufficient for assigning
an exit type. The next source should be a bond prospectus or credit rating
report.

Second, Chengdu has a usable company source. The Chengdu City Construction
Investment Management Group website describes the group as a municipal
state-owned enterprise focused on government-related major municipal projects
and market-oriented urban comprehensive development projects, with business
segments including infrastructure construction, urban comprehensive
development, urban operation services, urban industry investment, and smart
city construction. This source is useful for identifying the company and its
pre-exit function. The next source should be a bond prospectus or credit rating
report.

Third, Shenzhen has a usable government source. The Shenzhen SASAC page for
Shenzhen Special Zone Construction and Development Group describes the group as
a municipal comprehensive investment and financing platform company and as an
infrastructure investment, construction, and operation platform. This is a
strong source for platform identification. The next source should be bond or
rating disclosure material that indicates whether the group continues to
perform government financing functions after official exit or transformation.

No final exit labels are assigned in this collection pass. The current output is
source discovery only.

## 2026-06-20, follow-up search

The second search pass tried to move from company identification to bond and
rating documents.

First, the Shanghai Stock Exchange bond announcement page was inspected. Its
public page loads company bond announcements through `query.sse.com.cn` with
`sqlId = BS_ZQ_GGLL`. The relevant announcement categories include `1601` for
rating announcements and `1105` for issuance documents. A test query for
Guangzhou City Construction Investment Group using both the full company name
and the shorter keyword `广州城投` returned no records for 2023-01-01 to
2026-06-20 under the company/corporate bond bulletin categories. This does not
mean that the company has no bonds; it only means that this SSE route did not
find useful documents in this query.

Second, the NAFMII disclosure page was inspected. The page uses JavaScript and
WAF verification before loading the disclosure interface. For this reason, it
is not a good target for command-line collection in the current environment.
The project should use the website manually, use another accessible disclosure
portal, or rely on commercial databases if available.

Third, broad web search for exact company names plus `募集说明书` and
`跟踪评级报告` did not yet produce stable official documents for the three
started cases. The next collection pass should try ChinaBond's bond search,
company websites' disclosure sections, local SASAC pages, and issuer-specific
searches using bond abbreviations rather than only company names.
