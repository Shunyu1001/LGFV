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

## How This Changes The Paper

The paper should not present historical state capacity as a vague old variable. It should define it as a set of persistent institutional resources with observable historical proxies.

The main measure can be Qing administrative density. The interpretation is that denser historical administrative presence created more routinized local bureaucratic capacity, making it easier for contemporary local governments to move infrastructure finance from informal platform arrangements into formal budgetary or state-owned-asset systems.

The main alternative measure can be Ming-Qing elite density from CBDB. The interpretation is that regions with denser historical elite production had deeper pools of bureaucratic human capital and stronger traditions of administrative compliance.

The courier-route measure can test whether the result is really about administrative penetration rather than only economic geography or historical transport access.
