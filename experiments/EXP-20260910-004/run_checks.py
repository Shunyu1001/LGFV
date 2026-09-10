#!/usr/bin/env python3
"""Record every bounded evaluation command without changing global ledgers."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
COMMANDS = [
    ["python3", "scripts/build_validation_collection_package.py"],
    ["python3", "scripts/build_validation_collection_package.py", "--check"],
    ["python3", "-m", "unittest", "discover", "-s", "tests", "-p", "test_validation_collection_package.py", "-v"],
    ["python3", "scripts/build_human_confirmation_register.py", "--check"],
    ["python3", "scripts/validate_immutable.py"],
    ["python3", "scripts/validate_ledgers.py"],
    ["python3", "scripts/validate_labels.py"],
    ["python3", "scripts/validate_master_case_pool.py"],
    ["git", "diff", "--check"],
    ["git", "status", "--short"],
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", type=int, choices=(1, 2, 3), required=True)
    args = parser.parse_args()
    destination = OUT / f"attempt_{args.attempt}.json"
    if destination.exists():
        raise SystemExit("Attempt already recorded; do not overwrite history")
    if args.attempt > 1 and not (OUT / f"attempt_{args.attempt - 1}.json").exists():
        raise SystemExit("Prior attempt record required")
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    report = {"attempt": args.attempt, "base_commit": "4330c5728dec64ba30c1faec972fad0097622e9d",
              "execution_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "environment": {"PYTHONDONTWRITEBYTECODE": "1"}, "commands": []}
    for command in COMMANDS:
        completed = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True)
        report["commands"].append({"command": command, "returncode": completed.returncode,
                                   "stdout": completed.stdout, "stderr": completed.stderr})
        destination.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(f"exit={completed.returncode}: {' '.join(command)}", flush=True)
        if completed.returncode:
            print(completed.stdout + completed.stderr, flush=True)
    failed = sum(c["returncode"] != 0 for c in report["commands"])
    print(f"attempt={args.attempt}; failed_commands={failed}; log={destination}")
    return bool(failed)


if __name__ == "__main__":
    sys.exit(main())
