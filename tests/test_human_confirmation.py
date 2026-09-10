from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from human_confirmation import (  # noqa: E402
    CONFIRMED_NOTICE, REFERENCE, REPORT, case_is_human_checked,
    confirmed_rows, confirmation_notice, replace_confirmation_notice,
)


class HumanConfirmationTest(unittest.TestCase):
    def test_exact_scope_and_unreported_details(self):
        rows = confirmed_rows()
        self.assertEqual(len(rows), 94)
        self.assertTrue(all(not row["reviewer_identity"] for row in rows))
        self.assertTrue(all(not row["review_completed_on"] for row in rows))
        self.assertTrue(all(row["blinding_status"] == "not_reported" for row in rows))
        self.assertTrue(all("Codex" in row["original_label_producer"] for row in rows))

    def test_unknown_candidates_not_confirmed(self):
        for case_id in ("", "case_1", "new_surrogate", "mv_unknown"):
            self.assertFalse(case_is_human_checked(case_id))
            self.assertIn("await independent human confirmation", confirmation_notice(case_id))

    def test_confirmed_case_replaces_stale_notice_once(self):
        case_id = confirmed_rows()[0]["case_id"]
        self.assertTrue(case_is_human_checked(case_id))
        notice = replace_confirmation_notice(
            "Retain caveat. Working reference labels await independent human confirmation.", case_id
        )
        self.assertIn("Retain caveat.", notice)
        self.assertIn(CONFIRMED_NOTICE, notice)
        self.assertNotIn("await independent human confirmation", notice)
        self.assertEqual(replace_confirmation_notice(notice, case_id), notice)

    def test_changed_reference_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            altered = Path(tmp) / "reference.csv"
            altered.write_bytes(REFERENCE.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "snapshot"):
                confirmed_rows(altered, REPORT)

    def test_wrong_report_count_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            altered = Path(tmp) / "report.json"
            report = json.loads(REPORT.read_text())
            report["case_count"] = 95
            altered.write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError, "scope"):
                confirmed_rows(REFERENCE, altered)

    def test_provenance_compatibility_accepts_only_exact_reviewed_payloads(self):
        from build_probability_validation_frame import validate_protected_payload
        for relative in ("coding/codebook.md", "coding/label_provenance.md", "data/validation/label_role_registry.csv"):
            payload = (ROOT / relative).read_bytes()
            validate_protected_payload(relative, payload)
            with self.assertRaisesRegex(ValueError, "Protected input"):
                validate_protected_payload(relative, payload + b"\nunauthorized change")

    def test_screening_uses_current_confirmation_for_known_reference_only(self):
        from build_llm_screening_sample import classify
        confirmed = confirmed_rows()[0]
        source = {"label_source": "codex_source_packet_working_reference",
                  "source_row_id": confirmed["case_id"],
                  "exit_type": confirmed["confirmed_label"]}
        self.assertEqual(classify(source)["needs_human_review"], "false")
        source["source_row_id"] = "new_unconfirmed_case"
        self.assertEqual(classify(source)["needs_human_review"], "true")


if __name__ == "__main__":
    unittest.main()
