from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from build_sparse_outcome_model_audit import MODEL_IDS, run  # noqa: E402


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class SparseOutcomeModelAuditTest(unittest.TestCase):
    def test_fixed_audit_is_complete_and_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as first_tmp, tempfile.TemporaryDirectory() as second_tmp:
            first = Path(first_tmp)
            second = Path(second_tmp)
            first_summary = run(output_dir=first)
            second_summary = run(output_dir=second)

            self.assertEqual(first_summary, second_summary)
            self.assertEqual(first_summary["model_ids"], MODEL_IDS)
            self.assertFalse(first_summary["selection_by_sign_or_significance"])
            self.assertTrue(first_summary["baseline_reproduction"]["matches_at_pilot_precision"])
            self.assertEqual(first_summary["frozen_estimand"]["matched_gold_observations"], 84)
            self.assertEqual(first_summary["frozen_estimand"]["matched_gold_events"], 12)
            self.assertEqual(first_summary["frozen_estimand"]["complete_control_observations"], 78)
            self.assertEqual(first_summary["frozen_estimand"]["complete_control_events"], 12)

            expected_files = {
                "audit_summary.json",
                "coefficient_estimates.csv",
                "excluded_complete_control_cases.csv",
                "exploratory_sparse_outcome_coefficients.png",
                "exploratory_sparse_outcome_table.tex",
                "influential_cases.csv",
                "leave_one_out_influence.csv",
                "leave_one_out_summary.csv",
                "model_diagnostics.csv",
                "province_event_allocation.csv",
                "province_feasibility.csv",
                "rank_repair_diagnostics.csv",
                "sample_flow.csv",
                "sample_selection_diagnostics.csv",
            }
            self.assertEqual({path.name for path in first.iterdir()}, expected_files)
            self.assertEqual({path.name for path in second.iterdir()}, expected_files)
            for filename in expected_files:
                self.assertEqual((first / filename).read_bytes(), (second / filename).read_bytes())

            model_rows = csv_rows(first / "model_diagnostics.csv")
            self.assertEqual([row["model_id"] for row in model_rows], MODEL_IDS)
            self.assertTrue(all(row["converged"] == "True" for row in model_rows))
            self.assertEqual(
                {row["model_id"] for row in model_rows if row["observations"] == "84"},
                set(MODEL_IDS[:2]),
            )
            adjusted = [row for row in model_rows if row["observations"] == "78"]
            self.assertEqual({row["columns"] for row in adjusted}, {"8"})
            self.assertEqual({row["matrix_rank"] for row in adjusted}, {"8"})
            self.assertEqual(
                {row["platform_reference_category"] for row in adjusted},
                {"district/county platform"},
            )

            rank_rows = csv_rows(first / "rank_repair_diagnostics.csv")
            legacy = next(row for row in rank_rows if row["design"].startswith("legacy"))
            corrected = next(row for row in rank_rows if row["design"].startswith("corrected"))
            self.assertEqual((legacy["columns"], legacy["matrix_rank"]), ("9", "8"))
            self.assertEqual(legacy["rank_deficient"], "True")
            self.assertEqual((corrected["columns"], corrected["matrix_rank"]), ("8", "8"))
            self.assertEqual(corrected["rank_deficient"], "False")
            self.assertEqual(corrected["platform_reference_category"], "district/county platform")

            excluded = csv_rows(first / "excluded_complete_control_cases.csv")
            self.assertEqual(len(excluded), 6)
            self.assertEqual({row["exit_type"] for row in excluded}, {"nominal_exit"})
            self.assertEqual({row["institutional_change"] for row in excluded}, {"0"})

            influence = csv_rows(first / "leave_one_out_influence.csv")
            self.assertEqual(len(influence), 2 * 84 + 2 * 78)
            self.assertEqual({row["model_id"] for row in influence}, set(MODEL_IDS))
            influence_summary = csv_rows(first / "leave_one_out_summary.csv")
            self.assertEqual([row["model_id"] for row in influence_summary], MODEL_IDS)
            self.assertEqual(len(csv_rows(first / "influential_cases.csv")), 20)

            province = csv_rows(first / "province_feasibility.csv")
            self.assertEqual(len(province), 1)
            self.assertEqual(province[0]["eligible_for_estimation"], "False")
            self.assertIn("12", province[0]["events"])

            table = (first / "exploratory_sparse_outcome_table.tex").read_text(encoding="utf-8")
            self.assertIn("Exploratory sparse-outcome audit", table)
            self.assertIn("12 events", table)
            self.assertTrue(
                (first / "exploratory_sparse_outcome_coefficients.png").read_bytes().startswith(
                    b"\x89PNG\r\n\x1a\n"
                )
            )
            stored_summary = json.loads((first / "audit_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(stored_summary, first_summary)


if __name__ == "__main__":
    unittest.main()
