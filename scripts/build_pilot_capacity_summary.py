#!/usr/bin/env python3
"""Build pilot-case historical-capacity summary tables and figure."""

from __future__ import annotations

import csv
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-lgfv")

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:  # pragma: no cover - depends on local environment
    plt = None


ROOT = Path(__file__).resolve().parents[1]
LABELS = ROOT / "data" / "processed" / "human_validated_labels.csv"
CANDIDATES = ROOT / "data" / "candidate_city_plan.csv"
PILOT_MATRIX = ROOT / "data" / "analysis_inputs" / "pilot_coding_matrix.csv"
CAPACITY = ROOT / "data" / "analysis_inputs" / "cbdb_mingqing_elite_gadm_prefecture_counts.csv"
OUT_CSV = ROOT / "data" / "analysis_inputs" / "pilot_case_historical_capacity.csv"
OUT_DISTRIBUTION_CSV = ROOT / "data" / "analysis_inputs" / "pilot_exit_type_distribution.csv"
OUT_TEX = ROOT / "paper" / "tables" / "pilot_case_historical_capacity.tex"
OUT_VALIDATED_TEX = ROOT / "paper" / "tables" / "pilot_validated_exit_types.tex"
OUT_TIER_TEX = ROOT / "paper" / "tables" / "pilot_validation_tiers.tex"
OUT_DISTRIBUTION_TEX = ROOT / "paper" / "figures" / "pilot_exit_type_distribution.tex"
OUT_FIG = ROOT / "paper" / "figures" / "pilot_case_historical_capacity.png"

STRONG_CANDIDATE_IDS = {"pilot_sc_003"}
WEAK_CANDIDATE_IDS = {"pilot_gz_002", "pilot_gz_003"}
CITY_NAME_FIXES = {
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
    for case in cases:
        cap = cap_by_city.get(case_key(case["province"], case["city"]))
        if cap is None:
            raise SystemExit(f"No capacity match for {case['province']} {case['city']}")
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
    return sorted(output, key=lambda row: float(row["elite_per_1000_sqkm"]), reverse=True)


def write_latex(rows: list[dict]) -> None:
    OUT_TEX.parent.mkdir(parents=True, exist_ok=True)
    display_rows = rows
    with OUT_TEX.open("w", encoding="utf-8") as handle:
        handle.write("% Auto-generated by scripts/build_pilot_capacity_summary.py\n")
        handle.write("\\begin{table}[htbp]\n")
        handle.write("\\centering\n")
        handle.write("\\caption{Pilot cases and historical elite density}\n")
        handle.write("\\label{tab:pilot-historical-capacity}\n")
        handle.write("\\begin{tabular}{lllr}\n")
        handle.write("\\toprule\n")
        handle.write("City & Case status & Exit type/status & Elite density \\\\\n")
        handle.write("\\midrule\n")
        for row in display_rows:
            handle.write(
                f"{tex_escape(row['display_city'])} & "
                f"{tex_escape(row['display_case_status'])} & "
                f"{tex_escape(row['display_exit_type_or_status'])} & "
                f"{row['elite_per_1000_sqkm']} \\\\\n"
            )
        handle.write("\\bottomrule\n")
        handle.write("\\end{tabular}\n")
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
        handle.write("\\end{table}\n")


def write_validated_latex(rows: list[dict]) -> None:
    OUT_VALIDATED_TEX.parent.mkdir(parents=True, exist_ok=True)
    validated_rows = [row for row in rows if row["case_status"] == "human_validated"]
    with OUT_VALIDATED_TEX.open("w", encoding="utf-8") as handle:
        handle.write("% Auto-generated by scripts/build_pilot_capacity_summary.py\n")
        handle.write("\\begin{table}[htbp]\n")
        handle.write("\\centering\n")
        handle.write("\\caption{Human-validated pilot labels}\n")
        handle.write("\\label{tab:pilot-validated-labels}\n")
        handle.write("\\small\n")
        handle.write(
            "\\begin{tabular}{@{}>{\\raggedright\\arraybackslash}p{0.13\\linewidth}"
            ">{\\raggedright\\arraybackslash}p{0.42\\linewidth}"
            ">{\\raggedright\\arraybackslash}p{0.19\\linewidth}r@{}}\n"
        )
        handle.write("\\toprule\n")
        handle.write("City & Event basis & Final label & Elite density \\\\\n")
        handle.write("\\midrule\n")
        for row in validated_rows:
            handle.write(
                f"{tex_escape(row['display_city'])} & "
                f"{tex_escape(VALIDATED_EVENT_LABELS[row['case_id']])} & "
                f"{tex_escape(row['display_exit_type_or_status'])} & "
                f"{row['elite_per_1000_sqkm']} \\\\\n"
            )
        handle.write("\\bottomrule\n")
        handle.write("\\end{tabular}\n")
        handle.write(
            "\\begin{minipage}{0.96\\linewidth}\n"
            "\\vspace{0.5em}\\footnotesize Notes: Final labels are assigned "
            "after human review of the original source packets and are not "
            "assigned to source-only candidates. Elite density is measured as "
            "Ming-Qing jinshi and juren records per 1,000 square kilometers "
            "in the matched contemporary prefecture.\n"
            "\\end{minipage}\n"
        )
        handle.write("\\end{table}\n")


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


def write_distribution_csv(rows: list[dict]) -> None:
    fieldnames = [
        "validation_tier",
        "display_tier",
        "analytic_use",
        "total",
        *EXIT_FAMILY_ORDER,
    ]
    write_csv(OUT_DISTRIBUTION_CSV, fieldnames, rows)


def write_tier_latex(rows: list[dict]) -> None:
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
        for row in rows:
            handle.write(
                f"{tex_escape(str(row['display_tier']))} & "
                f"{row['total']} & "
                f"{tex_escape(str(row['analytic_use']))} \\\\\n"
            )
        handle.write("\\bottomrule\n")
        handle.write("\\end{tabular}\n")
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
    fieldnames = list(rows[0].keys())
    write_csv(OUT_CSV, fieldnames, rows)
    write_distribution_csv(distribution_rows)
    write_latex(rows)
    write_validated_latex(rows)
    write_tier_latex(distribution_rows)
    write_distribution_figure(distribution_rows)
    write_figure(rows)
    print(f"rows={len(rows)}")
    print(f"distribution_rows={len(distribution_rows)}")
    print(f"csv={OUT_CSV}")
    print(f"distribution_csv={OUT_DISTRIBUTION_CSV}")
    print(f"tex={OUT_TEX}")
    print(f"validated_tex={OUT_VALIDATED_TEX}")
    print(f"tier_tex={OUT_TIER_TEX}")
    print(f"distribution_tex={OUT_DISTRIBUTION_TEX}")
    print(f"figure={OUT_FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
