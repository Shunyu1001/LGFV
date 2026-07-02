#!/usr/bin/env python3
"""Extract text from downloaded PDF documents.

The output is written under data/processed, which is ignored by git. The script
prints a compact extraction report that can be copied into collection notes.
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import sys


def default_path(row: dict[str, str]) -> pathlib.Path:
    return pathlib.Path("data/raw") / row["case_id"] / f"{row['document_id']}.pdf"


def pending_case_ids(path: str) -> set[str]:
    if not path:
        return set()
    with open(path, newline="", encoding="utf-8") as handle:
        return {
            row["source_row_id"]
            for row in csv.DictReader(handle)
            if row.get("llm_label_status") == "pending"
        }


def extract_with_pypdf(pdf_path: pathlib.Path, max_pages: int) -> tuple[int, str]:
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    parts = []
    pages = reader.pages
    if max_pages:
        pages = pages[:max_pages]
    for index, page in enumerate(pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            parts.append(f"\n\n--- page {index} ---\n{text}")
    return len(reader.pages), "".join(parts).strip()


def extract_with_fitz(pdf_path: pathlib.Path, max_pages: int) -> tuple[int, str]:
    import fitz

    doc = fitz.open(str(pdf_path))
    parts = []
    limit = min(max_pages, doc.page_count) if max_pages else doc.page_count
    for index in range(limit):
        text = doc[index].get_text("text") or ""
        if text.strip():
            parts.append(f"\n\n--- page {index + 1} ---\n{text}")
    return doc.page_count, "".join(parts).strip()


def extract_pdf(pdf_path: pathlib.Path, backend: str, max_pages: int) -> tuple[int, str]:
    if backend == "pypdf":
        return extract_with_pypdf(pdf_path, max_pages)
    if backend == "fitz":
        return extract_with_fitz(pdf_path, max_pages)
    try:
        return extract_with_pypdf(pdf_path, max_pages)
    except ModuleNotFoundError:
        return extract_with_fitz(pdf_path, max_pages)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", default="data/document_inventory.csv")
    parser.add_argument("--case-id", default="")
    parser.add_argument("--pending-seed", default="")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--key-docs-only", action="store_true")
    parser.add_argument("--max-pages", type=int, default=0)
    parser.add_argument("--backend", choices=["auto", "pypdf", "fitz"], default="auto")
    args = parser.parse_args()

    with open(args.inventory, newline="") as f:
        rows = list(csv.DictReader(f))

    pending = pending_case_ids(args.pending_seed)
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(["document_id", "pages", "chars", "status"])
    for row in rows:
        if args.case_id and row["case_id"] != args.case_id:
            continue
        if pending and row["case_id"] not in pending:
            continue
        if args.key_docs_only and row.get("document_type", "") not in {
            "prospectus",
            "legal_opinion",
            "rating_report",
            "issuance_disclosure_document",
        }:
            continue
        local = row.get("local_file_path", "")
        pdf_path = pathlib.Path(local) if local else default_path(row)
        if not pdf_path.exists():
            writer.writerow([row["document_id"], 0, 0, "missing_pdf"])
            sys.stdout.flush()
            continue

        out_dir = pathlib.Path("data/processed") / row["case_id"]
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{row['document_id']}.txt"
        if args.skip_existing and out_path.exists() and out_path.stat().st_size > 200:
            writer.writerow([row["document_id"], 0, out_path.stat().st_size, "skip_existing"])
            sys.stdout.flush()
            continue

        try:
            pages, output = extract_pdf(pdf_path, args.backend, args.max_pages)
            out_path.write_text(output, encoding="utf-8")
            status = "ok" if output else "no_text"
            writer.writerow([row["document_id"], pages, len(output), status])
            sys.stdout.flush()
        except Exception as exc:
            message = " ".join(str(exc).split())
            writer.writerow([row["document_id"], 0, 0, f"error:{message}"])
            sys.stdout.flush()

    return 0


if __name__ == "__main__":
    sys.exit(main())
