#!/usr/bin/env python3
"""Build pilot-case historical-capacity summary tables and figure."""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-lgfv")

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:  # pragma: no cover - depends on local environment
    plt = None


ROOT = Path(__file__).resolve().parents[1]
LABELS = ROOT / "data" / "processed" / "human_validated_labels.csv"
CANDIDATES = ROOT / "data" / "candidate_city_plan.csv"
LLM_SEED = ROOT / "data" / "analysis_inputs" / "llm_candidate_pool_seed_2026_06_30.csv"
PILOT_MATRIX = ROOT / "data" / "analysis_inputs" / "pilot_coding_matrix.csv"
CAPACITY = ROOT / "data" / "analysis_inputs" / "cbdb_mingqing_elite_gadm_prefecture_counts.csv"
OUT_CSV = ROOT / "data" / "analysis_inputs" / "pilot_case_historical_capacity.csv"
OUT_DISTRIBUTION_CSV = ROOT / "data" / "analysis_inputs" / "pilot_exit_type_distribution.csv"
OUT_BIN_CSV = ROOT / "data" / "analysis_inputs" / "pilot_capacity_bin_exit_type.csv"
OUT_SOURCE_AUDIT_CSV = ROOT / "data" / "analysis_inputs" / "pilot_source_audit.csv"
OUT_MECHANISM_CSV = ROOT / "data" / "analysis_inputs" / "pilot_mechanism_evidence.csv"
OUT_TEX = ROOT / "paper" / "tables" / "pilot_case_historical_capacity.tex"
OUT_VALIDATED_TEX = ROOT / "paper" / "tables" / "pilot_validated_exit_types.tex"
OUT_TIER_TEX = ROOT / "paper" / "tables" / "pilot_validation_tiers.tex"
OUT_BIN_TEX = ROOT / "paper" / "tables" / "pilot_capacity_bin_exit_type.tex"
OUT_SOURCE_AUDIT_TEX = ROOT / "paper" / "tables" / "pilot_source_audit.tex"
OUT_MECHANISM_TEX = ROOT / "paper" / "tables" / "pilot_mechanism_evidence.tex"
OUT_DISTRIBUTION_TEX = ROOT / "paper" / "figures" / "pilot_exit_type_distribution.tex"
OUT_FIG = ROOT / "paper" / "figures" / "pilot_case_historical_capacity.png"

