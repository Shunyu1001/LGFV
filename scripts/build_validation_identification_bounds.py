#!/usr/bin/env python3
"""Finite-screen identification bounds conditional on retained reference labels.

No sampling model or missingness model is used. Scope exclusions and no-event
screen flags are not reference outcomes. Inputs are pinned to the experiment's
base commit, and every consistency check completes before outputs are written.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

from collapse_codex_surrogate_labels import compact_name
from human_confirmation import confirmed_rows

ROOT = Path(__file__).resolve().parents[1]
BASE = "4330c5728dec64ba30c1faec972fad0097622e9d"
EXPERIMENT = "EXP-20260910-006"
ARTIFACTS = Path("experiments") / EXPERIMENT
INPUTS = {
    "reference": "data/processed/working_reference_labels.csv",
    "report": "data/validation/human_confirmation_report_2026_09_10.json",
    "register": "data/validation/human_confirmation_register.csv",
    "issuers": "data/analysis_inputs/codex_surrogate_issuer_summary_2026_07_03_expanded.csv",
    "disclosures": "data/analysis_inputs/codex_surrogate_labels_2026_07_03_expanded.csv",
    "documents": "data/document_inventory.csv",
    "sources": "data/source_inventory.csv",
    "scope_sources": "data/validation/probability_validation_source_manifest.csv",
    "candidate": "data/validation/probability_validation_frame_candidate.csv",
    "origins": "data/validation/probability_validation_frame_origin_rows.csv",
    "design": "data/validation/probability_validation_sampling_design.csv",
    "crosswalk": "data/validation/probability_validation_geography_scope_crosswalk.csv",
    "flow": "data/validation/probability_validation_frame_flow.csv",
    "packet": "data/validation/independent_coding/blinded_probability_validation_packet.csv",
}
CLASSES = ("nominal_exit", "substantive_exit", "functional_transfer", "liquidation")
POSITIVE = "screen_positive_nominal"
NO_EVENT = "screened_no_direct_formal_event"
COMMON_ASSUMPTION = (
    "Conditional on each linked reference outcome being correct and valid for the "
    "corresponding screen issuer/event. Exact issuer identity and shared source "
    "anchors do not establish event/time comparability or independent same-event "
    "pairing; neither is proved here. Author-reported checking does not prove "
    "error-free labels. Unobserved outcomes are unrestricted."
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def parse_csv(raw: bytes) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    require(bool(reader.fieldnames), "CSV has no header")
    require(len(reader.fieldnames) == len(set(reader.fieldnames)), "Duplicate CSV headers")
    rows = list(reader)
    require(all(None not in r and None not in r.values() for r in rows), "Malformed CSV row")
    return rows


def tokens(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def unique_index(rows: list[dict], field: str, context: str, compact: bool = False) -> dict:
    indexed = {}
    for row in rows:
        value = row.get(field, "")
        require(isinstance(value, str) and bool(value.strip()), f"Empty {context} {field}")
        key = compact_name(value) if compact else value
        require(bool(key), f"Empty normalized {context} {field}")
        require(key not in indexed, f"Duplicate {context} {field}: {key}")
        indexed[key] = row
    return indexed


def reference_index(rows: list[dict]) -> dict:
    unique_index(rows, "case_id", "reference")
    groups = defaultdict(list)
    for row in rows:
        require(row.get("final_label") in (*CLASSES, "unclear"), "Invalid reference label")
        require(bool(compact_name(row.get("company_name", ""))), "Empty reference issuer")
        groups[compact_name(row["company_name"])].append(row)
    for key, group in groups.items():
        ids = ";".join(row["case_id"] for row in group)
        require(len({r["final_label"] for r in group}) == 1,
                f"Conflicting reference labels: {key}: {ids}")
        require(len(group) == 1, f"Ambiguous multiple reference cases: {key}: {ids}")
    return {key: group[0] for key, group in groups.items()}


def verify_payload(relative: str, raw: bytes, expected: str) -> None:
    require(digest(raw) == expected, f"Provenance hash mismatch: {relative}")


def load_inputs(root: Path) -> tuple[dict, dict]:
    data, hashes = {}, {}
    for name, relative in INPUTS.items():
        registered = subprocess.run(
            ["git", "show", f"{BASE}:{relative}"], cwd=root, check=True, capture_output=True
        ).stdout
        raw = (root / relative).read_bytes()
        verify_payload(relative, raw, digest(registered))
        hashes[relative] = digest(raw)
        data[name] = json.loads(raw) if name == "report" else parse_csv(raw)
    report = data["report"]
    require(report["source_snapshot"] == INPUTS["reference"], "Wrong confirmation source path")
    expected = confirmed_rows(root / INPUTS["reference"], root / INPUTS["report"])
    actual_by_id = unique_index(data["register"], "case_id", "confirmation register")
    expected_by_id = unique_index(expected, "case_id", "derived confirmation")
    require(actual_by_id == expected_by_id, "Confirmation register differs from exact report scope")
    require(report["probability_validation_completed"] is False,
            "This experiment does not support completed probability validation")
    return data, hashes


def audit_overlap(reference: list[dict], issuers: list[dict], disclosures: list[dict]) -> tuple:
    ref_by_name = reference_index(reference)
    ref_by_id = unique_index(reference, "case_id", "reference")
    issuer_by_name = unique_index(issuers, "issuer_name", "issuer", compact=True)
    unique_index(disclosures, "pool_id", "disclosure")
    selected = [r for r in disclosures
                if r["label_source"] == "codex_surrogate" and r["surrogate_status"] == "labeled"]
    unique_index(selected, "source_row_id", "selected disclosure")
    groups = defaultdict(list)
    for row in selected:
        require(bool(compact_name(row["issuer_name"])), "Empty selected disclosure issuer")
        require(row["exit_type"] in CLASSES, "Invalid selected disclosure label")
        groups[compact_name(row["issuer_name"])].append(row)
    require(set(groups) == set(issuer_by_name), "Issuer/disclosure group coverage mismatch")

    # Historical reference rows can repeat a source ID under a different pool and
    # analytical role. They are checked, retained, and never counted as surrogates.
    historical = [r for r in disclosures if r["label_source"] == "human_gold_standard"]
    historical_by_id = unique_index(historical, "source_row_id", "historical reference disclosure")
    require(set(historical_by_id) == set(ref_by_id), "Historical reference case coverage mismatch")
    for case_id, row in historical_by_id.items():
        ref = ref_by_id[case_id]
        require(row["exit_type"] == ref["final_label"], f"Original label changed: {case_id}")
        if row["issuer_name"]:
            require(row["issuer_name"] == ref["company_name"], f"Historical issuer mismatch: {case_id}")

    audit = []
    for key, issuer in sorted(issuer_by_name.items()):
        group = groups[key]
        require(all(r["issuer_name"] == issuer["issuer_name"] for r in group),
                f"Issuer normalization collision: {key}")
        counts = Counter(r["exit_type"] for r in group)
        label = next(iter(counts)) if len(counts) == 1 else "mixed"
        require(issuer["exit_type"] == label, f"Collapsed label mismatch: {key}")
        require(issuer["exit_type_counts"] == "; ".join(f"{k}:{v}" for k, v in sorted(counts.items())),
                f"Collapsed label count mismatch: {key}")
        require(int(issuer["surrogate_rows"]) == len(group), f"Disclosure count mismatch: {key}")
        source_ids, pool_ids = tokens(issuer["source_row_ids"]), tokens(issuer["pool_ids"])
        require(len(source_ids) == len(pool_ids) == len(group), f"Origin link lengths differ: {key}")
        require(Counter(zip(source_ids, pool_ids)) == Counter((r["source_row_id"], r["pool_id"]) for r in group),
                f"Inconsistent source/pool links: {key}")
        ref = ref_by_name.get(key)
        require(issuer["gold_standard_overlap"] == ("true" if ref else "false"),
                f"Inconsistent overlap flag: {key}")
        require(issuer["gold_case_id"] == (ref["case_id"] if ref else ""), f"Inconsistent case link: {key}")
        require(issuer["gold_final_label"] == (ref["final_label"] if ref else ""),
                f"Conflicting linked reference label: {key}")
        if ref:
            require(issuer["issuer_name"] == ref["company_name"], f"Non-exact reference issuer link: {key}")
        screen_docs = {d for r in group for d in tokens(r["evidence_basis"])}
        ref_docs = set(tokens(ref.get("primary_evidence_doc", "")) +
                       tokens(ref.get("secondary_evidence_doc", ""))) if ref else set()
        audit.append({
            "issuer_key": key, "issuer_name": issuer["issuer_name"],
            "screen_label": label, "disclosure_count": len(group),
            "source_row_ids": ";".join(sorted(source_ids)), "pool_ids": ";".join(sorted(pool_ids)),
            "reference_case_id": ref["case_id"] if ref else "",
            "reference_label": ref["final_label"] if ref else "",
            "outcome_status": "known" if ref and ref["final_label"] in CLASSES else "unknown",
            "source_supported_documents": ";".join(sorted(screen_docs)),
            "reference_official_exit_year": ref.get("official_exit_year", "") if ref else "",
            "reference_official_exit_event": ref.get("official_exit_event", "") if ref else "",
            "reference_case_in_screen_source_rows": "true" if ref and ref["case_id"] in source_ids else "false",
            "shared_reference_screen_document_ids": ";".join(sorted(ref_docs & screen_docs)),
            "event_time_alignment": "not_established" if ref else "no_reference_link",
            "independent_same_event_pairing": "not_established",
        })
    return audit, selected, ref_by_name


def audit_sources(data: dict, selected: list[dict]) -> list[dict]:
    documents = unique_index(data["documents"], "document_id", "document inventory")
    sources = unique_index(data["sources"], "source_id", "source inventory")
    used = set()
    for row in data["reference"]:
        primary = tokens(row["primary_evidence_doc"])
        require(bool(primary) and bool(row["primary_evidence_lines"]),
                f"Missing primary reference evidence: {row['case_id']}")
        used.update(primary + tokens(row["secondary_evidence_doc"]))
        for source_id in tokens(row["supplementary_source_id"]):
            require(source_id in sources, f"Unresolved reference source: {source_id}")
    for row in selected:
        ids = tokens(row["evidence_basis"])
        require(bool(ids), f"Missing selected disclosure evidence: {row['pool_id']}")
        require(all(d in documents for d in ids), f"Unresolved disclosure documents: {row['pool_id']}")
        require(all(documents[d]["case_id"] == row["source_row_id"] for d in ids),
                f"Inconsistent disclosure/document case links: {row['pool_id']}")
        used.update(ids)
    for row in data["origins"]:
        ids = tokens(row["evidence_document_ids"])
        # Two inherited alternative-case origin rows have no old inventory IDs.
        # Retain them explicitly; their scope sources are checked separately below.
        require(all(d in documents for d in ids), "Unresolved origin document links")
        require(all(documents[d]["case_id"] == row["source_row_id"] for d in ids),
                f"Inconsistent origin/document case links: {row['source_row_id']}")
        used.update(ids)
    links = []
    for doc_id in sorted(used):
        require(doc_id in documents, f"Unresolved reference document: {doc_id}")
        doc = documents[doc_id]
        require(doc["source_id"] in sources, f"Unresolved document source: {doc_id}")
        require(bool(doc["download_url"] or doc["document_page_url"]), f"No retrieval URL: {doc_id}")
        links.append({field: doc[field] for field in (
            "document_id", "case_id", "source_id", "document_page_url", "download_url", "local_file_path"
        )})
    return links


def audit_candidate(data: dict, audit: list[dict], ref_by_name: dict) -> tuple:
    candidates = unique_index(data["candidate"], "validation_unit_id", "candidate")
    unique_index(data["candidate"], "issuer_name", "candidate", compact=True)
    crosswalk = unique_index(data["crosswalk"], "validation_unit_id", "current scope")
    design = unique_index(data["design"], "frozen_stratum_id", "design")
    disclosure_by_pool = unique_index(data["disclosures"], "pool_id", "disclosure")
    screen_by_name = {r["issuer_key"]: r for r in audit}
    origins = defaultdict(list)
    seen_links = set()
    scope_sources = {}
    for row in data["scope_sources"]:
        key = (row["validation_unit_id"], row["document_id"])
        require(key not in scope_sources, f"Duplicate scope source link: {key}")
        scope_sources[key] = row
    for uid, row in crosswalk.items():
        for role in ("identity", "geography", "owner", "role"):
            doc_id = row[f"{role}_document_id"]
            if not doc_id:
                require(row["scope_disposition"] == "ineligible", f"Missing eligible scope source: {uid}/{role}")
                continue
            key = (uid, doc_id)
            require(key in scope_sources, f"Unresolved current scope source: {key}")
            source = scope_sources[key]
            require(bool(source["sha256"]) and bool(source["source_text_sha256"]) and
                    bool(source["download_url"] or source["document_page_url"]), f"Incomplete current scope provenance: {key}")
    for row in data["origins"]:
        uid = row["validation_unit_id"]
        require(uid in crosswalk, f"Origin unit outside crosswalk: {uid}")
        link = (row["source_row_id"], row["pool_id"])
        require(link not in seen_links, f"Duplicate origin link: {link}")
        seen_links.add(link)
        require(row["pool_id"] in disclosure_by_pool, f"Unknown origin pool: {link}")
        disclosure = disclosure_by_pool[row["pool_id"]]
        require(disclosure["source_row_id"] == row["source_row_id"], f"Inconsistent candidate link: {link}")
        require(disclosure["issuer_name"] == row["issuer_name"], f"Inconsistent candidate issuer: {uid}")
        require(row["screen_status"] in (POSITIVE, NO_EVENT), f"Unknown screen status: {uid}")
        require(row["scope_disposition"] in ("eligible", "ineligible"), f"Unresolved scope: {uid}")
        expected_flag = "true" if row["scope_disposition"] == "eligible" else "false"
        require(row["eligibility_flag"] == expected_flag, f"Contradictory origin eligibility: {uid}")
        require(row["scope_disposition"] == crosswalk[uid]["scope_disposition"], f"Scope disagreement: {uid}")
        origins[uid].append(row)
    require(set(origins) == set(crosswalk), "Origin/crosswalk unit coverage mismatch")
    require(set(candidates) == {uid for uid, r in crosswalk.items() if r["scope_disposition"] == "eligible"},
            "Candidate/eligible scope coverage mismatch")
    strata = Counter(r["frozen_stratum_id"] for r in candidates.values())
    require(set(strata) == set(design), "Candidate/design stratum coverage mismatch")
    for stratum, n in strata.items():
        row = design[stratum]
        require(int(row["stratum_population_n"]) == n, f"Design denominator mismatch: {stratum}")
        require(int(row["proposed_stratum_sample_n"]) == n and row["inclusion_probability"] == "1",
                f"Not the registered proposed census: {stratum}")
        require(row["random_draw_executed"] == "false" and row["approval_status"] == "proposal_only_PI_approval_required",
                "Proposal/draw status changed")
    unit_rows = []
    for uid, group in sorted(origins.items()):
        first = group[0]
        for field in ("issuer_name", "scope_disposition", "eligibility_flag", "screen_status"):
            require(len({r[field] for r in group}) == 1, f"Inconsistent origin unit {field}: {uid}")
        require(sorted(int(r["origin_position"]) for r in group) == list(range(1, len(group) + 1)),
                f"Missing/duplicate origin positions: {uid}")
        key = compact_name(first["issuer_name"])
        if uid in candidates:
            row = candidates[uid]
            for field in ("issuer_name", "scope_disposition", "eligibility_flag", "screen_status"):
                require(row[field] == first[field], f"Candidate/origin mismatch {field}: {uid}")
            require(row["geography_status"] == "source_supported_unique" and row["province"] and row["city"],
                    f"Candidate geography incomplete: {uid}")
            stratum = row["frozen_stratum_id"]
            for field in ("screen_status", "source_coverage_bin", "historical_capacity_bin",
                          "debt_pressure_availability", "administrative_level", "stratum_population_n",
                          "proposed_stratum_sample_n", "inclusion_probability", "random_draw_executed"):
                require(row[field] == design[stratum][field], f"Candidate/design mismatch {field}: {uid}")
        if first["screen_status"] == POSITIVE:
            require(key in screen_by_name, f"Positive candidate origin outside finite screen: {uid}")
            require(screen_by_name[key]["screen_label"] == "nominal_exit", f"Positive status/label mismatch: {uid}")
            require(not screen_by_name[key]["reference_case_id"], f"Candidate contains reference-overlap issuer: {uid}")
        else:
            require(key not in screen_by_name, f"No-event unit also in nominal screen: {uid}")
        require(key not in ref_by_name, f"Candidate origin overlaps human-confirmed reference: {uid}")
        unit_rows.append({
            "validation_unit_id": uid, "issuer_key": key, "issuer_name": first["issuer_name"],
            "scope_disposition": first["scope_disposition"], "screen_status": first["screen_status"],
            "origin_count": len(group), "source_row_ids": ";".join(sorted(r["source_row_id"] for r in group)),
            "reference_case_id": "", "reference_label": "", "outcome_status": "unknown",
            "origin_document_ids_missing": sum(not tokens(r["evidence_document_ids"]) for r in group),
            "current_scope_document_ids": ";".join(sorted({crosswalk[uid][f"{role}_document_id"]
                for role in ("identity", "geography", "owner", "role") if crosswalk[uid][f"{role}_document_id"]})),
        })
    unique_index(unit_rows, "issuer_key", "origin issuer")
    nonoverlap = {r["issuer_key"] for r in audit if not r["reference_case_id"]}
    require(nonoverlap == {r["issuer_key"] for r in unit_rows if r["screen_status"] == POSITIVE},
            "Nonoverlap screen/current origin membership mismatch")
    flow = {(r["stage"], r["disposition"]): r for r in data["flow"]}
    require(len(flow) == len(data["flow"]), "Duplicate flow rows")
    for stage, disposition, units in [
        ("proposed_frame", "all_legal_issuer_units", unit_rows),
        *[("scope_gate", flag, [r for r in unit_rows if r["scope_disposition"] == flag])
          for flag in ("eligible", "ineligible")],
        *[("eligible_screen_coverage", flag, [r for r in unit_rows
          if r["scope_disposition"] == "eligible" and r["screen_status"] == flag])
          for flag in (POSITIVE, NO_EVENT)],
    ]:
        row = flow[(stage, disposition)]
        require(int(row["issuer_unit_count"]) == len(units) and
                int(row["originating_disclosure_row_count"]) == sum(r["origin_count"] for r in units),
                f"Flow denominator mismatch: {stage}/{disposition}")
    packets = unique_index(data["packet"], "packet_case_id", "coding packet")
    completed_fields = ("coder_id", "coding_date", "case_eligible", "formal_event_found", "final_label", "coder_signature")
    require(all(not row[field] for row in packets.values() for field in completed_fields),
            "Coding packet contains decisions outside this experiment's confirmation scope")
    counts = {
        "candidate_units": len(candidates), "origin_units": len(unit_rows),
        "origin_rows": len(data["origins"]), "candidate_origin_rows": sum(len(origins[uid]) for uid in candidates),
        "candidate_screen_counts": dict(sorted(Counter(r["screen_status"] for r in candidates.values()).items())),
        "scope_counts": dict(sorted(Counter(r["scope_disposition"] for r in unit_rows).items())),
        "nonoverlap_scope_counts": dict(sorted(Counter(r["scope_disposition"] for r in unit_rows if r["screen_status"] == POSITIVE).items())),
        "candidate_reference_overlap": 0, "proposal_strata": len(strata), "proposal_only": True,
        "random_draw_executed": False, "final_freeze_approved": False,
        "existing_blank_packet_rows": len(packets),
        "existing_packet_candidate_overlap": len(set(packets) & set(candidates)),
        "origin_rows_without_legacy_document_ids": sum(not tokens(r["evidence_document_ids"]) for r in data["origins"]),
    }
    return unit_rows, counts


def bound_row(identifier: str, population: str, rows: list[dict], label: str,
              quantity: str = "label_share", restriction: str = "") -> dict:
    require(label in CLASSES, "Unknown bound target")
    labels = [r.get("reference_label", "") for r in rows]
    require(all(value in ("", "unclear", *CLASSES) for value in labels), "Invalid outcome in bound")
    n = len(rows)
    positive = labels.count(label)
    negative = sum(value in CLASSES and value != label for value in labels)
    unknown = n - positive - negative
    return {
        "bound_id": identifier, "experiment_id": EXPERIMENT, "population_id": population,
        "quantity": quantity, "target_label": label,
        "unit": "reference_case" if population == "confirmed_reference_cases" else "documentary_screen_issuer",
        "n": n, "known_positive": positive, "known_negative": negative, "unknown": unknown,
        "lower_numerator": positive, "upper_numerator": positive + unknown, "denominator": n,
        "lower": f"{positive / n:.12f}" if n else "",
        "upper": f"{(positive + unknown) / n:.12f}" if n else "",
        "status": "defined" if n else "undefined_empty_population",
        "interpretation": "selected_overlap_description" if quantity == "selected_concordance" else "deterministic_identification_bounds",
        "assumptions": COMMON_ASSUMPTION + (" " + restriction if restriction else ""),
    }


def make_bounds(audit: list[dict], references: list[dict], units: list[dict]) -> list[dict]:
    positive = [r for r in audit if r["screen_label"] == "nominal_exit"]
    overlap = [r for r in positive if r["reference_case_id"]]
    candidates = [r for r in units if r["scope_disposition"] == "eligible"]
    rows = [
        bound_row("VB-SCREEN-NOM", "expanded_finite_issuer_screen", audit, "nominal_exit",
                  restriction="Finite-screen nominal-label membership, not the share among eligible exits or a national estimand."),
        bound_row("VB-SCREEN-CORRECT", "expanded_screen_nominal_predictions", positive, "nominal_exit", "positive_label_correctness",
                  "Same finite-screen denominator only when every issuer is predicted nominal; not a performance-validation estimate."),
        bound_row("VB-UNKNOWN-NOM", "screen_without_reference_overlap", [r for r in audit if not r["reference_case_id"]], "nominal_exit"),
        bound_row("VB-SELECTED", "posthoc_selected_nominal_overlap", overlap, "nominal_exit", "selected_concordance",
                  "Selected after screening; cannot be extrapolated to unobserved issuers."),
        bound_row("VB-CANDIDATE-NOM", "current_eligible_candidate", candidates, "nominal_exit",
                  restriction="Screening eligibility is not a confirmed exit event; all candidate outcomes remain unknown."),
        bound_row("VB-CANDIDATE-CORRECT", "candidate_nominal_predictions", [r for r in candidates if r["screen_status"] == POSITIVE],
                  "nominal_exit", "positive_label_correctness"),
        bound_row("VB-NOEVENT-NOM", "candidate_no_direct_event_screen", [r for r in candidates if r["screen_status"] == NO_EVENT],
                  "nominal_exit", restriction="No-direct-event screening is not a negative nominal outcome."),
    ]
    for label in CLASSES:
        rows.append(bound_row("VB-REFERENCE-" + label.upper(), "confirmed_reference_cases",
                              [{"reference_label": r["final_label"]} for r in references], label,
                              restriction="Descriptive membership in the assembled reference set only."))
    return rows


def csv_bytes(rows: list[dict]) -> bytes:
    require(bool(rows), "Cannot serialize CSV without a schema")
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def json_bytes(value: dict | list) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("utf-8")


def table_text(bounds: list[dict], metrics: dict) -> str:
    names = {
        "VB-SCREEN-NOM": "Screen: nominal membership",
        "VB-SCREEN-CORRECT": "Screen: positive-label correctness",
        "VB-UNKNOWN-NOM": "Screen: no reference overlap",
        "VB-CANDIDATE-NOM": "Candidate: nominal membership",
        "VB-CANDIDATE-CORRECT": "Candidate: positive-label correctness",
        "VB-NOEVENT-NOM": "Candidate: no direct event",
    }
    lines = [
        "% Generated by scripts/build_validation_identification_bounds.py; EXP-20260910-006",
        r"\begin{table}[htbp]", r"\centering", r"\small",
        r"\caption{Conditional finite-screen identification bounds}", r"\label{tab:validation-identification-bounds}",
        r"\setlength{\tabcolsep}{3pt}", r"\begin{tabular}{@{}lrrrrrr@{}}", r"\toprule",
        r"Population and quantity & $N$ & $K_+$ & $K_-$ & $U$ & Lower & Upper \\", r"\midrule",
    ]
    for row in bounds:
        if row["bound_id"] not in names:
            continue
        lines.append(f"{names[row['bound_id']]} & {row['n']} & {row['known_positive']} & "
                     f"{row['known_negative']} & {row['unknown']} & "
                     f"{100 * float(row['lower']):.2f}\\% & {100 * float(row['upper']):.2f}\\% " + r"\\")
    selected = next(r for r in bounds if r["bound_id"] == "VB-SELECTED")
    lines.extend([
        r"\bottomrule", r"\end{tabular}", r"\par\vspace{4pt}", r"\begin{minipage}{\linewidth}\footnotesize",
        r"Notes: $K_+$ and $K_-$ count retained reference labels establishing membership and nonmembership;",
        r"$U=N-K_+-K_-$ counts unknown outcomes. The bounds are $K_+/N$ and $(K_++U)/N$.",
        f"Selected post-hoc overlap concordance is {selected['known_positive']}/{selected['n']}, reported separately.",
        f"The author report covers {metrics['reference_cases']} unchanged reference labels, not candidate outcomes.",
        "All bounds condition on each linked reference outcome being valid for the corresponding screen issuer/event.",
        "Issuer matching does not prove event/time alignment or independent same-event pairing.",
        "No sampling or missingness model is imposed;",
        "these are neither confidence intervals nor performance-validation estimates. Scope exclusions and",
        "no-direct-event flags are not coded as negative outcomes. The finite issuer screen is not a population",
        "of verified eligible exits, and the candidate remains a proposal pending final freeze and human coding.",
        r"\end{minipage}", r"\end{table}", "",
    ])
    return "\n".join(lines)


def notes_text(bounds: list[dict], metrics: dict) -> str:
    by_id = {r["bound_id"]: r for r in bounds}
    main = by_id["VB-SCREEN-NOM"]
    selected = by_id["VB-SELECTED"]
    candidate = metrics["candidate"]
    return f"""# Identification and scope

