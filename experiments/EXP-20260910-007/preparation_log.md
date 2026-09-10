# Integration preparation log

The baseline run passed all five commands and reproduced the fixed four-model
sparse-outcome audit. The first intermediate PDF build passed. One patch
context mismatch during claim/prose integration applied no partial changes;
the claim rows were then added before the corresponding results paragraphs.

The first direct adapter test run executed eight tests. Seven passed; the
synthetic projection roundtrip compared the floating-point result
0.4999999999999999 to 0.5 using exact tuple equality. The expected mean and
projection remain 0.5. Mechanical correction 1 replaces that assertion with a
12-decimal-place comparison and retains an explicit one-parameter shape check.
No estimator or criterion concerning real data, labels, or design changed.

The estimator worker's separate inherited freeze-validator failure and initial
extreme-prediction failure are preserved in EXP-20260910-005. The current
compatibility amendment only reuses already approved exact provenance hashes.
