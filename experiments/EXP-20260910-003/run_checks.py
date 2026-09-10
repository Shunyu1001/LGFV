"""Record every fixed verification command for the human-confirmation update."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parent
PYTHON = sys.executable
commands = [
    [PYTHON, "scripts/build_human_confirmation_register.py", "--check"],
    [PYTHON, "-m", "unittest", "discover", "-s", "tests", "-p", "test_human_confirmation.py"],
    [PYTHON, "-m", "unittest", "discover", "-s", "tests", "-p", "test_label_role_builders.py"],
    *[[PYTHON, f"scripts/{name}.py"] for name in (
        "validate_immutable", "validate_ledgers", "validate_labels", "validate_master_case_pool"
    )],
    [PYTHON, "scripts/build_llm_screening_sample.py",
     "--input", "data/analysis_inputs/codex_surrogate_labels_2026_07_03_expanded.csv",
     "--output", "data/analysis_inputs/llm_screening_sample_2026_07_03_expanded.csv",
     "--summary", "data/analysis_inputs/llm_screening_summary_2026_07_03_expanded.csv"],
    [PYTHON, "scripts/build_pilot_capacity_summary.py"],
    [PYTHON, "scripts/build_pilot_empirical_models.py"],
    [PYTHON, "scripts/build_dsl_surrogate_adjustment.py", "--issuers",
     "data/analysis_inputs/codex_surrogate_issuer_summary_2026_07_03_expanded.csv"],
    [PYTHON, "scripts/build_surrogate_empirical_core.py"],
    [PYTHON, "scripts/build_empirical_case_panel.py"],
    [PYTHON, "scripts/build_controlled_empirical_models.py"],
    [PYTHON, "scripts/validate_label_role_rebuild.py"],
    [PYTHON, "-m", "unittest", "discover", "-s", "tests", "-p", "test_probability_validation_frame.py"],
    [PYTHON, "scripts/validate_probability_validation_frame.py", "--source-dir",
     "/Users/shunyuhao/Documents/LGFV/data/raw/probability_validation_sources"],
    ["latexmk", "-g", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "paper/main.tex"],
]


def main():
    index = 1
    while (EXP / f"checks_attempt_{index}.json").exists():
        index += 1
    path = EXP / f"checks_attempt_{index}.json"
    report = {"started_at": datetime.now(timezone.utc).isoformat(), "commands": []}
    env = dict(os.environ)
    env["PATH"] = "/Users/shunyuhao/Library/TinyTeX/bin/universal-darwin:" + env.get("PATH", "")
    # Inputs are resolved under paper/ when compiling from the repository root.
    env["TEXINPUTS"] = str(ROOT / "paper") + "//:" + env.get("TEXINPUTS", "")
    env["BIBINPUTS"] = str(ROOT / "paper") + ":" + env.get("BIBINPUTS", "")
    for command in commands:
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True)
        report["commands"].append({
            "command": command, "returncode": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr,
        })
        path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"{result.returncode}: {' '.join(command)}", flush=True)
    failures = sum(item["returncode"] != 0 for item in report["commands"])
    print(f"failures={failures}; log={path.relative_to(ROOT)}")
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