Generated by `{EXPERIMENT}` from base commit `{BASE}`. The companion CSV
contains exact numerators and denominators; decimal endpoints are display values.

## Finite issuer screen

The expanded summary contains {main['n']} distinct issuers from
{metrics['selected_disclosure_rows']} selected disclosure rows. All
{metrics['nominal_predictions']} issuer predictions are nominal. Conditional on
each linked reference outcome being valid for the corresponding screen issuer
and event, the overlap supplies {main['known_positive']} known nominal outcomes,
{main['known_negative']} known nonnominal outcomes, and leaves {main['unknown']}
outcomes unknown. The resulting nominal-membership and positive-label-correctness
bounds are {main['lower_numerator']}/{main['n']} to
{main['upper_numerator']}/{main['n']} ({100 * float(main['lower']):.2f}% to
{100 * float(main['upper']):.2f}%). The unknown group alone has bounds zero to one.
Selected overlap concordance is {selected['known_positive']}/{selected['n']};
it is a separate post-hoc description, not an accuracy estimate for other issuers.

For an indicator with K positive reference outcomes, J negative reference
outcomes, and U unknown outcomes in a fixed N-unit set, each unknown indicator
can be zero or one. Summing gives K/N <= share <= (K+U)/N = 1-J/N. Both endpoints
are attainable under unrestricted outcome missingness conditional on the
accepted reference labels and their applicability to the screen issuer/event.
Feasible shares lie on the finite grid with step
1/N, not on a sampling distribution. There is no confidence level, p-value,
standard error, random-sampling claim, or missing-at-random assumption.

