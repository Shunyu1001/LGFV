# Surrogate Validation Queue

Date: 2026-07-02

This note summarizes the current human-review queue generated from the Codex surrogate-labeling pass. After the July 2 promotion batches, the queue is empty. The remaining 52 disclosure-level Codex surrogate `nominal_exit` labels collapse to 33 unique issuers, and all 33 issuers already overlap with the human gold-standard file under another case ID. These rows are useful as consistency checks and repeated-disclosure evidence, but they are not new validation targets.

The queue file is stored in `data/analysis_inputs/surrogate_validation_queue_2026_07_02.csv` and currently contains zero rows. The next data task is therefore no longer queue review. It is source-packet extraction and unresolved-case triage: 82 pending disclosures have usable text but no direct formal exit or compliance event identified by the conservative Codex pass, 67 have downloaded PDF records without usable extracted text, and 17 have no collected document packet.

Future queue rows should be generated only after new source packets produce non-overlap surrogate labels. A row should then be promoted to the gold-standard label file only if original PDF evidence supports both the formal event and the post-event functional assessment. Rows should be marked as boundary if the issuer is a specialized industrial, energy, provincial, or otherwise non-core LGFV entity whose inclusion would blur the sampling frame.
