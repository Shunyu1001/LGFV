"""Record current checks and compare a clean reconstruction with an idempotent run."""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BASE = "9977dd752f911bfd07dc4d434301041ef485c9f2"
OUTPUTS = [
    "data/validation/probability_validation_geography_scope_crosswalk.csv",
    "data/validation/probability_validation_unresolved_log.csv",
    "data/validation/probability_validation_source_manifest.csv",
    "data/validation/probability_validation_frame_candidate.csv",
    "data/validation/probability_validation_frame_origin_rows.csv",
    "data/validation/probability_validation_frame_flow.csv",
    "data/validation/probability_validation_sampling_design.csv",
    "experiments/EXP-20260910-001/metrics.json",
]


def hashes(root):
    return {path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in OUTPUTS}


def main():
    attempt = 1
    while (OUT / f"audit_attempt_{attempt}.json").exists():
        attempt += 1
    report = {"started_at": datetime.now(timezone.utc).isoformat(), "commands": []}

    def run(args, cwd=ROOT):
        result = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
        report["commands"].append({"args": args, "cwd": str(cwd), "returncode": result.returncode,
                                   "stdout": result.stdout, "stderr": result.stderr})
        return result.returncode

    run([sys.executable, "scripts/build_probability_validation_frame.py", "--integrate-exp004"])
    report["integrated_hashes"] = hashes(ROOT)
    run([sys.executable, "scripts/build_probability_validation_frame.py", "--integrate-exp004"])
    report["rerun_identical"] = hashes(ROOT) == report["integrated_hashes"]
    with tempfile.TemporaryDirectory(prefix="lgfv-exp20260910-") as tmp:
        clean = Path(tmp) / "clean"
        run(["git", "clone", "--quiet", "--shared", "--no-checkout", str(ROOT), str(clean)])
        run(["git", "checkout", "--quiet", "--detach", BASE], clean)
        for relative in ("scripts/build_probability_validation_frame.py", "experiments/EXP-20260910-001/brief.md"):
            target = clean / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        run([sys.executable, "scripts/build_probability_validation_frame.py", "--integrate-exp004"], clean)
        report["clean_reconstruction_hashes"] = hashes(clean)
        report["clean_reconstruction_identical"] = hashes(clean) == report["integrated_hashes"]
    commands = [
        [sys.executable, "scripts/validate_probability_validation_frame.py"],
        [sys.executable, "scripts/validate_validation_freeze_package.py"],
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_probability_validation_frame.py", "-v"],
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_validation_freeze_package.py", "-v"],
        *([sys.executable, f"scripts/{name}.py"] for name in (
            "validate_immutable", "validate_ledgers", "validate_labels", "validate_master_case_pool")),
    ]
    for command in commands:
        run(command)
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    report["all_passed"] = all(row["returncode"] == 0 for row in report["commands"]) and report["rerun_identical"] and report["clean_reconstruction_identical"]
    (OUT / f"audit_attempt_{attempt}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"attempt": attempt, "all_passed": report["all_passed"], "rerun_identical": report["rerun_identical"], "clean_reconstruction_identical": report["clean_reconstruction_identical"], "commands": [{"args": row["args"], "returncode": row["returncode"], "stderr_tail": row["stderr"][-1000:]} for row in report["commands"]]}, ensure_ascii=False))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
