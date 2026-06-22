#!/usr/bin/env python3
"""Build pilot-case historical-capacity summary tables and figure."""

from __future__ import annotations

import csv
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-lgfv")

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
LABELS = ROOT / "data" / "processed" / "human_validated_labels.csv"
CANDIDATES = ROOT / "data" / "candidate_city_plan.csv"
CAPACITY = ROOT / "data" / "analysis_inputs" / "cbdb_mingqing_elite_gadm_prefecture_counts.csv"
OUT_CSV = ROOT / "data" / "analysis_inputs" / "pilot_case_historical_capacity.csv"
OUT_TEX = ROOT / "paper" / "tables" / "pilot_case_historical_capacity.tex"
OUT_FIG = ROOT / "paper" / "figures" / "pilot_case_historical_capacity.png"

WEAK_CANDIDATE_IDS = {"pilot_gz_002", "pilot_gz_003"}
CITY_NAME_FIXES = {
    "Xian": "Xi'an",
}
CASE_STATUS_LABELS = {
    "human_validated": "Human-validated",
    "weak_capacity_candidate": "Weak-capacity candidate",
}
EXIT_STATUS_LABELS = {
    "substantive_exit": "Substantive exit",
    "nominal_exit": "Nominal exit",
    "functional_transfer": "Functional transfer",
    "documents_found": "Documents found",
    "source_started": "Source started",
}


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
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
        handle.write("\\caption{Pilot Cases and Historical Elite Density}\n")
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
            "Zunyi and Liupanshui are weak-capacity candidate cases rather "
            "than human-validated exit-type cases.\n"
            "\\end{minipage}\n"
        )
        handle.write("\\end{table}\n")


def write_figure(rows: list[dict]) -> None:
    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    plot_rows = sorted(rows, key=lambda row: float(row["elite_per_1000_sqkm"]))
    colors = [
        "#8c3b3b" if row["case_status"] == "weak_capacity_candidate" else "#2f6f8f"
        for row in plot_rows
    ]
    labels = [row["display_city"] for row in plot_rows]
    values = [float(row["elite_per_1000_sqkm"]) for row in plot_rows]

    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    ax.barh(labels, values, color=colors)
    ax.set_xlabel("Ming-Qing elite records per 1,000 sq. km")
    ax.set_ylabel("")
    ax.set_title("Historical Elite Density in Pilot Cases")
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
    fieldnames = list(rows[0].keys())
    write_csv(OUT_CSV, fieldnames, rows)
    write_latex(rows)
    write_figure(rows)
    print(f"rows={len(rows)}")
    print(f"csv={OUT_CSV}")
    print(f"tex={OUT_TEX}")
    print(f"figure={OUT_FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
