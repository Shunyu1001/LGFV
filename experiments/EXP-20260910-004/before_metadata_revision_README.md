# Validation collection handoff

This dated package covers 67 candidate issuer units, not a frozen sample or completed validation.

## Distribution

After separate collection authorization, give each coder only blinded_packets.csv, blinded_sources.csv, their own blinded_coder_1_entry.csv or blinded_coder_2_entry.csv, and the unchanged coding/codebook.md. Do not give coders coordinator files, historical comparisons, readiness, metrics, other decisions, or the full repository. IDs and original public-source content are necessary locators, not predictions. Blinding here means absence of inherited predictions/decisions in the instruments; actual coder blinding is not documented.

## Human entries

All decision, score, event, reviewer, date, and signature fields are blank. Empty means missing, not zero, false, nominal exit, or ineligible. The 67 units meet platform scope, not yet codebook exit-case eligibility. Ten have no direct formal-event screen; that is a screen, not a human decision. Record exit_case_eligibility separately as eligible, unresolved, or ineligible, and formal_event_found and post_event_evidence_found separately. Missing formal/post-event evidence leaves the exit case unresolved or ineligible and final_label blank. Only the four codebook exit labels are allowed; unresolved is not a fifth label or negative outcome. Keep each coder's decisions independent and retain the original forms before any separately authorized adjudication. The builder never imports or promotes submitted forms and refuses to overwrite changed outputs.

## Source reconstruction

Sources are the union of exact origin document IDs, exact unit-and-issuer source-manifest rows, and exact origin-case source inventory rows. No source searches or downloads were performed. Read original public documents using the recorded URLs or rights-approved local archive paths. Use expected hashes to verify cached raw/text files. Inventory flags and past retrieval claims are not current availability; coordinator_source_audit.csv and local_file_audit.json record actual local checks. Absolute paths refer to this machine and must be relocated explicitly on another machine. No raw documents are redistributed. Document coverage is not a human determination of event or post-event evidentiary sufficiency. The empty Guiyang origin-document list and missing historical Shenzhen raw page remain recorded; linked current sources do not erase those gaps.

## Historical labels and design

The reference report covers only its original 94 cases. The pair audit examines all 67 x 94 issuer/event pairs, requires exact issuer and event links, and never uses city or capacity links as label matches. Original production and author-reported checking remain distinct from new independent decisions. Proposed pi=1 and legacy frozen_stratum_id field names in the sidecar do not establish a freeze or realized inclusion probability. Human decisions and actual inclusion probabilities remain null; downstream validation estimates are blocked.

## Reproduction

From this worktree run python3 scripts/build_validation_collection_package.py --check and python3 -m unittest discover -s tests -p test_validation_collection_package.py -v. The builder checks each tracked input against its stated base Git object, including schema/order; it hashes local files only at recorded locations. A clean initial run without --check creates the dated files; reruns are idempotent. Changed forms or audits require a new authorized version, not overwriting this handoff. Hashes cover all generated outputs except the hash index itself.
