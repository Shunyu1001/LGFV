#!/usr/bin/env python3
"""Report actual collection gaps; dispatch only explicitly supplied analyses."""

import argparse
import csv
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from human_confirmation import confirmed_rows

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / "data/validation/collection_2026_09_10"
OUT = ROOT / "data/validation/inference_2026_09_10"
EXIT_LABELS = {"substantive_exit", "nominal_exit", "functional_transfer", "liquidation"}


def rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def indexed(records, field):
    result = {}
    for row in records:
        key = row.get(field)
        if not key or key in result:
            raise ValueError(f"missing or duplicate {field}: {key}")
        result[key] = row
    return result


def assess_collection(candidate, readiness, entries, confirmed):
    frame = indexed(candidate, "validation_unit_id")
    checks = indexed(readiness, "packet_case_id")
    responses = indexed(entries, "packet_case_id")
    if not frame or set(frame) != set(checks) or set(frame) != set(responses):
        raise ValueError("candidate, readiness, and response unit IDs must agree exactly")
    reference = indexed(confirmed, "case_id")
    completed, unresolved, untouched = [], [], []
    for uid, row in responses.items():
        fields = [row.get(name, "").strip() for name in
                  ("coder_id", "coding_date", "exit_case_eligibility", "formal_event_found",
                   "post_event_evidence_found", "final_label", "rationale", "coder_signature")]
        if not any(fields):
            untouched.append(uid)
            continue
        label = row.get("final_label", "").strip()
        if label and label not in EXIT_LABELS | {"unclear", "unresolved"}:
            raise ValueError(f"unsupported exit label for {uid}: {label}")
        if label in EXIT_LABELS:
            if row.get("exit_case_eligibility") != "eligible" or any(
                row.get(field) != "true" for field in ("formal_event_found", "post_event_evidence_found")
            ):
                raise ValueError(f"exit label lacks explicit event/function eligibility: {uid}")
            if all(row.get(field, "").strip() for field in
                   ("coder_id", "coding_date", "rationale", "formal_event_source_references",
                    "post_event_source_references", "coder_signature")):
                completed.append(uid)
                continue
        unresolved.append(uid)
    return {
        "schema_version": 1,
        "status": "not_estimated",
        "frame_units": len(frame),
        "author_reported_human_checked_reference_cases": len(reference),
        "completed_entry_records_pending_source_and_process_verification": len(completed),
        "unresolved_or_incomplete_entries": len(unresolved),
        "untouched_human_entries": len(untouched),
        "completed_entry_unit_ids": completed,
        "unresolved_unit_ids": unresolved,
        "untouched_unit_ids": untouched,
        "actual_selection_probabilities": None,
        "numerical_estimate": None,
        "blocking_reasons": [
            "no_explicit_approved_analysis_request_and_realized_selection_supplied",
            "human_entry_records_require_case_evidence_and_process_verification",
        ] + (["missing_or_unresolved_human_outcomes"] if untouched or unresolved else []),
        "note": "Proposed census probabilities are not response probabilities. Template completeness does not authenticate human review. The existing reference report does not cover new validation IDs.",
    }


def decode_request(raw):
    from design_based_validation import (AnalysisSpec, Design, Frame, FrameUnit,
                                        HumanResponse, Request, Selection, Stratum)
    frame = dict(raw["frame"])
    frame["units"] = tuple(FrameUnit(**{**r, "covariates": tuple(r["covariates"])}) for r in frame["units"])
    frame["covariate_names"] = tuple(frame["covariate_names"])
    design = dict(raw["design"])
    design["strata"] = tuple(Stratum(**r) for r in design["strata"])
    selection = dict(raw["selection"])
    selection["selected_unit_ids"] = tuple(selection["selected_unit_ids"])
    return Request(mode=raw["mode"], frame=Frame(**frame), design=Design(**design),
                   spec=AnalysisSpec(**raw["spec"]), selection=Selection(**selection),
                   responses=tuple(HumanResponse(**r) for r in raw["responses"]))


def run_approved_analysis(request_path, approvals_path, estimand="mean"):
    from design_based_validation import Approval, estimate_fixed_x, estimate_mean
    request = decode_request(json.loads(Path(request_path).read_text()))
    approvals = tuple(Approval(**row) for row in json.loads(Path(approvals_path).read_text()))
    if estimand == "mean":
        estimate = estimate_mean(request, approvals=approvals)
    elif estimand == "fixed_x":
        estimate = estimate_fixed_x(request, approvals=approvals)
    else:
        raise ValueError(f"unsupported estimand: {estimand}")
    return asdict(estimate)


def assemble_status(collection, source_hashes, estimate=None):
    requested = {"status": "not_requested", "numerical_estimate": None}
    if estimate is not None:
        requested = {
            "status": ("explicit_request_estimated" if estimate["mode"] == "actual"
                       else "synthetic_engine_check_only"),
            "numerical_estimate": estimate,
            "scope": "The supplied request, not automatically the current collection proposal.",
        }
    return {"schema_version": 2, "collection": collection,
            "source_hashes": source_hashes, "requested_analysis": requested}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--entries", type=Path, default=COLLECTION / "blinded_coder_1_entry.csv")
    parser.add_argument("--output-dir", type=Path, default=OUT)
    parser.add_argument("--request", type=Path)
    parser.add_argument("--approvals", type=Path)
    parser.add_argument("--estimand", choices=["mean", "fixed_x"], default="mean")
    args = parser.parse_args()
    if bool(args.request) != bool(args.approvals):
        raise ValueError("an explicit analysis request and its vetted approvals must be supplied together")
    source_paths = {
        "candidate": ROOT / "data/validation/probability_validation_frame_candidate.csv",
        "readiness": COLLECTION / "realized_input_readiness.json", "entries": args.entries,
    }
    status = assess_collection(rows(source_paths["candidate"]),
                               json.loads(source_paths["readiness"].read_text())["units"],
                               rows(args.entries), confirmed_rows())
    source_hashes = {name: hashlib.sha256(path.read_bytes()).hexdigest()
                     for name, path in source_paths.items()}
    estimate = None
    if args.request:
        estimate = run_approved_analysis(args.request, args.approvals, args.estimand)
    report = assemble_status(status, source_hashes, estimate)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "status.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"status={status['status']}; frame_units={status['frame_units']}; "
          f"untouched_human_entries={status['untouched_human_entries']}; "
          f"unresolved_entries={status['unresolved_or_incomplete_entries']}")


if __name__ == "__main__":
    main()
