#!/usr/bin/env python3
"""Harvest a seed pool of LGFV candidate disclosures from Shanghai Clearing.

The output is a source-discovery file, not a validated dataset. Each row is a
public announcement page that can later be turned into a source packet and sent
through the LLM-assisted labeling workflow.
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import re
import sys
from datetime import date

from search_shclearing_pages import CATEGORIES, iter_items


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    ROOT / "data" / "analysis_inputs" / f"shclearing_candidate_harvest_{date.today():%Y_%m_%d}.csv"
)

DEFAULT_TERMS = [
    "城市建设投资",
    "城市发展投资",
    "城市开发投资",
    "开发建设投资",
    "城乡建设投资",
    "建设投资",
    "基础设施投资",
    "交通投资",
    "产业投资",
    "国有资本投资",
    "投资控股",
    "城市运营",
]

HIGH_SIGNAL_PATTERNS = [
    "城市建设投资",
    "城市发展投资",
    "城市开发投资",
    "开发建设投资",
    "城乡建设投资",
    "城建投资",
    "城市投资",
    "基础设施投资",
]

MEDIUM_SIGNAL_PATTERNS = [
    "国有资本投资",
    "交通投资",
    "产业投资",
    "投资控股",
    "资产投资",
    "城市运营",
]

NOISE_PATTERNS = [
    ("subscription_notice", "申购说明"),
    ("correction", "更正"),
    ("withdrawal", "撤标"),
    ("rate_adjustment", "利率调整"),
    ("repayment_notice", "兑付"),
]


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def compact(text: str) -> str:
    return re.sub(r"\s+", "", text or "")


def infer_issuer(title: str) -> str:
    title = compact(title)
    title = re.sub(r"^关于", "", title)
    title = re.sub(r"_20\d{9,}.*$", "", title)
    match = re.search(r"20\d{2}年度", title)
    if match:
        return title[: match.start()]
    match = re.search(r"第[一二三四五六七八九十]+期", title)
    if match:
        return title[: match.start()]
    for marker in ("发行文件", "发行材料", "发行披露文件", "募集说明书", "申购说明"):
        if marker in title:
            return title.split(marker, 1)[0]
    return title


def announcement_type(title: str) -> tuple[str, str]:
    title = compact(title)
    for label, pattern in NOISE_PATTERNS:
        if pattern in title:
            return label, pattern
    if any(pattern in title for pattern in ("发行文件", "发行材料", "发行披露文件", "募集说明书")):
        return "issuance_packet", ""
    if "评级" in title:
        return "rating_report", ""
    return "other", ""


def instrument_type(category: str, title: str) -> str:
    if "中期票据" in title:
        return "mtn"
    if "超短期融资券" in title:
        return "scp"
    if "短期融资券" in title:
        return "cp"
    if "定向债务融资工具" in title:
        return "ppn"
    return category


def signal_strength(issuer: str) -> tuple[str, str]:
    issuer = compact(issuer)
    high_hits = [pattern for pattern in HIGH_SIGNAL_PATTERNS if pattern in issuer]
    if high_hits:
        return "high", ";".join(high_hits)
    medium_hits = [pattern for pattern in MEDIUM_SIGNAL_PATTERNS if pattern in issuer]
    if medium_hits:
        return "medium", ";".join(medium_hits)
    return "low", ""


def known_names() -> tuple[set[str], set[str]]:
    validated = {compact(row.get("company_name", "")) for row in read_csv(ROOT / "data" / "processed" / "human_validated_labels.csv")}
    master = {
        compact(row.get("company_name", "") or row.get("platform", ""))
        for row in read_csv(ROOT / "data" / "analysis_inputs" / "master_case_pool.csv")
    }
    return {name for name in validated if name}, {name for name in master if name}


def row_id(prefix: str, index: int) -> str:
    return f"{prefix}_{index:04d}"


def build_rows(args: argparse.Namespace) -> list[dict[str, str]]:
    categories = [item.strip() for item in args.categories.split(",") if item.strip()]
    terms = [item.strip() for item in args.terms if item.strip()]
    validated_names, master_names = known_names()

    seen: set[tuple[str, str, str]] = set()
    rows: list[dict[str, str]] = []
    for category in categories:
        for category_name, publish_date, title, url in iter_items(
            category, args.pages, args.sleep, args.timeout
        ):
            hits = [term for term in terms if term in title]
            if not hits:
                continue
            issuer = infer_issuer(title)
            ann_type, noise_reason = announcement_type(title)
            priority, signals = signal_strength(issuer)
            key = (issuer, title, url)
            if key in seen:
                continue
            seen.add(key)
            is_packet = "1" if ann_type == "issuance_packet" else "0"
            is_noise = "1" if noise_reason else "0"
            clean_issuer = compact(issuer)
            rows.append(
                {
                    "candidate_id": row_id(args.id_prefix, len(rows) + 1),
                    "harvest_date": f"{date.today():%Y-%m-%d}",
                    "source": "Shanghai Clearing House",
                    "search_terms": ";".join(hits),
                    "category": category_name,
                    "publish_date": publish_date,
                    "issuer_name": issuer,
                    "announcement_title": title,
                    "announcement_type": ann_type,
                    "instrument_type": instrument_type(category_name, title),
                    "source_url": url,
                    "is_issuance_packet": is_packet,
                    "is_noise": is_noise,
                    "noise_reason": noise_reason,
                    "lgfv_name_signal": signals,
                    "candidate_priority": priority,
                    "already_human_validated": "1" if clean_issuer in validated_names else "0",
                    "already_in_master_pool": "1" if clean_issuer in master_names else "0",
                    "llm_label_status": "pending",
                    "llm_label": "",
                    "llm_confidence": "",
                    "needs_source_packet": "1" if is_packet == "1" and is_noise == "0" else "0",
                    "notes": "",
                }
            )
    if args.only_issuance_packets:
        rows = [row for row in rows if row["is_issuance_packet"] == "1"]
    if args.drop_noise:
        rows = [row for row in rows if row["is_noise"] == "0"]
    if args.exclude_known:
        rows = [
            row
            for row in rows
            if row["already_human_validated"] == "0" and row["already_in_master_pool"] == "0"
        ]
    for index, row in enumerate(rows, start=1):
        row["candidate_id"] = row_id(args.id_prefix, index)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("terms", nargs="*", default=DEFAULT_TERMS)
    parser.add_argument("--categories", default=",".join(CATEGORIES))
    parser.add_argument("--pages", type=int, default=70)
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument("--timeout", type=float, default=8.0)
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--id-prefix", default=f"sch_{date.today():%Y%m%d}")
    parser.add_argument("--only-issuance-packets", action="store_true")
    parser.add_argument("--drop-noise", action="store_true")
    parser.add_argument("--exclude-known", action="store_true")
    args = parser.parse_args()

    rows = build_rows(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {args.output}")
    if rows:
        ready = sum(1 for row in rows if row["needs_source_packet"] == "1")
        high = sum(1 for row in rows if row["candidate_priority"] == "high")
        known = sum(1 for row in rows if row["already_human_validated"] == "1")
        print(f"issuance_packet_candidates={ready} high_priority={high} already_validated={known}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
