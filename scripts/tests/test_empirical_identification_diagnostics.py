from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from build_empirical_identification_diagnostics import run  # noqa: E402


class EmpiricalIdentificationDiagnosticsTest(unittest.TestCase):
    def test_outputs_are_complete_and_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as first_tmp, tempfile.TemporaryDirectory() as second_tmp:
            first = Path(first_tmp)
            second = Path(second_tmp)
            first_summary = run(output_dir=first)
            second_summary = run(output_dir=second)

            self.assertEqual(first_summary["matched_gold"]["observations"], 84)
            self.assertEqual(first_summary["matched_gold"]["events"], 12)
            self.assertEqual(first_summary["complete_control_subset"]["observations"], 78)
            self.assertTrue(
                first_summary["baseline_reproduction"]["matches_at_pilot_precision"]
            )
            self.assertFalse(first_summary["selection_by_sign_or_significance"])

            expected_files = {
                "sample_outcome_diagnostics.csv",
                "control_missingness.csv",
                "sample_selection_diagnostics.csv",
                "excluded_matched_gold_cases.csv",
                "functional_form_sensitivity.csv",
                "design_alias_diagnostics.csv",
                "leave_one_out_influence.csv",
                "diagnostic_summary.json",
            }
            self.assertEqual({path.name for path in first.iterdir()}, expected_files)
            self.assertEqual({path.name for path in second.iterdir()}, expected_files)
            for filename in expected_files:
                self.assertEqual((first / filename).read_bytes(), (second / filename).read_bytes())

            with (first / "functional_form_sensitivity.csv").open(
                newline="", encoding="utf-8"
            ) as handle:
                model_rows = list(csv.DictReader(handle))
            self.assertEqual(len(model_rows), 9)
            self.assertEqual({row["method"] for row in model_rows}, {"lpm", "logit", "firth_logit"})
            self.assertEqual(
                {row["specification"] for row in model_rows},
                {
                    "matched_gold_historical_only",
                    "complete_control_historical_only",
                    "complete_control_full_available_controls",
                },
            )

            with (first / "design_alias_diagnostics.csv").open(
                newline="", encoding="utf-8"
            ) as handle:
                alias_rows = list(csv.DictReader(handle))
            full_controls_alias = next(
                row
                for row in alias_rows
                if row["specification"] == "complete_control_full_available_controls"
            )
            self.assertEqual(full_controls_alias["rank_deficient"], "True")
            self.assertIn("intercept equals", full_controls_alias["identified_exact_alias"])

            stored_summary = json.loads((first / "diagnostic_summary.json").read_text())
            self.assertEqual(stored_summary, first_summary)


if __name__ == "__main__":
    unittest.main()
