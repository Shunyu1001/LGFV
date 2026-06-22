# Historical State Capacity Source Memo

## Purpose

The paper needs a historical state-capacity measure that can be linked to contemporary prefecture-level cities. The measure should be interpretable as historically rooted administrative or fiscal capacity rather than as a contemporary development proxy. It should also be feasible to construct with public or academically accessible data.

The strongest immediate strategy is to build more than one historical measure and then choose a main specification after checking coverage and matching quality. The current priority is to construct a historical administrative-density measure from CHGIS and a historical elite-density measure from CBDB. A transportation or courier-station measure can be added as a robustness check if the spatial join is manageable.

## Candidate Source 1: CHGIS V6

Source: China Historical Geographic Information System, Version 6.  
Main page: `https://chgis.fas.harvard.edu/data/chgis/v6/`  
Distribution page: `https://dataverse.harvard.edu/dataverse/chgis_v6`

CHGIS is the best starting point for historical administrative density. The project describes CHGIS as a free database of placenames and historical administrative units for Chinese dynasties. Version 6 was published in 2016 and includes time-series updates for counties and prefectures. The CHGIS V6 page also provides time-slice downloads for 1820, 1911, and 1990.

The most direct variable is historical administrative density. For each contemporary prefecture-level city, construct the number of Qing-era county-level or prefecture-level administrative units that intersect the contemporary city boundary, divided by land area. A second version can use distance from the contemporary city centroid to the nearest Qing prefectural seat or county seat.

Advantages:

- It maps directly onto the theoretical mechanism of administrative penetration.
- It can be spatially joined to contemporary prefecture boundaries.
- The 1820 and 1911 slices allow comparison between late-imperial administrative density and the Republican transition.

Limitations:

- Spatial joins will require harmonizing historical units to contemporary prefecture-level boundaries.
- Administrative density may partly proxy for population density or long-run economic development, so the empirical section should control for historical population or contemporary population where possible.

Initial use in the paper:

CHGIS should be the main historical state-capacity source. The first operational variable should be Qing county/prefecture density within contemporary prefecture boundaries.

## Candidate Source 2: CBDB

Source: China Biographical Database Project.  
Project page: `https://cbdb.hsites.harvard.edu/`  
SQLite release repository: `https://github.com/cbdb-project/cbdb_sqlite`  
Latest metadata: `https://raw.githubusercontent.com/cbdb-project/cbdb_sqlite/master/latest.json`

CBDB is a freely accessible relational database with biographical information on historical Chinese individuals. The project page states that it covers roughly 657,909 individuals as of May 2026, mainly from the seventh through nineteenth centuries. The GitHub repository points to a downloadable SQLite release; the current metadata file lists `cbdb_20260314.sqlite3`, generated on 2026-03-14, with a direct Hugging Face download URL.

The most relevant variable is historical elite density. Use CBDB to count Ming-Qing civil service degree holders, especially jinshi or other high-degree holders, by place of basic affiliation. Then aggregate those historical places to contemporary prefectures and divide by area or historical population proxy if available.

Advantages:

- It captures local elite formation and bureaucratic recruitment capacity.
- It is theoretically distinct from administrative-unit density.
- It can be used as an alternative measure or mechanism variable for persistent bureaucratic routines and compliance capacity.

Limitations:

- CBDB places must be matched to contemporary prefectures, probably through CHGIS place identifiers or spatial coordinates.
- Elite density is not identical to fiscal capacity. It should be interpreted as administrative-human-capital density, not as a direct tax-capacity measure.
- Coverage varies across dynasties and regions, so the paper should report missingness and possibly use broad dynastic windows rather than narrow year bins.

Initial use in the paper:

CBDB should be the second historical-capacity source. The first operational variable should be Ming-Qing high-degree-holder density by contemporary prefecture.

## Candidate Source 3: Ming Courier Routes And Stations

Source: CHGIS Other Historical Datasets.  
Page: `https://chgis.fas.harvard.edu/data/other/`

The CHGIS other-datasets page lists a 2016 shapefile for Ming Dynasty courier routes and stations. This can be used to construct a historical transportation and communication infrastructure measure. For each contemporary prefecture, calculate distance to the nearest courier route or station, or the density of courier stations within the prefecture.

Advantages:

- It captures state communication infrastructure rather than administrative hierarchy alone.
- It can serve as a mechanism or robustness check for the persistence of administrative reach.

Limitations:

- It is Ming-specific, while the main state-capacity story may be easier to explain with Qing administrative density.
- Courier routes may proxy for geography, trade, and military transport rather than purely administrative capacity.

Initial use in the paper:

Use this only after the CHGIS and CBDB variables are working. It is a robustness or mechanism variable, not the first main measure.

## Recommended Data Construction Order

First, download CHGIS V6 time-slice data and inspect the 1820 and 1911 administrative layers. The first task is not analysis but variable feasibility: identify the fields for administrative level, place name, geometry, and time slice.

