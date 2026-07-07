#!/usr/bin/env python3
"""Build collection templates for contemporary controls."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PANEL = ROOT / "data" / "analysis_inputs" / "empirical_case_panel.csv"
DEFAULT_CITY_CONTROLS = ROOT / "data" / "analysis_inputs" / "contemporary_city_controls.csv"
DEFAULT_SOURCE_BACKED_CONTROLS = (
    ROOT / "data" / "analysis_inputs" / "contemporary_city_controls_source_backed.csv"
)
DEFAULT_PLATFORM_CONTROLS = ROOT / "data" / "analysis_inputs" / "platform_control_coding_queue.csv"
DEFAULT_DOC = ROOT / "docs" / "contemporary_controls.md"

CITY_FIELDS = [
    "control_unit_id",
    "province",
    "control_city",
    "control_city_chn",
    "gadm_gid",
    "raw_cities",
    "case_count",
    "case_ids",
    "platforms",
    "capital_or_subprovincial_city",
    "preferred_control_year",
    "fallback_control_year",
    "gdp_value",
    "gdp_unit",
    "gdp_year",
    "gdp_source",
    "gdp_status",
    "population_value",
    "population_unit",
    "population_year",
    "population_source",
    "population_status",
    "gdp_per_capita_value",
    "gdp_per_capita_year",
    "gdp_per_capita_source",
    "gdp_per_capita_status",
    "general_public_budget_revenue",
    "general_public_budget_revenue_unit",
    "general_public_budget_revenue_year",
    "general_public_budget_revenue_source",
    "general_public_budget_revenue_status",
    "general_public_budget_expenditure",
    "general_public_budget_expenditure_unit",
    "general_public_budget_expenditure_year",
    "general_public_budget_expenditure_source",
    "general_public_budget_expenditure_status",
    "fiscal_self_sufficiency_value",
    "fiscal_self_sufficiency_year",
    "fiscal_self_sufficiency_source",
    "fiscal_self_sufficiency_status",
    "local_government_debt_balance",
    "local_government_debt_balance_unit",
    "local_government_debt_balance_year",
    "local_government_debt_balance_source",
    "local_government_debt_balance_status",
    "debt_pressure_value",
    "debt_pressure_definition",
    "debt_pressure_year",
    "debt_pressure_source",
    "debt_pressure_status",
    "government_fund_revenue",
    "government_fund_revenue_unit",
    "government_fund_revenue_year",
    "government_fund_revenue_source",
    "government_fund_revenue_status",
    "land_conveyance_revenue",
    "land_conveyance_revenue_unit",
    "land_conveyance_revenue_year",
    "land_conveyance_revenue_source",
    "land_conveyance_revenue_status",
    "land_finance_dependence_value",
    "land_finance_dependence_definition",
    "land_finance_dependence_year",
    "land_finance_dependence_source",
    "land_finance_dependence_status",
    "statistical_yearbook_query",
    "budget_final_account_query",
    "debt_query",
    "land_finance_query",
    "notes",
]

PLATFORM_FIELDS = [
    "case_id",
    "province",
    "city",
    "control_city",
    "platform",
    "exit_type",
    "label_source",
    "source_coverage_score",
    "source_doc_types",
    "platform_administrative_level",
    "platform_administrative_level_source",
    "platform_administrative_level_status",
    "platform_scope_notes",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def norm(value: str | None) -> str:
    return (value or "").strip()


def control_city(row: dict[str, str]) -> str:
    return norm(row.get("prefecture_name")) or norm(row.get("city"))


def control_city_chn(row: dict[str, str]) -> str:
    value = norm(row.get("prefecture_name_chn"))
    if "|" in value:
        value = value.split("|", 1)[0]
    return value


def control_unit_id(province: str, city: str) -> str:
    safe = (province + "_" + city).lower()
    for old, new in {
        " ": "_",
        "'": "",
        ".": "",
        "-": "_",
        "(": "",
        ")": "",
        "/": "_",
    }.items():
        safe = safe.replace(old, new)
    return safe


def cn_or_en(row: dict[str, str], en_city: str) -> str:
    return norm(row.get("control_city_chn")) or en_city


def build_city_controls(panel_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    gold_rows = [row for row in panel_rows if row.get("include_in_gold_sample") == "1"]
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in gold_rows:
        key = (norm(row.get("province")), control_city(row))
        grouped[key].append(row)

    rows: list[dict[str, str]] = []
    for (province, city), members in sorted(grouped.items()):
        first = members[0]
        raw_cities = sorted({norm(row.get("city")) for row in members if norm(row.get("city"))})
        case_ids = sorted({norm(row.get("case_id")) for row in members if norm(row.get("case_id"))})
        platforms = sorted({norm(row.get("platform")) for row in members if norm(row.get("platform"))})
        city_chn = control_city_chn(first)
        query_name = city_chn or city
        row = {field: "" for field in CITY_FIELDS}
        row["control_unit_id"] = control_unit_id(province, city)
        row["province"] = province
        row["control_city"] = city
        row["control_city_chn"] = city_chn
        row["gadm_gid"] = norm(first.get("gadm_gid"))
        row["raw_cities"] = "; ".join(raw_cities)
        row["case_count"] = str(len(case_ids))
        row["case_ids"] = "; ".join(case_ids)
        row["platforms"] = "; ".join(platforms)
        row["capital_or_subprovincial_city"] = (
            "1" if any(row.get("capital_or_subprovincial_city") == "1" for row in members) else "0"
        )
        row["preferred_control_year"] = "2024"
        row["fallback_control_year"] = "2023"
        for status_field in [
            "gdp_status",
            "population_status",
            "gdp_per_capita_status",
            "general_public_budget_revenue_status",
            "general_public_budget_expenditure_status",
            "fiscal_self_sufficiency_status",
            "local_government_debt_balance_status",
            "debt_pressure_status",
            "government_fund_revenue_status",
            "land_conveyance_revenue_status",
            "land_finance_dependence_status",
        ]:
            row[status_field] = "to_collect"
        row["debt_pressure_definition"] = "local_government_debt_balance / general_public_budget_revenue"
        row["land_finance_dependence_definition"] = "land_conveyance_revenue / general_public_budget_revenue"
        row["statistical_yearbook_query"] = f"{query_name} 2024 国民经济和社会发展统计公报 GDP 常住人口"
        row["budget_final_account_query"] = f"{query_name} 2024 财政决算 一般公共预算收入 一般公共预算支出"
        row["debt_query"] = f"{query_name} 2024 地方政府债务余额 决算"
        row["land_finance_query"] = f"{query_name} 2024 政府性基金收入 国有土地使用权出让收入 决算"
        row["notes"] = "Collect from official city statistical communique, final accounts, and debt disclosure where possible."
        rows.append(row)
    return rows


def merge_source_backed_controls(
    city_rows: list[dict[str, str]], source_rows: list[dict[str, str]]
) -> list[dict[str, str]]:
    source_by_id = {norm(row.get("control_unit_id")): row for row in source_rows}
    output: list[dict[str, str]] = []
    for row in city_rows:
        source = source_by_id.get(row["control_unit_id"])
        if not source:
            output.append(row)
            continue
        merged = row.copy()
        for field in CITY_FIELDS:
            value = norm(source.get(field))
            if value:
                merged[field] = value
        output.append(merged)
    return output


def infer_platform_level(row: dict[str, str]) -> tuple[str, str]:
    city = norm(row.get("city"))
    control = control_city(row)
    platform = norm(row.get("platform"))
    if any(token in platform for token in ["省", "自治区"]) and not any(
        token in platform for token in ["市", "区", "县", "开发区", "高新"]
    ):
        return "provincial_or_region_level", "rule_based_from_platform_name"
    if city and control and city != control:
        return "district_or_county_level", "rule_based_from_city_prefecture_mismatch"
    if any(token in platform for token in ["区", "县", "高新", "经开", "开发区", "新城", "新区", "知识城", "科学城", "上合", "吴中"]):
        return "district_or_development_zone_level", "rule_based_from_platform_name"
    if any(
        token in platform
        for token in [
            "市",
            "城投",
            "城建",
            "交通",
            "建设",
            "开发投资集团",
            "投资控股集团",
            "产业投资集团",
            "国资",
            "国有资本",
            "国有资产",
            "地铁",
        ]
    ):
        return "prefecture_or_municipal_level", "rule_based_from_platform_name"
    return "", ""


def build_platform_controls(panel_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    gold_rows = [row for row in panel_rows if row.get("include_in_gold_sample") == "1"]
    rows: list[dict[str, str]] = []
    for source in gold_rows:
        level, source_rule = infer_platform_level(source)
        row = {field: "" for field in PLATFORM_FIELDS}
        row["case_id"] = norm(source.get("case_id"))
        row["province"] = norm(source.get("province"))
        row["city"] = norm(source.get("city"))
        row["control_city"] = control_city(source)
        row["platform"] = norm(source.get("platform"))
        row["exit_type"] = norm(source.get("exit_type"))
        row["label_source"] = norm(source.get("label_source"))
        row["source_coverage_score"] = norm(source.get("source_coverage_score"))
        row["source_doc_types"] = norm(source.get("source_doc_types"))
        row["platform_administrative_level"] = level
        row["platform_administrative_level_source"] = source_rule
        row["platform_administrative_level_status"] = (
            "rule_based_pending_human_check" if level else "to_code_from_source_packet"
        )
        row["platform_scope_notes"] = "Review ownership, controller, and business-scope sections in the source packet."
        rows.append(row)
    return rows


def write_doc(path: Path, city_rows: list[dict[str, str]], platform_rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# Contemporary Controls\n\n")
        handle.write("This note documents the control-variable collection files generated by ")
        handle.write("`scripts/build_contemporary_control_queue.py`.\n\n")
        handle.write("## Outputs\n\n")
        handle.write("- `data/analysis_inputs/contemporary_city_controls.csv`\n")
        handle.write("- `data/analysis_inputs/contemporary_city_controls_source_backed.csv`\n")
        handle.write("- `data/analysis_inputs/platform_control_coding_queue.csv`\n\n")
        handle.write("The city-control file currently has ")
        handle.write(str(len(city_rows)))
        handle.write(" control units built from the 94 gold-standard cases. District or county ")
        handle.write("platforms are assigned to their matched prefecture-level control unit when ")
        handle.write("the historical-capacity crosswalk supplies a prefecture match.\n\n")
        handle.write("The platform-control queue currently has ")
        handle.write(str(len(platform_rows)))
        handle.write(" gold-standard case rows. Platform administrative level is pre-coded only ")
        handle.write("when a conservative rule can infer it from the platform name, specialized ")
        handle.write("sector, or from a city-prefecture mismatch. The current rules populate ")
        handle.write(str(sum(1 for row in platform_rows if row.get("platform_administrative_level"))))
        handle.write(" administrative-level pre-codes. These rule-based values remain pending ")
        handle.write("human check.\n\n")
        handle.write("## Control Definitions\n\n")
        handle.write("- Fiscal self-sufficiency: general public budget revenue divided by general public budget expenditure.\n")
        handle.write("- Debt pressure: local government debt balance divided by general public budget revenue.\n")
        handle.write("- Land finance dependence: land conveyance revenue divided by general public budget revenue.\n")
        handle.write("- GDP per capita: GDP divided by resident population, preferably from the same official statistical communique.\n\n")
        handle.write("Preferred year is 2024, with 2023 as fallback. Values should come from official ")
        handle.write("city statistical communiques, budget final accounts, local debt disclosures, ")
        handle.write("or finance-bureau final-account tables. When the first-pass source is a ")
        handle.write("rating-agency compilation of public data, the status field marks it as ")
        handle.write("`source_backed_secondary_compilation` so it can later be replaced by ")
        handle.write("official source tables. The templates include Chinese search queries for ")
        handle.write("each control unit to make source collection reproducible.\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel", type=Path, default=DEFAULT_PANEL)
    parser.add_argument("--city-controls", type=Path, default=DEFAULT_CITY_CONTROLS)
    parser.add_argument("--source-backed-controls", type=Path, default=DEFAULT_SOURCE_BACKED_CONTROLS)
    parser.add_argument("--platform-controls", type=Path, default=DEFAULT_PLATFORM_CONTROLS)
    parser.add_argument("--doc", type=Path, default=DEFAULT_DOC)
    args = parser.parse_args()

    panel_rows = read_csv(args.panel)
    city_rows = build_city_controls(panel_rows)
    if args.source_backed_controls.exists():
        city_rows = merge_source_backed_controls(city_rows, read_csv(args.source_backed_controls))
    platform_rows = build_platform_controls(panel_rows)
    write_csv(args.city_controls, city_rows, CITY_FIELDS)
    write_csv(args.platform_controls, platform_rows, PLATFORM_FIELDS)
    write_doc(args.doc, city_rows, platform_rows)
    coded_platform = sum(1 for row in platform_rows if row["platform_administrative_level"])
    print(f"city_control_units={len(city_rows)}")
    print(f"platform_control_rows={len(platform_rows)}")
    print(f"rule_based_platform_levels={coded_platform}")
    print(f"city_controls={args.city_controls}")
    print(f"platform_controls={args.platform_controls}")
    print(f"doc={args.doc}")


if __name__ == "__main__":
    main()
