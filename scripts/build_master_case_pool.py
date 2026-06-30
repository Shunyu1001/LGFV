#!/usr/bin/env python3
"""Build the master LGFV case-pool file.

The master file is the case-level scaffold for scaling the project from pilot
labels to a larger LLM-coded and human-validated dataset. It combines the
candidate city-platform list, validated labels, source-document inventory, and
historical-capacity measures. Contemporary fiscal variables remain explicit
placeholders until those data are collected.
"""

from __future__ import annotations

import argparse
import csv
import pathlib
from collections import defaultdict


OUTPUT_COLUMNS = [
    "case_id",
    "case_pool_status",
    "validation_status",
    "validation_tier",
    "sampling_frame",
    "selection_stratum",
    "oversample_low_capacity",
    "oversample_high_debt",
    "province",
    "city",
    "prefecture_name",
    "prefecture_name_chn",
    "platform",
    "company_name",
    "unified_social_credit_code",
    "gadm_gid",
    "source_doc_ids",
    "source_doc_count",
    "source_doc_types",
    "source_ids",
    "source_coverage_score",
    "formal_event_year",
    "formal_event",
    "formal_event_source_doc",
    "continued_function",
    "continued_function_source_doc",
    "continued_function_evidence_score",
    "exit_type",
    "confidence",
    "alternative_label",
    "ambiguity_note",
    "caveat",
    "historical_capacity_bin",
    "historical_capacity_label",
    "elite_density_percentile",
    "elite_per_1000_sqkm",
    "jinshi_per_1000_sqkm",
    "juren_per_1000_sqkm",
    "debt_pressure_value",
    "debt_pressure_year",
    "debt_pressure_bin",
    "debt_pressure_source",
    "debt_pressure_status",
    "land_finance_dependence_value",
    "land_finance_dependence_year",
    "land_finance_dependence_bin",
    "land_finance_dependence_source",
    "land_finance_dependence_status",
    "llm_label",
    "llm_confidence",
    "llm_model",
    "human_reviewer",
    "validation_date",
    "notes",
]

VALIDATED_LABELS = {
    "substantive_exit",
    "nominal_exit",
    "functional_transfer",
    "liquidation",
    "unclear",
}


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: pathlib.Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in OUTPUT_COLUMNS})