Second, assemble a contemporary prefecture boundary file. The project needs one stable modern boundary layer for prefecture-level cities. Once this layer is chosen, all historical measures should be spatially joined to the same modern units.

Third, construct Qing administrative density. Count historical county-level and prefecture-level units intersecting each contemporary prefecture, and divide by prefecture land area.

Fourth, download the CBDB SQLite release and inspect tables related to persons, offices, entry into civil-service degrees, and addresses. The first pass should count Ming-Qing high-degree holders by basic affiliation and join those affiliations to CHGIS or contemporary prefectures.

Fifth, add courier-route or courier-station proximity only after the two main measures work.

## Current Construction Status

The first CBDB construction pass has been implemented in
`scripts/prepare_cbdb_elite_counts.py`. The script downloads or reads the local
CBDB SQLite release, records the release metadata, extracts the entry codes
linked to jinshi and juren examination categories, and writes a place-level
count file:

- `data/analysis_inputs/cbdb_mingqing_elite_place_counts.csv`
- `data/diagnostics/cbdb_release_metadata.csv`
- `data/diagnostics/cbdb_exam_entry_codes.csv`
- `data/diagnostics/cbdb_elite_address_coverage.csv`
- `data/diagnostics/cbdb_schema_summary.csv`

The current local CBDB file is `cbdb_20260620.sqlite3`. The SQLite checksum
matches the metadata stored inside the downloaded Hugging Face zip. The first
pass uses Ming, Qing, and Southern Ming biography dynasties; entry types
`040101` and `040102`; and preferred address types for basic affiliation,
Ming household address, actual residence, household registration address, and
alternate basic affiliation. The script produces 3,514 historical places with
non-missing preferred addresses. It identifies 98,880 Ming-Qing examination
elite persons in total, of whom 91,241 have a preferred address and 7,639 do
not.

This output is not yet the final historical-capacity measure. Its unit is a
CBDB historical place, not a contemporary prefecture-level city. The next step
is to join the CBDB place identifiers or coordinates to CHGIS and then to a
stable contemporary prefecture boundary file.

The first contemporary-boundary match has now been implemented in
`scripts/match_cbdb_to_gadm_prefectures.py`. The script uses GADM 4.1 China
ADM2 boundaries as a local modern prefecture-level boundary source. GADM's
China ADM2 file contains 368 administrative units and includes province and
prefecture names, Chinese names, and prefecture type fields. Because GADM
allows academic and other non-commercial use but does not allow redistribution
of the raw boundary data, the boundary zip is stored only in `data/raw/` and is
not committed to the repository.

The matching script assigns CBDB historical places to GADM ADM2 polygons using
their longitude and latitude, then aggregates jinshi and juren counts to the
modern prefecture. It writes:

- `data/analysis_inputs/cbdb_place_to_gadm_prefecture_crosswalk.csv`
- `data/analysis_inputs/cbdb_mingqing_elite_gadm_prefecture_counts.csv`
- `data/diagnostics/cbdb_gadm_match_coverage.csv`
- `data/diagnostics/cbdb_gadm_unmatched_places.csv`
- `data/diagnostics/gadm_china_adm2_metadata.csv`

The first match assigns 3,356 of 3,514 CBDB historical places to a GADM ADM2
unit. These matched places account for 89,433 of the 91,241 examination-elite
persons with preferred addresses. The unmatched cases account for 1,808 persons
and are concentrated among banner categories, broad historical regions, missing
coordinates, Taiwan, and other places that do not fall cleanly inside the
mainland China GADM boundary. The resulting prefecture table covers 286
contemporary GADM ADM2 units with at least one matched CBDB place. The table
also reports approximate prefecture area and elite, jinshi, and juren counts
per 1,000 square kilometers.

The CHGIS construction pass has been started with
`scripts/inspect_chgis_archives.py`. This script reads locally downloaded CHGIS
zip files and writes archive and DBF-field inventories without requiring
geopandas. Harvard Dataverse blocked automated API access during the current
run, so the 1820 and 1911 CHGIS V6 time-slice zip files still need to be
downloaded manually into `data/raw/historical/chgis/` before the field
inspection can proceed.

## How This Changes The Paper

The paper should not present historical state capacity as a vague old variable. It should define it as a set of persistent institutional resources with observable historical proxies.

The main measure can be Qing administrative density. The interpretation is that denser historical administrative presence created more routinized local bureaucratic capacity, making it easier for contemporary local governments to move infrastructure finance from informal platform arrangements into formal budgetary or state-owned-asset systems.

The main alternative measure can be Ming-Qing elite density from CBDB. The interpretation is that regions with denser historical elite production had deeper pools of bureaucratic human capital and stronger traditions of administrative compliance.

The courier-route measure can test whether the result is really about administrative penetration rather than only economic geography or historical transport access.
