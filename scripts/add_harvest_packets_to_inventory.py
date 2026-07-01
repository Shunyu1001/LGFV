#!/usr/bin/env python3
"""Add harvested Shanghai Clearing pages to source/document inventories."""

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
DEFAULT_HARVEST = ROOT / "data" / "analysis_inputs" / "shclearing_candidate_harvest_broad_2026_06_30.csv"
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


def compact(text: str) -> str:
    return re.sub(r"\s+", "", html.unescape(text or ""))


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def js_var(text: str, name: str) -> str:
    match = re.search(rf'var\s+{re.escape(name)}\s*=\s*"(?P<value>.*?)";', text, re.S)
    return html.unescape(match.group("value")) if match else ""


def page_title_and_date(text: str) -> tuple[str, str]:
    titles = [compact(match) for match in re.findall(r"<h3>\s*(.*?)\s*</h3>", text, re.S)]
    informative = [
        title
        for title in titles
        if any(term in title for term in ("发行", "票据", "融资券", "披露", "文件", "材料"))
        and "注册" not in title
    ]
    date_match = re.search(r"<h3>.*?</h3>\s*<p>\s*(?P<date>\d{4}-\d{2}-\d{2})\s*</p>", text, re.S)
    return max(informative or titles or [""], key=len), date_match.group("date") if date_match else ""


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


def infer_document_type(title: str) -> str:
    if "募集说明书" in title:
        return "prospectus"
    if "法律意见书" in title:
        return "legal_opinion"
    if "评级" in title:
        return "rating_report"
    if "审计报告" in title:
        return "financial_report"
    if "财务报表" in title:
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


def source_row(candidate: dict[str, str], title: str, source_date: str, doc_count: int) -> dict[str, str]:
    cid = candidate["candidate_id"]
    issuer = candidate["issuer_name"]
    return {
        "source_id": f"src_{cid}",
        "case_id": cid,
        "province": "",
        "city": "",
        "company_name": issuer,
        "source_type": "issuance_disclosure",
        "source_title": f"上海清算所{title}" if title else candidate["announcement_title"],
        "source_date": source_date or candidate["publish_date"],
        "source_url": candidate["source_url"],
        "local_file_path": "data/document_inventory.csv",
        "language": "Chinese",
        "text_extracted": "no",
        "usable_for_labeling": "yes",
        "key_terms": "不承担政府融资职能;退出融资平台;基础设施建设;土地整理;代建;政府购买服务;PPP;BT",
        "notes": f"Harvest candidate priority={candidate['candidate_priority']}; {doc_count} attached documents.",
    }


def document_row(candidate: dict[str, str], source_date: str, index: int, file_name: str, desc_name: str) -> dict[str, str]:
    cid = candidate["candidate_id"]
    document_id = f"doc_{cid}_{index:03d}"
    return {
        "document_id": document_id,
        "case_id": cid,
        "source_id": f"src_{cid}",
        "province": "",
        "city": "",
        "company_name": candidate["issuer_name"],
        "document_type": infer_document_type(desc_name),
        "document_title": desc_name,
        "document_date": source_date or candidate["publish_date"],
        "document_page_url": candidate["source_url"],
        "download_url": make_download_url(file_name, desc_name),
        "local_file_path": f"data/raw/{cid}/{document_id}.pdf",
        "text_extracted": "no",
        "usable_for_labeling": "yes",
        "notes": f"Harvest candidate priority={candidate['candidate_priority']}",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--harvest", type=pathlib.Path, default=DEFAULT_HARVEST)
    parser.add_argument("--priority", choices=["all", "high", "medium"], default="high")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    candidates = [
        row
        for row in read_csv(args.harvest)
        if row.get("needs_source_packet") == "1"
        and row.get("already_human_validated") == "0"
        and row.get("already_in_master_pool") == "0"
    ]
    if args.priority == "high":
        candidates = [row for row in candidates if row.get("candidate_priority") == "high"]
    elif args.priority == "medium":
        candidates = [row for row in candidates if row.get("candidate_priority") in {"high", "medium"}]
    if args.limit:
        candidates = candidates[: args.limit]

    source_rows = read_csv(SOURCE_INVENTORY)
    source_fields = list(source_rows[0].keys())
    doc_rows = read_csv(DOCUMENT_INVENTORY)
    doc_fields = list(doc_rows[0].keys())
    existing_sources = {row["source_id"] for row in source_rows}
    existing_docs = {row["document_id"] for row in doc_rows}

    pages_added = 0
    docs_added = 0
    failures: list[str] = []
    for candidate in candidates:
        try:
            text = fetch(candidate["source_url"])
            title, source_date = page_title_and_date(text)
            docs = parse_documents(text)
            if not docs:
                failures.append(f"{candidate['candidate_id']}: no attached documents")
                continue
            srow = source_row(candidate, title, source_date, len(docs))
            if srow["source_id"] not in existing_sources:
                source_rows.append(srow)
                existing_sources.add(srow["source_id"])
                pages_added += 1
            for index, (file_name, desc_name) in enumerate(docs, start=1):
                drow = document_row(candidate, source_date, index, file_name, desc_name)
                if drow["document_id"] in existing_docs:
                    continue
                doc_rows.append(drow)
                existing_docs.add(drow["document_id"])
                docs_added += 1
        except Exception as exc:
            failures.append(f"{candidate['candidate_id']}: {exc}")

    write_csv(SOURCE_INVENTORY, source_rows, source_fields)
    write_csv(DOCUMENT_INVENTORY, doc_rows, doc_fields)
    print(f"candidate_pages={len(candidates)} pages_added={pages_added} documents_added={docs_added} failures={len(failures)}")
    for item in failures[:20]:
        print(f"failure: {item}")
    return 1 if failures and not docs_added else 0


if __name__ == "__main__":
    sys.exit(main())
