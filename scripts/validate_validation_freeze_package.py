#!/usr/bin/env python3
"""Validate the EXP-20260831-002/003 freeze-decision package.

The default check uses only tracked files. Optional ``--cache-dir`` arguments
also verify the temporary raw caches and every registered PDF-page text hash.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEX64 = re.compile(r"^[0-9a-f]{64}$")

FROZEN_HASHES = {
    "immutable/research_charter.md": "6e649d8618856f9eb128ad8318759385375c04d4f860bbf61f513ba2cc368b4c",
    "immutable/analysis_plan.md": "5a8c5527bfbc0d604d31631c8eb0e48f86021ff33c0ce9ed717f2d01724f5f16",
    "immutable/evaluation_protocol.md": "d0e225924dd770cf1d1c2fff57939bc7a7344e3e116c0d751cde4f0cef35f3ac",
    "immutable/data_manifest.yaml": "c2b34c94a95421ac9f49982eee4565d5ab3c885d3263ba105eaedd78de052424",
    "coding/codebook.md": "877a898bfc125e9bfd35c1f612b5034a00ab30cd3a9f9efaca7f10aab9dc9b66",
    "coding/label_provenance.md": "fde96643b2038e571ef7f604af9d26cf08c142b7086f644696da825e5922e55f",
    "data/validation/label_role_registry.csv": "48b2610cc26c8f411d04fdabd692b9706fa3846a266b2f1509bfabcbc71b099b",
    "data/processed/working_reference_labels.csv": "c1e6bd66b7f498a6100422b9f4a66a61374eb47f65fc7fe5f0446f503e2afd18",
    "data/analysis_inputs/codex_surrogate_labels_2026_07_03_expanded.csv": "cfced00afd193fa68d95db10888d05069fab27e7c957832d29bf6260ac44dfbe",
    "data/validation/probability_validation_geography_scope_crosswalk.csv": "fc72c263dade64d3404d873fec0b40328429346661710d24988c448fbeb711d2",
    "data/validation/probability_validation_unresolved_log.csv": "5c9ede8c97b86add246ab99b2a6a052375f849f9be9fecc02abd4c95f368571c",
    "data/validation/probability_validation_source_manifest.csv": "5713057b161939748a334426bb41e5ed1ce59adc4519204ea0b1d31b0bb1d664",
    "data/validation/probability_validation_frame_candidate.csv": "a31000f9896b86c6bbd9327716761fb28386ea08a57c7845b8884e1a36be168c",
    "data/validation/probability_validation_frame_origin_rows.csv": "2799dda51d7cbe05c1960ae35ae67354dbaedf0495d5315cbcca2038ba2fe2f7",
    "data/validation/probability_validation_frame_flow.csv": "57929324912b1ab3db7eb97c72709fdbcf5424783087c64baa433f385a22a423",
    "data/validation/probability_validation_sampling_design.csv": "f525276471be1911b125f6e41d4ad870ad49f20b70f8cd09face4e80532c8abd",
}

RAW_FILENAMES = {
    "doc_exp10_20260704_0013_006": "doc_exp10_20260704_0013_006.pdf",
    "web_hkex_szi_2025_interim": "shenzhen_international_2025_interim.pdf",
    "doc_sch_20260630_0135_010": "doc_sch_20260630_0135_010.pdf",
    "doc_sch_20260630_0135_002": "doc_sch_20260630_0135_002.pdf",
    "web_chinamoney_dyg_2025_legal_opinion": "dongyangguang_2025_legal_opinion.pdf",
    "web_saac_guiyang_public_transport_current_name": "web_saac_guiyang_public_transport_current_name.html",
    "web_guiyang_2022_midyear_bond_report": "guiyang_2022_midyear_bond_report.pdf",
    "web_guiyang_2023_bond_agent_report": "guiyang_2023_bond_agent_report.pdf",
    "web_guiyang_s1_environment_report": "guiyang_s1_environment_report.pdf",
    "web_guiyang_identity_arbitration_2026": "guiyang_identity_arbitration_2026.pdf",
}

COMBINED_PAGE_SPECS = {
    "web_hkex_szi_2025_interim": ([5], "86fc747ee4d834807bb3ea6a38482c4ec0b790c8ce1acc6e7ca7dfe836eba70f"),
    "web_chinamoney_dyg_2025_legal_opinion": ([5], "d1bead5ad234a167842d2251ac19c21389996e8816ff1aa3d7b15f4059c5e112"),
    "web_guiyang_2022_midyear_bond_report": ([6, 7, 8, 9, 13], "bfe1e176378df375f4512f09a918f472f24aa171b720d4382682a4908d20ed33"),
    "web_guiyang_2023_bond_agent_report": ([1, 5, 9], "331a0503ae4056ba23de9631ea15d74e4acacd09be765dfa123b9fe1d694f74a"),
    "web_guiyang_s1_environment_report": ([70], "c91d417f83b5a329e8f37676807eb0b94e7ea51f52c624aff0b0da24d8b7cd33"),
    "web_guiyang_identity_arbitration_2026": ([1, 2], "f209f8b9334d54f4f3c64886edd96130c22be6ef87966e6dab8cf4095147d5f1"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path, delimiter: str = ",") -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def manifest_hash_entries(path: Path, section: str) -> list[tuple[str, str]]:
    """Read the simple path/SHA pairs used by these run manifests."""
    entries: list[tuple[str, str]] = []
    current_path: str | None = None
    in_section = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if raw_line == f"{section}:":
            in_section = True
            continue
        if in_section and raw_line and not raw_line.startswith(" "):
            break
        if not in_section:
            continue
        line = raw_line.strip()
        if line.startswith("- path: "):
            current_path = line.removeprefix("- path: ")
        elif line.startswith("sha256: ") and current_path is not None:
            entries.append((current_path, line.removeprefix("sha256: ")))
            current_path = None
    return entries


def normalized_page_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in text.split("\n")).strip() + "\n"


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_raw_caches(
    manifests: list[dict[str, str]],
    excerpts: list[dict[str, str]],
    cache_dirs: list[Path],
    errors: list[str],
) -> None:
    try:
        import pdfplumber
    except ImportError:
        errors.append("pdfplumber is required when --cache-dir is supplied")
        return

    located: dict[str, Path] = {}
    for row in manifests:
        document_id = row["document_id"]
        if document_id == "tracked_chinabond_bond_inventory":
            path = ROOT / "data/bond_inventory.csv"
        else:
            filename = RAW_FILENAMES[document_id]
            candidates = [directory / filename for directory in cache_dirs]
            path = next((candidate for candidate in candidates if candidate.exists()), None)
            if path is None:
                errors.append(f"raw cache not found for {document_id}: {filename}")
                continue
        located[document_id] = path
        require(sha256(path) == row["raw_sha256"], f"raw hash mismatch: {document_id}", errors)
        require(path.stat().st_size == int(row["retrieved_bytes"]), f"raw byte-size mismatch: {document_id}", errors)

    for row in excerpts:
        match = re.search(r"PDF page (\d+)", row["locator"])
        if not match:
            continue
        document_id = row["document_id"]
        path = located.get(document_id)
        if path is None:
            continue
        page_number = int(match.group(1))
        with pdfplumber.open(path) as pdf:
            text = normalized_page_text(pdf.pages[page_number - 1].extract_text() or "")
        observed = hashlib.sha256(text.encode()).hexdigest()
        require(observed == row["page_text_sha256"], f"page-text hash mismatch: {row['excerpt_id']}", errors)

    for document_id, (pages, expected) in COMBINED_PAGE_SPECS.items():
        path = located.get(document_id)
        if path is None:
            continue
        chunks: list[str] = []
        with pdfplumber.open(path) as pdf:
            for page_number in pages:
                text = normalized_page_text(pdf.pages[page_number - 1].extract_text() or "")
                chunks.append(f"=== PDF PAGE {page_number} ===\n{text}")
        observed = hashlib.sha256("".join(chunks).encode()).hexdigest()
        require(observed == expected, f"combined extraction hash mismatch: {document_id}", errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", action="append", default=[], type=Path)
    args = parser.parse_args()
    errors: list[str] = []

    for relative, expected in FROZEN_HASHES.items():
        path = ROOT / relative
        require(path.exists(), f"missing frozen input: {relative}", errors)
        if path.exists():
            require(sha256(path) == expected, f"frozen input changed: {relative}", errors)

    all_manifests: list[dict[str, str]] = []
    all_excerpts: list[dict[str, str]] = []
    all_decisions: list[dict[str, str]] = []
    expected_records = {"EXP-20260831-002": (5, 7, 2), "EXP-20260831-003": (6, 12, 2)}
    for experiment, counts in expected_records.items():
        directory = ROOT / "experiments" / experiment
        manifest = read_csv(directory / "source_manifest.csv")
        excerpts = read_csv(directory / "source_excerpts.csv")
        decisions = read_csv(directory / "case_decisions.csv")
        metrics = json.loads((directory / "metrics.json").read_text(encoding="utf-8"))
        run_manifest = directory / "run_manifest.yaml"
        require((len(manifest), len(excerpts), len(decisions)) == counts, f"record counts changed: {experiment}", errors)
        document_ids = {row["document_id"] for row in manifest}
        require(len(document_ids) == len(manifest), f"duplicate document ID: {experiment}", errors)
        for row in manifest:
            require(bool(HEX64.fullmatch(row["raw_sha256"])), f"invalid raw hash: {row['document_id']}", errors)
            require(row["local_copy_committed"] in {"true", "false"}, f"invalid local-copy flag: {row['document_id']}", errors)
        for row in excerpts:
            require(row["document_id"] in document_ids, f"orphan excerpt: {row['excerpt_id']}", errors)
            require(bool(HEX64.fullmatch(row["page_text_sha256"])), f"invalid page hash: {row['excerpt_id']}", errors)
        require(metrics["random_draw_executed"] is False, f"random draw flag true: {experiment}", errors)
        require(metrics["raw_sources_committed"] is False, f"raw sources committed: {experiment}", errors)
        require(metrics["integrated_registered_frame_gates_closed"] == 0, f"frame integration occurred: {experiment}", errors)
        for section in ("inputs", "outputs"):
            entries = manifest_hash_entries(run_manifest, section)
            require(bool(entries), f"run manifest has no {section}: {experiment}", errors)
            for relative, expected in entries:
                path = ROOT / relative
                require(path.exists(), f"run-manifest file missing: {relative}", errors)
                if path.exists():
                    require(sha256(path) == expected, f"run-manifest hash mismatch: {relative}", errors)
        all_manifests.extend(manifest)
        all_excerpts.extend(excerpts)
        all_decisions.extend(decisions)

    disposition_counts = Counter(row["evidence_disposition"] for row in all_decisions)
    require(len(all_decisions) == 4, "expected exactly four audited gates", errors)
    require(disposition_counts == Counter({"resolved_existing_rule": 3, "unresolved_rule_required": 1}), "evidence gate counts changed", errors)
    require({row["validation_unit_id"] for row in all_decisions} == {"mv_2547f5fbc2e2", "mv_940b87861065", "mv_dd84e076bf32"}, "audited unit set changed", errors)
    require(all(row["integrated_into_registered_frame"] == "false" for row in all_decisions), "a decision was silently integrated", errors)

    unresolved = read_csv(ROOT / "data/validation/probability_validation_unresolved_log.csv")
    require(len(unresolved) == 4, "registered unresolved-log gate count is not four", errors)
    require(len({row["validation_unit_id"] for row in unresolved}) == 3, "registered unresolved-log unit count is not three", errors)

    cr = (ROOT / "change_requests/CR-20260831-001.md").read_text(encoding="utf-8")
    require("Status: proposed; PI decision required" in cr, "change request is not pending", errors)
    require("Implemented: no" in cr, "change request appears implemented", errors)
    rebuild = (ROOT / "experiments/EXP-20260831-004/brief.md").read_text(encoding="utf-8")
    require("Status: prospective; not executed" in rebuild, "prospective rebuild status changed", errors)
    require("Do not execute this experiment" in rebuild, "prospective rebuild stop rule missing", errors)

    exp_ledger = read_csv(ROOT / "ledgers/experiments.tsv", delimiter="\t")
    exp_rows = {row["experiment_id"]: row for row in exp_ledger}
    require(exp_rows.get("EXP-20260831-002", {}).get("status") == "quarantine", "EXP-20260831-002 ledger row missing or wrong", errors)
    require(exp_rows.get("EXP-20260831-003", {}).get("status") == "keep", "EXP-20260831-003 ledger row missing or wrong", errors)
    require("EXP-20260831-004" not in exp_rows, "prospective unexecuted experiment should not have a result row", errors)

    change_ledger = read_csv(ROOT / "ledgers/change_requests.tsv", delimiter="\t")
    change_rows = [row for row in change_ledger if row["change_request_id"] == "CR-20260831-001"]
    require(len(change_rows) == 1 and change_rows[0]["status"] == "proposed", "change-request ledger row missing or wrong", errors)

    issues = read_csv(ROOT / "ledgers/reviewer_issues.tsv", delimiter="\t")
    issue_rows = [row for row in issues if row["issue_id"] == "R-011"]
    require(len(issue_rows) == 1 and issue_rows[0]["status"] == "open", "R-011 reviewer issue missing or wrong", errors)

    raw_artifacts = list((ROOT / "experiments/EXP-20260831-002").rglob("*.pdf"))
    raw_artifacts += list((ROOT / "experiments/EXP-20260831-003").rglob("*.pdf"))
    require(not raw_artifacts, "raw PDF committed inside evidence package", errors)

    if args.cache_dir:
        validate_raw_caches(all_manifests, all_excerpts, args.cache_dir, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("validation freeze package: PASS")
    print("evidence gates: 3 resolved under existing rules; 1 rule-required; 0 integrated")
    print("registered frame: 4 open gates across 3 units; random draws: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
