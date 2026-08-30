import csv
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_validator():
    path = ROOT / "scripts/validate_probability_validation_frame.py"
    spec = importlib.util.spec_from_file_location("probability_frame_validator", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def read_csv(path: str):
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class ProbabilityValidationFrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_validator()
        cls.summary = cls.validator.validate()
        cls.candidate = read_csv("data/validation/probability_validation_frame_candidate.csv")
        cls.origins = read_csv("data/validation/probability_validation_frame_origin_rows.csv")
        cls.crosswalk = read_csv("data/validation/probability_validation_geography_scope_crosswalk.csv")

    def test_registered_gaps_have_honest_dispositions(self):
        self.assertEqual(self.summary["baseline_geography_resolved"], 88)
        self.assertEqual(self.summary["baseline_geography_unresolved"], 0)
        self.assertEqual(self.summary["baseline_scope_resolved"], 96)
        self.assertEqual(self.summary["baseline_scope_unresolved"], 2)

    def test_candidate_is_unique_and_eligible(self):
        unit_ids = [row["validation_unit_id"] for row in self.candidate]
        legal_keys = [row["normalized_legal_issuer_key"] for row in self.candidate]
        self.assertEqual(len(unit_ids), len(set(unit_ids)))
        self.assertEqual(len(legal_keys), len(set(legal_keys)))
        self.assertTrue(all(row["scope_disposition"] == "eligible" for row in self.candidate))

    def test_every_origin_row_is_retained(self):
        self.assertEqual(len(self.origins), 157)
        self.assertEqual(len({(row["validation_unit_id"], row["origin_position"]) for row in self.origins}), 157)

    def test_both_screen_strata_and_nonzero_probabilities(self):
        self.assertEqual(
            {row["screen_status"] for row in self.candidate},
            {"screen_positive_nominal", "screened_no_direct_formal_event"},
        )
        self.assertTrue(all(float(row["inclusion_probability"]) > 0 for row in self.candidate))

    def test_no_random_draw_or_outcome_fields(self):
        forbidden = {"exit_type", "formal_event_found", "continued_function_found", "selected_case"}
        self.assertTrue(all(row["random_draw_executed"] == "false" for row in self.candidate))
        self.assertTrue(forbidden.isdisjoint(self.candidate[0]))

    def test_unresolved_units_are_not_silently_included(self):
        unresolved = {
            row["validation_unit_id"]
            for row in self.crosswalk
            if row["scope_disposition"] == "unresolved_after_search"
            or row["geography_status"] != "source_supported_unique"
        }
        candidate = {row["validation_unit_id"] for row in self.candidate}
        self.assertTrue(unresolved)
        self.assertTrue(unresolved.isdisjoint(candidate))


if __name__ == "__main__":
    unittest.main()
