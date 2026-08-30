#!/usr/bin/env python3
"""Audit whether each gold-label evidence packet can be reconstructed."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--gold",
        default="data/processed/human_validated_labels.csv",
    )
    parser.add_argument("--documents", default="data/document_inventory.csv")
    parser.add_argument("--sources", default="data/source_inventory.csv")
    parser.add_argument(
        "--output",
        default="data/diagnostics/source_reconstruction_audit.csv",
    )
    parser.add_argument(
        "--report",
        default="docs/reproducibility/source_reconstruction_audit.md",
    )
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def split_ids(value: str) -> list[str]:
    return [item.strip() for item in value.replace("|", ";").split(";") if item.strip()]


def unique_index(rows: list[dict[str, str]], key: str, label: str) -> dict[str, dict[str, str]]:
    values = [row.get(key, "").strip() for row in rows]
    counts = Counter(value for value in values if value)
    duplicates = sorted(value for value, count in counts.items() if count > 1)
    if duplicates:
        raise ValueError(f"Duplicate {label} identifiers: {', '.join(duplicates)}")
    return {row[key].strip(): row for row in rows if row.get(key, "").strip()}


def local_exists(root: Path, local_path: str) -> bool:
    if not local_path:
        return False
    path = Path(local_path)
    return path.exists() if path.is_absolute() else (root / path).exists()


def find_memos(root: Path, case_id: str, company_name: str) -> list[str]:
    matches: list[str] = []
    for path in sorted((root / "coding").glob("pilot_evidence_*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if case_id in text or (company_name and company_name in text):
            matches.append(str(path.relative_to(root)))
    return matches


def yes(value: bool) -> str:
    return "yes" if value else "no"


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    gold = read_csv(root / args.gold)
    documents = read_csv(root / args.documents)
    sources = read_csv(root / args.sources)
    document_by_id = unique_index(documents, "document_id", "document")
    source_by_id = unique_index(sources, "source_id", "source")

    audit_rows: list[dict[str, str]] = []
    for case in gold:
        primary_ids = split_ids(case.get("primary_evidence_doc", ""))
        secondary_ids = split_ids(case.get("secondary_evidence_doc", ""))
        supplementary_ids = split_ids(case.get("supplementary_source_id", ""))
        document_ids = primary_ids + secondary_ids
        missing_document_ids = [item for item in document_ids if item not in document_by_id]
        missing_source_ids = [item for item in supplementary_ids if item not in source_by_id]
        resolved_documents = [document_by_id[item] for item in document_ids if item in document_by_id]
        local_ids = [
            item
            for item in document_ids
            if item in document_by_id
            and local_exists(root, document_by_id[item].get("local_file_path", "").strip())
        ]
        url_ids = [
            item
            for item in document_ids
            if item in document_by_id
            and (
                document_by_id[item].get("document_page_url", "").strip()
                or document_by_id[item].get("download_url", "").strip()
            )
        ]
        memos = find_memos(root, case.get("case_id", ""), case.get("company_name", ""))
        audit_rows.append(
            {
                "case_id": case.get("case_id", ""),
                "province": case.get("province", ""),
                "city": case.get("city", ""),
                "company_name": case.get("company_name", ""),
                "final_label": case.get("final_label", ""),
                "final_confidence": case.get("final_confidence", ""),
                "source_coverage_score": case.get("source_coverage_score", ""),
                "primary_reference_count": str(len(primary_ids)),
                "secondary_reference_count": str(len(secondary_ids)),
                "supplementary_reference_count": str(len(supplementary_ids)),
                "all_identifiers_resolved": yes(not missing_document_ids and not missing_source_ids),
                "all_evidence_files_local": yes(bool(document_ids) and len(local_ids) == len(document_ids)),
                "some_evidence_file_local": yes(bool(local_ids)),
                "all_documents_have_recovery_url": yes(bool(document_ids) and len(url_ids) == len(document_ids)),
                "dedicated_evidence_memo_found": yes(bool(memos)),
                "resolved_local_document_count": str(len(local_ids)),
                "resolved_url_document_count": str(len(url_ids)),
                "missing_document_ids": ";".join(missing_document_ids),
                "missing_source_ids": ";".join(missing_source_ids),
                "missing_local_document_ids": ";".join(
                    item for item in document_ids if item not in local_ids
                ),
                "document_types": ";".join(
                    sorted({row.get("document_type", "").strip() for row in resolved_documents if row.get("document_type", "").strip()})
                ),
                "evidence_memo_paths": ";".join(memos),
            }
        )

    output_path = root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(audit_rows[0]) if audit_rows else []
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(audit_rows)

    def count(field: str) -> int:
        return sum(row[field] == "yes" for row in audit_rows)

    unresolved = [row for row in audit_rows if row["all_identifiers_resolved"] == "no"]
    incomplete_local = [row for row in audit_rows if row["all_evidence_files_local"] == "no"]
    no_memo = [row for row in audit_rows if row["dedicated_evidence_memo_found"] == "no"]
    report = [
        "# Source reconstruction audit",
        "",
        "This audit tests whether the evidence references recorded for each human-validated case resolve against the tracked inventories and whether the cited documents can be recovered from local files or stable URLs. It does not revalidate substantive labels.",
        "",
        "## Results",
        "",
        f"- Human-validated cases: {len(audit_rows)}.",
        f"- Cases with all document and source identifiers resolved: {count('all_identifiers_resolved')}.",
        f"- Cases with every cited evidence document stored locally: {count('all_evidence_files_local')}.",
        f"- Cases with at least one cited evidence document stored locally: {count('some_evidence_file_local')}.",
        f"- Cases with a recovery URL for every cited document: {count('all_documents_have_recovery_url')}.",
        f"- Cases matched to at least one dedicated evidence memo: {count('dedicated_evidence_memo_found')}.",
        "",
        "## Remaining gaps",
        "",
        "Cases with unresolved identifiers: " + (", ".join(row["case_id"] for row in unresolved) or "none") + ".",
        "",
        "Cases without a complete local evidence packet: " + (", ".join(row["case_id"] for row in incomplete_local) or "none") + ".",
        "",
        "Cases without an exact case-ID or company-name match in a dedicated evidence memo: " + (", ".join(row["case_id"] for row in no_memo) or "none") + ".",
        "",
        "The case-level audit is stored in `data/diagnostics/source_reconstruction_audit.csv`. URL availability records a recovery route, not proof that a remote document will remain accessible. Local-file coverage records file presence, not an independent check of document authenticity or coding accuracy.",
    ]
    report_path = root / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"cases={len(audit_rows)}")
    print(f"all_identifiers_resolved={count('all_identifiers_resolved')}")
    print(f"all_evidence_files_local={count('all_evidence_files_local')}")
    print(f"all_documents_have_recovery_url={count('all_documents_have_recovery_url')}")
    print(f"dedicated_evidence_memo_found={count('dedicated_evidence_memo_found')}")
    if args.strict and unresolved:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
