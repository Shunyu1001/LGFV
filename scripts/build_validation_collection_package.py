#!/usr/bin/env python3
"""Build a dated, source-auditable collection instrument, never new labels."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "4330c5728dec64ba30c1faec972fad0097622e9d"
BASE_REPOSITORY = Path("/Users/shunyuhao/Documents/LGFV")
EXPERIMENT = "EXP-20260910-004"
OUTPUT = Path("data/validation/collection_2026_09_10")
V = "data/validation/"
INPUTS = {
    "candidate": V + "probability_validation_frame_candidate.csv",
    "origins": V + "probability_validation_frame_origin_rows.csv",
    "design": V + "probability_validation_sampling_design.csv",
    "manifest": V + "probability_validation_source_manifest.csv",
    "documents": "data/document_inventory.csv",
    "sources": "data/source_inventory.csv",
    "reference": "data/processed/working_reference_labels.csv",
    "report": V + "human_confirmation_report_2026_09_10.json",
    "register": V + "human_confirmation_register.csv",
    "historical": V + "independent_coding/blinded_probability_validation_packet.csv",
    "archive": "experiments/EXP-20260910-002/source_archive_attempt_2.json",
    "codebook": "coding/codebook.md",
    "analysis_plan": "immutable/analysis_plan.md",
    "state": "ledgers/research_state.yaml",
}
LABELS = ("substantive_exit", "nominal_exit", "functional_transfer", "liquidation")
ENTRY_FIELDS = [
    "coder_id", "coding_date", "exit_case_eligibility", "formal_event_found", "post_event_evidence_found",
    "formal_event_year", "formal_event_summary", "formal_event_source_references",
    "baseline_platform_function", "post_event_function", "post_event_source_references",
    "final_label", "alternative_label", "confidence", "source_coverage_score",
    "continued_function_evidence_score", "rationale", "ambiguity_note",
    "remaining_caveat", "coder_signature",
]
PACKET_FIELDS = ["packet_case_id", "issuer_name", "province", "city", "source_record_ids"]
SOURCE_FIELDS = [
    "packet_case_id", "source_record_id", "document_id", "source_id",
    "document_title", "document_type", "document_date", "document_page_url",
    "download_url", "inventory_archive_path", "manifest_archive_path",
    "manifest_text_archive_path", "expected_raw_sha256", "expected_text_sha256",
]
ADJUDICATION_FIELDS = [
    "packet_case_id", "coder_1_decision_reference", "coder_2_decision_reference",
    "agreement_status", "adjudicated_label", "adjudication_rationale",
    "adjudication_source_references", "adjudicator_id", "adjudication_date",
    "adjudicator_signature",
]
PAIR_FIELDS = [
    "packet_case_id", "reference_case_id", "issuer_exact_match",
    "origin_case_exact_match", "primary_event_document_exact_match",
    "event_exact_match", "historical_capacity_link_only", "mapping_status", "reason",
]
MAPPING_FIELDS = [
    "packet_case_id", "reference_case_id", "confirmed_reference_label",
    "report_id", "label_role", "mapping_status", "reason",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def csv_bytes(rows: list[dict], fields: list[str] | None = None) -> bytes:
    fields = fields or list(rows[0])
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        require(set(row) == set(fields), "Output schema mismatch")
        writer.writerow(row)
    return handle.getvalue().encode("utf-8")


def parse_csv(raw: bytes, fields: list[str] | None = None) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    header = reader.fieldnames
    require(bool(header) and len(header) == len(set(header)), "Duplicate or empty CSV schema")
    if fields is not None:
        require(header == fields, "CSV schema changed (including column order)")
    rows = list(reader)
    require(all(None not in row and None not in row.values() for row in rows), "Malformed CSV row")
    return rows


def unique(rows: list[dict], fields: tuple[str, ...]) -> dict[tuple, dict]:
    result = {}
    for row in rows:
        key = tuple(row[field] for field in fields)
        require(all(key) and key not in result, f"Duplicate or empty key {fields}: {key}")
        result[key] = row
    return result


def split_ids(value: str) -> list[str]:
    if not value:
        return []
    parts = value.split(";")
    require(all(parts) and len(parts) == len(set(parts)), "Duplicate/empty ID in list")
    return parts


def verify_payload(path: str, raw: bytes, canonical: bytes) -> None:
    if path.endswith(".csv"):
        fields = next(csv.reader(io.StringIO(canonical.decode("utf-8-sig"))))
        parse_csv(raw, fields)
    require(sha256(raw) == sha256(canonical), f"Pinned input hash mismatch: {path}")


def load_inputs(root: Path = ROOT) -> tuple[dict, list[dict]]:
    data, hashes = {}, []
    for name, relative in INPUTS.items():
        canonical = subprocess.check_output(["git", "show", f"{BASE}:{relative}"], cwd=ROOT)
        # Coordinator state is audit context, not a mutable scientific input.
        raw = canonical if name == "state" else (root / relative).read_bytes()
        verify_payload(relative, raw, canonical)
        data[name] = parse_csv(raw) if relative.endswith(".csv") else (
            json.loads(raw) if relative.endswith(".json") else raw.decode("utf-8")
        )
        hashes.append({"path": relative, "base_commit": BASE, "sha256": sha256(raw),
                       "bytes": len(raw), "rows": len(data[name]) if relative.endswith(".csv") else None,
                       "pin_policy": "baseline_snapshot_only" if name == "state" else "strict_current_scientific_input"})
    return data, hashes


def authorized_reference_rows(data: dict) -> list[dict]:
    reference, report, register = data["reference"], data["report"], data["register"]
    require(report["report_id"] == "HC-20260910-001", "Unsupported report")
    require(report["source_snapshot"] == INPUTS["reference"], "Wrong report snapshot")
    require(report["case_count"] == len(reference) == 94, "Report scope is not exactly 94")
    require(dict(Counter(row["final_label"] for row in reference)) == report["outcome_counts"],
            "Report outcome counts mismatch")
    require(report["scope_exclusions"] == ["surrogate labels", "probability-frame candidates",
                                           "control variables", "mechanism codes"], "Report scope changed")
    require(report["reviewer_identity"] is None and report["review_completed_on"] is None,
            "Unreported reviewer metadata changed")
    require(report["blinding_status"] == "not_reported" and
            report["independent_coder_decisions_received"] is False and
            report["signed_coding_forms_received"] is False and
            report["probability_validation_completed"] is False, "Report protocol changed")
    refs = unique(reference, ("case_id",))
    regs = unique(register, ("case_id",))
    require(refs.keys() == regs.keys(), "Confirmation register case scope mismatch")
    result = []
    for (case_id,), row in sorted(refs.items()):
        reg = regs[(case_id,)]
        require(row["final_label"] in LABELS, "Invalid reference label")
        expected = {
            "case_id": case_id, "confirmed_label": row["final_label"],
            "original_label_producer": row["reference_label_producer"],
            "confirmation_status": "human_checked_no_revision_author_reported",
            "confirmation_basis": "author_report_of_completed_human_check",
            "report_id": report["report_id"], "reported_by": report["reported_by"],
            "reported_on": report["reported_on"], "reviewer_identity": "",
            "review_completed_on": "", "blinding_status": "not_reported",
            "source_snapshot_sha256": report["source_snapshot_sha256"],
        }
        require(reg == expected, f"Unauthorized reference mapping: {case_id}")
        result.append({**reg, "issuer_name": row["company_name"],
                       "official_exit_year": row["official_exit_year"],
                       "official_exit_event": row["official_exit_event"],
                       "primary_evidence_doc": row["primary_evidence_doc"],
                       "primary_evidence_lines": row["primary_evidence_lines"],
                       "label_role": "historical_reference_author_report_only"})
    return result


def match_reference(unit: dict, origins: list[dict], ref: dict) -> dict:
    # Neither geography nor punctuation/alias similarity is identity evidence.
    issuer = unit["issuer_name"] == ref["company_name"]
    linked_origins = [o for o in origins if o["source_row_id"] == ref["case_id"]]
    primary = bool(ref["primary_evidence_doc"]) and any(
        ref["primary_evidence_doc"] in split_ids(o["evidence_document_ids"]) for o in linked_origins
    )
    event = bool(linked_origins and primary and ref["official_exit_year"] and ref["official_exit_event"])
    matched = issuer and event
    reason = "exact_issuer_case_and_primary_event_document" if matched else (
        "issuer_not_exact" if not issuer else "event_case_or_primary_evidence_not_exact"
    )
    return {
        "packet_case_id": unit["validation_unit_id"], "reference_case_id": ref["case_id"],
        "issuer_exact_match": str(issuer).lower(),
        "origin_case_exact_match": str(bool(linked_origins)).lower(),
        "primary_event_document_exact_match": str(primary).lower(),
        "event_exact_match": str(event).lower(),
        "historical_capacity_link_only": str(ref["case_id"] in split_ids(
            unit["historical_capacity_source_case_ids"])).lower(),
        "mapping_status": "exact_historical_reference" if matched else "unmatched",
        "reason": reason,
    }


def historical_mapping(unit_id: str, pairs: list[dict], reference: list[dict]) -> dict:
    matched = [p for p in pairs if p["mapping_status"] == "exact_historical_reference"]
    case_id = matched[0]["reference_case_id"] if len(matched) == 1 else ""
    lookup = {r["case_id"]: r for r in reference}
    return {
        "packet_case_id": unit_id, "reference_case_id": case_id,
        "confirmed_reference_label": lookup[case_id]["confirmed_label"] if case_id else "",
        "report_id": "HC-20260910-001" if case_id else "",
        "label_role": "historical_reference_only_not_new_validation" if case_id else "missing",
        "mapping_status": "exact_historical_reference" if case_id else "unmatched",
        "reason": "exact_issuer_case_and_primary_event_document" if case_id else (
            "ambiguous_multiple_reference_events" if len(matched) > 1 else
            "no_exact_issuer_in_report_scope" if not any(p["issuer_exact_match"] == "true" for p in pairs)
            else "no_exact_event_in_report_scope"),
    }


def map_outcome(label: str | None) -> int | None:
    if label in (None, "", "liquidation"):
        return None
    require(label in LABELS, f"Unrecognized label, no aliases accepted: {label}")
    return {"nominal_exit": 0, "substantive_exit": 1, "functional_transfer": 1}[label]


def human_entry_state(row: dict) -> dict:
    label = row.get("final_label", "")
    map_outcome(label)
    eligibility = row.get("exit_case_eligibility", "")
    require(eligibility in ("", "eligible", "unresolved", "ineligible"), "Unknown exit eligibility state")
    for field in ("formal_event_found", "post_event_evidence_found"):
        require(row.get(field, "") in ("", "yes", "no", "unresolved"), "Unknown evidence state")
    sufficient_fields = all(row.get(field) for field in (
        "formal_event_summary", "formal_event_source_references", "post_event_function",
        "post_event_source_references")) and all(row.get(field) == "yes" for field in (
            "formal_event_found", "post_event_evidence_found"))
    require(eligibility != "eligible" or sufficient_fields, "Exit eligibility lacks formal/post-event evidence")
    require(not label or (eligibility == "eligible" and sufficient_fields),
            "Label requires separate exit eligibility and formal/post-event evidence")
    return {"label": label or None, "entry_state": "submitted_unverified" if label else "missing",
            "exit_case_eligibility": eligibility or "unresolved",
            "realized_validation_outcome": None, "reviewer_identity": row.get("coder_id") or None,
            "signature": row.get("coder_signature") or None}


def archive_path(directory: Path, filename: str) -> str:
    if not filename:
        return ""
    require(Path(filename).name == filename and filename not in (".", ".."), "Unsafe cache filename")
    return str(directory / filename)


def audit_file(path: str, expected: str, cache: dict) -> dict:
    if not path:
        return {"state": "missing_locator", "sha256": None, "bytes": None}
    if path not in cache:
        location = Path(path)
        if not location.is_file():
            cache[path] = {"state": "missing_file", "sha256": None, "bytes": None}
        else:
            try:
                raw = location.read_bytes()
                cache[path] = {"state": "present_unanchored", "sha256": sha256(raw), "bytes": len(raw)}
            except OSError as error:
                cache[path] = {"state": "unreadable", "sha256": None, "bytes": None,
                               "error": type(error).__name__}
    result = dict(cache[path])
    if result["sha256"] and expected:
        result["state"] = "verified" if result["sha256"] == expected else "hash_mismatch"
    return result


def validate_blinded(raw: bytes, fields: list[str], blank_fields: list[str]) -> list[dict]:
    rows = parse_csv(raw, fields)
    for row in rows:
        require(all(row[f] == "" for f in blank_fields), "Label/process value leaked into blank instrument")
        for value in row.values():
            require(not any(token in value for token in (
                "screen_positive_nominal", "screened_no_direct_formal_event",
                "codex_surrogate", "human_checked_no_revision_author_reported", *LABELS,
            )), "Inherited label/status leaked into blinded values")
    return rows


def build_outputs(data: dict, input_hashes: list[dict]) -> dict[str, bytes]:
    units = sorted(data["candidate"], key=lambda r: r["validation_unit_id"])
    unit_index = unique(units, ("validation_unit_id",))
    unique(units, ("issuer_name",))
    require(len(units) == 67, "Current candidate must contain exactly 67 units")
    unique(data["origins"], ("validation_unit_id", "origin_position"))
    unique(data["origins"], ("source_row_id", "pool_id"))
    documents = {key[0]: value for key, value in unique(data["documents"], ("document_id",)).items()}
    unique(data["sources"], ("source_id",))
    unique(data["manifest"], ("validation_unit_id", "document_id"))
    unique(data["archive"]["verified_cache_files"], ("document_id", "filename"))
    designs = unique(data["design"], ("frozen_stratum_id",))
    old = {key[0]: value for key, value in unique(data["historical"], ("packet_case_id",)).items()}
    archive = Path(data["archive"]["directory"])
    require(archive.is_absolute(), "Archive directory must be an explicit locator")
    reference = authorized_reference_rows(data)
    reference_hash = next(r["sha256"] for r in input_hashes if r["path"] == INPUTS["reference"])
    require(reference_hash == data["report"]["source_snapshot_sha256"], "Report snapshot hash mismatch")
    grouped_origins, grouped_manifest, grouped_sources = defaultdict(list), defaultdict(list), defaultdict(list)
    for row in data["origins"]:
        if (row["validation_unit_id"],) in unit_index:
            grouped_origins[row["validation_unit_id"]].append(row)
    require(sum(map(len, grouped_origins.values())) == 74, "Expected 74 eligible origin rows")
    for row in data["manifest"]:
        grouped_manifest[row["validation_unit_id"]].append(row)
    for row in data["sources"]:
        grouped_sources[row["case_id"]].append(row)
    records = {name: {id(row): f"{INPUTS[name]}#record={i}" for i, row in enumerate(data[name], 1)}
               for name in ("candidate", "origins", "manifest", "documents", "sources")}
    packets, sources, source_audit, sidecar, pairs, mappings, comparisons, readiness = ([] for _ in range(8))
    file_cache = {}
    for unit in units:
        uid = unit["validation_unit_id"]
        require(unit["scope_disposition"] == "eligible" and unit["eligibility_flag"] == "true",
                f"Ineligible candidate: {uid}")
        design = designs[(unit["frozen_stratum_id"],)]
        require(design["approval_status"] == "proposal_only_PI_approval_required" and
                unit["random_draw_executed"] == design["random_draw_executed"] == "false",
                "Design is not an undrawn proposal")
        for field in set(design) & set(unit):
            require(unit[field] == design[field], f"Candidate/design mismatch: {uid} {field}")
        origins = sorted(grouped_origins[uid], key=lambda r: int(r["origin_position"]))
        require(bool(origins), f"Missing origin rows: {uid}")
        for origin in origins:
            for field in ("issuer_name", "eligibility_flag", "scope_disposition", "screen_status"):
                require(origin[field] == unit[field], f"Origin/candidate mismatch: {uid} {field}")
        origin_docs = {doc for o in origins for doc in split_ids(o["evidence_document_ids"])}
        manifest = {m["document_id"]: m for m in grouped_manifest[uid]}
        require(all(m["issuer_name"] == unit["issuer_name"] for m in manifest.values()), "Manifest issuer mismatch")
        unit_sources = []
        for doc_id in sorted(origin_docs | manifest.keys()):
            doc, meta = documents.get(doc_id, {}), manifest.get(doc_id, {})
            require(doc_id not in origin_docs or bool(doc), f"Unknown origin document: {doc_id}")
            if doc:
                require(doc["company_name"] == unit["issuer_name"], "Document issuer mismatch")
            for origin in origins:
                if doc_id in split_ids(origin["evidence_document_ids"]):
                    require(doc["case_id"] == origin["source_row_id"], "Document/origin case mismatch")
            inventory_path = doc.get("local_file_path", "")
            if inventory_path:
                require(not Path(inventory_path).is_absolute() and ".." not in Path(inventory_path).parts,
                        "Unsafe inventory path")
                inventory_path = str(BASE_REPOSITORY / inventory_path)
            source = {
                "packet_case_id": uid, "source_record_id": f"{uid}:document:{doc_id}",
                "document_id": doc_id, "source_id": doc.get("source_id", ""),
                **{field: meta.get(field) or doc.get(field, "") for field in (
                    "document_title", "document_type", "document_date", "document_page_url", "download_url")},
                "inventory_archive_path": inventory_path,
                "manifest_archive_path": archive_path(archive, meta.get("raw_cache_filename", "")),
                "manifest_text_archive_path": archive_path(archive, meta.get("text_cache_filename", "")),
                "expected_raw_sha256": meta.get("sha256", ""),
                "expected_text_sha256": meta.get("source_text_sha256", ""),
            }
            unit_sources.append(source)
            raw_audit = audit_file(source["manifest_archive_path"], source["expected_raw_sha256"], file_cache)
            text_audit = audit_file(source["manifest_text_archive_path"], source["expected_text_sha256"], file_cache)
            inventory_audit = audit_file(inventory_path, source["expected_raw_sha256"], file_cache)
            source_audit.append({
                "packet_case_id": uid, "source_record_id": source["source_record_id"],
                "origin_source_row_ids": ";".join(o["source_row_id"] for o in origins
                                                   if doc_id in split_ids(o["evidence_document_ids"])),
                "document_inventory_record": records["documents"].get(id(doc), ""),
                "source_manifest_record": records["manifest"].get(id(meta), ""),
                "source_inventory_record": "",
                "link_basis": "origin_document_id" if doc_id in origin_docs else "manifest_exact_unit_and_issuer",
                "historical_access_status": meta.get("access_status", ""),
                "historical_error": meta.get("error", ""),
                "rights_note": meta.get("rights_note", "Public source locator only; no raw redistribution."),
                "raw_archive_state": raw_audit["state"], "raw_observed_sha256": raw_audit["sha256"],
                "text_archive_state": text_audit["state"], "text_observed_sha256": text_audit["sha256"],
                "inventory_file_state": inventory_audit["state"],
                "inventory_observed_sha256": inventory_audit["sha256"],
            })
        source_origins = defaultdict(list)
        for origin in origins:
            for src in grouped_sources[origin["source_row_id"]]:
                require(src["company_name"] == unit["issuer_name"], "Source inventory issuer mismatch")
                source_origins[src["source_id"]].append(origin["source_row_id"])
        for source_id, origin_ids in sorted(source_origins.items()):
            src = next(s for s in grouped_sources[origin_ids[0]] if s["source_id"] == source_id)
            source = {field: "" for field in SOURCE_FIELDS}
            source.update(packet_case_id=uid, source_record_id=f"{uid}:source:{source_id}", source_id=source_id,
                          document_title=src["source_title"], document_type=src["source_type"],
                          document_date=src["source_date"], document_page_url=src["source_url"])
            unit_sources.append(source)
            source_audit.append({
                "packet_case_id": uid, "source_record_id": source["source_record_id"],
                "origin_source_row_ids": ";".join(origin_ids), "document_inventory_record": "",
                "source_manifest_record": "", "source_inventory_record": records["sources"][id(src)],
                "link_basis": "exact_origin_case_and_issuer", "historical_access_status": "not_recorded",
                "historical_error": "", "rights_note": "Public locator; inventory path is not raw evidence.",
                "raw_archive_state": "inventory_reference_not_raw_source", "raw_observed_sha256": None,
                "text_archive_state": "inventory_reference_not_raw_source", "text_observed_sha256": None,
                "inventory_file_state": "inventory_reference_not_raw_source", "inventory_observed_sha256": None,
            })
        unit_sources.sort(key=lambda r: r["source_record_id"])
        sources.extend(unit_sources)
        packets.append({"packet_case_id": uid, "issuer_name": unit["issuer_name"],
                        "province": unit["province"], "city": unit["city"],
                        "source_record_ids": ";".join(s["source_record_id"] for s in unit_sources)})
        unit_pairs = [match_reference(unit, origins, ref) for ref in sorted(data["reference"], key=lambda r: r["case_id"])]
        pairs.extend(unit_pairs)
        mappings.append(historical_mapping(uid, unit_pairs, reference))
        sidecar.append({"packet_case_id": uid, "candidate_record": records["candidate"][id(unit)],
                        "design_interpretation": "proposal_only_not_frozen_or_realized",
                        **unit, "origin_record_locators": ";".join(records["origins"][id(o)] for o in origins),
                        "source_row_ids": ";".join(o["source_row_id"] for o in origins),
                        "pool_ids": ";".join(o["pool_id"] for o in origins),
                        "realized_inclusion_probability": "", "freeze_authorization_id": ""})
        historical = old.get(uid, {})
        old_docs = set(split_ids(historical.get("packet_document_ids", "")))
        new_docs = {s["document_id"] for s in unit_sources if s["document_id"]}
        comparisons.append({
            "packet_case_id": uid, "historical_packet_membership": "present" if historical else "absent",
            "current_packet_membership": "present", "historical_document_count": len(old_docs),
            "current_document_count": len(new_docs), "retained_document_ids": ";".join(sorted(old_docs & new_docs)),
            "added_document_ids": ";".join(sorted(new_docs - old_docs)),
            "historical_only_document_ids": ";".join(sorted(old_docs - new_docs)),
        })
        audits = [a for a in source_audit if a["packet_case_id"] == uid]
        missing_origin_docs = [o["source_row_id"] for o in origins if not o["evidence_document_ids"]]
        public_locators = all(s["document_page_url"] or s["download_url"] for s in unit_sources)
        verified = sum(a["raw_archive_state"] == "verified" for a in audits)
        readiness.append({
            "packet_case_id": uid, "packet_source_records": len(unit_sources),
            "public_locator_readiness": "ready" if public_locators and unit_sources else "missing",
            "origin_document_state": "missing_for_some_origins" if missing_origin_docs else "complete",
            "origins_without_document_ids": missing_origin_docs,
            "manifest_verified_raw_documents": verified,
            "raw_archive_missing_records": [a["source_record_id"] for a in audits if a["raw_archive_state"] == "missing_file"],
            "source_hash_mismatches": [a["source_record_id"] for a in audits if "hash_mismatch" in
                                      (a["raw_archive_state"], a["text_archive_state"], a["inventory_file_state"])],
            "source_sufficiency_for_final_label": None,
            "platform_scope_eligibility": "eligible",
            "codebook_exit_eligibility": None, "codebook_exit_readiness": "unresolved_pending_human_evidence",
            "formal_event_human_decision": None, "coder_1_label": None, "coder_2_label": None,
            "post_event_evidence_human_decision": None,
            "adjudicated_label": None, "realized_validation_outcome": None,
            "reviewer_identity": None, "actual_review_date": None, "signature": None,
            "independent_coding_readiness": "missing_human_decisions",
            "design_readiness": "missing_freeze_and_collection_authorization",
            "proposed_inclusion_probability": unit["inclusion_probability"],
            "realized_inclusion_probability": None,
            "reference_mapping_readiness": mappings[-1]["mapping_status"],
            "reference_unmatched_reason": mappings[-1]["reason"],
            "realized_input_readiness": "blocked",
            "blocking_reasons": ["no_authorized_realized_design", "no_new_human_labels",
                                 "no_independent_decisions_or_process_metadata", "source_sufficiency_not_human_assessed"],
        })
    unique(sources, ("source_record_id",))
    require(all(r["public_locator_readiness"] == "ready" for r in readiness), "Incomplete locator coverage")
    require(not any(r["source_hash_mismatches"] for r in readiness), "Source hash mismatch")
    for (stratum,), design in designs.items():
        n = sum(u["frozen_stratum_id"] == stratum for u in units)
        require(n == int(design["stratum_population_n"]), "Stratum count mismatch")
    outputs = {
        "blinded_packets.csv": csv_bytes(packets, PACKET_FIELDS),
        "blinded_sources.csv": csv_bytes(sources, SOURCE_FIELDS),
        "coordinator_design_sidecar.csv": csv_bytes(sidecar),
        "coordinator_source_audit.csv": csv_bytes(source_audit),
        "coordinator_reference_report_scope.csv": csv_bytes(reference),
        "coordinator_reference_pair_audit.csv": csv_bytes(pairs, PAIR_FIELDS),
        "coordinator_reference_mappings.csv": csv_bytes(mappings, MAPPING_FIELDS),
        "historical_packet_comparison.csv": csv_bytes(comparisons),
        "input_hashes.json": json_bytes(input_hashes),
        "local_file_audit.json": json_bytes({path: value for path, value in sorted(file_cache.items())}),
        "realized_input_readiness.json": json_bytes({"units": readiness, "schema_version": 1}),
    }
    for role in ("coder_1", "coder_2"):
        rows = [{**p, **dict.fromkeys(ENTRY_FIELDS, "")} for p in packets]
        outputs[f"blinded_{role}_entry.csv"] = csv_bytes(rows, PACKET_FIELDS + ENTRY_FIELDS)
    outputs["adjudication_entry.csv"] = csv_bytes([
        {field: p["packet_case_id"] if field == "packet_case_id" else "" for field in ADJUDICATION_FIELDS}
        for p in packets], ADJUDICATION_FIELDS)
    for name, fields, blanks in (
        ("blinded_packets.csv", PACKET_FIELDS, []), ("blinded_sources.csv", SOURCE_FIELDS, []),
        ("blinded_coder_1_entry.csv", PACKET_FIELDS + ENTRY_FIELDS, ENTRY_FIELDS),
        ("blinded_coder_2_entry.csv", PACKET_FIELDS + ENTRY_FIELDS, ENTRY_FIELDS),
        ("adjudication_entry.csv", ADJUDICATION_FIELDS, ADJUDICATION_FIELDS[1:]),
    ):
        validate_blinded(outputs[name], fields, blanks)
    old_only = sorted(set(old) - {p["packet_case_id"] for p in packets})
    metrics = {
        "experiment_id": EXPERIMENT, "base_commit": BASE,
        "current_units": len(units), "eligible_origin_rows": sum(map(len, grouped_origins.values())),
        "source_locator_records": len(sources), "document_locator_records": sum(bool(s["document_id"]) for s in sources),
        "units_with_public_locators": sum(r["public_locator_readiness"] == "ready" for r in readiness),
        "units_with_verified_manifest_raw": sum(r["manifest_verified_raw_documents"] > 0 for r in readiness),
        "verified_manifest_raw_documents": sum(r["manifest_verified_raw_documents"] for r in readiness),
        "units_with_missing_origin_document_ids": sum(bool(r["origins_without_document_ids"]) for r in readiness),
        "historical_packet_units": len(old), "retained_historical_units": len(old) - len(old_only),
        "added_current_units": sum(p["packet_case_id"] not in old for p in packets), "historical_only_units": old_only,
        "report_covered_reference_cases": len(reference), "reference_pairs_audited": len(pairs),
        "exact_issuer_pairs": sum(p["issuer_exact_match"] == "true" for p in pairs),
        "exact_issuer_event_mappings": sum(m["mapping_status"] == "exact_historical_reference" for m in mappings),
        "unmatched_reasons": dict(Counter(m["reason"] for m in mappings)),
        "historical_capacity_linked_units_not_label_matches": sum(bool(u["historical_capacity_source_case_ids"]) for u in units),
        "proposed_strata": len(designs), "screen_counts_coordinator_only": dict(Counter(u["screen_status"] for u in units)),
        "blank_coder_rows_per_sheet": len(packets), "populated_human_entry_cells": 0,
        "human_labels": None, "realized_outcome_counts": None, "coder_agreement": None,
        "realized_inclusion_probabilities": None, "realized_input_readiness": "blocked",
        "freeze_executed_by_this_package": False, "draw_executed_by_this_package": False,
        "human_coding_executed_by_this_package": False,
        "source_hash_mismatch_records": sum(len(r["source_hash_mismatches"]) for r in readiness),
        "missing_historical_raw_records": sum(len(r["raw_archive_missing_records"]) for r in readiness),
    }
    outputs["metrics.json"] = json_bytes(metrics)
    outputs["schema.json"] = json_bytes({
        "schema_version": 1, "missing_csv_value": "", "missing_json_value": None,
        "allowed_final_labels": list(LABELS),
        "exit_case_eligibility_values": ["eligible", "unresolved", "ineligible", ""],
        "evidence_decision_values": ["yes", "no", "unresolved", ""],
        "institutional_change_mapping": {label: map_outcome(label) for label in (*LABELS, "")},
        "blinded_packet_columns": PACKET_FIELDS, "blinded_source_columns": SOURCE_FIELDS,
        "blank_entry_columns": ENTRY_FIELDS, "adjudication_columns": ADJUDICATION_FIELDS,
        "source_record_id_rule": "validation_unit_id + :document:/:source: + exact inventory/manifest ID",
        "input_record_locator_rule": "#record=N is the 1-based CSV data record, excluding header",
        "issuer_identity_rule": "literal full issuer-name equality; no normalization or aliases",
        "event_identity_rule": "exact origin source_row_id == reference case_id AND primary event document in that origin; reference event/year nonempty",
        "authority_rule": "HC-20260910-001 applies to 94 original reference cases only; no new independent label is authorized",
        "entry_import_rule": "Submitted fields remain unverified; this builder cannot authorize labels or realized design",
    })
    outputs["README.md"] = (
        "# Validation collection handoff\n\n"
        "This dated package covers 67 candidate issuer units, not a frozen sample or completed validation.\n\n"
        "## Distribution\n\n"
        "After separate collection authorization, give each coder only blinded_packets.csv, blinded_sources.csv, "
        "their own blinded_coder_1_entry.csv or blinded_coder_2_entry.csv, and the unchanged coding/codebook.md. "
        "Do not give coders coordinator files, historical comparisons, readiness, metrics, other decisions, "
        "or the full repository. IDs and original public-source content are necessary locators, not predictions. "
        "Blinding here means absence of inherited predictions/decisions in the instruments; actual coder blinding is not documented.\n\n"
        "## Human entries\n\n"
        "All decision, score, event, reviewer, date, and signature fields are blank. Empty means missing, "
        "not zero, false, nominal exit, or ineligible. The 67 units meet platform scope, not yet codebook "
        "exit-case eligibility. Ten have no direct formal-event screen; that is a screen, not a human "
        "decision. Record exit_case_eligibility separately as eligible, unresolved, or ineligible, and "
        "formal_event_found and post_event_evidence_found separately. Missing formal/post-event evidence "
        "leaves the exit case unresolved or ineligible and final_label blank. Only the four codebook "
        "exit labels are allowed; unresolved is not a fifth label or negative outcome. Keep each coder's decisions independent and retain "
        "the original forms before any separately authorized adjudication. The builder never imports or "
        "promotes submitted forms and refuses to overwrite changed outputs.\n\n"
        "## Source reconstruction\n\n"
        "Sources are the union of exact origin document IDs, exact unit-and-issuer source-manifest rows, "
        "and exact origin-case source inventory rows. No source searches or downloads were performed. "
        "Read original public documents using the recorded URLs or rights-approved local archive paths. "
        "Use expected hashes to verify cached raw/text files. Inventory flags and past retrieval claims are "
        "not current availability; coordinator_source_audit.csv and local_file_audit.json record actual local "
        "checks. Absolute paths refer to this machine and must be relocated explicitly on another machine. "
        "No raw documents are redistributed. Document coverage is not a human determination of event or "
        "post-event evidentiary sufficiency. The empty Guiyang origin-document list and missing historical "
        "Shenzhen raw page remain recorded; linked current sources do not erase those gaps.\n\n"
        "## Historical labels and design\n\n"
        "The reference report covers only its original 94 cases. The pair audit examines all 67 x 94 "
        "issuer/event pairs, requires exact issuer and event links, and never uses city or capacity links "
        "as label matches. Original production and author-reported checking remain distinct from new "
        "independent decisions. Proposed pi=1 and legacy frozen_stratum_id field names in the sidecar "
        "do not establish a freeze or realized inclusion probability. Human decisions and actual inclusion "
        "probabilities remain null; downstream validation estimates are blocked.\n\n"
        "## Reproduction\n\n"
        "From this worktree run python3 scripts/build_validation_collection_package.py --check and "
        "python3 -m unittest discover -s tests -p test_validation_collection_package.py -v. "
        "The builder checks scientific inputs against their stated base Git objects, including schema/order. "
        "Coordinator research_state.yaml is read from the base Git object as historical audit context only; "
        "later ledger or README updates do not invalidate this package. No live approval is inferred from "
        "the baseline: actual authorization and analytic requests require a separate coordinator overlay. "
        "it hashes local files only at recorded locations. A clean initial run without --check creates "
        "the dated files; reruns are idempotent. Changed forms or audits require a new authorized version, "
        "not overwriting this handoff. Hashes cover all generated outputs except the hash index itself.\n"
    ).encode()
    outputs["output_hashes.json"] = json_bytes({name: sha256(raw) for name, raw in sorted(outputs.items())})
    return outputs


def write_outputs(outputs: dict[str, bytes], destination: Path, check: bool = False) -> None:
    mismatches = [name for name, raw in outputs.items()
                  if not (destination / name).exists() or (destination / name).read_bytes() != raw]
    if check:
        require(not mismatches, f"Stale/changed collection outputs: {mismatches}")
        return
    changed = [name for name in mismatches if (destination / name).exists()]
    require(not changed, f"Refusing to overwrite existing outputs/human entries: {changed}")
    destination.mkdir(parents=True, exist_ok=True)
    for name in mismatches:
        (destination / name).write_bytes(outputs[name])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify, without writing any files")
    args = parser.parse_args()
    data, hashes = load_inputs()
    outputs = build_outputs(data, hashes)
    write_outputs(outputs, ROOT / OUTPUT, check=args.check)
    print("collection_package=byte_identical" if args.check else "collection_package=created_or_identical")
    print(outputs["metrics.json"].decode(), end="")


if __name__ == "__main__":
    main()
