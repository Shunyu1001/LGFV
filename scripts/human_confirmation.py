"""Resolve the author's human-check report against an exact reference snapshot."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "data/processed/working_reference_labels.csv"
REPORT = ROOT / "data/validation/human_confirmation_report_2026_09_10.json"
REGISTER = ROOT / "data/validation/human_confirmation_register.csv"
CONFIRMED_STATUS = "human_checked_no_revision_author_reported"
PENDING_NOTICE = "Working reference labels await independent human confirmation."
CONFIRMED_NOTICE = (
    "Reference labels were human-checked without revision, as reported by the author "
    "on 10 September 2026; blind double coding is not documented."
)


def confirmed_rows(reference: Path = REFERENCE, report_path: Path = REPORT) -> list[dict[str, str]]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    raw = reference.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != report["source_snapshot_sha256"]:
        raise ValueError("Human confirmation does not cover this reference snapshot")
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
    case_ids = [row["case_id"] for row in rows]
    if len(rows) != report["case_count"] or len(set(case_ids)) != len(rows) or not all(case_ids):
        raise ValueError("Human confirmation case scope mismatch")
    if dict(Counter(row["final_label"] for row in rows)) != report["outcome_counts"]:
        raise ValueError("Human confirmation outcome counts mismatch")
    if report["confirmation_status"] != CONFIRMED_STATUS:
        raise ValueError("Unsupported human confirmation status")
    if report["basis"] != "author_report_of_completed_human_check":
        raise ValueError("Unsupported human confirmation basis")
    return [
        {
            "case_id": row["case_id"],
            "confirmed_label": row["final_label"],
            "original_label_producer": row["reference_label_producer"],
            "confirmation_status": CONFIRMED_STATUS,
            "confirmation_basis": report["basis"],
            "report_id": report["report_id"],
            "reported_by": report["reported_by"],
            "reported_on": report["reported_on"],
            "reviewer_identity": report["reviewer_identity"] or "",
            "review_completed_on": report["review_completed_on"] or "",
            "blinding_status": report["blinding_status"],
            "source_snapshot_sha256": digest,
        }
        for row in rows
    ]


@lru_cache(maxsize=1)
def confirmed_case_ids() -> frozenset[str]:
    return frozenset(row["case_id"] for row in confirmed_rows())


def case_is_human_checked(case_id: str) -> bool:
    return bool(case_id) and case_id in confirmed_case_ids()


def confirmation_notice(case_id: str) -> str:
    return CONFIRMED_NOTICE if case_is_human_checked(case_id) else PENDING_NOTICE


def replace_confirmation_notice(text: str, case_id: str) -> str:
    # Remove the superseded snapshot notice without touching evidence caveats.
    cleaned = (text or "").replace(PENDING_NOTICE, "").replace(CONFIRMED_NOTICE, "").strip()
    return " ".join(part for part in (cleaned, confirmation_notice(case_id)) if part)
