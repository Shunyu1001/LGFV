#!/usr/bin/env python3
"""Match CBDB historical places to modern GADM China ADM2 prefectures.

The script uses the place-level CBDB output from prepare_cbdb_elite_counts.py
and a locally downloaded GADM 4.1 China ADM2 GeoJSON zip. GADM is freely
available for academic and other non-commercial use, but redistribution of the
raw boundary file is not allowed. For that reason, the raw GeoJSON zip stays in
data/raw and is ignored by git; this script writes only small derived tables and
diagnostics.
"""

from __future__ import annotations

import csv
import json
import math
import sys
import urllib.request
import zipfile
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "historical" / "modern_boundaries"
INPUT = ROOT / "data" / "analysis_inputs" / "cbdb_mingqing_elite_place_counts.csv"
OUT_DIR = ROOT / "data" / "analysis_inputs"
DIAG_DIR = ROOT / "data" / "diagnostics"

GADM_URL = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_CHN_2.json.zip"
GADM_ZIP = RAW_DIR / "gadm41_CHN_2.json.zip"


def download_gadm() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if GADM_ZIP.exists():
        return
    with urllib.request.urlopen(GADM_URL, timeout=60) as response:
        with GADM_ZIP.open("wb") as handle:
            handle.write(response.read())


def read_gadm(download: bool) -> dict:
    if not GADM_ZIP.exists():
        if download:
            download_gadm()
        else:
            raise SystemExit(
                f"Missing {GADM_ZIP}. Re-run with --download to fetch the GADM "
                "China ADM2 GeoJSON zip for local academic use."
            )
    with zipfile.ZipFile(GADM_ZIP) as archive:
        json_members = [name for name in archive.namelist() if name.endswith(".json")]
        if not json_members:
            raise SystemExit(f"{GADM_ZIP} does not contain a GeoJSON file.")
        return json.loads(archive.read(sorted(json_members)[0]).decode("utf-8"))


def rings_from_geometry(geometry: dict) -> list[list[list[float]]]:
    geom_type = geometry.get("type")
    coords = geometry.get("coordinates", [])
    if geom_type == "Polygon":
        return coords
    if geom_type == "MultiPolygon":
        rings: list[list[list[float]]] = []
        for polygon in coords:
            rings.extend(polygon)
        return rings
    return []


def polygon_groups_from_geometry(geometry: dict) -> list[list[list[list[float]]]]:
    geom_type = geometry.get("type")
    coords = geometry.get("coordinates", [])
    if geom_type == "Polygon":
        return [coords]
    if geom_type == "MultiPolygon":
        return coords
    return []


def bbox_for_rings(rings: list[list[list[float]]]) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []
    for ring in rings:
        for x, y, *_ in ring:
            xs.append(float(x))
            ys.append(float(y))
    return min(xs), min(ys), max(xs), max(ys)


def ring_area_sqkm(ring: list[list[float]]) -> float:
    if len(ring) < 3:
        return 0.0
    radius_km = 6371.0088
    mean_lat = sum(float(point[1]) for point in ring) / len(ring)
    cos_lat = math.cos(math.radians(mean_lat))
    projected = [
        (
            math.radians(float(point[0])) * radius_km * cos_lat,
            math.radians(float(point[1])) * radius_km,
        )
        for point in ring
    ]
    area = 0.0
    for (x1, y1), (x2, y2) in zip(projected, projected[1:] + projected[:1]):
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0


def geometry_area_sqkm(geometry: dict) -> float:
    total = 0.0
    for polygon in polygon_groups_from_geometry(geometry):
        if not polygon:
            continue
        exterior = ring_area_sqkm(polygon[0])
        holes = sum(ring_area_sqkm(ring) for ring in polygon[1:])
        total += max(exterior - holes, 0.0)
    return total


def point_in_ring(x: float, y: float, ring: list[list[float]]) -> bool:
    inside = False
    if len(ring) < 3:
        return False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = float(ring[i][0]), float(ring[i][1])
        xj, yj = float(ring[j][0]), float(ring[j][1])
        crosses = (yi > y) != (yj > y)
        if crosses:
            x_intersect = (xj - xi) * (y - yi) / ((yj - yi) or 1e-15) + xi
            if x < x_intersect:
                inside = not inside
        j = i
    return inside