STRONG_CANDIDATE_IDS = {"pilot_sc_003"}
WEAK_CANDIDATE_IDS = {"pilot_gz_002", "pilot_gz_003"}
CITY_NAME_FIXES = {
    "Gaochun": "Nanjing",
    "Ganzhou Zhanggong": "Ganzhou",
    "Haian": "Nantong",
    "Jinghai": "Tianjin",
    "Nanjing Jiangning": "Nanjing",
    "Suzhou Xiangcheng": "Suzhou",
    "Tianjin Jinnan": "Tianjin",
    "Yuyao": "Ningbo",
    "Wenling": "Taizhou",
    "Yixing": "Wuxi",
    "Changshu": "Suzhou",
    "Zhangjiagang": "Suzhou",
    "Xinghua": "Taizhou",
    "Xian": "Xi'an",
}
CASE_STATUS_LABELS = {
    "human_validated": "Human-validated",
    "strong_candidate": "Strong candidate",
    "weak_capacity_candidate": "Weak-capacity candidate",
}
EXIT_STATUS_LABELS = {
    "substantive_exit": "Substantive exit",
    "nominal_exit": "Nominal exit",
    "functional_transfer": "Functional transfer",
    "nominal_exit_or_functional_persistence": "Near-miss functional persistence",
    "documents_found": "Documents found",
    "source_started": "Source started",
}
TIER_LABELS = {
    "human_validated": "Human-validated",
    "strong_candidate": "Strong candidate",
    "boundary_candidate": "Boundary case",
    "source_only_candidate": "Source-only candidate",
}
TIER_USE = {
    "human_validated": "Used as final pilot labels",
    "strong_candidate": "Used for provisional patterns and next validation",
    "boundary_candidate": "Used to define scope conditions",
    "source_only_candidate": "Used to guide source collection",
}
EXIT_FAMILY_LABELS = {
    "substantive_exit": "Substantive exit",
    "nominal_exit": "Nominal exit",
    "functional_transfer": "Functional transfer",
    "unclear": "Unclear or boundary",
}
EXIT_FAMILY_SHORT = {
    "substantive_exit": "S",
    "nominal_exit": "N",
    "functional_transfer": "F",
    "unclear": "U",
}
EXIT_FAMILY_ORDER = [
    "substantive_exit",
    "nominal_exit",
    "functional_transfer",
    "unclear",
]
CAPACITY_BIN_ORDER = ["high", "middle", "low"]
CAPACITY_BIN_LABELS = {
    "high": "High historical capacity",
    "middle": "Middle historical capacity",
    "low": "Low historical capacity",
}
EXIT_FAMILY_COLORS = {
    "substantive_exit": "black!70",
    "nominal_exit": "black!40",
    "functional_transfer": "black!20",
    "unclear": "white",
}
VALIDATED_EVENT_LABELS = {
    "pilot_gd_001": "2014 fiscal-funded project management",
    "pilot_zj_001": "2022 municipal platform consolidation",
    "pilot_sc_001": "2015 no-government-financing language",
    "pilot_sn_xian_hightech": "2012 platform-list exit disclosure",
    "pilot_hn_002": "2013 banking-regulator platform-list exit",
    "pilot_zj_002": "2015 no-government-financing and negative platform-function evidence",
    "pilot_zj_003": "2015 no-government-financing with group-level public functions",
    "pilot_js_004": "2015 no-government-financing with project-repayment exposure",
    "pilot_hn_004": "2020 transfer out of CBIRC platform management",
    "pilot_sd_001": "2015 no-government-financing and non-platform-list disclosure",
    "pilot_js_003": "2015 no-government-financing with entrusted construction",
    "pilot_gd_003": "2018 non-platform-list disclosure with fiscal-settlement projects",
    "pilot_js_001_alt_metro": "2015 no-government-financing with rail project finance",
}
MECHANISM_EVIDENCE = {
    "pilot_gd_001": {
        "fiscal_absorption": "Budget-funded project management and 2018 fiscal debt replacement.",
        "coordination": "Post-2014 role shift appears across issuer, rating, and debt-replacement documents.",
        "project_asset_governance": "Public projects remain as management tasks rather than new platform financing.",
    },
    "pilot_gd_001_alt_metro": {
        "fiscal_absorption": "Municipal and district fiscal capital contributions fund rail construction, while the company still raises remaining project funds through debt financing.",
        "coordination": "The Guangzhou government, finance bureau, metro issuer, and rail-construction subsidiary are linked through municipal rail planning, fiscal contributions, and state ownership.",
        "project_asset_governance": "Urban rail construction, operation, property development around stations, land-reserve proceeds, subsidies, and injected assets remain inside the metro group.",
    },
    "pilot_js_001_alt_metro": {
        "fiscal_absorption": "City and district fiscal funds and demolition funds provide rail project capital, while follow-on financing relies on syndicated loans and other debt financing.",
        "coordination": "Nanjing SASAC, the finance bureau, the metro issuer, and PPP project entities are linked through municipal rail planning, fiscal contributions, and state ownership.",
        "project_asset_governance": "Urban rail construction, operation, resource development, PPP project companies, subsidies, pledged income rights, and injected capital remain inside the metro group.",
    },
    "pilot_zj_001": {
        "fiscal_absorption": "Debt succession and asset transfer occurred through formal reorganization.",
        "coordination": "Qiantou transfer, city-investment consolidation, and Anju creation link multiple municipal entities.",
        "project_asset_governance": "Public project and housing functions moved within the municipal platform system.",
    },
    "pilot_sc_001": {
        "fiscal_absorption": "Debt replacement and government-bond pass-through coexist with fiscal-payment chains.",
        "coordination": "Issuer compliance language is present, but an independent exit-list source is still missing.",
        "project_asset_governance": "The same issuer continues infrastructure investment and financing functions.",
    },
    "pilot_sn_xian_hightech": {
        "fiscal_absorption": "Direct fiscal-substitution evidence remains limited.",
        "coordination": "The 2012 platform-list exit is issuer-disclosed; later business-module transfers appear partial.",
        "project_asset_governance": "The issuer retains BT, entrusted-construction, and government-repurchase exposure.",
    },
    "pilot_hn_002": {
        "fiscal_absorption": "Service-contract and fiscal-settlement evidence appears after formal exit.",
        "coordination": "Hunan banking-regulator exit is reported in issuer and legal documents.",
        "project_asset_governance": "Land preparation, major projects, fiscal settlement, and government support continue.",
    },
    "pilot_zj_002": {
        "fiscal_absorption": "Negative evidence shows no government purchase service, BT, PPP, land preparation, or fiscal repayment.",
        "coordination": "Issuer-level compliance evidence is strong; an independent list source is still missing.",
        "project_asset_governance": "No major continuing platform function is found; a residual receivable is treated as engineering background.",
    },
    "pilot_zj_003": {
        "fiscal_absorption": "Fiscal construction payments and fiscal compensation remain visible.",
        "coordination": "Issuer-level compliance is paired with group-level relocation of public functions.",
        "project_asset_governance": "The municipal group continues land preparation, affordable housing, and public-utility functions.",
    },
    "pilot_js_004": {
        "fiscal_absorption": "Budgeted government-purchase payments, fiscal subsidies, and project-repurchase support remain visible.",
        "coordination": "Issuer no-government-financing language is present; a direct government list source is still missing.",
        "project_asset_governance": "Shantytown redevelopment, water infrastructure, land preparation, and entrusted construction continue.",
    },
    "pilot_hn_004": {
        "fiscal_absorption": "Annual government payments for entrusted construction and fiscal subsidies remain visible.",
        "coordination": "Exit, re-entry, and 2020 CBIRC transfer-out language give the formal event unusual clarity.",
        "project_asset_governance": "The same issuer continues entrusted construction, land preparation, infrastructure, and affordable housing.",
    },
    "pilot_sd_001": {
        "fiscal_absorption": "Land-preparation gains and fiscal subsidies compensate the issuer.",
        "coordination": "Non-platform-list disclosure is present; the original list basis has not yet been collected.",
        "project_asset_governance": "Land preparation, government authorization, infrastructure, affordable housing, and entrusted assets continue.",
    },
    "pilot_js_003": {
        "fiscal_absorption": "Government-supported affordable housing and real-business-background government receivables remain visible.",
        "coordination": "Issuer compliance language is present; a separate platform-list source is still missing.",
        "project_asset_governance": "Land preparation, infrastructure entrusted construction, and affordable housing continue.",
    },
    "pilot_gd_003": {
        "fiscal_absorption": "Fiscal settlement for entrusted construction and contract-based payments are documented.",
        "coordination": "SASAC-entrusted land preparation coexists with disclosure that the issuer was outside the 2018 platform directory.",
        "project_asset_governance": "Public project tasks are formalized through SASAC-owned land and contract settlement.",
    },
    "sch_20260630_0019": {
        "fiscal_absorption": "Fiscal cash inflows, subsidies, and government-related current accounts remain central to repayment capacity.",
        "coordination": "The development-zone committee, Kaisheng Group, and Tenghai are linked through state ownership and 2021 shareholder reorganization.",
        "project_asset_governance": "Housing construction, municipal engineering, wastewater, industrial-park, and resettlement-housing project funds remain inside the issuer system.",
    },
    "sch_20260630_0142": {
        "fiscal_absorption": "Government subsidies, government-related receivables, and payment timing from the tourism-zone management committee remain central to operations.",
        "coordination": "The issuer is tied to Gaochun state-asset ownership and to district tourism-infrastructure project counterparties.",
        "project_asset_governance": "Tourism infrastructure, old-street redevelopment, forest-park, Cittaslow, transport-facility, and real-estate development functions remain inside the issuer group.",
    },
    "sch_20260630_0068": {
        "fiscal_absorption": "Fiscal subsidies, fiscal settlement, and government-related receivables remain central to project repayment and cash flow.",
        "coordination": "The issuer, Xiuzhou government counterparties, district SOEs, and Jiaxing SASAC are linked through entrusted-construction and state-asset arrangements.",
        "project_asset_governance": "Infrastructure, resettlement housing, land preparation, entrusted construction, and municipal project assets remain inside the issuer group.",
    },
    "expand_gx_nanning_chengtou": {
        "fiscal_absorption": "Since 2018 some designated municipal project funds are arranged by municipal finance, while shantytown government-purchase-service receivables remain fiscal-payment dependent.",
        "coordination": "Nanning SASAC, municipal finance, housing and construction authorities, and platform subsidiaries are linked through project-owner designation, government purchase service, and state-capital support.",
        "project_asset_governance": "Urban roads, bridges, key municipal projects, shantytown redevelopment, affordable housing, tolling, receivables, and injected assets remain inside the issuer group.",
    },
}
LATEX_TEXT_REPLACEMENTS = {
    "棚户区改造": "shantytown redevelopment",
    "市政水利设施配套": "municipal water facilities",
    "政府购买服务": "government purchase service",
    "财政性资金": "fiscal funds",
    "委托建设": "entrusted construction",
    "委托代建": "entrusted construction",
    "代建": "entrusted construction",
    "保障性安居": "affordable housing",
    "保障房": "affordable housing",
    "土地整理": "land preparation",
    "工程款": "project payments",
    "回购": "repurchase",
}


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fmt_float(value: str, digits: int = 2) -> str:
    if value in ("", None):
        return ""
    return f"{float(value):.{digits}f}"