The primary quantity is nominal-label membership for the associated packets in
the finite issuer screen. It is not nominal-exit prevalence among verified
eligible city-platform exits. Four-class exhaustiveness is not imposed on this
screen. The four class counts in the confirmed reference set are reported
separately without extension to unconfirmed or no-event units.

## Event alignment

The {metrics['overlap_issuers']} matches establish exact issuer identity, not
independent same-event pairing. Of these, {metrics['overlap_with_reference_case_as_source']}
contain the reference case ID among their screen source-row IDs and
{metrics['overlap_with_shared_documents']} share at least one listed reference
evidence document. These are source anchors, not proof that the screen and
reference refer to the same event, post-event period, or independent decision.
No event-time alignment is certified in this experiment. The issuer audit retains
each reference event description and year, source-row links, and shared document
IDs for coordinator review. Without assuming that linked reference outcomes
apply to the corresponding screen issuer/event, all {main['n']} current-screen
outcomes may remain unknown and the nominal-membership bounds are zero to one.

## Candidate readiness

The current origin file has {candidate['origin_units']} issuer units and
{candidate['origin_rows']} origin rows. The eligible candidate has
{candidate['candidate_units']} issuers and {candidate['candidate_origin_rows']}
origin rows, split into {candidate['candidate_screen_counts'].get(POSITIVE, 0)}
nominal-screen positives and {candidate['candidate_screen_counts'].get(NO_EVENT, 0)}
no-direct-event screens. No candidate issuer overlaps the author-confirmed
reference set. Each candidate nominal-membership bound is therefore zero to one;
positive-label correctness uses only the positive-screen stratum. A no-direct-event
flag is not evidence of a nonnominal exit or of no actual event.

