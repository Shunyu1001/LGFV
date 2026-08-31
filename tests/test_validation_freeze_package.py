import csv
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def rows(path: str):
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class ValidationFreezePackageTests(unittest.TestCase):
    def test_validator_passes_without_temporary_caches(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_validation_freeze_package.py")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_exact_evidence_gate_counts(self):
        decisions = rows("experiments/EXP-20260831-002/case_decisions.csv")
        decisions += rows("experiments/EXP-20260831-003/case_decisions.csv")
        self.assertEqual(len(decisions), 4)
        self.assertEqual(
            Counter(row["evidence_disposition"] for row in decisions),
            Counter({"resolved_existing_rule": 3, "unresolved_rule_required": 1}),
        )
        self.assertTrue(all(row["integrated_into_registered_frame"] == "false" for row in decisions))

    def test_registered_frame_remains_quarantined(self):
        unresolved = rows("data/validation/probability_validation_unresolved_log.csv")
        self.assertEqual(len(unresolved), 4)
        self.assertEqual(len({row["validation_unit_id"] for row in unresolved}), 3)

    def test_no_draw_and_no_raw_source_commit(self):
        for experiment in ("EXP-20260831-002", "EXP-20260831-003"):
            metrics = json.loads((ROOT / "experiments" / experiment / "metrics.json").read_text())
            self.assertFalse(metrics["random_draw_executed"])
            self.assertFalse(metrics["raw_sources_committed"])
            self.assertEqual(metrics["integrated_registered_frame_gates_closed"], 0)
            self.assertFalse(list((ROOT / "experiments" / experiment).rglob("*.pdf")))

    def test_change_request_and_rebuild_are_prospective(self):
        change_request = (ROOT / "change_requests/CR-20260831-001.md").read_text()
        self.assertIn("Status: proposed; PI decision required", change_request)
        self.assertIn("Implemented: no", change_request)
        rebuild = (ROOT / "experiments/EXP-20260831-004/brief.md").read_text()
        self.assertIn("Status: prospective; not executed", rebuild)
        self.assertIn("Do not execute this experiment", rebuild)

    def test_codex_is_not_described_as_human_validation(self):
        memo = (ROOT / "experiments/EXP-20260831-003/freeze_decision_memo.md").read_text()
        self.assertIn("not independent\nhuman validation", memo)


if __name__ == "__main__":
    unittest.main()
