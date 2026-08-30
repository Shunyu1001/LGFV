from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "audit_empirical_narrative_numbers.py"
sys.path.insert(0, str(ROOT / "scripts"))

from audit_empirical_narrative_numbers import audit  # noqa: E402


class EmpiricalNarrativeNumberAuditTest(unittest.TestCase):
    def test_current_manuscript_has_only_recorded_coefficient_mismatches(self) -> None:
        rows, summary = audit()
        self.assertEqual(summary["claims_audited"], 33)
        self.assertEqual(summary["match"], 30)
        self.assertEqual(summary["mismatch"], 3)
        self.assertEqual(summary["missing_text"], 0)
        self.assertEqual(summary["ambiguous_text"], 0)
        self.assertEqual(
            set(summary["mismatch_claim_ids"]),
            {
                "elite_density_effect_pp",
                "high_capacity_effect_pp",
                "capacity_rank_effect_pp",
            },
        )
        mismatch_values = {
            row["claim_id"]: (row["reported_value"], row["generated_value"])
            for row in rows
            if row["status"] == "mismatch"
        }
        self.assertEqual(mismatch_values["elite_density_effect_pp"], ("6.3", "6.6"))
        self.assertEqual(mismatch_values["high_capacity_effect_pp"], ("17.1", "16.1"))
        self.assertEqual(mismatch_values["capacity_rank_effect_pp"], ("13.5", "12.5"))

    def test_check_mode_returns_nonzero_for_traceable_mismatches(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 1)
        summary = json.loads(completed.stdout)
        self.assertEqual(summary["mismatch"], 3)

    def test_report_files_are_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "audit.csv"
            summary_path = Path(tmp) / "audit.json"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output",
                    str(output),
                    "--summary",
                    str(summary_path),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertTrue(output.exists())
            self.assertEqual(json.loads(summary_path.read_text())["claims_audited"], 33)


if __name__ == "__main__":
    unittest.main()
