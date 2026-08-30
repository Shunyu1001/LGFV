#!/usr/bin/env python3
"""Validate the tracked immutable research-control files."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "immutable" / "frozen_checksums.sha256"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    if not MANIFEST.exists():
        raise SystemExit("Missing immutable/frozen_checksums.sha256")

    errors: list[str] = []
    checked = 0
    for raw_line in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        expected, relative = line.split(maxsplit=1)
        path = ROOT / relative
        if not path.exists():
            errors.append(f"missing: {relative}")
            continue
        observed = sha256(path)
        if observed != expected:
            errors.append(f"checksum mismatch: {relative}")
        checked += 1

    if errors:
        raise SystemExit("\n".join(errors))
    print("immutable_validation=ok")
    print(f"files={checked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
