from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_codex_surrogate_labels as codex_labels  # noqa: E402
import build_llm_candidate_pool_seed as candidate_seed  # noqa: E402
import build_llm_screening_sample as screening  # noqa: E402
from label_roles import (  # noqa: E402
    WORKING_REFERENCE_ANALYTIC_ROLE,
    WORKING_REFERENCE_LABEL_SOURCE,
    WORKING_REFERENCE_POOL_STATUS,
    WORKING_REFERENCE_PRODUCER,
    WORKING_REFERENCE_SCREENING_STATUS,
)


AUTHORITATIVE_ISSUERS = (
    ROOT
    / "data"
    / "analysis_inputs"
    / "codex_surrogate_issuer_summary_2026_07_03_expanded.csv"
)
FORBIDDEN_TEXT = (
    "human_gold_standard",
    "gold_outcome",
    "gold standard",
    "gold-standard",
    "gold labels",
    "gold plus",
    "validated-sample",
    "author-reviewed",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def assert_no_false_provenance(test: unittest.TestCase, text: str) -> None:
    lowered = text.lower()
    for phrase in FORBIDDEN_TEXT:
        test.assertNotIn(phrase, lowered)


class CanonicalLabelRoleUnitTest(unittest.TestCase):
    def test_legacy_master_status_emits_working_reference_role(self) -> None:
        row = candidate_seed.master_row(
            {
                "case_id": "case_1",
                "validation_status": "human_validated",
                "company_name": "Issuer",
            },
            1,
        )
        self.assertEqual(row["llm_label_status"], WORKING_REFERENCE_POOL_STATUS)
        self.assertEqual(
            row["human_review_status"], "pending_independent_human_confirmation"
        )
        self.assertIn("await independent human confirmation", row["notes"])

    def test_source_packet_reference_is_not_emitted_as_human_label(self) -> None:
        seed = {
            "pool_id": "master_0001",
            "source_row_id": "case_1",
            "province": "Test",
            "city": "Test City",
            "issuer_name": "Issuer",
            "validation_status": "human_validated",
        }
        reference = {
            "case_1": {
                "case_id": "case_1",
                "final_label": "nominal_exit",
                "final_confidence": "medium",
                "source_coverage_score": "4",
                "final_rationale": "Formal language coexists with a continuing function.",
            }
        }
        row = codex_labels.reference_row(seed, reference)
        self.assertEqual(row["label_source"], WORKING_REFERENCE_LABEL_SOURCE)
        self.assertEqual(row["labeler"], WORKING_REFERENCE_PRODUCER)
        self.assertEqual(row["needs_human_review"], "true")
        self.assertIn("independent human confirmation", row["missing_information"])

    def test_screening_preserves_working_reference_role(self) -> None:
        row = screening.classify(
            {
                "label_source": "human_gold_standard",
                "surrogate_status": "not_surrogate",
                "exit_type": "functional_transfer",
            }
        )
        self.assertEqual(row["screening_status"], WORKING_REFERENCE_SCREENING_STATUS)
        self.assertEqual(row["label_source"], WORKING_REFERENCE_LABEL_SOURCE)
        self.assertEqual(row["needs_human_review"], "true")
        self.assertIn("independent human confirmation", row["missing_information"])
        self.assertTrue(row["usable_for_exit_type_analysis"] == "true")

    def test_screening_normalizes_legacy_boundary_role(self) -> None:
        row = screening.classify(
            {
                "label_source": "human_reviewed_boundary",
                "missing_information": "Excluded from gold labels.",
            }
        )
        self.assertEqual(row["label_source"], "codex_source_packet_boundary_review")
        self.assertEqual(row["needs_human_review"], "true")
        assert_no_false_provenance(self, row["missing_information"])


class LabelRolePipelineTest(unittest.TestCase):
    def run_script(self, script: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *args],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_dsl_surrogate_and_panel_builds_preserve_counts_and_roles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            diagnostics = out / "dsl_diagnostics.csv"
            augmented = out / "dsl_augmented.csv"
            dsl_tex = out / "dsl.tex"
            self.run_script(
                "build_dsl_surrogate_adjustment.py",
                "--issuers",
                str(AUTHORITATIVE_ISSUERS),
                "--diagnostics",
                str(diagnostics),
                "--augmented",
                str(augmented),
                "--tex",
                str(dsl_tex),
            )

            diagnostic_values = {row["quantity"]: row["value"] for row in read_csv(diagnostics)}
            self.assertEqual(diagnostic_values["working_reference_labels"], "94")
            self.assertEqual(diagnostic_values["working_reference_nominal_exit"], "82")
            self.assertEqual(diagnostic_values["working_reference_institutional_change"], "12")
            self.assertEqual(diagnostic_values["surrogate_reference_overlap_issuers"], "61")
            self.assertEqual(diagnostic_values["nonoverlap_surrogate_issuers"], "97")
            self.assertEqual(diagnostic_values["raw_nominal_precision"], "1.000")

            augmented_rows = read_csv(augmented)
            self.assertEqual(
                [row["observations"] for row in augmented_rows], ["94", "191", "191"]
            )
            self.assertEqual(
                [row["nominal_exit"] for row in augmented_rows],
                ["82.00", "178.22", "173.25"],
            )
            assert_no_false_provenance(self, dsl_tex.read_text(encoding="utf-8"))
            assert_no_false_provenance(self, augmented.read_text(encoding="utf-8"))

            flow = out / "flow.csv"
            empirical_input = out / "issuer_input.csv"
            flow_tex = out / "flow.tex"
            adjusted_tex = out / "adjusted.tex"
            self.run_script(
                "build_surrogate_empirical_core.py",
                "--issuers",
                str(AUTHORITATIVE_ISSUERS),
                "--dsl",
                str(diagnostics),
                "--augmented",
                str(augmented),
                "--flow",
                str(flow),
                "--input",
                str(empirical_input),
                "--flow-tex",
                str(flow_tex),
                "--adjusted-tex",
                str(adjusted_tex),
            )
            input_rows = read_csv(empirical_input)
            roles = Counter(row["analytic_role"] for row in input_rows)
            self.assertEqual(len(input_rows), 252)
            self.assertEqual(roles[WORKING_REFERENCE_ANALYTIC_ROLE], 94)
            self.assertEqual(roles["surrogate_overlap_check"], 61)
            self.assertEqual(roles["surrogate_auxiliary_nonoverlap"], 97)
            self.assertEqual(
                {row["label_source"] for row in input_rows if row["analytic_role"] == WORKING_REFERENCE_ANALYTIC_ROLE},
                {WORKING_REFERENCE_LABEL_SOURCE},
            )
            assert_no_false_provenance(self, empirical_input.read_text(encoding="utf-8"))
            assert_no_false_provenance(self, adjusted_tex.read_text(encoding="utf-8"))

            panel = out / "panel.csv"
            coverage = out / "coverage.csv"
            coverage_tex = out / "coverage.tex"
            self.run_script(
                "build_empirical_case_panel.py",
                "--surrogate",
                str(empirical_input),
                "--panel",
                str(panel),
                "--coverage",
                str(coverage),
                "--coverage-tex",
                str(coverage_tex),
            )
            panel_rows = read_csv(panel)
            self.assertEqual(len(panel_rows), 191)
            self.assertEqual(
                sum(row["include_in_gold_sample"] == "1" for row in panel_rows), 94
            )
            self.assertEqual(
                sum(
                    row["include_in_current_validated_model_sample"] == "1"
                    for row in panel_rows
                ),
                84,
            )
            self.assertEqual(
                sum(
                    row["include_in_full_controls_regression_sample"] == "1"
                    for row in panel_rows
                ),
                78,
            )
            self.assertEqual(
                {
                    row["analytic_role"]
                    for row in panel_rows
                    if row["include_in_gold_sample"] == "1"
                },
                {WORKING_REFERENCE_ANALYTIC_ROLE},
            )
            assert_no_false_provenance(self, panel.read_text(encoding="utf-8"))
            assert_no_false_provenance(self, coverage_tex.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
