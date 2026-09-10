# Corrective integration assessment

Disposition: quarantine, 2026-09-10.

The current integration and a clean reconstruction from `9977dd7` produced
identical hashes for all seven frame outputs and the experiment metrics. An
immediate rerun was also identical. The independent input-integrity tests and
six historical freeze-package tests passed. Immutable, ledger, label, and
master-pool checks passed. The 67-unit candidate remains provisional.

The full source check did not pass. Recovery reproduced 158 of 159 cited raw
documents and their registered text representations. The live Shenzhen SASAC
profile returned 76,974 bytes with raw hash
`2d13b660ee1b469483ca81f79e7843140cce78814e8fc77b7f22c6aa7acb9550`,
not the registered 77,052 bytes and hash
`9b6232467e0f605517f8e73c5741dbf1e05d0f5c7891f198b6f59105bbd88407`.
The replacement was not written to the old cache filename. Current validation
and the dependent integration-test setup correctly failed on that absent raw
snapshot. No acceptance criterion was relaxed.

Three recovery diagnostics are retained. The first lacked the PDF extraction
executable; the second used a different Poppler version and lacked the four
registered pdfplumber layout extractions; the third reproduced all PDF hashes
using the original bundled Poppler and the registered pdfplumber settings.
These are input-recovery diagnostics, not three successful validation runs.
`audit_attempt_1.json` preserves the actual full run and its failures.

The independent AI review prompted fixed acceptance hashes for the two
approved crosswalk records and added source, exact baseline-manifest checks,
complete origin-metadata invariance, and raw-PDF reconstruction of the new
Guiyang text. This is an implementation review, not human outcome validation.

Further inspection of the inherited Shenzhen profile citation also found that
its owner excerpt consisted of website navigation rather than focal-issuer
ownership evidence. A separate pre-result source-renewal experiment is required
to review and register the current source and correct these locators. The old
manifest, this failure, and all working-reference and surrogate labels remain
unchanged. No sampling draw was executed.
