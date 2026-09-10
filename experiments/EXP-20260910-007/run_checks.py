#!/usr/bin/env python3
"""Retain each verification attempt without replacing earlier results."""

import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PYTHON = sys.executable


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["baseline", "integrated", "build"], required=True)
    args = parser.parse_args()
    commands = {
        "baseline": [
            [PYTHON, "scripts/validate_immutable.py"],
            [PYTHON, "scripts/build_human_confirmation_register.py", "--check"],
            [PYTHON, "scripts/validate_probability_validation_frame.py", "--source-dir",
             "/Users/shunyuhao/Documents/LGFV/data/raw/probability_validation_sources"],
            [PYTHON, "scripts/build_sparse_outcome_model_audit.py", "--output-dir",
             str(OUT / "sparse_outcome")],
            [PYTHON, "scripts/validate_label_role_rebuild.py"],
        ],
        "integrated": [
            [PYTHON, "scripts/build_validation_collection_package.py", "--check"],
            [PYTHON, "scripts/build_validation_identification_bounds.py", "--check"],
            [PYTHON, "-m", "unittest", "discover", "-s", "tests", "-p", "test_validation_collection_package.py"],
            [PYTHON, "-m", "unittest", "discover", "-s", "tests", "-p", "test_design_based_validation.py"],
            [PYTHON, "-m", "unittest", "discover", "-s", "tests", "-p", "test_validation_identification_bounds.py"],
            [PYTHON, "scripts/build_validation_inference_status.py"],
            [PYTHON, "-m", "unittest", "discover", "-s", "tests", "-p", "test_validation_inference_status.py"],
            [PYTHON, "scripts/validate_immutable.py"],
            [PYTHON, "scripts/validate_ledgers.py"],
            [PYTHON, "scripts/build_human_confirmation_register.py", "--check"],
            [PYTHON, "scripts/validate_label_role_rebuild.py"],
            [PYTHON, "-m", "unittest", "discover", "-s", "tests"],
            ["git", "diff", "--check"],
        ],
        "build": [["latexmk", "-g", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "paper/main.tex"]],
    }[args.phase]
    env = os.environ.copy()
    env["PATH"] = "/Users/shunyuhao/Library/TinyTeX/bin/universal-darwin:" + env["PATH"]
    env["TEXINPUTS"] = str(ROOT / "paper") + "//:"
    env["BIBINPUTS"] = str(ROOT / "paper") + ":"
    result = {"phase": args.phase, "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "commands": []}
    attempt = 1
    while (OUT / f"checks_{args.phase}_{attempt}.json").exists():
        attempt += 1
    destination = OUT / f"checks_{args.phase}_{attempt}.json"
    for command in commands:
        process = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True)
        result["commands"].append({"command": command, "returncode": process.returncode,
                                   "stdout": process.stdout, "stderr": process.stderr})
        destination.write_text(json.dumps(result, indent=2) + "\n")
        print(f"{process.returncode}: {' '.join(command)}", flush=True)
    failures = sum(row["returncode"] != 0 for row in result["commands"])
    print(f"failures={failures}; log={destination.relative_to(ROOT)}", flush=True)
    return bool(failures)


if __name__ == "__main__":
    sys.exit(main())
