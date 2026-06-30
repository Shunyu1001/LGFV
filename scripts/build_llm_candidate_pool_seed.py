#!/usr/bin/env python3
"""Build a seed pool for LLM-assisted LGFV exit screening.

The file combines the curated master case pool with newly harvested public
disclosure pages. It is intentionally broader than the validated dataset. LLM
labels should be treated as surrogate labels until checked against the human
validation protocol.
"""

from __future__ import annotations

import argparse
import csv
import pathlib
from datetime import date


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_MASTER = ROOT / "data" / "analysis_inputs" / "master_case_pool.csv"
DEFAULT_HARVEST = ROOT / "data" / "analysis_inputs" / f"shclearing_candidate_harvest_broad_{date.today():%Y_%m_%d}.csv"
DEFAULT_OUTPUT = ROOT / "data" / "analysis_inputs" / f"llm_candidate_pool_seed_{date.today():%Y_%m_%d}.csv"

FIELDS = [
    "pool_id",
    "pool_source",
    "source_row_id",
    "validation_status",
    "case_pool_status",
    "province",
    "city",
    "issuer_name",
    "platform",
    "source_doc_count",
    "source_url",
    "announcement_title",
    "announcement_type",
    "instrument_type",
    "candidate_priority",
    "historical_capacity_bin",
    "debt_pressure_status",
    "land_finance_dependence_status",
    "llm_label_status",
    "llm_label",
    "llm_confidence",
    "human_review_status",
    "notes",
]


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def master_row(row: dict[str, str], index: int) -> dict[str, str]:
    validation_status = row.get("validation_status", "")
    return {
        "pool_id": f"master_{index:04d}",
        "pool_source": "master_case_pool",
        "source_row_id": row.get("case_id", ""),
        "validation_status": validation_status,
        "case_pool_status": row.get("case_pool_status", ""),
        "province": row.get("province", ""),
        "city": row.get("city", ""),
        "issuer_name": row.get("company_name", "") or row.get("platform", ""),
        "platform": row.get("platform", ""),
        "source_doc_count": row.get("source_doc_count", ""),
        "source_url": row.get("source_ids", ""),
        "announcement_title": "",
        "announcement_type": "",
        "instrument_type": "",
        "candidate_priority": "curated",
        "historical_capacity_bin": row.get("historical_capacity_bin", ""),
        "debt_pressure_status": row.get("debt_pressure_status", ""),
        "land_finance_dependence_status": row.get("land_finance_dependence_status", ""),
        "llm_label_status": "gold_standard" if validation_status == "human_validated" else "pending",
        "llm_label": row.get("llm_label", ""),
        "llm_confidence": row.get("llm_confidence", ""),
        "human_review_status": validation_status,
        "notes": row.get("notes", ""),
    }


def harvest_row(row: dict[str, str], index: int) -> dict[str, str]:
    return {
        "pool_id": f"harvest_{index:04d}",
        "pool_source": "shclearing_harvest_broad",
        "source_row_id": row.get("candidate_id", ""),
        "validation_status": "not_validated",
        "case_pool_status": "candidate_harvest",
        "province": "",
        "city": "",
        "issuer_name": row.get("issuer_name", ""),
        "platform": row.get("issuer_name", ""),
        "source_doc_count": "1",
        "source_url": row.get("source_url", ""),
        "announcement_title": row.get("announcement_title", ""),
        "announcement_type": row.get("announcement_type", ""),
        "instrument_type": row.get("instrument_type", ""),
        "candidate_priority": row.get("candidate_priority", ""),
        "historical_capacity_bin": "",
        "debt_pressure_status": "not_collected",
        "land_finance_dependence_status": "not_collected",
        "llm_label_status": row.get("llm_label_status", "pending") or "pending",
        "llm_label": row.get("llm_label", ""),
        "llm_confidence": row.get("llm_confidence", ""),
        "human_review_status": "not_reviewed",
        "notes": row.get("notes", ""),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", type=pathlib.Path, default=DEFAULT_MASTER)
    parser.add_argument("--harvest", type=pathlib.Path, default=DEFAULT_HARVEST)
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    rows: list[dict[str, str]] = []
    for index, row in enumerate(read_csv(args.master), start=1):
        rows.append(master_row(row, index))
    for index, row in enumerate(read_csv(args.harvest), start=1):
        rows.append(harvest_row(row, index))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    unique_issuers = {row["issuer_name"] for row in rows if row["issuer_name"]}
    human_validated = sum(1 for row in rows if row["validation_status"] == "human_validated")
    pending_llm = sum(1 for row in rows if row["llm_label_status"] == "pending")
    print(f"wrote {len(rows)} rows to {args.output}")
    print(f"unique_issuers={len(unique_issuers)} human_validated={human_validated} pending_llm={pending_llm}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
