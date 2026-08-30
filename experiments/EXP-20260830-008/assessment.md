# Experiment assessment

## Status

`quarantine`

The exact-key geography audit is reproducible and preserves the null result,
but it does not meet the predeclared coverage threshold. The proposed frame
remains unsuitable for a validation draw.

## Results

The Experiment 003 frame contains five units with preexisting province and city
and 128 incomplete units. Exact identifier joins were attempted in the frozen
source order against the master case pool, expanded candidate seed, source
inventory, and document inventory. The permitted exact normalized issuer-name
fallback was also checked. None of the 128 incomplete units received a unique
province-city pair. No conflicting pair was found because the matched tracked
records also lack usable geography for these units.

The experiment therefore resolved 0 of the required 116 incomplete units and
failed the 90 percent coverage threshold. It used no company-name parsing,
external lookup, manual imputation, random seed, sample draw, or label change.
The enriched frame and crosswalk preserve all 128 units as unresolved.

## Interpretation

The missing geography is not recoverable by joining the currently tracked
analysis inventories. A successful repair requires new traceable issuer-level
metadata or human verification against original or authoritative documents.
The work must also distinguish city-platform issuers from provincial, central,
specialized, and other boundary entities. Assigning a city from a recognizable
company name would violate the experiment rule and the repository's audit
standard.

## Required next work

Create a rights-aware geography and scope packet for the 128 unresolved issuer
units. Each proposed city and province should cite an authoritative company,
government, exchange, registration, or source-packet record and should record
whether the issuer meets the city-platform inclusion rule. Ambiguous and
non-core issuers remain boundary cases. The PI must approve the resulting
eligible frame and probability design before sampling.

This work requires source collection or human verification beyond the current
tracked metadata. Additional mechanical joins over the same files are not a
high-value experiment.
