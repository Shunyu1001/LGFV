"""Verify source renewal, prior-result preservation, and reproducible frame outputs."""

import csv
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
PRIOR = "cfee3b9"
FILES = ["geography_scope_crosswalk", "unresolved_log", "source_manifest", "frame_candidate", "frame_origin_rows", "frame_flow", "sampling_design"]
OUTPUTS = [f"data/validation/probability_validation_{name}.csv" for name in FILES]
OUTPUTS.append("experiments/EXP-20260910-002/metrics.json")
BUILD = [sys.executable, "scripts/build_probability_validation_frame.py", "--integrate-exp004", "--renew-source"]


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def hashes(root):
    return {path: sha((root / path).read_bytes()) for path in OUTPUTS}


def archive_sources():
    def rows(relative):
        with (ROOT / relative).open(newline="") as handle:
            return list(csv.DictReader(handle))
    crosswalk = rows("data/validation/probability_validation_geography_scope_crosswalk.csv")
    used = {(row["validation_unit_id"], row[f"{prefix}_document_id"]) for row in crosswalk for prefix in ("identity", "geography", "owner", "role")}
    manifest = [row for row in rows("data/validation/probability_validation_source_manifest.csv") if (row["validation_unit_id"], row["document_id"]) in used]
    destination = Path("/Users/shunyuhao/Documents/LGFV/data/raw/probability_validation_sources")
    destination.mkdir(parents=True, exist_ok=True)
    records = []
    for row in manifest:
        for field, hash_field in (("raw_cache_filename", "sha256"), ("text_cache_filename", "source_text_sha256")):
            if not row[field]:
                continue
            source = Path("/tmp/lgfv-exp015-sources") / row[field]
            target = destination / row[field]
            assert sha(source.read_bytes()) == row[hash_field]
            if target.exists():
                assert sha(target.read_bytes()) == row[hash_field], "Refusing to overwrite an existing source"
            else:
                shutil.copy2(source, target)
            assert sha(target.read_bytes()) == row[hash_field]
            records.append({"document_id": row["document_id"], "filename": row[field], "sha256": row[hash_field]})
    return {"directory": str(destination), "cited_sources": len(manifest), "verified_cache_files": records, "raw_files_committed": False}


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

    run(BUILD)
    report["integrated_hashes"] = hashes(ROOT)
    run(BUILD)
    report["rerun_identical"] = hashes(ROOT) == report["integrated_hashes"]
    invariant_paths = [f"data/validation/probability_validation_{name}.csv" for name in ("frame_candidate", "frame_origin_rows", "frame_flow", "sampling_design")]
    invariant_paths += subprocess.check_output(["git", "ls-tree", "-r", "--name-only", PRIOR, "experiments/EXP-20260910-001"], cwd=ROOT, text=True).splitlines()
    report["prior_artifact_hashes"] = {}
    for path in invariant_paths:
        expected = subprocess.check_output(["git", "show", f"{PRIOR}:{path}"], cwd=ROOT)
        report["prior_artifact_hashes"][path] = {"expected": sha(expected), "observed": sha((ROOT / path).read_bytes())}
    report["prior_artifacts_unchanged"] = all(row["expected"] == row["observed"] for row in report["prior_artifact_hashes"].values())
    with tempfile.TemporaryDirectory(prefix="lgfv-renewal-") as tmp:
        clean = Path(tmp) / "clean"
        run(["git", "clone", "--quiet", "--shared", "--no-checkout", str(ROOT), str(clean)])
        run(["git", "checkout", "--quiet", "--detach", BASE], clean)
        inputs = ["scripts/build_probability_validation_frame.py", "experiments/EXP-20260910-002/brief.md", "experiments/EXP-20260910-002/renewed_source_manifest.csv", "experiments/EXP-20260910-002/crosswalk_evidence_patch.json"]
        for relative in inputs:
            target = clean / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        run(BUILD, clean)
        report["clean_reconstruction_hashes"] = hashes(clean)
        report["clean_reconstruction_identical"] = hashes(clean) == report["integrated_hashes"]
    commands = [
        [sys.executable, "scripts/validate_probability_validation_frame.py"],
        [sys.executable, "scripts/validate_validation_freeze_package.py"],
        *([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", f"test_{name}.py", "-v"] for name in ("probability_validation_frame", "validation_freeze_package")),
        *([sys.executable, f"scripts/{name}.py"] for name in ("validate_immutable", "validate_ledgers", "validate_labels", "validate_master_case_pool")),
    ]
    for command in commands:
        run(command)
    report["all_passed"] = all(row["returncode"] == 0 for row in report["commands"]) and report["rerun_identical"] and report["clean_reconstruction_identical"] and report["prior_artifacts_unchanged"]
    if report["all_passed"]:
        archive = archive_sources()
        archive_path = OUT / f"source_archive_attempt_{attempt}.json"
        archive_path.write_text(json.dumps(archive, ensure_ascii=False, indent=2) + "\n")
        report["archive_manifest"] = archive_path.name
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    (OUT / f"audit_attempt_{attempt}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"attempt": attempt, "all_passed": report["all_passed"], "rerun_identical": report["rerun_identical"], "clean_reconstruction_identical": report["clean_reconstruction_identical"], "prior_artifacts_unchanged": report["prior_artifacts_unchanged"], "commands": [{"args": row["args"], "returncode": row["returncode"], "stderr_tail": row["stderr"][-1200:]} for row in report["commands"]]}, ensure_ascii=False))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
