#!/usr/bin/env python3
"""Inspect locally downloaded CHGIS archives.

Harvard Dataverse may block automated downloads. This script assumes CHGIS zip
files have been downloaded manually into data/raw/historical/chgis. It lists
archive contents and, where possible, reads shapefile DBF headers without
requiring geopandas or shapely. The output is a small CSV that helps decide
which layers can support Qing administrative-density measures.
"""

from __future__ import annotations

import csv
import struct
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "historical" / "chgis"
DIAG_DIR = ROOT / "data" / "diagnostics"


def read_dbf_fields(data: bytes) -> list[dict]:
    """Return DBF field descriptors from raw bytes."""
    if len(data) < 32:
        return []
    header_len = struct.unpack("<H", data[8:10])[0]
    fields = []
    offset = 32
    while offset + 32 <= min(header_len, len(data)):
        descriptor = data[offset : offset + 32]
        if descriptor[0] == 0x0D:
            break
        name = descriptor[:11].split(b"\x00", 1)[0].decode("latin1", errors="replace")
        field_type = chr(descriptor[11])
        length = descriptor[16]
        decimal_count = descriptor[17]
        fields.append(
            {
                "field_name": name,
                "field_type": field_type,
                "field_length": length,
                "decimal_count": decimal_count,
            }
        )
        offset += 32
    return fields


def write_rows(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    DIAG_DIR.mkdir(parents=True, exist_ok=True)

    archive_rows: list[dict] = []
    field_rows: list[dict] = []

    for zip_path in sorted(RAW_DIR.glob("*.zip")):
        with zipfile.ZipFile(zip_path) as archive:
            for info in archive.infolist():
                suffix = Path(info.filename).suffix.lower()
                archive_rows.append(
                    {
                        "archive": zip_path.name,
                        "member": info.filename,
                        "suffix": suffix,
                        "file_size": info.file_size,
                    }
                )
                if suffix == ".dbf":
                    fields = read_dbf_fields(archive.read(info.filename))
                    stem = str(Path(info.filename).with_suffix(""))
                    for field in fields:
                        row = {
                            "archive": zip_path.name,
                            "layer": stem,
                            **field,
                        }
                        field_rows.append(row)

    write_rows(
        DIAG_DIR / "chgis_archive_inventory.csv",
        ["archive", "member", "suffix", "file_size"],
        archive_rows,
    )
    write_rows(
        DIAG_DIR / "chgis_dbf_fields.csv",
        [
            "archive",
            "layer",
            "field_name",
            "field_type",
            "field_length",
            "decimal_count",
        ],
        field_rows,
    )

    print(f"archives={len(list(RAW_DIR.glob('*.zip')))}")
    print(f"archive_members={len(archive_rows)}")
    print(f"dbf_fields={len(field_rows)}")
    if not archive_rows:
        print(
            "No CHGIS zip files found. Download CHGIS V6 1820 and 1911 time "
            "slices into data/raw/historical/chgis, then re-run this script."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
