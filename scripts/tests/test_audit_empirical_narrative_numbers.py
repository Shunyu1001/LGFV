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
    def test_current_manuscript_matches_all_registered_quantities(self) -> None:
        rows, summary = audit()
        self.assertEqual(summary["claims_audited"], 43)
        self.assertEqual(summary["match"], 43)
        self.assertEqual(summary["mismatch"], 0)
        self.assertEqual(summary["missing_text"], 0)
        self.assertEqual(summary["ambiguous_text"], 0)
        self.assertEqual(summary["mismatch_claim_ids"], [])
        self.assertTrue(all(row["status"] == "match" for row in rows))

    def test_check_mode_returns_zero_for_consistent_manuscript(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0)
        summary = json.loads(completed.stdout)
        self.assertEqual(summary["match"], 43)

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
            summary = json.loads(summary_path.read_text())
            self.assertEqual(summary["claims_audited"], 43)
            self.assertEqual(summary["match"], 43)


if __name__ == "__main__":
    unittest.main()
