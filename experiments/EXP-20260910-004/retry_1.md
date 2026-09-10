# Mechanical retry 1

Attempt 1 built the package, reproduced it byte-for-byte, and passed all five
read-only repository checks. Eighteen of 19 collection tests passed. One test
incorrectly assumed all four historical packet IDs remained in the current
candidate. The builder correctly reported three retained IDs, 64 additions,
and historical-only mv_83fa1cb2dc9e. The current origin table marks this issuer
ineligible. No frame or packet membership is changed to satisfy the test.

Correction: compare the historical and current exact ID sets directly, including
their difference, instead of assuming the historical packet is a subset. The
original success criterion was an accurate comparison, not retaining all four
historical units. This corrects a test fixture, not a hypothesis or criterion.
All production code and generated output bytes are unchanged. Retain
attempt_1.json in full; execute the same command list as attempt 2. One of two
mechanical retries is used.