def tex_escape(value: str) -> str:
    return (
        value.replace("\\", "\\textbackslash{}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("$", "\\$")
        .replace("#", "\\#")
        .replace("_", "\\_")
        .replace("{", "\\{")
        .replace("}", "\\}")
    )


def tex_clean(value: str) -> str:
    for source, replacement in LATEX_TEXT_REPLACEMENTS.items():
        value = value.replace(source, f" {replacement} ")
    value = "".join(char if ord(char) < 128 else " " for char in value)
    return " ".join(value.split())


def source_label(doc_id: str, lines: str) -> str:
    year = next((part for part in doc_id.split("_") if part.isdigit() and len(part) == 4), "")
    if "prospectus" in doc_id:
        source_type = "prospectus"
    elif "rating" in doc_id:
        source_type = "rating report"
    elif "legal" in doc_id:
        source_type = "legal opinion"
    elif "mtn" in doc_id:
        source_type = "MTN disclosure"
    elif "scp" in doc_id:
        source_type = "SCP disclosure"
    else:
        source_type = "source document"
    prefix = f"{year} {source_type}".strip()
    return f"{prefix}, lines {lines}"


def capacity_key(row: dict) -> tuple[str, str]:
    return row["province_name"], row["prefecture_name"]


def case_key(province: str, city: str) -> tuple[str, str]:
    return province, CITY_NAME_FIXES.get(city, city)


def build_rows() -> list[dict]:
    cap_rows = read_csv(CAPACITY)
    cap_by_city = {capacity_key(row): row for row in cap_rows}

    cases: list[dict] = []
    for row in read_csv(LABELS):
        cases.append(
            {
                "case_id": row["case_id"],
                "province": row["province"],
                "city": row["city"],
                "company_name": row["company_name"],
                "case_status": "human_validated",
                "exit_type_or_status": row["final_label"],
                "final_confidence": row["final_confidence"],
            }
        )

    for row in read_csv(CANDIDATES):
        if row["case_id"] in STRONG_CANDIDATE_IDS:
            cases.append(
                {
                    "case_id": row["case_id"],
                    "province": row["province"],
                    "city": row["city"],
                    "company_name": row["target_platform"],
                    "case_status": "strong_candidate",
                    "exit_type_or_status": "nominal_exit_or_functional_persistence",
                    "final_confidence": "",
                }
            )
        if row["case_id"] in WEAK_CANDIDATE_IDS:
            cases.append(
                {
                    "case_id": row["case_id"],
                    "province": row["province"],
                    "city": row["city"],
                    "company_name": row["target_platform"],
                    "case_status": "weak_capacity_candidate",
                    "exit_type_or_status": row["evidence_status"],
                    "final_confidence": "",
                }
            )

    output: list[dict] = []
    skipped: list[str] = []
    for case in cases:
        cap = cap_by_city.get(case_key(case["province"], case["city"]))
        if cap is None:
            skipped.append(f"{case['province']} {case['city']} ({case['case_id']})")
            continue
        output.append(
            {
                **case,
                "display_city": cap["prefecture_name"],
                "display_case_status": CASE_STATUS_LABELS.get(
                    case["case_status"], case["case_status"]
                ),
                "display_exit_type_or_status": EXIT_STATUS_LABELS.get(
                    case["exit_type_or_status"], case["exit_type_or_status"]
                ),
                "gadm_gid": cap["GID_2"],
                "prefecture_name": cap["prefecture_name"],
                "prefecture_name_chn": cap["prefecture_name_chn"],
                "matched_cbdb_places": cap["matched_cbdb_places"],
                "area_sqkm_approx": fmt_float(cap["area_sqkm_approx"], 3),
                "elite_persons": cap["elite_persons"],
                "jinshi_persons": cap["jinshi_persons"],
                "juren_persons": cap["juren_persons"],
                "elite_per_1000_sqkm": fmt_float(cap["elite_per_1000_sqkm"]),
                "jinshi_per_1000_sqkm": fmt_float(cap["jinshi_per_1000_sqkm"]),
                "juren_per_1000_sqkm": fmt_float(cap["juren_per_1000_sqkm"]),
            }
        )
    if skipped:
        print(
            "WARNING: skipped capacity-unmatched cases: " + "; ".join(skipped),
            file=sys.stderr,
        )
    return sorted(output, key=lambda row: float(row["elite_per_1000_sqkm"]), reverse=True)


def write_latex(rows: list[dict]) -> None:
    OUT_TEX.parent.mkdir(parents=True, exist_ok=True)
    display_rows = rows
    with OUT_TEX.open("w", encoding="utf-8") as handle:
        handle.write("% Auto-generated by scripts/build_pilot_capacity_summary.py\n")
        handle.write("\\begingroup\n")
        handle.write("\\small\n")
        handle.write("\\begin{longtable}{lllr}\n")
        handle.write("\\caption{Pilot cases and historical elite density}\\label{tab:pilot-historical-capacity}\\\\\n")
        handle.write("\\toprule\n")
        handle.write("City & Case status & Exit type/status & Elite density \\\\\n")
        handle.write("\\midrule\n")
        handle.write("\\endfirsthead\n")
        handle.write("\\toprule\n")
        handle.write("City & Case status & Exit type/status & Elite density \\\\\n")
        handle.write("\\midrule\n")
        handle.write("\\endhead\n")
        for row in display_rows:
            handle.write(
                f"{tex_escape(row['display_city'])} & "
                f"{tex_escape(row['display_case_status'])} & "
                f"{tex_escape(row['display_exit_type_or_status'])} & "
                f"{row['elite_per_1000_sqkm']} \\\\\n"
            )
        handle.write("\\bottomrule\n")
        handle.write("\\end{longtable}\n")
        handle.write(
            "\\begin{minipage}{0.92\\linewidth}\n"
            "\\vspace{0.5em}\\footnotesize Notes: Elite density is the number "
            "of Ming-Qing jinshi and juren records matched from CBDB to GADM "
            "4.1 China ADM2 boundaries, scaled per 1,000 square kilometers. "
            "Luzhou is a strong near-miss candidate rather than a final "
            "human-validated label because a direct platform-list exit source "
            "has not yet been found. Zunyi and Liupanshui are weak-capacity "
            "candidate cases rather than human-validated exit-type cases.\n"
            "\\end{minipage}\n"
        )
        handle.write("\\endgroup\n")


def write_validated_latex(rows: list[dict]) -> None:
    OUT_VALIDATED_TEX.parent.mkdir(parents=True, exist_ok=True)
    validated_rows = [row for row in rows if row["case_status"] == "human_validated"]
    labels_by_id = {row["case_id"]: row for row in read_csv(LABELS)}
    with OUT_VALIDATED_TEX.open("w", encoding="utf-8") as handle:
        handle.write("% Auto-generated by scripts/build_pilot_capacity_summary.py\n")
        handle.write("\\begingroup\n")
        handle.write("\\small\n")
        handle.write(
            "\\begin{longtable}{@{}>{\\raggedright\\arraybackslash}p{0.13\\linewidth}"
            ">{\\raggedright\\arraybackslash}p{0.42\\linewidth}"
            ">{\\raggedright\\arraybackslash}p{0.19\\linewidth}r@{}}\n"
        )
        handle.write("\\caption{Human-validated pilot labels}\\label{tab:pilot-validated-labels}\\\\\n")
        handle.write("\\toprule\n")
        handle.write("City & Event basis & Final label & Elite density \\\\\n")
        handle.write("\\midrule\n")
        handle.write("\\endfirsthead\n")
        handle.write("\\toprule\n")
        handle.write("City & Event basis & Final label & Elite density \\\\\n")
        handle.write("\\midrule\n")
        handle.write("\\endhead\n")
        for row in validated_rows:
            event_basis = VALIDATED_EVENT_LABELS.get(row["case_id"])
            if event_basis is None:
                label_row = labels_by_id.get(row["case_id"], {})
                event_basis = tex_clean(label_row.get("official_exit_event", ""))[:120]
            handle.write(
                f"{tex_escape(row['display_city'])} & "
                f"{tex_escape(event_basis)} & "
                f"{tex_escape(row['display_exit_type_or_status'])} & "
                f"{row['elite_per_1000_sqkm']} \\\\\n"
            )
        handle.write("\\bottomrule\n")
        handle.write("\\end{longtable}\n")
        handle.write(
            "\\begin{minipage}{0.96\\linewidth}\n"
            "\\vspace{0.5em}\\footnotesize Notes: Final labels are assigned "
            "after human review of the original source packets and are not "
            "assigned to source-only candidates. Elite density is measured as "
            "Ming-Qing jinshi and juren records per 1,000 square kilometers "
            "in the matched contemporary prefecture.\n"
            "\\end{minipage}\n"
        )
        handle.write("\\endgroup\n")


def build_distribution_rows() -> list[dict]:
    matrix_rows = read_csv(PILOT_MATRIX)
    grouped: dict[str, dict[str, int | str]] = {}
    for row in matrix_rows:
        tier = row["validation_tier"]
        if tier not in grouped:
            grouped[tier] = {
                "validation_tier": tier,
                "display_tier": TIER_LABELS.get(tier, tier),
                "analytic_use": TIER_USE.get(tier, ""),
                "total": 0,
                **{family: 0 for family in EXIT_FAMILY_ORDER},
            }
        family = row["exit_type_family"]
        if family not in EXIT_FAMILY_ORDER:
            family = "unclear"
        grouped[tier]["total"] = int(grouped[tier]["total"]) + 1
        grouped[tier][family] = int(grouped[tier][family]) + 1

    tier_order = {
        "human_validated": 0,
        "strong_candidate": 1,
        "boundary_candidate": 2,
        "source_only_candidate": 3,
    }
    return sorted(
        grouped.values(),
        key=lambda row: tier_order.get(str(row["validation_tier"]), 99),
    )


def build_capacity_bin_rows() -> list[dict]:
    grouped: dict[str, dict[str, int | str]] = {}
    for bin_name in CAPACITY_BIN_ORDER:
        grouped[bin_name] = {
            "historical_capacity_bin": bin_name,
            "display_bin": CAPACITY_BIN_LABELS[bin_name],
            "total": 0,
            **{family: 0 for family in EXIT_FAMILY_ORDER[:-1]},
        }

    rows = [row for row in build_rows() if row["case_status"] == "human_validated"]
    rows = sorted(rows, key=lambda row: float(row["elite_per_1000_sqkm"]), reverse=True)
    total = len(rows)
    for rank_desc, row in enumerate(rows, start=1):
        percentile = 1.0 if total == 1 else 1.0 - ((rank_desc - 1) / (total - 1))
        if percentile >= 2 / 3:
            bin_name = "high"
        elif percentile >= 1 / 3:
            bin_name = "middle"
        else:
            bin_name = "low"

        family = row["exit_type_or_status"]
        if family not in EXIT_FAMILY_ORDER[:-1]:
            continue
        grouped[bin_name]["total"] = int(grouped[bin_name]["total"]) + 1
        grouped[bin_name][family] = int(grouped[bin_name][family]) + 1

    return [grouped[bin_name] for bin_name in CAPACITY_BIN_ORDER]


def validated_display_rows() -> list[dict]:
    built_rows = [row for row in build_rows() if row["case_status"] == "human_validated"]
    labels_by_id = {row["case_id"]: row for row in read_csv(LABELS)}
    matrix_by_id = {row["case_id"]: row for row in read_csv(PILOT_MATRIX)}
    rows: list[dict] = []
    for row in built_rows:
        case_id = row["case_id"]
        label_row = labels_by_id[case_id]
        matrix_row = matrix_by_id.get(case_id, {})
        mechanism = MECHANISM_EVIDENCE.get(case_id, {})
        rows.append(
            {
                **row,
                "official_exit_event": label_row["official_exit_event"],
                "primary_source": (
                    f"{label_row['primary_evidence_doc']} lines "
                    f"{label_row['primary_evidence_lines']}"
                ),
                "primary_source_short": source_label(
                    label_row["primary_evidence_doc"],
                    label_row["primary_evidence_lines"],
                ),
                "secondary_source": (
                    f"{label_row['secondary_evidence_doc']} lines "
                    f"{label_row['secondary_evidence_lines']}"
                ),
                "formal_exit_evidence": matrix_row.get(
                    "formal_exit_evidence", label_row["official_exit_event"]
                ),
                "continued_function_evidence": matrix_row.get(
                    "continued_function_evidence", label_row["final_rationale"]
                ),
                "fiscal_substitution_evidence": matrix_row.get(
                    "fiscal_substitution_evidence", label_row["final_rationale"]
                ),
                "fiscal_absorption": mechanism.get(
                    "fiscal_absorption",
                    "Evidence not separately mechanism-coded in the current pilot table.",
                ),
                "coordination": mechanism.get(
                    "coordination",
                    "Evidence not separately mechanism-coded in the current pilot table.",
                ),
                "project_asset_governance": mechanism.get(
                    "project_asset_governance",
                    label_row["final_rationale"],
                ),
            }
        )
    return rows


def build_source_audit_rows() -> list[dict]:
    return [
        {
            "case_id": row["case_id"],
            "city": row["display_city"],
            "primary_source": row["primary_source"],
            "primary_source_short": row["primary_source_short"],
            "formal_event": row["formal_exit_evidence"],
            "post_event_function": row["continued_function_evidence"],
            "final_label": row["display_exit_type_or_status"],
        }
        for row in validated_display_rows()
    ]


def build_mechanism_rows() -> list[dict]:
    return [
        {
            "case_id": row["case_id"],
            "city": row["display_city"],
            "final_label": row["display_exit_type_or_status"],
            "fiscal_absorption": row["fiscal_absorption"],
            "coordination": row["coordination"],
            "project_asset_governance": row["project_asset_governance"],
        }
        for row in validated_display_rows()
    ]


def write_distribution_csv(rows: list[dict]) -> None:
    fieldnames = [
        "validation_tier",
        "display_tier",
        "analytic_use",
        "total",
        *EXIT_FAMILY_ORDER,
    ]
    write_csv(OUT_DISTRIBUTION_CSV, fieldnames, rows)


def write_capacity_bin_csv(rows: list[dict]) -> None:
    fieldnames = [
        "historical_capacity_bin",
        "display_bin",
        "total",
        "substantive_exit",
        "nominal_exit",
        "functional_transfer",
    ]
    write_csv(OUT_BIN_CSV, fieldnames, rows)


def write_source_audit_csv(rows: list[dict]) -> None:
    fieldnames = [
        "case_id",
        "city",
        "primary_source",
        "primary_source_short",
        "formal_event",
        "post_event_function",
        "final_label",
    ]
    write_csv(OUT_SOURCE_AUDIT_CSV, fieldnames, rows)


def write_mechanism_csv(rows: list[dict]) -> None:
    fieldnames = [
        "case_id",
        "city",
        "final_label",
        "fiscal_absorption",
        "coordination",
        "project_asset_governance",
    ]
    write_csv(OUT_MECHANISM_CSV, fieldnames, rows)


def write_tier_latex(rows: list[dict]) -> None:
    human_count = len(read_csv(LABELS))
    seed_rows = read_csv(LLM_SEED)
    seed_count = len(seed_rows)
    pending_count = sum(
        1 for row in seed_rows if row.get("llm_label_status", "") == "pending"
    )
    boundary_count = sum(
        1
        for row in seed_rows
        if "boundary_reviewed"
        in {
            row.get("validation_status", ""),
            row.get("case_pool_status", ""),
            row.get("llm_label_status", ""),
            row.get("human_review_status", ""),
        }
    )
    matched_count = len(validated_display_rows())
    unmatched_count = max(human_count - matched_count, 0)

    OUT_TIER_TEX.parent.mkdir(parents=True, exist_ok=True)
    with OUT_TIER_TEX.open("w", encoding="utf-8") as handle:
        handle.write("% Auto-generated by scripts/build_pilot_capacity_summary.py\n")
        handle.write("\\begin{table}[htbp]\n")
        handle.write("\\centering\n")
        handle.write("\\caption{Validation tiers in the expanded pilot}\n")
        handle.write("\\label{tab:pilot-validation-tiers}\n")
        handle.write("\\begin{tabular}{@{}lrl@{}}\n")
        handle.write("\\toprule\n")
        handle.write("Tier & Cases & Use in the paper \\\\\n")
        handle.write("\\midrule\n")
        tier_rows = [
            ("Human-validated label file", human_count, "Used as gold-standard labels"),
            (
                "Historically matched validated subset",
                matched_count,
                "Used for pilot descriptive tables",
            ),
            ("Candidate disclosure pool", seed_count, "Used for LLM-assisted screening"),
            ("Boundary-reviewed packets", boundary_count, "Used to define scope conditions"),
            ("Pending LLM/human validation", pending_count, "Used for future sample expansion"),
        ]
        for label, count, use in tier_rows:
            handle.write(f"{tex_escape(label)} & {count} & {tex_escape(use)} \\\\\n")
        handle.write("\\bottomrule\n")
        handle.write("\\end{tabular}\n")
        handle.write(
            "\\begin{minipage}{0.96\\linewidth}\n"
            "\\vspace{0.5em}\\footnotesize Notes: The historically matched subset is smaller\n"
            "than the full label file because the current CBDB-GADM crosswalk does not\n"
            f"yet contain usable historical-capacity matches for {unmatched_count} validated cases.\n"
            "Candidate disclosures are issuer-disclosure rows rather than final\n"
            "city-platform labels.\n"
            "\\end{minipage}\n"
        )
        handle.write("\\end{table}\n")


def write_source_audit_latex(rows: list[dict]) -> None:
    OUT_SOURCE_AUDIT_TEX.parent.mkdir(parents=True, exist_ok=True)
    with OUT_SOURCE_AUDIT_TEX.open("w", encoding="utf-8") as handle:
        handle.write("% Auto-generated by scripts/build_pilot_capacity_summary.py\n")
        handle.write("\\begingroup\n")
        handle.write("\\tiny\n")
        handle.write("\\renewcommand{\\arraystretch}{0.92}\n")
        handle.write("\\setlength{\\tabcolsep}{2pt}\n")
        handle.write("\\begin{longtable}{@{}"
                     ">{\\raggedright\\arraybackslash}p{0.10\\linewidth}"
                     ">{\\raggedright\\arraybackslash}p{0.17\\linewidth}"
                     ">{\\raggedright\\arraybackslash}p{0.23\\linewidth}"
                     ">{\\raggedright\\arraybackslash}p{0.34\\linewidth}"
                     ">{\\raggedright\\arraybackslash}p{0.10\\linewidth}@{}}\n")
        handle.write("\\caption{Source audit for human-validated pilot labels}\\label{tab:pilot-source-audit}\\\\\n")
        handle.write("\\toprule\n")
        handle.write("City & Primary source & Formal event & Post-event function & Label \\\\\n")
        handle.write("\\midrule\n")
        handle.write("\\endfirsthead\n")
        handle.write("\\toprule\n")
        handle.write("City & Primary source & Formal event & Post-event function & Label \\\\\n")
        handle.write("\\midrule\n")
        handle.write("\\endhead\n")
        for row in rows:
            handle.write(
                f"{tex_escape(tex_clean(row['city']))} & "
                f"{tex_escape(tex_clean(row['primary_source_short']))} & "
                f"{tex_escape(tex_clean(row['formal_event']))} & "
                f"{tex_escape(tex_clean(row['post_event_function']))} & "
                f"{tex_escape(tex_clean(row['final_label']))} \\\\\n"
            )
        handle.write("\\bottomrule\n")
        handle.write("\\end{longtable}\n")
        handle.write("\\endgroup\n")


def write_mechanism_latex(rows: list[dict]) -> None:
    OUT_MECHANISM_TEX.parent.mkdir(parents=True, exist_ok=True)
    with OUT_MECHANISM_TEX.open("w", encoding="utf-8") as handle:
        handle.write("% Auto-generated by scripts/build_pilot_capacity_summary.py\n")
        handle.write("\\begingroup\n")
        handle.write("\\scriptsize\n")
        handle.write("\\renewcommand{\\arraystretch}{0.92}\n")
        handle.write("\\setlength{\\tabcolsep}{2pt}\n")
        handle.write("\\begin{longtable}{@{}"
                     ">{\\raggedright\\arraybackslash}p{0.10\\linewidth}"
                     ">{\\raggedright\\arraybackslash}p{0.12\\linewidth}"
                     ">{\\raggedright\\arraybackslash}p{0.23\\linewidth}"
                     ">{\\raggedright\\arraybackslash}p{0.25\\linewidth}"
                     ">{\\raggedright\\arraybackslash}p{0.25\\linewidth}@{}}\n")
        handle.write("\\caption{Mechanism evidence in human-validated pilot cases}\\label{tab:pilot-mechanism-evidence}\\\\\n")
        handle.write("\\toprule\n")
        handle.write(
            "City & Label & Fiscal absorption & Bureaucratic coordination & "
            "Project and asset governance \\\\\n"
        )
        handle.write("\\midrule\n")
        handle.write("\\endfirsthead\n")
        handle.write("\\toprule\n")
        handle.write(
            "City & Label & Fiscal absorption & Bureaucratic coordination & "
            "Project and asset governance \\\\\n"
        )
        handle.write("\\midrule\n")
        handle.write("\\endhead\n")
        for row in rows:
            handle.write(
                f"{tex_escape(tex_clean(row['city']))} & "
                f"{tex_escape(tex_clean(row['final_label']))} & "
                f"{tex_escape(tex_clean(row['fiscal_absorption']))} & "
                f"{tex_escape(tex_clean(row['coordination']))} & "
                f"{tex_escape(tex_clean(row['project_asset_governance']))} \\\\\n"
            )
        handle.write("\\bottomrule\n")
        handle.write("\\end{longtable}\n")
        handle.write("\\endgroup\n")


def write_capacity_bin_latex(rows: list[dict]) -> None:
    OUT_BIN_TEX.parent.mkdir(parents=True, exist_ok=True)
    matched_total = sum(int(row["total"]) for row in rows)
    with OUT_BIN_TEX.open("w", encoding="utf-8") as handle:
        handle.write("% Auto-generated by scripts/build_pilot_capacity_summary.py\n")
        handle.write("\\begin{table}[htbp]\n")
        handle.write("\\centering\n")
        handle.write("\\caption{Historical capacity bin and validated exit type}\n")
        handle.write("\\label{tab:pilot-capacity-bin-exit-type}\n")
        handle.write("\\begin{tabular}{@{}lrrrr@{}}\n")
        handle.write("\\toprule\n")
        handle.write(
            "Historical capacity bin & Substantive & Nominal & Functional transfer & Total \\\\\n"
        )
        handle.write("\\midrule\n")
        for row in rows:
            handle.write(
                f"{tex_escape(str(row['display_bin']))} & "
                f"{row['substantive_exit']} & "
                f"{row['nominal_exit']} & "
                f"{row['functional_transfer']} & "
                f"{row['total']} \\\\\n"
            )
        handle.write("\\bottomrule\n")
        handle.write("\\end{tabular}\n")
        handle.write(
            "\\begin{minipage}{0.92\\linewidth}\n"
            "\\vspace{0.5em}\\footnotesize Notes: The table uses only the "
            f"{matched_total} historically matched human-validated pilot labels. Capacity bins are assigned "
            "from the CBDB-GADM Ming-Qing elite-density measure among matched "
            "human-validated cases. Counts are descriptive and are not population "
            "estimates.\n"
            "\\end{minipage}\n"
        )
        handle.write("\\end{table}\n")


def distribution_cells(row: dict) -> str:
    total = int(row["total"])
    cells: list[str] = []
    scale = 0.48
    for family in EXIT_FAMILY_ORDER:
        count = int(row[family])
        width = 0 if total == 0 else count / total * scale
        color = EXIT_FAMILY_COLORS[family]
        if count == 0:
            continue
        if family == "unclear":
            cells.append(
                "\\fcolorbox{black!50}{white}"
                f"{{\\color{{white}}\\rule{{{width:.3f}\\linewidth}}{{1.25ex}}}}"
            )
        else:
            cells.append(
                f"{{\\color{{{color}}}\\rule{{{width:.3f}\\linewidth}}{{1.25ex}}}}"
            )
    return "".join(cells)


def count_text(row: dict) -> str:
    parts = []
    for family in EXIT_FAMILY_ORDER:
        count = int(row[family])
        if count:
            parts.append(f"{EXIT_FAMILY_SHORT[family]}={count}")
    return "; ".join(parts)


def write_distribution_figure(rows: list[dict]) -> None:
    OUT_DISTRIBUTION_TEX.parent.mkdir(parents=True, exist_ok=True)
    with OUT_DISTRIBUTION_TEX.open("w", encoding="utf-8") as handle:
        handle.write("% Auto-generated by scripts/build_pilot_capacity_summary.py\n")
        handle.write("\\begin{figure}[htbp]\n")
        handle.write("\\centering\n")
        handle.write("\\caption{Exit-type distribution in the expanded pilot}\n")
        handle.write("\\label{fig:pilot-exit-type-distribution}\n")
        handle.write("\\small\n")
        handle.write(
            "\\begin{tabular}{@{}>{\\raggedright\\arraybackslash}p{0.16\\linewidth}"
            ">{\\raggedright\\arraybackslash}p{0.53\\linewidth}"
            ">{\\raggedright\\arraybackslash}p{0.20\\linewidth}@{}}\n"
        )
        handle.write("\\toprule\n")
        handle.write("Validation tier & Distribution & Counts \\\\\n")
        handle.write("\\midrule\n")
        for row in rows:
            handle.write(
                f"{tex_escape(str(row['display_tier']))} "
                f"$(n={row['total']})$ & "
                f"{distribution_cells(row)} & "
                f"{tex_escape(count_text(row))} \\\\\n"
            )
        handle.write("\\bottomrule\n")
        handle.write("\\end{tabular}\n")
        handle.write(
            "\\vspace{0.5em}\n"
            "\\begin{minipage}{0.92\\linewidth}\n"
            "\\footnotesize Notes: S = substantive exit, N = nominal exit, "
            "F = functional transfer, and U = unclear or boundary. Dark gray "
            "indicates substantive exit, medium gray nominal exit, light gray "
            "functional transfer, and outlined white unclear or boundary cases. "
            "The figure reports the evidence map, not final population estimates.\n"
            "\\end{minipage}\n"
        )
        handle.write("\\end{figure}\n")


def write_figure(rows: list[dict]) -> None:
    if plt is None:
        print("matplotlib not available; keeping existing figure file")
        return
    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    plot_rows = sorted(rows, key=lambda row: float(row["elite_per_1000_sqkm"]))
    colors = [
        "#8c3b3b"
        if row["case_status"] == "weak_capacity_candidate"
        else "#b06a2c"
        if row["case_status"] == "strong_candidate"
        else "#2f6f8f"
        for row in plot_rows
    ]
    labels = [row["display_city"] for row in plot_rows]
    values = [float(row["elite_per_1000_sqkm"]) for row in plot_rows]

    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    ax.barh(labels, values, color=colors)
    ax.set_xlabel("Ming-Qing elite records per 1,000 sq. km")
    ax.set_ylabel("")
    ax.set_title("Historical elite density in pilot cases")
    ax.grid(axis="x", color="#d9d9d9", linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#999999")
    for i, value in enumerate(values):
        ax.text(value + max(values) * 0.015, i, f"{value:.1f}", va="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT_FIG, dpi=200)
    plt.close(fig)


def main() -> int:
    rows = build_rows()
    distribution_rows = build_distribution_rows()
    capacity_bin_rows = build_capacity_bin_rows()
    source_audit_rows = build_source_audit_rows()
    mechanism_rows = build_mechanism_rows()
    fieldnames = list(rows[0].keys())
    write_csv(OUT_CSV, fieldnames, rows)
    write_distribution_csv(distribution_rows)
    write_capacity_bin_csv(capacity_bin_rows)
    write_source_audit_csv(source_audit_rows)
    write_mechanism_csv(mechanism_rows)
    write_latex(rows)
    write_validated_latex(rows)
    write_tier_latex(distribution_rows)
    write_capacity_bin_latex(capacity_bin_rows)
    write_source_audit_latex(source_audit_rows)
    write_mechanism_latex(mechanism_rows)
    write_distribution_figure(distribution_rows)
    write_figure(rows)
    print(f"rows={len(rows)}")
    print(f"distribution_rows={len(distribution_rows)}")
    print(f"capacity_bin_rows={len(capacity_bin_rows)}")
    print(f"source_audit_rows={len(source_audit_rows)}")
    print(f"mechanism_rows={len(mechanism_rows)}")
    print(f"csv={OUT_CSV}")
    print(f"distribution_csv={OUT_DISTRIBUTION_CSV}")
    print(f"capacity_bin_csv={OUT_BIN_CSV}")
    print(f"source_audit_csv={OUT_SOURCE_AUDIT_CSV}")
    print(f"mechanism_csv={OUT_MECHANISM_CSV}")
    print(f"tex={OUT_TEX}")
    print(f"validated_tex={OUT_VALIDATED_TEX}")
    print(f"tier_tex={OUT_TIER_TEX}")
    print(f"capacity_bin_tex={OUT_BIN_TEX}")
    print(f"source_audit_tex={OUT_SOURCE_AUDIT_TEX}")
    print(f"mechanism_tex={OUT_MECHANISM_TEX}")
    print(f"distribution_tex={OUT_DISTRIBUTION_TEX}")
    print(f"figure={OUT_FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