There are {candidate['proposal_strata']} proposed census strata, with no executed
draw and no final freeze approval. The inherited blank coding packet contains
{candidate['existing_blank_packet_rows']} rows, of which
{candidate['existing_packet_candidate_overlap']} match the current candidate;
none supplies a completed outcome. Current geography and scope readiness is
inherited from the base-commit records and is not a new raw-source audit.
There are {candidate['origin_rows_without_legacy_document_ids']} inherited origin
rows without legacy document IDs; both are retained and linked to the separate
current scope-source manifest, not silently omitted or treated as outcome evidence.

## Union denominator

Exact issuer names imply an arithmetic union of {metrics['reference_cases']} +
{main['n']} - {metrics['overlap_issuers']} = {metrics['arithmetic_issuer_union']}
issuer identities. This does not establish a union of eligible city-platform
exit cases. Among the {main['unknown']} nonoverlap screen issuers, current scope
records classify {candidate['nonoverlap_scope_counts'].get('eligible', 0)} as
eligible and {candidate['nonoverlap_scope_counts'].get('ineligible', 0)} as
ineligible for the candidate design. Scope exclusions are not human-confirmed
outcome negatives. No unconditional or conditional city-platform-union bounds
are supplied: treating every union identity as an eligible, uniquely timed
case would require an unsupported eligibility and event-alignment assumption.