def split_values(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def unique_join(values: list[str]) -> str:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return ";".join(out)


def case_status_from_inputs(candidate: dict[str, str], label: dict[str, str] | None) -> str:
    if label:
        return "human_validated"
    status = candidate.get("evidence_status", "").strip()
    if status == "documents_found":
        return "llm_candidate_ready"
    if status == "source_started":
        return "source_started"
    return "candidate_not_started"


def validation_status(label: dict[str, str] | None) -> str:
    return "human_validated" if label else "not_validated"


def validation_tier(candidate: dict[str, str], label: dict[str, str] | None) -> str:
    if label:
        return "gold_standard"
    status = candidate.get("evidence_status", "").strip()
    if status == "documents_found":
        return "documented_candidate"
    if status == "source_started":
        return "source_started"
    return "source_only_candidate"


def debt_oversample_flag(candidate: dict[str, str]) -> str:
    stratum = candidate.get("selection_stratum", "")
    notes = " ".join(
        [
            candidate.get("selection_basis", ""),
            candidate.get("notes", ""),
            candidate.get("next_collection_priority", ""),
        ]
    )
    text = f"{stratum} {notes}".lower()
    return "1" if "debt" in text else "0"


def low_capacity_flag(candidate: dict[str, str]) -> str:
    return "1" if candidate.get("historical_capacity_bin", "") == "low" else "0"


def build_doc_index(document_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    by_case: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for row in document_rows:
        case_id = row.get("case_id", "").strip()
        if not case_id:
            continue
        by_case[case_id]["document_ids"].append(row.get("document_id", "").strip())
        by_case[case_id]["document_types"].append(row.get("document_type", "").strip())
        by_case[case_id]["source_ids"].append(row.get("source_id", "").strip())
    return {
        case_id: {
            "source_doc_ids": unique_join(values["document_ids"]),
            "source_doc_count": str(len([value for value in values["document_ids"] if value])),
            "source_doc_types": unique_join(values["document_types"]),
            "source_ids": unique_join(values["source_ids"]),
        }
        for case_id, values in by_case.items()
    }


def source_doc_subset(documents: str, preferred: str) -> str:
    docs = split_values(preferred)
    if docs:
        return unique_join(docs)
    return documents


def build_rows(
    candidate_rows: list[dict[str, str]],
    label_rows: list[dict[str, str]],
    document_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    labels = {row["case_id"]: row for row in label_rows if row.get("case_id")}
    doc_index = build_doc_index(document_rows)

    rows: list[dict[str, str]] = []
    seen_cases: set[str] = set()
    for candidate in candidate_rows:
        case_id = candidate.get("case_id", "").strip()
        if not case_id:
            continue
        seen_cases.add(case_id)
        label = labels.get(case_id)
        docs = doc_index.get(case_id, {})

        formal_event = ""
        formal_year = ""
        continued_function = ""
        exit_type = ""
        confidence = ""
        source_coverage = ""
        continued_score = ""
        if label:
            formal_event = label.get("official_exit_event", "")
            formal_year = label.get("official_exit_year", "")
            continued_function = label.get("final_rationale", "")
            exit_type = label.get("final_label", "")
            confidence = label.get("final_confidence", "")
            source_coverage = label.get("source_coverage_score", "")
            continued_score = ""
        else:
            exit_type = ""
            confidence = ""

        debt_status = "not_collected"
        if debt_oversample_flag(candidate) == "1":
            debt_status = "targeted_for_collection"

        row = {
            "case_id": case_id,
            "case_pool_status": case_status_from_inputs(candidate, label),
            "validation_status": validation_status(label),
            "validation_tier": validation_tier(candidate, label),
            "sampling_frame": "pilot_expansion",
            "selection_stratum": candidate.get("selection_stratum", ""),
            "oversample_low_capacity": low_capacity_flag(candidate),
            "oversample_high_debt": debt_oversample_flag(candidate),
            "province": candidate.get("province", ""),
            "city": candidate.get("city", ""),
            "prefecture_name": candidate.get("capacity_prefecture_name", ""),
            "prefecture_name_chn": candidate.get("capacity_prefecture_name_chn", ""),
            "platform": candidate.get("target_platform", "") or (label or {}).get("company_name", ""),
            "company_name": (label or {}).get("company_name", "") or candidate.get("target_platform", ""),
            "unified_social_credit_code": "",
            "gadm_gid": candidate.get("gadm_gid", ""),
            "source_doc_ids": docs.get("source_doc_ids", ""),
            "source_doc_count": docs.get("source_doc_count", "0"),
            "source_doc_types": docs.get("source_doc_types", ""),
            "source_ids": docs.get("source_ids", ""),
            "source_coverage_score": source_coverage,
            "formal_event_year": formal_year,
            "formal_event": formal_event,
            "formal_event_source_doc": source_doc_subset(
                docs.get("source_doc_ids", ""), (label or {}).get("primary_evidence_doc", "")
            ),
            "continued_function": continued_function,
            "continued_function_source_doc": source_doc_subset(
                docs.get("source_doc_ids", ""), (label or {}).get("secondary_evidence_doc", "")
            ),
            "continued_function_evidence_score": continued_score,
            "exit_type": exit_type,
            "confidence": confidence,
            "alternative_label": (label or {}).get("alternative_label", ""),
            "ambiguity_note": (label or {}).get("ambiguity_note", ""),
            "caveat": (label or {}).get("caveat", ""),
            "historical_capacity_bin": candidate.get("historical_capacity_bin", ""),
            "historical_capacity_label": candidate.get("historical_capacity_label", ""),
            "elite_density_percentile": candidate.get("elite_density_percentile", ""),
            "elite_per_1000_sqkm": candidate.get("elite_per_1000_sqkm", ""),
            "jinshi_per_1000_sqkm": candidate.get("jinshi_per_1000_sqkm", ""),
            "juren_per_1000_sqkm": candidate.get("juren_per_1000_sqkm", ""),
            "debt_pressure_value": "",
            "debt_pressure_year": "",
            "debt_pressure_bin": "",
            "debt_pressure_source": "",
            "debt_pressure_status": debt_status,
            "land_finance_dependence_value": "",
            "land_finance_dependence_year": "",
            "land_finance_dependence_bin": "",
            "land_finance_dependence_source": "",
            "land_finance_dependence_status": "not_collected",
            "llm_label": "",
            "llm_confidence": "",
            "llm_model": "",
            "human_reviewer": (label or {}).get("human_reviewer", ""),
            "validation_date": (label or {}).get("validation_date", ""),
            "notes": (label or {}).get("notes", "") or candidate.get("notes", ""),
        }
        rows.append(row)

    for case_id, label in labels.items():
        if case_id in seen_cases:
            continue
        docs = doc_index.get(case_id, {})
        rows.append(
            {
                "case_id": case_id,
                "case_pool_status": "human_validated",
                "validation_status": "human_validated",
                "validation_tier": "gold_standard",
                "sampling_frame": "label_file_only",
                "province": label.get("province", ""),
                "city": label.get("city", ""),
                "platform": label.get("company_name", ""),
                "company_name": label.get("company_name", ""),
                "source_doc_ids": docs.get("source_doc_ids", ""),
                "source_doc_count": docs.get("source_doc_count", "0"),
                "source_doc_types": docs.get("source_doc_types", ""),
                "source_ids": docs.get("source_ids", ""),
                "source_coverage_score": label.get("source_coverage_score", ""),
                "formal_event_year": label.get("official_exit_year", ""),
                "formal_event": label.get("official_exit_event", ""),
                "formal_event_source_doc": label.get("primary_evidence_doc", ""),
                "continued_function": label.get("final_rationale", ""),
                "continued_function_source_doc": label.get("secondary_evidence_doc", ""),
                "exit_type": label.get("final_label", ""),
                "confidence": label.get("final_confidence", ""),
                "alternative_label": label.get("alternative_label", ""),
                "ambiguity_note": label.get("ambiguity_note", ""),
                "caveat": label.get("caveat", ""),
                "debt_pressure_status": "not_collected",
                "land_finance_dependence_status": "not_collected",
                "human_reviewer": label.get("human_reviewer", ""),
                "validation_date": label.get("validation_date", ""),
                "notes": label.get("notes", ""),
            }
        )

    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--candidates",
        default="data/analysis_inputs/candidate_city_historical_capacity.csv",
    )
    parser.add_argument("--labels", default="data/processed/human_validated_labels.csv")
    parser.add_argument("--documents", default="data/document_inventory.csv")
    parser.add_argument("--output", default="data/analysis_inputs/master_case_pool.csv")
    args = parser.parse_args()

    rows = build_rows(
        read_csv(pathlib.Path(args.candidates)),
        read_csv(pathlib.Path(args.labels)),
        read_csv(pathlib.Path(args.documents)),
    )
    write_csv(pathlib.Path(args.output), rows)
    print(f"wrote={args.output}")
    print(f"rows={len(rows)}")
    print(f"columns={len(OUTPUT_COLUMNS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
