#!/usr/bin/env python3
"""Build the case-level empirical panel for the LGFV paper."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GOLD = ROOT / "data" / "processed" / "human_validated_labels.csv"
DEFAULT_MASTER = ROOT / "data" / "analysis_inputs" / "master_case_pool.csv"
DEFAULT_CAPACITY = ROOT / "data" / "analysis_inputs" / "pilot_case_historical_capacity.csv"
DEFAULT_SURROGATE = ROOT / "data" / "analysis_inputs" / "issuer_level_surrogate_empirical_input.csv"
DEFAULT_CITY_CONTROLS = ROOT / "data" / "analysis_inputs" / "contemporary_city_controls.csv"
DEFAULT_PLATFORM_CONTROLS = ROOT / "data" / "analysis_inputs" / "platform_control_coding_queue.csv"
DEFAULT_PANEL = ROOT / "data" / "analysis_inputs" / "empirical_case_panel.csv"
DEFAULT_COVERAGE = ROOT / "data" / "analysis_inputs" / "empirical_case_panel_coverage.csv"
DEFAULT_COVERAGE_TEX = ROOT / "paper" / "tables" / "empirical_case_panel_coverage.tex"

CAPITAL_OR_SUBPROVINCIAL = {
    "Beijing",
    "Changchun",
    "Chengdu",
    "Chongqing",
    "Dalian",
    "Guangzhou",
    "Hangzhou",
    "Harbin",
    "Jinan",
    "Nanjing",
    "Ningbo",
    "Qingdao",
    "Shanghai",
    "Shenyang",
    "Shenzhen",
    "Wuhan",
    "Xiamen",
    "Xian",
}

PANEL_FIELDS = [
    "panel_id",
    "case_id",
    "analytic_role",
    "include_in_gold_sample",
    "include_in_historical_capacity_sample",
    "include_in_adjusted_descriptive_sample",
    "include_in_current_validated_model_sample",
    "include_in_full_controls_regression_sample",
    "label_source",
    "exit_type",
    "institutional_change",
    "substantive_exit",
    "nominal_exit",
    "functional_transfer",
    "liquidation",
    "confidence",
    "province",
    "city",
    "control_city",
    "control_unit_id",
    "platform",
    "company_name",
    "capital_or_subprovincial_city",
    "province_fixed_effect",
    "historical_capacity_bin",
    "historical_capacity_label",
    "elite_density_percentile",
    "elite_per_1000_sqkm",
    "jinshi_per_1000_sqkm",
    "juren_per_1000_sqkm",
    "gadm_gid",
    "prefecture_name",
    "prefecture_name_chn",
    "source_coverage_score",
    "continued_function_evidence_score",
    "source_doc_count",
    "source_doc_types",
    "bond_disclosure_quality_status",
    "contemporary_fiscal_capacity_value",
    "contemporary_fiscal_capacity_year",
    "contemporary_fiscal_capacity_source",
    "contemporary_fiscal_capacity_status",
    "gdp_per_capita_value",
    "gdp_per_capita_year",
    "gdp_per_capita_source",
    "gdp_per_capita_status",
    "fiscal_self_sufficiency_value",
    "fiscal_self_sufficiency_year",
    "fiscal_self_sufficiency_source",
    "fiscal_self_sufficiency_status",
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
    "platform_administrative_level",
    "platform_administrative_level_source",
    "platform_administrative_level_status",
    "surrogate_source_row_ids",
    "surrogate_gold_overlap",
    "surrogate_gold_case_id",
    "surrogate_rows",
    "notes",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_csv_if_exists(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    return read_csv(path)


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def tex_escape(value: object) -> str:
    text = "" if value is None else str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def norm(value: str | None) -> str:
    return (value or "").strip()


def is_true(value: str | None) -> bool:
    return norm(value).lower() in {"1", "true", "yes"}


def binary_outcomes(exit_type: str) -> dict[str, str]:
    return {
        "institutional_change": "1" if exit_type in {"substantive_exit", "functional_transfer"} else "0",
        "substantive_exit": "1" if exit_type == "substantive_exit" else "0",
        "nominal_exit": "1" if exit_type == "nominal_exit" else "0",
        "functional_transfer": "1" if exit_type == "functional_transfer" else "0",
        "liquidation": "1" if exit_type == "liquidation" else "0",
    }


def blank_panel_row() -> dict[str, str]:
    return {field: "" for field in PANEL_FIELDS}


def index_by(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {norm(row.get(key)): row for row in rows if norm(row.get(key))}


def control_city_from_panel_row(row: dict[str, str]) -> str:
    return norm(row.get("prefecture_name")) or norm(row.get("city"))


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


def merge_historical(row: dict[str, str], capacity: dict[str, str]) -> None:
    row["gadm_gid"] = norm(capacity.get("gadm_gid"))
    row["prefecture_name"] = norm(capacity.get("prefecture_name"))
    row["prefecture_name_chn"] = norm(capacity.get("prefecture_name_chn"))
    row["elite_per_1000_sqkm"] = norm(capacity.get("elite_per_1000_sqkm"))
    row["jinshi_per_1000_sqkm"] = norm(capacity.get("jinshi_per_1000_sqkm"))
    row["juren_per_1000_sqkm"] = norm(capacity.get("juren_per_1000_sqkm"))


def merge_master(row: dict[str, str], master: dict[str, str]) -> None:
    for field in [
        "historical_capacity_bin",
        "historical_capacity_label",
        "elite_density_percentile",
        "elite_per_1000_sqkm",
        "jinshi_per_1000_sqkm",
        "juren_per_1000_sqkm",
        "gadm_gid",
        "prefecture_name",
        "prefecture_name_chn",
        "source_doc_count",
        "source_doc_types",
        "continued_function_evidence_score",
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
    ]:
        if norm(master.get(field)):
            row[field] = norm(master.get(field))


def merge_city_controls(row: dict[str, str], city_controls: dict[str, dict[str, str]]) -> None:
    control_id = row.get("control_unit_id")
    controls = city_controls.get(control_id, {})
    if not controls:
        return
    row["gdp_per_capita_value"] = norm(controls.get("gdp_per_capita_value"))
    row["gdp_per_capita_year"] = norm(controls.get("gdp_per_capita_year"))
    row["gdp_per_capita_source"] = norm(controls.get("gdp_per_capita_source"))
    row["gdp_per_capita_status"] = norm(controls.get("gdp_per_capita_status")) or row["gdp_per_capita_status"]
    row["fiscal_self_sufficiency_value"] = norm(controls.get("fiscal_self_sufficiency_value"))
    row["fiscal_self_sufficiency_year"] = norm(controls.get("fiscal_self_sufficiency_year"))
    row["fiscal_self_sufficiency_source"] = norm(controls.get("fiscal_self_sufficiency_source"))
    row["fiscal_self_sufficiency_status"] = (
        norm(controls.get("fiscal_self_sufficiency_status")) or row["fiscal_self_sufficiency_status"]
    )
    row["contemporary_fiscal_capacity_value"] = row["fiscal_self_sufficiency_value"]
    row["contemporary_fiscal_capacity_year"] = row["fiscal_self_sufficiency_year"]
    row["contemporary_fiscal_capacity_source"] = row["fiscal_self_sufficiency_source"]
    row["contemporary_fiscal_capacity_status"] = row["fiscal_self_sufficiency_status"]
    row["debt_pressure_value"] = norm(controls.get("debt_pressure_value"))
    row["debt_pressure_year"] = norm(controls.get("debt_pressure_year"))
    row["debt_pressure_source"] = norm(controls.get("debt_pressure_source"))
    row["debt_pressure_status"] = norm(controls.get("debt_pressure_status")) or row["debt_pressure_status"]
    row["land_finance_dependence_value"] = norm(controls.get("land_finance_dependence_value"))
    row["land_finance_dependence_year"] = norm(controls.get("land_finance_dependence_year"))
    row["land_finance_dependence_source"] = norm(controls.get("land_finance_dependence_source"))
    row["land_finance_dependence_status"] = (
        norm(controls.get("land_finance_dependence_status")) or row["land_finance_dependence_status"]
    )


def merge_platform_controls(row: dict[str, str], platform_controls: dict[str, dict[str, str]]) -> None:
    controls = platform_controls.get(row.get("case_id"), {})
    if not controls:
        return
    for field in [
        "platform_administrative_level",
        "platform_administrative_level_source",
        "platform_administrative_level_status",
    ]:
        if norm(controls.get(field)):
            row[field] = norm(controls.get(field))


def source_quality_status(row: dict[str, str]) -> str:
    score = norm(row.get("source_coverage_score"))
    if not score:
        return "missing"
    try:
        numeric = int(float(score))
    except ValueError:
        return "review"
    if numeric >= 3:
        return "multi-source original or near-original packet"
    if numeric == 2:
        return "limited but usable packet"
    if numeric == 1:
        return "partial packet"
    return "missing or unusable packet"


def default_control_status(row: dict[str, str]) -> None:
    if not row["contemporary_fiscal_capacity_status"]:
        row["contemporary_fiscal_capacity_status"] = "to_collect"
    if not row["gdp_per_capita_status"]:
        row["gdp_per_capita_status"] = "to_collect"
    if not row["fiscal_self_sufficiency_status"]:
        row["fiscal_self_sufficiency_status"] = "to_collect"
    if not row["debt_pressure_status"]:
        row["debt_pressure_status"] = "to_collect"
    if not row["land_finance_dependence_status"]:
        row["land_finance_dependence_status"] = "to_collect"
    if not row["platform_administrative_level_status"]:
        row["platform_administrative_level_status"] = "to_code_from_source_packet"
    row["bond_disclosure_quality_status"] = source_quality_status(row)


def build_gold_rows(
    gold: list[dict[str, str]],
    master_by_case: dict[str, dict[str, str]],
    capacity_by_case: dict[str, dict[str, str]],
    city_controls: dict[str, dict[str, str]],
    platform_controls: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index, source in enumerate(gold, start=1):
        case_id = norm(source.get("case_id"))
        exit_type = norm(source.get("final_label"))
        row = blank_panel_row()
        row["panel_id"] = f"gold_{index:04d}"
        row["case_id"] = case_id
        row["analytic_role"] = "gold_outcome"
        row["include_in_gold_sample"] = "1"
        row["include_in_adjusted_descriptive_sample"] = "1"
        row["label_source"] = "human_gold_standard"
        row["exit_type"] = exit_type
        row.update(binary_outcomes(exit_type))
        row["confidence"] = norm(source.get("final_confidence"))
        row["province"] = norm(source.get("province"))
        row["city"] = norm(source.get("city"))
        row["platform"] = norm(source.get("company_name"))
        row["company_name"] = norm(source.get("company_name"))
        row["source_coverage_score"] = norm(source.get("source_coverage_score"))
        row["province_fixed_effect"] = row["province"]
        row["capital_or_subprovincial_city"] = "1" if row["city"] in CAPITAL_OR_SUBPROVINCIAL else "0"
        row["notes"] = norm(source.get("notes"))
        if case_id in master_by_case:
            merge_master(row, master_by_case[case_id])
        if case_id in capacity_by_case:
            merge_historical(row, capacity_by_case[case_id])
        row["control_city"] = control_city_from_panel_row(row)
        row["control_unit_id"] = control_unit_id(row["province"], row["control_city"])
        default_control_status(row)
        merge_city_controls(row, city_controls)
        merge_platform_controls(row, platform_controls)
        row["include_in_historical_capacity_sample"] = "1" if row["elite_per_1000_sqkm"] else "0"
        row["include_in_current_validated_model_sample"] = (
            "1" if row["include_in_historical_capacity_sample"] == "1" else "0"
        )
        row["include_in_full_controls_regression_sample"] = (
            "1"
            if row["include_in_current_validated_model_sample"] == "1"
            and row["fiscal_self_sufficiency_value"]
            and row["debt_pressure_value"]
            and row["land_finance_dependence_value"]
            and row["platform_administrative_level"]
            else "0"
        )
        rows.append(row)
    return rows


def build_surrogate_rows(
    surrogate: list[dict[str, str]],
    existing_count: int,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for source in surrogate:
        if source.get("analytic_role") != "surrogate_auxiliary_nonoverlap":
            continue
        if not is_true(source.get("include_in_adjusted_descriptive_sample")):
            continue
        index = existing_count + len(rows) + 1
        exit_type = norm(source.get("observed_or_surrogate_label"))
        row = blank_panel_row()
        row["panel_id"] = f"surrogate_{index:04d}"
        row["case_id"] = norm(source.get("analytic_id"))
        row["analytic_role"] = "surrogate_auxiliary_nonoverlap"
        row["include_in_gold_sample"] = "0"
        row["include_in_historical_capacity_sample"] = "0"
        row["include_in_adjusted_descriptive_sample"] = "1"
        row["include_in_current_validated_model_sample"] = "0"
        row["include_in_full_controls_regression_sample"] = "0"
        row["label_source"] = "codex_surrogate"
        row["exit_type"] = exit_type
        row.update(binary_outcomes(exit_type))
        row["confidence"] = norm(source.get("confidence"))
        row["province"] = norm(source.get("province"))
        row["city"] = norm(source.get("city"))
        row["platform"] = norm(source.get("issuer_name"))
        row["company_name"] = norm(source.get("issuer_name"))
        row["control_city"] = norm(row.get("city"))
        row["control_unit_id"] = control_unit_id(row["province"], row["control_city"]) if row["province"] and row["control_city"] else ""
        row["source_coverage_score"] = norm(source.get("source_coverage_score"))
        row["continued_function_evidence_score"] = norm(source.get("continued_function_evidence_score"))
        row["province_fixed_effect"] = row["province"]
        row["capital_or_subprovincial_city"] = "1" if row["city"] in CAPITAL_OR_SUBPROVINCIAL else "0"
        row["surrogate_source_row_ids"] = norm(source.get("source_row_ids"))
        row["surrogate_gold_overlap"] = norm(source.get("gold_standard_overlap"))
        row["surrogate_gold_case_id"] = norm(source.get("gold_case_id"))
        row["surrogate_rows"] = norm(source.get("surrogate_rows"))
        row["notes"] = norm(source.get("notes"))
        default_control_status(row)
        rows.append(row)
    return rows


def nonempty_count(rows: list[dict[str, str]], field: str) -> int:
    return sum(1 for row in rows if norm(row.get(field)))


def build_coverage(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    gold_rows = [row for row in rows if row["include_in_gold_sample"] == "1"]
    adjusted_rows = [row for row in rows if row["include_in_adjusted_descriptive_sample"] == "1"]
    current_model_rows = [
        row for row in rows if row["include_in_current_validated_model_sample"] == "1"
    ]
    full_controls_rows = [
        row for row in rows if row["include_in_full_controls_regression_sample"] == "1"
    ]
    return [
        {
            "component": "Gold-standard labels",
            "available": str(len(gold_rows)),
            "denominator": str(len(rows)),
            "use": "Outcome scale and human validation",
        },
        {
            "component": "Adjusted descriptive sample",
            "available": str(len(adjusted_rows)),
            "denominator": str(len(rows)),
            "use": "Gold labels plus non-overlap surrogate nominal-exit screens",
        },
        {
            "component": "Historical capacity match",
            "available": str(nonempty_count(gold_rows, "elite_per_1000_sqkm")),
            "denominator": str(len(gold_rows)),
            "use": "Validated-sample descriptive patterns and current regression",
        },
        {
            "component": "Current validated-model rows",
            "available": str(len(current_model_rows)),
            "denominator": str(len(gold_rows)),
            "use": "Rows with gold labels and historical capacity",
        },
        {
            "component": "Full-controls regression rows",
            "available": str(len(full_controls_rows)),
            "denominator": str(len(gold_rows)),
            "use": "Rows with gold labels, historical capacity, and contemporary controls",
        },
        {
            "component": "Source coverage score",
            "available": str(nonempty_count(rows, "source_coverage_score")),
            "denominator": str(len(rows)),
            "use": "Bond disclosure quality and measurement-quality control",
        },
        {
            "component": "Debt pressure",
            "available": str(nonempty_count(rows, "debt_pressure_value")),
            "denominator": str(len(rows)),
            "use": "Contemporary alternative explanation, to be collected",
        },
        {
            "component": "Land finance dependence",
            "available": str(nonempty_count(rows, "land_finance_dependence_value")),
            "denominator": str(len(rows)),
            "use": "Contemporary alternative explanation, to be collected",
        },
        {
            "component": "Fiscal self-sufficiency",
            "available": str(nonempty_count(rows, "fiscal_self_sufficiency_value")),
            "denominator": str(len(rows)),
            "use": "Contemporary fiscal capacity, to be collected",
        },
        {
            "component": "Platform administrative level",
            "available": str(nonempty_count(rows, "platform_administrative_level")),
            "denominator": str(len(rows)),
            "use": "Issuer-level hierarchy control, rule-based pre-codes pending human check",
        },
    ]


def write_coverage_tex(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write("% Auto-generated by scripts/build_empirical_case_panel.py\n")
        handle.write("\\begin{table}[htbp]\n")
        handle.write("\\centering\n")
        handle.write("\\caption{Empirical case-panel coverage}\\label{tab:empirical-case-panel-coverage}\n")
        handle.write("\\small\n")
        handle.write("\\setlength{\\tabcolsep}{4pt}\n")
        handle.write("\\begin{tabular}{@{}p{0.28\\linewidth}rrp{0.42\\linewidth}@{}}\n")
        handle.write("\\toprule\n")
        handle.write("Component & Available & Denominator & Use \\\\\n")
        handle.write("\\midrule\n")
        for row in rows:
            handle.write(
                f"{tex_escape(row['component'])} & {row['available']} & {row['denominator']} & "
                f"{tex_escape(row['use'])} \\\\\n"
            )
        handle.write("\\bottomrule\n")
        handle.write("\\end{tabular}\n")
        handle.write("\\begin{minipage}{0.94\\linewidth}\n")
        handle.write(
            "\\vspace{0.5em}\\footnotesize Notes: The panel combines human-validated "
            "gold labels with non-overlap issuer-level surrogate labels. Main regression-ready "
            "rows are restricted to gold-standard cases with a historical-capacity match. "
            "Full-controls regression rows require contemporary controls in addition to the "
            "gold label and historical-capacity match. "
            "Contemporary fiscal, debt, land-finance, and platform-hierarchy controls are "
            "explicitly retained as collection fields rather than imputed.\n"
        )
        handle.write("\\end{minipage}\n")
        handle.write("\\end{table}\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", type=Path, default=DEFAULT_GOLD)
    parser.add_argument("--master", type=Path, default=DEFAULT_MASTER)
    parser.add_argument("--capacity", type=Path, default=DEFAULT_CAPACITY)
    parser.add_argument("--surrogate", type=Path, default=DEFAULT_SURROGATE)
    parser.add_argument("--city-controls", type=Path, default=DEFAULT_CITY_CONTROLS)
    parser.add_argument("--platform-controls", type=Path, default=DEFAULT_PLATFORM_CONTROLS)
    parser.add_argument("--panel", type=Path, default=DEFAULT_PANEL)
    parser.add_argument("--coverage", type=Path, default=DEFAULT_COVERAGE)
    parser.add_argument("--coverage-tex", type=Path, default=DEFAULT_COVERAGE_TEX)
    args = parser.parse_args()

    gold = read_csv(args.gold)
    master = read_csv(args.master)
    capacity = read_csv(args.capacity)
    surrogate = read_csv(args.surrogate)
    city_control_rows = read_csv_if_exists(args.city_controls)
    platform_control_rows = read_csv_if_exists(args.platform_controls)

    master_by_case = index_by(master, "case_id")
    capacity_by_case = index_by(capacity, "case_id")
    city_controls = index_by(city_control_rows, "control_unit_id")
    platform_controls = index_by(platform_control_rows, "case_id")

    rows = build_gold_rows(gold, master_by_case, capacity_by_case, city_controls, platform_controls)
    rows.extend(build_surrogate_rows(surrogate, len(rows)))
    coverage_rows = build_coverage(rows)

    write_csv(args.panel, rows, PANEL_FIELDS)
    write_csv(args.coverage, coverage_rows, ["component", "available", "denominator", "use"])
    write_coverage_tex(args.coverage_tex, coverage_rows)

    role_counts = Counter(row["analytic_role"] for row in rows)
    label_counts = Counter(row["exit_type"] for row in rows)
    print(f"panel_rows={len(rows)}")
    print(f"gold_rows={role_counts['gold_outcome']}")
    print(f"surrogate_nonoverlap_rows={role_counts['surrogate_auxiliary_nonoverlap']}")
    print(f"historical_capacity_gold_rows={nonempty_count([row for row in rows if row['include_in_gold_sample'] == '1'], 'elite_per_1000_sqkm')}")
    print(f"current_validated_model_rows={sum(1 for row in rows if row['include_in_current_validated_model_sample'] == '1')}")
    print(f"full_controls_regression_rows={sum(1 for row in rows if row['include_in_full_controls_regression_sample'] == '1')}")
    print("exit_type_counts=" + ";".join(f"{key}:{value}" for key, value in sorted(label_counts.items())))
    print(f"panel_csv={args.panel}")
    print(f"coverage_csv={args.coverage}")
    print(f"coverage_tex={args.coverage_tex}")


if __name__ == "__main__":
    main()