def point_in_geometry(x: float, y: float, rings: list[list[list[float]]]) -> bool:
    """Return true if a point is inside any outer ring and outside holes.

    GADM polygons usually contain an outer ring followed by zero or more inner
    rings. GeoJSON does not mark ring roles after flattening MultiPolygons, so
    this function uses odd-even parity across all rings. This is sufficient for
    point matching to administrative polygons.
    """

    inside = False
    for ring in rings:
        if point_in_ring(x, y, ring):
            inside = not inside
    return inside


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def to_int(value: str) -> int:
    if value in ("", None):
        return 0
    return int(float(value))


def to_float(value: str) -> float | None:
    if value in ("", None):
        return None
    return float(value)


def density(count: int, area_sqkm: float) -> str:
    if area_sqkm <= 0:
        return ""
    return f"{count / area_sqkm * 1000:.6f}"


def main() -> int:
    download = "--download" in sys.argv
    gadm = read_gadm(download=download)
    cbdb_rows = read_csv(INPUT)

    polygons = []
    metadata_rows = []
    for feature in gadm["features"]:
        props = feature["properties"]
        rings = rings_from_geometry(feature["geometry"])
        if not rings:
            continue
        bbox = bbox_for_rings(rings)
        area_sqkm = geometry_area_sqkm(feature["geometry"])
        record = {
            "props": props,
            "rings": rings,
            "bbox": bbox,
            "area_sqkm": area_sqkm,
        }
        polygons.append(record)
        metadata_rows.append(
            {
                "GID_2": props.get("GID_2", ""),
                "NAME_1": props.get("NAME_1", ""),
                "NL_NAME_1": props.get("NL_NAME_1", ""),
                "NAME_2": props.get("NAME_2", ""),
                "NL_NAME_2": props.get("NL_NAME_2", ""),
                "TYPE_2": props.get("TYPE_2", ""),
                "ENGTYPE_2": props.get("ENGTYPE_2", ""),
                "area_sqkm_approx": f"{area_sqkm:.3f}",
            }
        )

    crosswalk_rows = []
    unmatched_rows = []
    aggregate: dict[str, dict] = {}

    for row in cbdb_rows:
        x = to_float(row["x_coord"])
        y = to_float(row["y_coord"])
        match = None
        if x is not None and y is not None:
            for polygon in polygons:
                minx, miny, maxx, maxy = polygon["bbox"]
                if not (minx <= x <= maxx and miny <= y <= maxy):
                    continue
                if point_in_geometry(x, y, polygon["rings"]):
                    match = polygon["props"]
                    break

        numeric_fields = [
            "elite_persons",
            "jinshi_persons",
            "juren_persons",
            "ming_persons",
            "qing_persons",
        ]
        counts = {field: to_int(row[field]) for field in numeric_fields}

        if match is None:
            unmatched_rows.append(
                {
                    "c_addr_id": row["c_addr_id"],
                    "addr_name": row["addr_name"],
                    "addr_name_chn": row["addr_name_chn"],
                    "x_coord": row["x_coord"],
                    "y_coord": row["y_coord"],
                    **counts,
                }
            )
            continue

        gid = match.get("GID_2", "")
        crosswalk_rows.append(
            {
                "c_addr_id": row["c_addr_id"],
                "addr_name": row["addr_name"],
                "addr_name_chn": row["addr_name_chn"],
                "CHGIS_PT_ID": row["CHGIS_PT_ID"],
                "x_coord": row["x_coord"],
                "y_coord": row["y_coord"],
                "GID_2": gid,
                "province_name": match.get("NAME_1", ""),
                "province_name_chn": match.get("NL_NAME_1", ""),
                "prefecture_name": match.get("NAME_2", ""),
                "prefecture_name_chn": match.get("NL_NAME_2", ""),
                "prefecture_type": match.get("ENGTYPE_2", ""),
                **counts,
            }
        )

        if gid not in aggregate:
            aggregate[gid] = {
                "GID_2": gid,
                "province_name": match.get("NAME_1", ""),
                "province_name_chn": match.get("NL_NAME_1", ""),
                "prefecture_name": match.get("NAME_2", ""),
                "prefecture_name_chn": match.get("NL_NAME_2", ""),
                "prefecture_type": match.get("ENGTYPE_2", ""),
                "area_sqkm_approx": f"{polygon['area_sqkm']:.3f}",
                "matched_cbdb_places": 0,
                "elite_persons": 0,
                "jinshi_persons": 0,
                "juren_persons": 0,
                "ming_persons": 0,
                "qing_persons": 0,
            }
        aggregate[gid]["matched_cbdb_places"] += 1
        for field, value in counts.items():
            aggregate[gid][field] += value

    prefecture_rows = sorted(
        aggregate.values(),
        key=lambda row: (-row["elite_persons"], row["province_name"], row["prefecture_name"]),
    )
    for row in prefecture_rows:
        area = float(row["area_sqkm_approx"])
        row["elite_per_1000_sqkm"] = density(row["elite_persons"], area)
        row["jinshi_per_1000_sqkm"] = density(row["jinshi_persons"], area)
        row["juren_per_1000_sqkm"] = density(row["juren_persons"], area)

    coverage = {
        "cbdb_place_rows": len(cbdb_rows),
        "matched_place_rows": len(crosswalk_rows),
        "unmatched_place_rows": len(unmatched_rows),
        "gadm_prefecture_rows": len(polygons),
        "matched_gadm_prefecture_rows": len(prefecture_rows),
        "elite_persons_in_input": sum(to_int(row["elite_persons"]) for row in cbdb_rows),
        "elite_persons_matched": sum(row["elite_persons"] for row in prefecture_rows),
        "elite_persons_unmatched": sum(to_int(row["elite_persons"]) for row in unmatched_rows),
        "boundary_source": "GADM 4.1 China ADM2",
        "boundary_url": GADM_URL,
        "license_note": (
            "GADM is free for academic and other non-commercial use; raw "
            "boundary redistribution is not allowed."
        ),
    }

    write_csv(
        OUT_DIR / "cbdb_place_to_gadm_prefecture_crosswalk.csv",
        [
            "c_addr_id",
            "addr_name",
            "addr_name_chn",
            "CHGIS_PT_ID",
            "x_coord",
            "y_coord",
            "GID_2",
            "province_name",
            "province_name_chn",
            "prefecture_name",
            "prefecture_name_chn",
            "prefecture_type",
            "elite_persons",
            "jinshi_persons",
            "juren_persons",
            "ming_persons",
            "qing_persons",
        ],
        crosswalk_rows,
    )
    write_csv(
        OUT_DIR / "cbdb_mingqing_elite_gadm_prefecture_counts.csv",
        [
            "GID_2",
            "province_name",
            "province_name_chn",
            "prefecture_name",
            "prefecture_name_chn",
            "prefecture_type",
            "area_sqkm_approx",
            "matched_cbdb_places",
            "elite_persons",
            "jinshi_persons",
            "juren_persons",
            "ming_persons",
            "qing_persons",
            "elite_per_1000_sqkm",
            "jinshi_per_1000_sqkm",
            "juren_per_1000_sqkm",
        ],
        prefecture_rows,
    )
    write_csv(
        DIAG_DIR / "gadm_china_adm2_metadata.csv",
        [
            "GID_2",
            "NAME_1",
            "NL_NAME_1",
            "NAME_2",
            "NL_NAME_2",
            "TYPE_2",
            "ENGTYPE_2",
            "area_sqkm_approx",
        ],
        metadata_rows,
    )
    write_csv(
        DIAG_DIR / "cbdb_gadm_match_coverage.csv",
        list(coverage.keys()),
        [coverage],
    )
    write_csv(
        DIAG_DIR / "cbdb_gadm_unmatched_places.csv",
        [
            "c_addr_id",
            "addr_name",
            "addr_name_chn",
            "x_coord",
            "y_coord",
            "elite_persons",
            "jinshi_persons",
            "juren_persons",
            "ming_persons",
            "qing_persons",
        ],
        sorted(unmatched_rows, key=lambda row: -row["elite_persons"]),
    )

    print(f"gadm_prefectures={len(polygons)}")
    print(f"cbdb_places={len(cbdb_rows)}")
    print(f"matched_places={len(crosswalk_rows)}")
    print(f"unmatched_places={len(unmatched_rows)}")
    print(f"matched_prefectures={len(prefecture_rows)}")
    print(f"elite_persons_matched={coverage['elite_persons_matched']}")
    print(f"elite_persons_unmatched={coverage['elite_persons_unmatched']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
