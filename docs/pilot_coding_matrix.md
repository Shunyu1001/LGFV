# Pilot Coding Matrix

## Purpose

The pilot coding matrix translates the current evidence packets into a case-level
research instrument. It has two purposes. First, it records the best current
classification for each city-platform case without treating every row as a final
label. Second, it makes the next round of source collection conditional on what
is still missing for each case.

The matrix is stored in
`data/analysis_inputs/pilot_coding_matrix.csv`. It should be read together with
the case evidence packets in `coding/`, the codebook in `coding/codebook.md`,
and the human-validated labels in `data/processed/human_validated_labels.csv`.

## Validation tiers

The current rows fall into four tiers. First, `human_validated` rows already
have a reviewed label in `data/processed/human_validated_labels.csv`. These
cases can be used to illustrate the coding scheme and to test whether the
categories are operational. Second, `strong_candidate` rows have enough primary
or near-primary material to make a provisional classification, but still need
human review and at least one additional source check before being promoted to a
final label. Third, `boundary_candidate` rows are useful because they expose a
scope condition of the design. They should not be pooled with ordinary
weak-capacity cases until the paper decides how to separate historical state
capacity from contemporary fiscal capacity. Fourth, `source_only_candidate`
rows document useful evidence trails but do not yet support a final exit-type
classification.

This distinction is important for the paper. The matrix is not a completed
dataset. It is a disciplined coding log that prevents suggestive evidence from
being mistaken for validated data.

## Initial patterns

The matrix suggests three patterns that are worth retaining in the research
design. First, high-capacity cases are more likely to contain evidence of formal
fiscal substitution or organizational consolidation. Guangzhou City Construction
Investment Group is the cleanest current example, while Hangzhou shows a
related but different pattern in which public functions continue inside a
reorganized city investment system. Second, low-capacity cases more often show
compliance language alongside continuing public-project financing, fiscal
settlements, receivables, subsidies, or debt-resolution pressure. Zhuzhou and
Luzhou are the most useful non-Guizhou cases for this pattern. Third, Shenzhen
shows why the historical-capacity measure cannot be used mechanically. Its
imperial-era elite density is low, but its contemporary administrative and
fiscal capacity is unusually high, so the case should be treated as a boundary
case rather than as evidence for the low-capacity mechanism.

## Coding use

The matrix should be used in three ways. First, it provides a compact case map
for the paper's empirical-design section. It shows that the pilot contains
variation in historical capacity, document quality, and exit-type candidates.
Second, it identifies the next validation targets. The most useful promotions
are Zhuzhou and Luzhou, because both have low historical capacity and relatively
strong evidence of functional persistence after formal compliance language.
Third, it separates inclusion questions from labeling questions. Metro
companies and Shenzhen-type cases may be analytically useful, but their status
as core LGFV cases should be decided before their labels are used in any count
or comparison.

## Next validation sequence

The next coding round has three steps. First, review Zhuzhou and Luzhou against
the codebook and decide whether each is best coded as `nominal_exit` or
`functional_transfer`. Second, resolve the boundary status of Nanjing Metro,
Guangzhou Metro, and Shenzhen Special Zone Construction and Development Group.
This is a scope decision rather than a simple coding decision. Third, add only
one new high-capacity case and one new low-capacity case after these reviews are
complete. Otherwise, the pilot will accumulate source packets faster than it
accumulates validated labels.

The first review memo for this step is
`docs/validation_memo_zhuzhou_luzhou.md`. It recommends treating Zhuzhou as
close to promotion as a `nominal_exit` case, while keeping Luzhou as a strong
candidate until a direct formal-exit or debt-resolution source is found.
