"""Read-only numeric, scope, and standalone-layout checks for coordinator review."""

import csv
import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
REL = HERE.relative_to(ROOT)
BASE = "4330c5728dec64ba30c1faec972fad0097622e9d"


def main():
    target = HERE / "delivery_verification.json"
    if target.exists():
        raise SystemExit("Do not overwrite delivery verification")
    report = {"commands": []}
    commands = [
        ["python3", "-m", "unittest", "discover", "-s", "tests", "-p", "test_human_confirmation.py", "-v"],
        ["latexmk", "-g", "-pdf", "-interaction=nonstopmode", "-halt-on-error",
         f"-outdir={REL}", str(REL / "table_preview.tex")],
        ["pdftoppm", "-scale-to", "1600", "-png", "-singlefile", str(REL / "table_preview.pdf"), str(REL / "table_preview")],
        ["python3", "scripts/build_validation_identification_bounds.py", "--check"],
        ["git", "diff", "--check"],
    ]
    for command in commands:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        report["commands"].append({"command": command, "returncode": result.returncode,
                                   "stdout": result.stdout, "stderr": result.stderr})
        target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(" ".join(command), "=>", result.returncode, flush=True)
        if result.returncode:
            raise SystemExit(result.returncode)
    rows = list(csv.DictReader((ROOT / "data/analysis_inputs/validation_identification_bounds.csv").open()))
    for row in rows:
        n, k, j, u = (int(row[f]) for f in ("n", "known_positive", "known_negative", "unknown"))
        assert n == k + j + u
        assert int(row["lower_numerator"]) == k
        assert int(row["upper_numerator"]) == n - j
        assert abs(Fraction(row["lower"]) - Fraction(k, n)) <= Fraction(1, 10**12)
        assert abs(Fraction(row["upper"]) - Fraction(n - j, n)) <= Fraction(1, 10**12)
    original = subprocess.run(["git", "ls-tree", "-r", "--name-only", BASE], cwd=ROOT,
                              capture_output=True, text=True, check=True).stdout.splitlines()
    mismatches = []
    for relative in original:
        expected = subprocess.run(["git", "show", f"{BASE}:{relative}"], cwd=ROOT,
                                  capture_output=True, check=True).stdout
        path = ROOT / relative
        if not path.exists() or hashlib.sha256(path.read_bytes()).digest() != hashlib.sha256(expected).digest():
            mismatches.append(relative)
    assert not mismatches, mismatches
    log = (HERE / "table_preview.log").read_text()
    warnings = [line for line in log.splitlines() if "Overfull" in line or "Underfull" in line]
    assert not warnings, warnings
    report.update({"bound_rows_independently_recomputed": len(rows), "unchanged_base_files": len(original),
                   "base_file_mismatches": mismatches, "standalone_table_box_warnings": warnings,
                   "full_manuscript_build_executed": False})
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("delivery_verification=passed", flush=True)


if __name__ == "__main__":
    main()