## Provenance and limits

`{metrics['report_id']}` covers only the exact {metrics['reference_cases']}-case
reference snapshot and reports no revisions. Original outcomes and producer
metadata are retained. The report does not identify the reviewer, actual review
date, blinding, signatures, or independent coder decisions. The bounds are
conditional on the retained labels being correct, not proof of their accuracy.
If their correctness is also unrestricted, the true-outcome bounds widen to
zero to one. This experiment does not establish independent reliability,
probability validation, recall, calibration, national prevalence, or a main
empirical estimand.

Every reference issuer has exactly one case in this snapshot; no duplicate
case is dropped. All {metrics['overlap_issuers']} overlap issuer names agree
exactly with their linked reference case. The raw disclosure file repeats
{metrics['source_ids_repeated_across_roles']} source identifiers across distinct
analytical-role rows. Pools identify those rows; the selected surrogate subset
has unique source identifiers. Every historical reference disclosure resolves
by case ID and preserves its original label; none has an empty issuer name.
Empty issuer names outside the reference and selected-surrogate roles do not
enter the finite screened-issuer population.

Document and source identifiers resolve to the tracked inventories. URLs and
expected local paths are provenance, not evidence of fresh retrieval or proof
that a raw file exists. The inventories are not substitutes for source packets.

## Coordinator identifiers

