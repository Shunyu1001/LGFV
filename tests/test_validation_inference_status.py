from dataclasses import asdict
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_validation_inference_status import assess_collection, assemble_status, run_approved_analysis


class CollectionStatusTests(unittest.TestCase):
    def setUp(self):
        self.frame = [{"validation_unit_id": "v1", "inclusion_probability": "1"}]
        self.readiness = [{"packet_case_id": "v1", "proposed_inclusion_probability": "1"}]
        self.entries = [{"packet_case_id": "v1", "final_label": ""}]
        self.confirmed = [{"case_id": "old_reference", "confirmed_label": "nominal_exit"}]

    def assess(self):
        return assess_collection(self.frame, self.readiness, self.entries, self.confirmed)

    def test_proposed_census_and_old_reference_do_not_supply_outcomes(self):
        out = self.assess()
        self.assertEqual(out["untouched_human_entries"], 1)
        self.assertIsNone(out["numerical_estimate"])
        self.assertIsNone(out["actual_selection_probabilities"])

    def test_missing_ids_rejected(self):
        self.entries = []
        with self.assertRaisesRegex(ValueError, "IDs must agree"):
            self.assess()

    def test_duplicate_ids_rejected(self):
        self.entries *= 2
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.assess()

    def test_no_formal_event_remains_unresolved(self):
        self.entries[0].update(coder_id="coder", formal_event_found="false", final_label="unclear")
        out = self.assess()
        self.assertEqual(out["unresolved_or_incomplete_entries"], 1)
        self.assertEqual(out["completed_entry_records_pending_source_and_process_verification"], 0)

    def test_classification_without_event_is_rejected(self):
        self.entries[0].update(final_label="nominal_exit", formal_event_found="false")
        with self.assertRaisesRegex(ValueError, "eligibility"):
            self.assess()

    def test_complete_record_does_not_authorize_estimation(self):
        self.entries[0].update(final_label="nominal_exit", formal_event_found="true",
                               post_event_evidence_found="true", exit_case_eligibility="eligible",
                               coder_id="reviewer", coding_date="2026-09-10", rationale="evidence",
                               formal_event_source_references="source1", post_event_source_references="source2",
                               coder_signature="reviewer")
        out = self.assess()
        self.assertEqual(out["completed_entry_records_pending_source_and_process_verification"], 1)
        self.assertEqual(out["status"], "not_estimated")
        self.assertIsNone(out["numerical_estimate"])

    def test_invalid_label_rejected(self):
        self.entries[0]["final_label"] = "0"
        with self.assertRaisesRegex(ValueError, "unsupported exit label"):
            self.assess()

    def test_explicit_synthetic_census_roundtrip(self):
        from design_based_validation import (AnalysisSpec, Approval, Design, Frame, FrameUnit,
                                            HumanResponse, Request, Selection, Stratum, specification_sha256)
        units = tuple(FrameUnit(f"synthetic:u{i}", "stratum", 1.0, 1.0, (1.0,)) for i in range(2))
        request = Request(
            "synthetic", Frame("synthetic:frame", "frozen_approved", "issuer", "all_units_verified",
                               "synthetic:eligibility", ("intercept",), units),
            Design("synthetic:design", "synthetic:frame", "approved", (Stratum("stratum", 2, 2, "census"),),
                   True, "synthetic:probabilities"),
            AnalysisSpec("synthetic:binary", "synthetic:definition", "fixed_prespecified",
                         "synthetic:prediction", "synthetic:covariates", True),
            Selection("synthetic:frame", "synthetic:design", "synthetic:selection", "realized_verified",
                      tuple(u.unit_id for u in units), "synthetic:roster", "synthetic:verification"),
            tuple(HumanResponse(u.unit_id, "synthetic:frame", "synthetic:selection", "synthetic:binary",
                                "completed", "known", True, float(i), "synthetic", "synthetic:reviewer",
                                "2026-09-10", "synthetic:review") for i, u in enumerate(units)),
        )
        approval = Approval("synthetic:frame", "synthetic:design", "synthetic",
                            specification_sha256(request), "approved", "synthetic:approver", "synthetic:approval")
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "request.json"
            approved = Path(tmp) / "approval.json"
            source.write_text(json.dumps(asdict(request)))
            approved.write_text(json.dumps([asdict(approval)]))
            estimate = run_approved_analysis(source, approved)
            self.assertEqual(estimate["point"], (0.5,))
            self.assertEqual(estimate["mode"], "synthetic")
            projection = run_approved_analysis(source, approved, "fixed_x")
            self.assertEqual(len(projection["point"]), 1)
            self.assertAlmostEqual(projection["point"][0], 0.5, places=12)

    def test_requested_analysis_does_not_change_collection_status(self):
        original = self.assess()
        for mode in ("actual", "synthetic"):
            with self.subTest(mode=mode):
                estimate = {"mode": mode, "point": (0.5,), "frame_id": "unrelated-frame"}
                report = assemble_status(original, {"candidate": "hash"}, estimate)
                self.assertEqual(report["collection"], original)
                self.assertEqual(report["collection"]["status"], "not_estimated")
                self.assertIsNone(report["collection"]["numerical_estimate"])
                self.assertEqual(report["collection"]["untouched_human_entries"], 1)
                self.assertEqual(report["requested_analysis"]["numerical_estimate"], estimate)

    def test_no_request_preserves_missing_estimate(self):
        report = assemble_status(self.assess(), {})
        self.assertEqual(report["requested_analysis"]["status"], "not_requested")
        self.assertIsNone(report["requested_analysis"]["numerical_estimate"])


if __name__ == "__main__":
    unittest.main()
