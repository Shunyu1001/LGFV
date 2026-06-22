#!/usr/bin/env python3
"""Prepare CBDB Ming-Qing examination-elite counts by historical place.

This script keeps the large CBDB SQLite file in data/raw, then writes small
tracked outputs that document the database version, relevant entry codes, and a
first-pass place-level count of Ming-Qing jinshi and juren records. The output is
not yet a prefecture-level historical-capacity variable; it still needs a
spatial or CHGIS-ID crosswalk to contemporary prefectures.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
import sys
import urllib.request
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "historical" / "cbdb"
OUT_DIR = ROOT / "data" / "analysis_inputs"
DIAG_DIR = ROOT / "data" / "diagnostics"

GITHUB_META_URL = (
    "https://raw.githubusercontent.com/cbdb-project/cbdb_sqlite/master/latest.json"
)
DEFAULT_DOWNLOAD_URL = (
    "https://huggingface.co/datasets/cbdb/cbdb-sqlite/resolve/main/latest.zip"
)

JINSHI_TYPE = "040101"
JUREN_TYPE = "040102"
MING_QING_DYNASTIES = (19, 20, 80)
PREFERRED_ADDRESS_TYPES = (1, 16, 6, 7, 14)


def fetch_url(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_cbdb_sqlite(download: bool) -> tuple[Path, dict]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DIAG_DIR.mkdir(parents=True, exist_ok=True)

    sqlite_files = sorted(RAW_DIR.glob("cbdb_*.sqlite3"), reverse=True)
    metadata: dict = {}
    if sqlite_files:
        local_meta = RAW_DIR / "latest_zip.json"
        if local_meta.exists():
            metadata = json.loads(local_meta.read_text(encoding="utf-8"))
        elif (RAW_DIR / "latest.zip").exists():
            with zipfile.ZipFile(RAW_DIR / "latest.zip") as archive:
                json_members = [
                    name for name in archive.namelist() if name.endswith(".json")
                ]
                if json_members:
                    zip_meta_name = sorted(json_members)[-1]
                    metadata = json.loads(
                        archive.read(zip_meta_name).decode("utf-8")
                    )
                    local_meta.write_text(
                        json.dumps(metadata, indent=2, ensure_ascii=False),
                        encoding="utf-8",
                    )
                else:
                    metadata = {"source": "local"}
        else:
            metadata = {"source": "local"}
        metadata["sqlite_filename"] = sqlite_files[0].name
        return sqlite_files[0], metadata

    if not download:
        raise SystemExit(
            "No local CBDB SQLite file found. Re-run with --download after "
            "confirming that the 100MB+ download is acceptable."
        )

    github_meta = json.loads(fetch_url(GITHUB_META_URL).decode("utf-8"))
    (RAW_DIR / "latest_github.json").write_text(
        json.dumps(github_meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    zip_path = RAW_DIR / "latest.zip"
    if not zip_path.exists():
        download_url = github_meta.get("download_url") or DEFAULT_DOWNLOAD_URL
        with urllib.request.urlopen(download_url, timeout=60) as response:
            with zip_path.open("wb") as handle:
                for chunk in iter(lambda: response.read(1024 * 1024), b""):
                    handle.write(chunk)

    with zipfile.ZipFile(zip_path) as archive:
        members = archive.namelist()
        sqlite_members = [name for name in members if name.endswith(".sqlite3")]
        json_members = [name for name in members if name.endswith(".json")]
        if not sqlite_members:
            raise SystemExit("Downloaded CBDB zip did not contain a SQLite file.")
        sqlite_member = sorted(sqlite_members)[-1]
        archive.extract(sqlite_member, RAW_DIR)
        if json_members:
            zip_meta_name = sorted(json_members)[-1]
            zip_meta = json.loads(archive.read(zip_meta_name).decode("utf-8"))
            (RAW_DIR / "latest_zip.json").write_text(
                json.dumps(zip_meta, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            metadata = zip_meta
        else:
            metadata = github_meta

    sqlite_path = RAW_DIR / sqlite_member
    metadata["sqlite_filename"] = sqlite_path.name
    return sqlite_path, metadata


def write_rows(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def table_count(cur: sqlite3.Cursor, table: str) -> int:
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    return int(cur.fetchone()[0])


def main() -> int:
    download = "--download" in sys.argv
    sqlite_path, metadata = ensure_cbdb_sqlite(download=download)
    sqlite_hash = sha256(sqlite_path)

    con = sqlite3.connect(sqlite_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    schema_rows: list[dict] = []
    cur.execute(
        "SELECT name, type FROM sqlite_master "
        "WHERE type IN ('table', 'view') ORDER BY name"
    )
    for row in cur.fetchall():
        name = row["name"]
        schema_rows.append(
            {
                "object_name": name,
                "object_type": row["type"],
                "row_count": table_count(cur, name) if row["type"] == "table" else "",
            }
        )
    write_rows(
        DIAG_DIR / "cbdb_schema_summary.csv",
        ["object_name", "object_type", "row_count"],
        schema_rows,
    )

    cur.execute(
        """
        SELECT e.c_entry_code,
               e.c_entry_desc,
               e.c_entry_desc_chn,
               GROUP_CONCAT(r.c_entry_type, ';') AS entry_types
        FROM ENTRY_CODES e
        LEFT JOIN ENTRY_CODE_TYPE_REL r ON e.c_entry_code = r.c_entry_code
        WHERE r.c_entry_type IN (?, ?)
        GROUP BY e.c_entry_code, e.c_entry_desc, e.c_entry_desc_chn
        ORDER BY e.c_entry_code
        """,
        (JINSHI_TYPE, JUREN_TYPE),
    )
    entry_rows = [dict(row) for row in cur.fetchall()]
    write_rows(
        DIAG_DIR / "cbdb_exam_entry_codes.csv",
        ["c_entry_code", "c_entry_desc", "c_entry_desc_chn", "entry_types"],
        entry_rows,
    )

    cur.execute(
        """
        WITH preferred_addr AS (
          SELECT c_personid,
                 c_addr_id,
                 c_addr_type,
                 ROW_NUMBER() OVER (
                   PARTITION BY c_personid
                   ORDER BY
                     CASE c_addr_type
                       WHEN 1 THEN 1
                       WHEN 16 THEN 2
                       WHEN 6 THEN 3
                       WHEN 7 THEN 4
                       WHEN 14 THEN 5
                       ELSE 99
                     END,
                     c_sequence
                 ) AS rn
          FROM BIOG_ADDR_DATA
          WHERE c_addr_type IN (1, 16, 6, 7, 14)
            AND c_addr_id IS NOT NULL
            AND c_addr_id > 0
        ),
        elite AS (
          SELECT DISTINCT
                 b.c_personid,
                 b.c_name,
                 b.c_name_chn,
                 b.c_dy,
                 d.c_dynasty,
                 d.c_dynasty_chn,
                 e.c_year,
                 CASE
                   WHEN r.c_entry_type = '040101' THEN 'jinshi'
                   WHEN r.c_entry_type = '040102' THEN 'juren'
                   ELSE 'other'
                 END AS elite_type,
                 pa.c_addr_id,
                 pa.c_addr_type
          FROM ENTRY_DATA e
          JOIN ENTRY_CODE_TYPE_REL r
            ON e.c_entry_code = r.c_entry_code
          JOIN BIOG_MAIN b
            ON e.c_personid = b.c_personid
          LEFT JOIN DYNASTIES d
            ON b.c_dy = d.c_dy
          LEFT JOIN preferred_addr pa
            ON e.c_personid = pa.c_personid AND pa.rn = 1
          WHERE r.c_entry_type IN ('040101', '040102')
            AND b.c_dy IN (19, 20, 80)
        )
        SELECT elite.c_addr_id,
               a.c_name AS addr_name,
               a.c_name_chn AS addr_name_chn,
               a.c_admin_type,
               a.c_admin_cat_code,
               a.x_coord,
               a.y_coord,
               a.CHGIS_PT_ID,
               COUNT(DISTINCT elite.c_personid) AS elite_persons,
               COUNT(DISTINCT CASE WHEN elite.elite_type = 'jinshi'
                    THEN elite.c_personid END) AS jinshi_persons,
               COUNT(DISTINCT CASE WHEN elite.elite_type = 'juren'
                    THEN elite.c_personid END) AS juren_persons,
               COUNT(DISTINCT CASE WHEN elite.c_dy = 19
                    THEN elite.c_personid END) AS ming_persons,
               COUNT(DISTINCT CASE WHEN elite.c_dy IN (20, 80)
                    THEN elite.c_personid END) AS qing_persons,
               MIN(NULLIF(elite.c_year, 0)) AS first_entry_year,
               MAX(NULLIF(elite.c_year, 0)) AS last_entry_year
        FROM elite
        LEFT JOIN ADDR_CODES a
          ON elite.c_addr_id = a.c_addr_id
        WHERE elite.c_addr_id IS NOT NULL
        GROUP BY elite.c_addr_id,
                 a.c_name,
                 a.c_name_chn,
                 a.c_admin_type,
                 a.c_admin_cat_code,
                 a.x_coord,
                 a.y_coord,
                 a.CHGIS_PT_ID
        ORDER BY elite_persons DESC, jinshi_persons DESC, addr_name_chn
        """
    )
    place_rows = [dict(row) for row in cur.fetchall()]
    write_rows(
        OUT_DIR / "cbdb_mingqing_elite_place_counts.csv",
        [
            "c_addr_id",
            "addr_name",
            "addr_name_chn",
            "c_admin_type",
            "c_admin_cat_code",
            "x_coord",
            "y_coord",
            "CHGIS_PT_ID",
            "elite_persons",
            "jinshi_persons",
            "juren_persons",
            "ming_persons",
            "qing_persons",
            "first_entry_year",
            "last_entry_year",
        ],
        place_rows,
    )

    cur.execute(
        """
        WITH preferred_addr AS (
          SELECT c_personid,
                 c_addr_id,
                 ROW_NUMBER() OVER (
                   PARTITION BY c_personid
                   ORDER BY
                     CASE c_addr_type
                       WHEN 1 THEN 1
                       WHEN 16 THEN 2
                       WHEN 6 THEN 3
                       WHEN 7 THEN 4
                       WHEN 14 THEN 5
                       ELSE 99
                     END,
                     c_sequence
                 ) AS rn
          FROM BIOG_ADDR_DATA
          WHERE c_addr_type IN (1, 16, 6, 7, 14)
            AND c_addr_id IS NOT NULL
            AND c_addr_id > 0
        ),
        elite AS (
          SELECT DISTINCT b.c_personid, pa.c_addr_id
          FROM ENTRY_DATA e
          JOIN ENTRY_CODE_TYPE_REL r
            ON e.c_entry_code = r.c_entry_code
          JOIN BIOG_MAIN b
            ON e.c_personid = b.c_personid
          LEFT JOIN preferred_addr pa
            ON e.c_personid = pa.c_personid AND pa.rn = 1
          WHERE r.c_entry_type IN ('040101', '040102')
            AND b.c_dy IN (19, 20, 80)
        )
        SELECT
          COUNT(DISTINCT c_personid) AS elite_persons_total,
          COUNT(DISTINCT CASE WHEN c_addr_id IS NOT NULL THEN c_personid END)
            AS elite_persons_with_preferred_addr,
          COUNT(DISTINCT CASE WHEN c_addr_id IS NULL THEN c_personid END)
            AS elite_persons_without_preferred_addr
        FROM elite
        """
    )
    coverage = dict(cur.fetchone())
    write_rows(
        DIAG_DIR / "cbdb_elite_address_coverage.csv",
        [
            "elite_persons_total",
            "elite_persons_with_preferred_addr",
            "elite_persons_without_preferred_addr",
        ],
        [coverage],
    )

    metadata_row = {
        "source": "CBDB SQLite",
        "sqlite_file": sqlite_path.name,
        "sqlite_sha256": sqlite_hash,
        "metadata_sha256": metadata.get("sha256", ""),
        "generated_at_utc": metadata.get("generated_at_utc", ""),
        "download_url": metadata.get("download_url")
        or metadata.get("huggingface_url", "")
        or DEFAULT_DOWNLOAD_URL,
        "person_rows": table_count(cur, "BIOG_MAIN"),
        "entry_rows": table_count(cur, "ENTRY_DATA"),
        "place_count_rows": len(place_rows),
        "elite_persons_total": coverage["elite_persons_total"],
        "elite_persons_with_preferred_addr": coverage[
            "elite_persons_with_preferred_addr"
        ],
        "elite_persons_without_preferred_addr": coverage[
            "elite_persons_without_preferred_addr"
        ],
        "note": (
            "Counts use Ming, Qing, and Southern Ming biography dynasties; "
            "entry types 040101 and 040102; preferred address types 1, 16, 6, "
            "7, and 14. Join to contemporary prefectures is not yet complete."
        ),
    }
    write_rows(
        DIAG_DIR / "cbdb_release_metadata.csv",
        list(metadata_row.keys()),
        [metadata_row],
    )

    print(f"sqlite={sqlite_path}")
    print(f"schema_rows={len(schema_rows)}")
    print(f"exam_entry_codes={len(entry_rows)}")
    print(f"place_count_rows={len(place_rows)}")
    print(f"output={OUT_DIR / 'cbdb_mingqing_elite_place_counts.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
