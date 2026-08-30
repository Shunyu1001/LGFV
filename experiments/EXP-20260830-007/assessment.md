# Experiment assessment

## Status

`quarantine`

The structural part of the proposed frame is reproducible, but the identifier
gate fails. The outputs must not be used to draw a validation sample until the
missing geography is resolved and the PI approves the validation design.

## Results

The expanded files produce 133 unique, named, source-available, non-overlap
issuer units. The frame contains the predeclared 97 one-sided positive issuers
and 36 issuers for which the screen found no direct formal event. Every
positive issuer matches exactly one row in the 97-row validation queue. No
frame issuer overlaps the gold file, and every unit has source-row, pool, and
evidence-document identifiers. The generated validation-unit identifiers are
unique.

The geographic readiness criterion fails. Province and city are both missing
for 128 of the 133 issuer units, producing 256 blank required design fields.
The candidate source files therefore do not yet support the proposed
city-platform validation frame as specified. This is not a formatting defect:
the missing geography prevents a check that every issuer is tied to the unit
defined in the codebook and prevents any approved geographic stratification or
coverage summary.

The prediction-free coder template contains all 133 units, their packet
identifiers, and blank coding fields. It contains no screen status, surrogate
label, confidence, model rationale, existing label, gold indicator, or sample
selection field. All coder-entry cells are blank. The template remains an
artifact for review and must not be circulated for coding until its geography
and scope fields are completed from traceable sources.

## Integrity decision

The result is quarantined rather than repaired post hoc. The success criteria
required complete issuer, province, city, source-row, pool, and document
identifiers. The experiment found complete packet identifiers but incomplete
geography. No random seed was set, no sample was drawn, and no label was
assigned or changed.

## Required next work

The next bounded experiment should attempt a deterministic, source-traceable
join from each validation issuer to an existing city and province record. It
must predeclare the source hierarchy and must not infer geography from company
names when the tracked records conflict or remain blank. Issuers that are
provincial, central, specialized, or otherwise outside the codebook's
city-platform frame must remain explicit boundary cases rather than receiving
an imputed city.

After the join, the PI must review the resulting eligible frame and approve or
revise the probability allocation before any sampling draw.