- `VB-SCREEN-NOM` and `VB-SCREEN-CORRECT`: finite-screen bounds.
- `VB-SELECTED`: selected-overlap description only.
- `VB-CANDIDATE-NOM`, `VB-CANDIDATE-CORRECT`, and `VB-NOEVENT-NOM`: unknown candidate outcomes.
- `VB-REFERENCE-*`: assembled reference-set class descriptions.
- Existing claims C-009 and C-010 provide the overlap and author-report context;
  any manuscript insertion or new material claim requires coordinator ledger review.

No manuscript, global ledger, input snapshot, or human report is changed.
"""


def build(root: Path = ROOT) -> dict[Path, bytes]:
    data, hashes = load_inputs(root)
    audit, selected, ref_by_name = audit_overlap(data["reference"], data["issuers"], data["disclosures"])
    document_links = audit_sources(data, selected)
    unit_rows, candidate_counts = audit_candidate(data, audit, ref_by_name)
    bounds = make_bounds(audit, data["reference"], unit_rows)
    overlap = sum(bool(r["reference_case_id"]) for r in audit)
    metrics = {
        "experiment_id": EXPERIMENT, "base_commit": BASE, "report_id": data["report"]["report_id"],
        "reference_cases": len(data["reference"]), "reference_unique_issuers": len(ref_by_name),
        "reference_counts": dict(sorted(Counter(r["final_label"] for r in data["reference"]).items())),
        "reference_ambiguous_issuers": 0, "issuer_rows": len(audit),
        "selected_disclosure_rows": len(selected), "all_disclosure_rows": len(data["disclosures"]),
        "nominal_predictions": sum(r["screen_label"] == "nominal_exit" for r in audit),
        "overlap_issuers": overlap, "nonoverlap_issuers": len(audit) - overlap,
        "overlap_with_reference_case_as_source": sum(r["reference_case_in_screen_source_rows"] == "true" for r in audit),
        "overlap_with_shared_documents": sum(bool(r["shared_reference_screen_document_ids"]) for r in audit),
        "independent_same_event_pairing_established": False,
        "arithmetic_issuer_union": len(ref_by_name) + len(audit) - overlap,
        "city_platform_union_bounds_reported": False,
        "source_ids_repeated_across_roles": sum(n > 1 for n in Counter(r["source_row_id"] for r in data["disclosures"]).values()),
        "historical_reference_rows_with_empty_issuer": sum(not r["issuer_name"] for r in data["disclosures"] if r["label_source"] == "human_gold_standard"),
        "resolved_document_identifiers": len(document_links), "candidate": candidate_counts,
    }
    reference_audit = [{field: r[field] for field in (
        "case_id", "company_name", "province", "city", "official_exit_year", "final_label",
        "primary_evidence_doc", "primary_evidence_lines", "secondary_evidence_doc", "secondary_evidence_lines",
        "supplementary_source_id", "reference_label_producer", "human_confirmation_status"
    )} for r in sorted(data["reference"], key=lambda r: r["case_id"])]
    outputs = {
        Path("data/analysis_inputs/validation_identification_bounds.csv"): csv_bytes(bounds),
        Path("paper/tables/validation_identification_bounds.tex"): table_text(bounds, metrics).encode("utf-8"),
        ARTIFACTS / "issuer_audit.csv": csv_bytes(audit),
        ARTIFACTS / "reference_audit.csv": csv_bytes(reference_audit),
        ARTIFACTS / "disclosure_audit.csv": csv_bytes([{field: r[field] for field in (
            "pool_id", "source_row_id", "issuer_name", "label_source", "surrogate_status",
            "exit_type", "formal_event_found", "formal_event_summary", "continued_function_summary", "evidence_basis"
        )} for r in sorted(selected, key=lambda r: r["pool_id"])]),
        ARTIFACTS / "candidate_audit.csv": csv_bytes(unit_rows),
        ARTIFACTS / "document_links.csv": csv_bytes(document_links),
        ARTIFACTS / "metrics.json": json_bytes(metrics),
        ARTIFACTS / "notes.md": notes_text(bounds, metrics).encode("utf-8"),
    }
    manifest = {
        "experiment_id": EXPERIMENT, "base_commit": BASE,
        "input_sha256": hashes,
        "output_sha256": {str(path): digest(raw) for path, raw in sorted(outputs.items())},
        "producer_sha256": digest(Path(__file__).read_bytes()),
        "brief_sha256": digest((root / ARTIFACTS / "brief.md").read_bytes()),
        "dependencies_sha256": {str(p): digest((root / p).read_bytes()) for p in (
            Path("scripts/collapse_codex_surrogate_labels.py"), Path("scripts/human_confirmation.py"))},
        "command": "python3 scripts/build_validation_identification_bounds.py",
        "uncertainty": "deterministic missing-outcome bounds conditional on retained reference labels",
    }
    outputs[ARTIFACTS / "run_manifest.json"] = json_bytes(manifest)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify generated bytes without writing files")
    args = parser.parse_args()
    outputs = build()
    for relative, raw in outputs.items():
        target = ROOT / relative
        if args.check:
            require(target.exists() and target.read_bytes() == raw, f"Generated output differs: {relative}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    print(f"validation_identification_bounds={'verified' if args.check else 'written'}; artifacts={len(outputs)}")


if __name__ == "__main__":
    main()
