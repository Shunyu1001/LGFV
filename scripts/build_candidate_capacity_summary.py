#!/usr/bin/env python3
"""Attach CBDB-GADM historical elite density to all candidate cities."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "data" / "candidate_city_plan.csv"
CAPACITY = ROOT / "data" / "analysis_inputs" / "cbdb_mingqing_elite_gadm_prefecture_counts.csv"
OUT_CSV = ROOT / "data" / "analysis_inputs" / "candidate_city_historical_capacity.csv"
OUT_UNMATCHED = ROOT / "data" / "diagnostics" / "candidate_capacity_unmatched.csv"
OUT_MEMO = ROOT / "docs" / "candidate_capacity_prioritization.md"

CITY_NAME_FIXES = {
    "Xian": "Xi'an",
    "Honghe": "HongheHaniandYi",
}

TERCILE_LABELS = {
    "high": "High historical elite density",
    "middle": "Middle historical elite density",
    "low": "Low historical elite density",
}

STATUS_LABELS = {
    "documents_found": "documents found",
    "source_started": "source started",
    "candidate_only": "candidate only",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fmt_float(value: str | float, digits: int = 2) -> str:
    if value in ("", None):
        return ""
    return f"{float(value):.{digits}f}"


def capacity_key(row: dict[str, str]) -> tuple[str, str]:
    return row["province_name"], row["prefecture_name"]


def candidate_key(row: dict[str, str]) -> tuple[str, str]:
    return row["province"], CITY_NAME_FIXES.get(row["city"], row["city"])


def assign_capacity_bins(
    matched_unique: dict[tuple[str, str], dict[str, str]],
) -> dict[tuple[str, str], dict[str, str]]:
    by_density = sorted(
        matched_unique.items(),
        key=lambda item: float(item[1]["elite_per_1000_sqkm"]),
        reverse=True,
    )
    total = len(by_density)
    out: dict[tuple[str, str], dict[str, str]] = {}

    for rank_desc, (key, cap) in enumerate(by_density, start=1):
        percentile = 1.0 if total == 1 else 1.0 - ((rank_desc - 1) / (total - 1))
        if percentile >= 2 / 3:
            capacity_bin = "high"
        elif percentile >= 1 / 3:
            capacity_bin = "middle"
        else:
            capacity_bin = "low"

        out[key] = {
            "elite_density_rank_desc": str(rank_desc),
            "elite_density_percentile": fmt_float(percentile, 3),
            "historical_capacity_bin": capacity_bin,
            "historical_capacity_label": TERCILE_LABELS[capacity_bin],
        }
    return out


def collection_priority(row: dict[str, str]) -> str:
    if row["evidence_status"] == "documents_found":
        return "already_documented"
    if row["evidence_status"] == "source_started":
        return "complete_started_source_collection"
    if row["historical_capacity_bin"] == "high":
        return "search_high_capacity_case"
    if row["historical_capacity_bin"] == "low":
        return "search_low_capacity_case"
    return "search_middle_capacity_case"


def build_rows() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    candidates = read_csv(CANDIDATES)
    capacity_rows = read_csv(CAPACITY)
    cap_by_city = {capacity_key(row): row for row in capacity_rows}

    unmatched: list[dict[str, str]] = []
    matched_unique: dict[tuple[str, str], dict[str, str]] = {}
    for row in candidates:
        key = candidate_key(row)
        cap = cap_by_city.get(key)
        if cap is None:
            unmatched.append(
                {
                    "case_id": row["case_id"],
                    "province": row["province"],
                    "city": row["city"],
                    "match_province": key[0],
                    "match_city": key[1],
                }
            )
            continue
        matched_unique[key] = cap

    bins = assign_capacity_bins(matched_unique)

    rows: list[dict[str, str]] = []
    for row in candidates:
        key = candidate_key(row)
        cap = cap_by_city.get(key)
        if cap is None:
            continue

        out = {
            "case_id": row["case_id"],
            "priority": row["priority"],
            "province": row["province"],
            "city": row["city"],
            "target_platform": row["target_platform"],
            "selection_stratum": row["selection_stratum"],
            "evidence_status": row["evidence_status"],
            "collection_status": row["collection_status"],
            "gadm_gid": cap["GID_2"],
            "capacity_prefecture_name": cap["prefecture_name"],
            "capacity_prefecture_name_chn": cap["prefecture_name_chn"],
            "matched_cbdb_places": cap["matched_cbdb_places"],
            "area_sqkm_approx": fmt_float(cap["area_sqkm_approx"], 3),
            "elite_persons": cap["elite_persons"],
            "jinshi_persons": cap["jinshi_persons"],
            "juren_persons": cap["juren_persons"],
            "elite_per_1000_sqkm": fmt_float(cap["elite_per_1000_sqkm"]),
            "jinshi_per_1000_sqkm": fmt_float(cap["jinshi_per_1000_sqkm"]),
            "juren_per_1000_sqkm": fmt_float(cap["juren_per_1000_sqkm"]),
            **bins[key],
        }
        out["next_collection_priority"] = collection_priority(out)
        rows.append(out)

    return sorted(
        rows,
        key=lambda item: (
            int(item["elite_density_rank_desc"]),
            int(item["priority"]),
            item["case_id"],
        ),
    ), unmatched


def top_case(rows: list[dict[str, str]], bin_name: str) -> list[dict[str, str]]:
    usable = [
        row
        for row in rows
        if row["historical_capacity_bin"] == bin_name
        and row["evidence_status"] != "documents_found"
    ]
    status_order = {"source_started": 0, "candidate_only": 1}
    ranked = sorted(
        usable,
        key=lambda row: (
            status_order.get(row["evidence_status"], 2),
            int(row["priority"]),
            int(row["elite_density_rank_desc"]),
            row["case_id"],
        ),
    )
    out: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for row in ranked:
        key = (row["province"], row["city"])
        if key in seen:
            continue
        out.append(row)
        seen.add(key)
        if len(out) == 5:
            break
    return out


def write_memo(rows: list[dict[str, str]], unmatched: list[dict[str, str]]) -> None:
    OUT_MEMO.parent.mkdir(parents=True, exist_ok=True)

    unique_by_key: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        unique_by_key[(row["province"], row["city"])] = row

    bin_counts = defaultdict(int)
    for row in unique_by_key.values():
        bin_counts[row["historical_capacity_bin"]] += 1

    high_next = top_case(rows, "high")
    low_next = top_case(rows, "low")
    middle_next = top_case(rows, "middle")

    with OUT_MEMO.open("w", encoding="utf-8") as handle:
        handle.write("# Candidate Historical-Capacity Prioritization\n\n")
        handle.write(
            "This memo attaches the CBDB-GADM Ming-Qing elite-density measure "
            "to the full candidate city list. The purpose is not to treat the "
            "candidate list as a representative sample. It is to discipline the "
            "next round of source collection by making historical-capacity "
            "variation explicit before additional cases are chosen.\n\n"
        )
        handle.write("## Coverage\n\n")
        handle.write(
            f"The current candidate file contains {len(rows)} platform rows "
            f"covering {len(unique_by_key)} unique province-city pairs. All "
            "candidate rows match to a GADM ADM2 unit after applying a small "
            "name crosswalk for Xi'an and Honghe Hani and Yi Autonomous "
            "Prefecture.\n\n"
        )
        handle.write(
            "The unique cities divide into "
            f"{bin_counts['high']} high-density, {bin_counts['middle']} "
            f"middle-density, and {bin_counts['low']} low-density cases. The "
            "bins are based on the candidate cities themselves, so they should "
            "be read as a sampling guide rather than as national cutpoints.\n\n"
        )

        handle.write("## Recommended Next Collection\n\n")
        handle.write(
            "The next collection round should keep one high-capacity search, "
            "one low-capacity search, and one middle-capacity search active at "
            "the same time. This will keep the evidence base from drifting "
            "toward only coastal document-rich cases or only debt-stress cases.\n\n"
        )

        for title, case_rows in [
            ("High historical capacity", high_next),
            ("Low historical capacity", low_next),
            ("Middle historical capacity", middle_next),
        ]:
            handle.write(f"### {title}\n\n")
            for row in case_rows:
                platform = row["target_platform"] or "platform not yet selected"
                status = STATUS_LABELS.get(row["evidence_status"], row["evidence_status"])
                handle.write(
                    f"- {row['province']} {row['city']} ({platform}): "
                    f"elite density {row['elite_per_1000_sqkm']} per 1,000 sq. km; "
                    f"{status}.\n"
                )
            handle.write("\n")

        handle.write("## Files\n\n")
        handle.write(
            "- `data/analysis_inputs/candidate_city_historical_capacity.csv`\n"
            "- `data/diagnostics/candidate_capacity_unmatched.csv`\n\n"
        )
        if unmatched:
            handle.write(
                "The diagnostic file contains unmatched rows and should be "
                "checked before using the output.\n"
            )
        else:
            handle.write(
                "The unmatched diagnostic file is empty apart from the header.\n"
            )


def main() -> int:
    rows, unmatched = build_rows()
    if not rows:
        raise SystemExit("No matched candidate rows.")

    write_csv(OUT_CSV, list(rows[0].keys()), rows)
    unmatched_fields = ["case_id", "province", "city", "match_province", "match_city"]
    write_csv(OUT_UNMATCHED, unmatched_fields, unmatched)
    write_memo(rows, unmatched)

    print(f"rows={len(rows)}")
    print(f"unmatched={len(unmatched)}")
    print(f"csv={OUT_CSV}")
    print(f"diagnostics={OUT_UNMATCHED}")
    print(f"memo={OUT_MEMO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
