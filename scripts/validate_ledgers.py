#!/usr/bin/env python3
"""Run lightweight schema and reference checks for autoresearch ledgers."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGERS = ROOT / "ledgers"

REQUIRED = {
    "experiments.tsv": {"experiment_id", "loop", "base_commit", "status", "artifact_path"},
    "claims.csv": {"claim_id", "claim_text", "claim_type", "importance", "status"},
    "literature.csv": {"source_id", "title", "verification_status"},
    "reviewer_issues.tsv": {"issue_id", "severity", "issue", "status", "owner"},
    "change_requests.tsv": {"change_request_id", "object", "status"},
}

ALLOWED_EXPERIMENT_STATUS = {"keep", "discard", "quarantine", "crash", "invalid"}


def rows(path: Path) -> list[dict[str, str]]:
    delimiter = "\t" if path.suffix == ".tsv" else ","
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def main() -> int:
    errors: list[str] = []
    seen: dict[str, set[str]] = {}
    for name, required in REQUIRED.items():
        path = LEDGERS / name
        if not path.exists():
            errors.append(f"missing ledger: {name}")
            continue
        ledger_rows = rows(path)
        fieldnames = set(ledger_rows[0].keys()) if ledger_rows else set(
            next(csv.reader(path.open(encoding="utf-8"), delimiter="\t" if path.suffix == ".tsv" else ","))
        )
        missing = required - fieldnames
        if missing:
            errors.append(f"{name}: missing columns {sorted(missing)}")
        id_field = next((field for field in fieldnames if field.endswith("_id")), None)
        if id_field:
            ids = [row.get(id_field, "") for row in ledger_rows if row.get(id_field, "")]
            if len(ids) != len(set(ids)):
                errors.append(f"{name}: duplicate {id_field}")
            seen[name] = set(ids)

    experiment_rows = rows(LEDGERS / "experiments.tsv")
    for row in experiment_rows:
        if row.get("status") not in ALLOWED_EXPERIMENT_STATUS:
            errors.append(f"experiments.tsv: invalid status {row.get('status')}")
        artifact = row.get("artifact_path", "")
        if artifact and not (ROOT / artifact).exists():
            errors.append(f"experiments.tsv: missing artifact path {artifact}")

    if errors:
        raise SystemExit("\n".join(errors))
    print("ledger_validation=ok")
    for name in sorted(REQUIRED):
        print(f"{name}={len(rows(LEDGERS / name))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
