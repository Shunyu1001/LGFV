#!/usr/bin/env python3
"""Build the next validation target queue.

The output is a search queue rather than a validated dataset. Existing pilot
cases are carried forward from the historical-capacity candidate file, and
additional city-platform targets are added to push the queue above 50 cases.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "analysis_inputs" / "candidate_city_historical_capacity.csv"
OUTPUT = ROOT / "data" / "analysis_inputs" / "validation_expansion_targets.csv"


FIELDNAMES = [
    "target_id",
    "priority",
    "province",
    "city",
    "target_platform",
    "platform_status",
    "selection_stratum",
    "historical_capacity_bin",
    "debt_pressure_target",
    "land_finance_target",
    "source_search_status",
    "next_search_terms",
    "notes",
]


ADDITIONAL_TARGETS = [
    {
        "target_id": "expand_ah_hefei_jiantou",
        "priority": "2",
        "province": "Anhui",
        "city": "Hefei",
        "target_platform": "合肥市建设投资控股(集团)有限公司",
        "platform_status": "needs_confirmation",
        "selection_stratum": "additional_provincial_capital",
        "historical_capacity_bin": "to_merge",
        "debt_pressure_target": "medium",
        "land_finance_target": "to_collect",
    },
    {
        "target_id": "expand_ah_wuhu_jiantou",
        "priority": "3",
        "province": "Anhui",
        "city": "Wuhu",
        "target_platform": "芜湖市建设投资有限公司",
        "platform_status": "needs_confirmation",
        "selection_stratum": "additional_prefecture_case",
        "historical_capacity_bin": "to_merge",
        "debt_pressure_target": "medium",
        "land_finance_target": "to_collect",
    },
    {
        "target_id": "expand_hb_wuhan_chengtou",
        "priority": "2",
        "province": "Hubei",
        "city": "Wuhan",
        "target_platform": "武汉市城市建设投资开发集团有限公司",
        "platform_status": "needs_confirmation",
        "selection_stratum": "additional_provincial_capital",
        "historical_capacity_bin": "to_merge",
        "debt_pressure_target": "medium",
        "land_finance_target": "to_collect",
    },
    {
        "target_id": "expand_hb_yichang_chengtou",
        "priority": "3",
        "province": "Hubei",
        "city": "Yichang",
        "target_platform": "宜昌城市发展投资集团有限公司",
        "platform_status": "needs_confirmation",
        "selection_stratum": "additional_prefecture_case",
        "historical_capacity_bin": "to_merge",
        "debt_pressure_target": "medium",
        "land_finance_target": "to_collect",
    },
    {
        "target_id": "expand_hen_zhengzhou_chengfa",
        "priority": "2",
        "province": "Henan",
        "city": "Zhengzhou",
        "target_platform": "郑州发展投资集团有限公司",
        "platform_status": "needs_confirmation",
        "selection_stratum": "additional_provincial_capital",
        "historical_capacity_bin": "to_merge",
        "debt_pressure_target": "medium",
        "land_finance_target": "to_collect",
    },
    {
        "target_id": "expand_hen_luoyang_chengtou",
        "priority": "3",
        "province": "Henan",
        "city": "Luoyang",
        "target_platform": "洛阳城市发展投资集团有限公司",
        "platform_status": "needs_confirmation",
        "selection_stratum": "additional_prefecture_case",
        "historical_capacity_bin": "to_merge",
        "debt_pressure_target": "medium",
        "land_finance_target": "to_collect",
    },
    {
        "target_id": "expand_fj_fuzhou_chengtou",
        "priority": "2",
        "province": "Fujian",
        "city": "Fuzhou",
        "target_platform": "福州城市建设投资集团有限公司",
        "platform_status": "needs_confirmation",
        "selection_stratum": "additional_coastal_capital",
        "historical_capacity_bin": "to_merge",
        "debt_pressure_target": "low",
        "land_finance_target": "to_collect",
    },
    {
        "target_id": "expand_fj_xiamen_luqiao",
        "priority": "3",
        "province": "Fujian",
        "city": "Xiamen",
        "target_platform": "厦门路桥建设集团有限公司",
        "platform_status": "needs_confirmation",
        "selection_stratum": "additional_coastal_city",
        "historical_capacity_bin": "to_merge",
        "debt_pressure_target": "low",
        "land_finance_target": "to_collect",
    },
    {
        "target_id": "expand_gx_nanning_chengtou",
        "priority": "2",
        "province": "Guangxi",
        "city": "Nanning",
        "target_platform": "南宁城市建设投资集团有限责任公司",
        "platform_status": "needs_confirmation",
        "selection_stratum": "additional_western_capital",
        "historical_capacity_bin": "to_merge",
        "debt_pressure_target": "medium",
        "land_finance_target": "to_collect",
    },
    {
        "target_id": "expand_gx_liuzhou_chengtou",
        "priority": "3",
        "province": "Guangxi",
        "city": "Liuzhou",
        "target_platform": "广西柳州市城市建设投资发展集团有限公司",
        "platform_status": "needs_confirmation",
        "selection_stratum": "additional_prefecture_case",
        "historical_capacity_bin": "to_merge",
        "debt_pressure_target": "medium",
        "land_finance_target": "to_collect",
    },
    {
        "target_id": "expand_jx_nanchang_chengtou",
        "priority": "2",
        "province": "Jiangxi",
        "city": "Nanchang",
        "target_platform": "南昌城市建设投资发展有限公司",
        "platform_status": "needs_confirmation",
        "selection_stratum": "additional_provincial_capital",
        "historical_capacity_bin": "to_merge",
        "debt_pressure_target": "medium",
        "land_finance_target": "to_collect",
    },
    {
        "target_id": "expand_jx_ganzhou_chengtou",
        "priority": "3",
        "province": "Jiangxi",
        "city": "Ganzhou",
        "target_platform": "赣州城市开发投资集团有限责任公司",
        "platform_status": "needs_confirmation",
        "selection_stratum": "additional_prefecture_case",
        "historical_capacity_bin": "to_merge",
        "debt_pressure_target": "medium",
        "land_finance_target": "to_collect",
    },
    {
        "target_id": "expand_sx_taiyuan_longcheng",
        "priority": "3",
        "province": "Shanxi",
        "city": "Taiyuan",
        "target_platform": "太原市龙城发展投资集团有限公司",
        "platform_status": "needs_confirmation",
        "selection_stratum": "additional_northern_capital",
        "historical_capacity_bin": "to_merge",
        "debt_pressure_target": "medium",
        "land_finance_target": "to_collect",
    },
    {
        "target_id": "expand_sx_datong_jiantou",
        "priority": "3",
        "province": "Shanxi",
        "city": "Datong",
        "target_platform": "大同市经济建设投资集团有限责任公司",
        "platform_status": "needs_confirmation",
        "selection_stratum": "additional_resource_city",
        "historical_capacity_bin": "to_merge",
        "debt_pressure_target": "medium",
        "land_finance_target": "to_collect",
    },
    {
        "target_id": "expand_ln_shenyang_chengjian",
        "priority": "3",
        "province": "Liaoning",
        "city": "Shenyang",
        "target_platform": "沈阳城市建设发展集团有限公司",
        "platform_status": "needs_confirmation",
        "selection_stratum": "additional_northeast_capital",
        "historical_capacity_bin": "to_merge",
        "debt_pressure_target": "medium",
        "land_finance_target": "to_collect",
    },
    {
        "target_id": "expand_ln_dalian_chengtou",
        "priority": "3",
        "province": "Liaoning",
        "city": "Dalian",
        "target_platform": "大连市城市建设投资集团有限公司",
        "platform_status": "needs_confirmation",
        "selection_stratum": "additional_coastal_city",
        "historical_capacity_bin": "to_merge",
        "debt_pressure_target": "medium",
        "land_finance_target": "to_collect",
    },
    {
        "target_id": "expand_heb_shijiazhuang_chengfa",
        "priority": "3",
        "province": "Hebei",
        "city": "Shijiazhuang",
        "target_platform": "石家庄国控城市发展投资集团有限责任公司",
        "platform_status": "needs_confirmation",
        "selection_stratum": "additional_northern_capital",
        "historical_capacity_bin": "to_merge",
        "debt_pressure_target": "medium",
        "land_finance_target": "to_collect",
    },
    {
        "target_id": "expand_heb_tangshan_chengtou",
        "priority": "3",
        "province": "Hebei",
        "city": "Tangshan",
        "target_platform": "唐山市城市建设投资集团有限公司",
        "platform_status": "needs_confirmation",
        "selection_stratum": "additional_industrial_city",
        "historical_capacity_bin": "to_merge",
        "debt_pressure_target": "medium",
        "land_finance_target": "to_collect",
    },
    {
        "target_id": "expand_hlj_harbin_hatou",
        "priority": "3",
        "province": "Heilongjiang",
        "city": "Harbin",
        "target_platform": "哈尔滨投资集团有限责任公司",
        "platform_status": "needs_confirmation",
        "selection_stratum": "additional_northeast_capital",
        "historical_capacity_bin": "to_merge",
        "debt_pressure_target": "medium",
        "land_finance_target": "to_collect",
    },
    {
        "target_id": "expand_jl_changchun_chengfa",
        "priority": "3",
        "province": "Jilin",
        "city": "Changchun",
        "target_platform": "长春城市开发(集团)有限公司",
        "platform_status": "needs_confirmation",
        "selection_stratum": "additional_northeast_capital",
        "historical_capacity_bin": "to_merge",
        "debt_pressure_target": "medium",
        "land_finance_target": "to_collect",
    },
]


def search_terms(city: str, platform: str) -> str:
    if platform:
        return (
            f"{platform} 退出融资平台 | {platform} 不承担政府融资职能 | "
            f"{platform} 募集说明书 | {platform} 跟踪评级报告"
        )
    return (
        f"{city} 城投 | {city} 城市建设投资 | {city} 融资平台退出 | "
        f"{city} 市场化转型"
    )


def platform_status(row: dict[str, str]) -> str:
    platform = row.get("target_platform", "").strip()
    evidence_status = row.get("evidence_status", "").strip()
    if not platform:
        return "to_identify"
    if evidence_status in {"documents_found", "source_started"}:
        return "documented_candidate"
    return "needs_confirmation"


def build_existing_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with INPUT.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            platform = row.get("target_platform", "").strip()
            city = row["city"].strip()
            city_search_name = (
                row.get("capacity_prefecture_name_chn", "").split("|")[0].strip()
                or city
            )
            rows.append(
                {
                    "target_id": row["case_id"],
                    "priority": row["priority"],
                    "province": row["province"],
                    "city": city,
                    "target_platform": platform,
                    "platform_status": platform_status(row),
                    "selection_stratum": row["selection_stratum"],
                    "historical_capacity_bin": row["historical_capacity_bin"],
                    "debt_pressure_target": (
                        "high"
                        if row["selection_stratum"] == "debt_pressure_inland"
                        else "to_collect"
                    ),
                    "land_finance_target": "to_collect",
                    "source_search_status": row["collection_status"],
                    "next_search_terms": search_terms(city_search_name, platform),
                    "notes": row["next_collection_priority"],
                }
            )
    return rows


def build_additional_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in ADDITIONAL_TARGETS:
        platform = row["target_platform"]
        rows.append(
            {
                **row,
                "source_search_status": "not_started",
                "next_search_terms": search_terms(row["city"], platform),
                "notes": "additional_target_for_50_case_expansion",
            }
        )
    return rows


def main() -> None:
    rows = build_existing_rows() + build_additional_rows()
    seen: set[str] = set()
    unique_rows: list[dict[str, str]] = []
    for row in rows:
        if row["target_id"] in seen:
            raise ValueError(f"Duplicate target_id: {row['target_id']}")
        seen.add(row["target_id"])
        unique_rows.append(row)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(unique_rows)

    print(f"Wrote {len(unique_rows)} targets to {OUTPUT}")


if __name__ == "__main__":
    main()
