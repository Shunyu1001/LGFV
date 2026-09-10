"""Append-only local attempts; never writes the shared experiment ledger."""

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
COMMANDS = [
    ["python3", "scripts/build_validation_identification_bounds.py"],
    ["python3", "scripts/build_validation_identification_bounds.py", "--check"],
    ["python3", "-m", "unittest", "discover", "-s", "tests", "-p", "test_validation_identification_bounds.py", "-v"],
    ["python3", "scripts/validate_immutable.py"],
    ["python3", "scripts/validate_ledgers.py"],
    ["python3", "scripts/validate_labels.py"],
    ["python3", "scripts/validate_master_case_pool.py"],
    ["git", "diff", "--check"],
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("attempt", type=int)
    args = parser.parse_args()
    target = HERE / f"checks_attempt_{args.attempt}.json"
    if target.exists():
        raise SystemExit("Attempt already exists; do not overwrite audit history")
    record = {"attempt": args.attempt, "started_utc": datetime.now(timezone.utc).isoformat(), "commands": []}
    for command in COMMANDS:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        record["commands"].append({"command": command, "returncode": result.returncode,
                                   "stdout": result.stdout, "stderr": result.stderr})
        target.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print(" ".join(command), "=>", result.returncode, flush=True)
        if result.returncode:
            print(result.stdout + result.stderr, flush=True)
            raise SystemExit(result.returncode)
    print(f"Recorded {target.name}")


if __name__ == "__main__":
    main()
