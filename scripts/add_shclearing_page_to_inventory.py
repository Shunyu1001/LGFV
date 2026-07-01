#!/usr/bin/env python3
"""Add a Shanghai Clearing disclosure page to source and document inventories."""

from __future__ import annotations

import argparse
import csv
import html
import pathlib
import re
import sys
import urllib.parse
import urllib.request


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE_INVENTORY = ROOT / "data" / "source_inventory.csv"
DOCUMENT_INVENTORY = ROOT / "data" / "document_inventory.csv"
DOWNLOAD_BASE = "https://www.shclearing.com.cn/wcm/shch/pages/client/download/download.jsp"


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: pathlib.Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def js_var(text: str, name: str) -> str:
    match = re.search(rf'var\s+{re.escape(name)}\s*=\s*"(?P<value>.*?)";', text, re.S)
    return html.unescape(match.group("value")) if match else ""


def page_title_and_date(text: str) -> tuple[str, str]:
    title_candidates = [
        re.sub(r"\s+", "", html.unescape(match))
        for match in re.findall(r"<h3>\s*(.*?)\s*</h3>", text, re.S)
    ]
    informative_titles = [
        title
        for title in title_candidates
        if any(term in title for term in ("发行", "票据", "融资券", "披露", "文件", "材料"))
        and "注册" not in title
    ]
    date_match = re.search(r"<h3>.*?</h3>\s*<p>\s*(?P<date>\d{4}-\d{2}-\d{2})\s*</p>", text, re.S)
    title = max(informative_titles or title_candidates or [""], key=len)
    source_date = date_match.group("date") if date_match else ""
    return title, source_date


def infer_document_type(title: str) -> str:
    if "募集说明书" in title:
        return "prospectus"
    if "法律意见书" in title:
        return "legal_opinion"
    if "评级" in title:
        return "rating_report"
    if "财务报表" in title or "审计报告" in title:
        return "financial_statement"
    if "发行方案" in title:
        return "issuance_plan"
    if "承诺函" in title:
        return "commitment_letter"
    if "申购说明" in title:
        return "subscription_notice"
    return "issuance_disclosure_document"


def make_download_url(file_name: str, down_name: str) -> str:
    p_file = pathlib.PurePosixPath(file_name).name
    return DOWNLOAD_BASE + "?" + urllib.parse.urlencode({"FileName": p_file, "DownName": down_name})


def parse_documents(text: str) -> list[tuple[str, str]]:
    file_names = [item for item in js_var(text, "fileNames").split(";;") if item.strip()]
    desc_names = [item for item in js_var(text, "descNames").split(";;") if item.strip()]
    if not file_names:
        current_file = js_var(text, "currentFile")
        file_name = js_var(text, "fileName")
        if current_file:
            file_names = [current_file]
            desc_names = [file_name or pathlib.PurePosixPath(current_file).name]
    return list(zip(file_names, desc_names))


def append_unique(rows: list[dict[str, str]], new_row: dict[str, str], key: str) -> tuple[list[dict[str, str]], bool]:
    existing = {row.get(key, "") for row in rows}
    if new_row.get(key, "") in existing:
        return rows, False
    return rows + [new_row], True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--doc-prefix", required=True)
    parser.add_argument("--province", required=True)
    parser.add_argument("--city", required=True)
    parser.add_argument("--company-name", required=True)
    parser.add_argument("--page-url", required=True)
    parser.add_argument("--source-type", default="issuance_disclosure")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    text = fetch(args.page_url)
    page_title, page_date = page_title_and_date(text)
    docs = parse_documents(text)
    if not docs:
        raise SystemExit(f"No attached documents found for {args.page_url}")

    source_rows = read_csv(SOURCE_INVENTORY)
    source_fields = list(source_rows[0].keys())
    source_row = {
        "source_id": args.source_id,
        "case_id": args.case_id,
        "province": args.province,
        "city": args.city,
        "company_name": args.company_name,
        "source_type": args.source_type,
        "source_title": f"上海清算所{page_title}" if page_title else f"上海清算所{args.company_name}发行披露文件",
        "source_date": page_date,
        "source_url": args.page_url,
        "local_file_path": "data/document_inventory.csv",
        "language": "Chinese",
        "text_extracted": "partial",
        "usable_for_labeling": "yes",
        "key_terms": "不承担政府融资职能;退出融资平台;基础设施建设;土地整理;代建;政府购买服务;PPP;BT",
        "notes": args.notes or f"Shanghai Clearing disclosure page with {len(docs)} attached documents",
    }
    source_rows, source_added = append_unique(source_rows, source_row, "source_id")
    write_csv(SOURCE_INVENTORY, source_rows, source_fields)

    doc_rows = read_csv(DOCUMENT_INVENTORY)
    doc_fields = list(doc_rows[0].keys())
    added_docs = 0
    for index, (file_name, desc_name) in enumerate(docs, start=1):
        document_id = f"{args.doc_prefix}_{index:03d}"
        local_file = f"data/raw/{args.case_id}/{document_id}.pdf"
        new_row = {
            "document_id": document_id,
            "case_id": args.case_id,
            "source_id": args.source_id,
            "province": args.province,
            "city": args.city,
            "company_name": args.company_name,
            "document_type": infer_document_type(desc_name),
            "document_title": desc_name,
            "document_date": page_date,
            "document_page_url": args.page_url,
            "download_url": make_download_url(file_name, desc_name),
            "local_file_path": local_file,
            "text_extracted": "no",
            "usable_for_labeling": "yes",
            "notes": "",
        }
        doc_rows, added = append_unique(doc_rows, new_row, "document_id")
        added_docs += int(added)
    write_csv(DOCUMENT_INVENTORY, doc_rows, doc_fields)

    print(f"source_added={int(source_added)} documents_found={len(docs)} documents_added={added_docs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
