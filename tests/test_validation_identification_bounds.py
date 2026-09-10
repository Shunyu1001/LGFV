from __future__ import annotations

import copy
import itertools
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_validation_identification_bounds as bounds
from human_confirmation import confirmed_rows


def fixture():
    reference = [{"case_id": "r1", "company_name": "Alpha", "final_label": "nominal_exit"}]
    selected = [{"pool_id": "p1", "source_row_id": "s1", "issuer_name": "Alpha",
                 "label_source": "codex_surrogate", "surrogate_status": "labeled",
                 "exit_type": "nominal_exit", "evidence_basis": "d1"},
                {"pool_id": "p2", "source_row_id": "s2", "issuer_name": "Beta",
                 "label_source": "codex_surrogate", "surrogate_status": "labeled",
                 "exit_type": "nominal_exit", "evidence_basis": "d2"}]
    historical = {"pool_id": "h1", "source_row_id": "r1", "issuer_name": "Alpha",
                  "label_source": "human_gold_standard", "surrogate_status": "not_surrogate",
                  "exit_type": "nominal_exit"}
    issuers = [{"issuer_name": name, "surrogate_rows": "1", "source_row_ids": source,
                "pool_ids": pool, "exit_type": "nominal_exit", "exit_type_counts": "nominal_exit:1",
                "gold_standard_overlap": "true" if name == "Alpha" else "false",
                "gold_case_id": "r1" if name == "Alpha" else "",
                "gold_final_label": "nominal_exit" if name == "Alpha" else ""}
               for name, source, pool in (("Alpha", "s1", "p1"), ("Beta", "s2", "p2"))]
    return reference, issuers, [historical, *selected]


class IdentificationBoundsTest(unittest.TestCase):
    def row(self, labels):
        return bounds.bound_row("test", "finite", [{"reference_label": x} for x in labels], "nominal_exit")

    def test_complete_labels(self):
        row = self.row(["nominal_exit", "functional_transfer", "nominal_exit"])
        self.assertEqual((row["known_positive"], row["known_negative"], row["unknown"]), (2, 1, 0))
        self.assertEqual(row["lower"], row["upper"])
        self.assertAlmostEqual(float(row["lower"]), 2 / 3)

    def test_no_labels_and_unclear_are_unknown(self):
        row = self.row(["", "unclear", ""])
        self.assertEqual((row["known_positive"], row["known_negative"], row["unknown"]), (0, 0, 3))
        self.assertEqual((float(row["lower"]), float(row["upper"])), (0, 1))

    def test_negative_labels_reduce_upper(self):
        row = self.row(["nominal_exit", "substantive_exit", "liquidation", "", ""])
        self.assertEqual((row["lower_numerator"], row["upper_numerator"], row["denominator"]), (1, 3, 5))

    def test_empty_population_is_undefined(self):
        row = self.row([])
        self.assertEqual((row["lower"], row["upper"]), ("", ""))
        self.assertEqual(row["status"], "undefined_empty_population")
        self.assertEqual(bounds.audit_overlap([], [], [])[0], [])

    def test_invalid_label_does_not_become_unknown(self):
        with self.assertRaisesRegex(ValueError, "Invalid outcome"):
            self.row(["misspelled_label"])

    def test_extrema_attainable_for_all_small_completions(self):
        for positive in range(4):
            for negative in range(4):
                for unknown in range(4):
                    labels = ["nominal_exit"] * positive + ["functional_transfer"] * negative + [""] * unknown
                    if not labels:
                        continue
                    row = self.row(labels)
                    completions = [(positive + sum(x)) / len(labels)
                                   for x in itertools.product((0, 1), repeat=unknown)]
                    self.assertAlmostEqual(float(row["lower"]), min(completions))
                    self.assertAlmostEqual(float(row["upper"]), max(completions))

    def test_all_reference_classes(self):
        for label in bounds.CLASSES:
            row = bounds.bound_row("t", "ref", [{"reference_label": c} for c in bounds.CLASSES], label)
            self.assertEqual((row["known_positive"], row["known_negative"], row["unknown"]), (1, 3, 0))

    def test_no_event_is_not_a_negative_outcome(self):
        unit = {"scope_disposition": "eligible", "screen_status": bounds.NO_EVENT, "reference_label": ""}
        rows = {r["bound_id"]: r for r in bounds.make_bounds([], [], [unit])}
        self.assertEqual(rows["VB-NOEVENT-NOM"]["unknown"], 1)
        self.assertEqual(rows["VB-NOEVENT-NOM"]["known_negative"], 0)
        self.assertEqual(rows["VB-CANDIDATE-CORRECT"]["n"], 0)

    def test_ordinary_overlap_and_complete_no_overlap(self):
        reference, issuers, disclosures = fixture()
        audit, selected, _ = bounds.audit_overlap(reference, issuers, disclosures)
        self.assertEqual((len(audit), len(selected)), (2, 2))
        self.assertEqual([r["outcome_status"] for r in audit], ["known", "unknown"])
        issuers[0].update(gold_standard_overlap="false", gold_case_id="", gold_final_label="")
        audit, _, _ = bounds.audit_overlap([], issuers, disclosures[1:])
        self.assertTrue(all(r["outcome_status"] == "unknown" for r in audit))

    def test_inconsistent_issuer_links(self):
        for field, value in (("gold_case_id", "other"), ("gold_standard_overlap", "false"),
                             ("gold_final_label", "functional_transfer"), ("pool_ids", "p2"),
                             ("source_row_ids", "s2"), ("surrogate_rows", "2"),
                             ("exit_type", "functional_transfer"), ("exit_type_counts", "nominal_exit:2")):
            with self.subTest(field=field):
                ref, iss, disc = fixture()
                iss[0][field] = value
                with self.assertRaises(ValueError):
                    bounds.audit_overlap(ref, iss, disc)

    def test_conflicting_reference_labels(self):
        ref, iss, disc = fixture()
        ref.append({"case_id": "r2", "company_name": "Alpha", "final_label": "functional_transfer"})
        with self.assertRaisesRegex(ValueError, "Conflicting reference labels"):
            bounds.audit_overlap(ref, iss, disc)

    def test_same_label_duplicate_case_is_not_overwritten(self):
        ref, iss, disc = fixture()
        ref.append({**ref[0], "case_id": "r2"})
        with self.assertRaisesRegex(ValueError, "Ambiguous multiple reference cases"):
            bounds.audit_overlap(ref, iss, disc)

    def test_duplicate_reference_case_id(self):
        ref, iss, disc = fixture()
        with self.assertRaisesRegex(ValueError, "Duplicate reference case_id"):
            bounds.audit_overlap(ref + ref, iss, disc)

    def test_duplicate_issuer_including_normalization_collision(self):
        for name in ("Alpha", "Al-pha"):
            ref, iss, disc = fixture()
            iss.append({**iss[0], "issuer_name": name})
            with self.assertRaisesRegex(ValueError, "Duplicate issuer"):
                bounds.audit_overlap(ref, iss, disc)

    def test_empty_issuer_is_rejected(self):
        ref, iss, disc = fixture()
        iss[0]["issuer_name"] = ""
        with self.assertRaisesRegex(ValueError, "Empty issuer"):
            bounds.audit_overlap(ref, iss, disc)

    def test_duplicate_selected_source_and_pool_fail(self):
        for field in ("source_row_id", "pool_id"):
            ref, iss, disc = fixture()
            disc[2][field] = disc[1][field]
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                bounds.audit_overlap(ref, iss, disc)

    def test_original_label_mismatch(self):
        ref, iss, disc = fixture()
        disc[0]["exit_type"] = "functional_transfer"
        with self.assertRaisesRegex(ValueError, "Original label changed"):
            bounds.audit_overlap(ref, iss, disc)

    def test_negative_overlap_is_retained(self):
        ref, iss, disc = fixture()
        ref[0]["final_label"] = disc[0]["exit_type"] = iss[0]["gold_final_label"] = "functional_transfer"
        audit, _, _ = bounds.audit_overlap(ref, iss, disc)
        row = bounds.make_bounds(audit, ref, [])[1]
        self.assertEqual((row["known_positive"], row["known_negative"], row["unknown"]), (0, 1, 1))

    def test_positive_correctness_uses_prediction_denominator(self):
        audit = [{"screen_label": "nominal_exit", "reference_case_id": "", "reference_label": ""},
                 {"screen_label": "functional_transfer", "reference_case_id": "", "reference_label": ""}]
        rows = {r["bound_id"]: r for r in bounds.make_bounds(audit, [], [])}
        self.assertEqual(rows["VB-SCREEN-NOM"]["n"], 2)
        self.assertEqual(rows["VB-SCREEN-CORRECT"]["n"], 1)

    def test_provenance_hash_mismatch(self):
        raw = b"immutable content"
        bounds.verify_payload("fixture", raw, bounds.digest(raw))
        with self.assertRaisesRegex(ValueError, "Provenance hash mismatch"):
            bounds.verify_payload("fixture", raw + b"\n", bounds.digest(raw))

    def test_confirmation_reference_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            altered = Path(tmp) / "reference.csv"
            altered.write_bytes((ROOT / bounds.INPUTS["reference"]).read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "snapshot"):
                confirmed_rows(altered, ROOT / bounds.INPUTS["report"])

    def test_confirmation_register_mismatch_fails_even_with_file_hash_authorized(self):
        original = bounds.parse_csv

        def altered(raw):
            rows = original(raw)
            if rows and "confirmed_label" in rows[0]:
                rows[0]["confirmed_label"] = "liquidation"
            return rows

        with patch.object(bounds, "parse_csv", side_effect=altered):
            with self.assertRaisesRegex(ValueError, "register differs"):
                bounds.load_inputs(ROOT)

    def test_csv_empty_and_malformed_inputs(self):
        self.assertEqual(bounds.parse_csv(b"a,b\n"), [])
        for raw in (b"", b"a,a\nx,y\n", b"a,b\nx\n", b"a,b\nx,y,z\n"):
            with self.assertRaises(ValueError):
                bounds.parse_csv(raw)


class CurrentInputAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, _ = bounds.load_inputs(ROOT)
        cls.audit, cls.selected, cls.refs = bounds.audit_overlap(
            cls.data["reference"], cls.data["issuers"], cls.data["disclosures"])

    def test_actual_snapshot_counts_and_deterministic_outputs(self):
        first, second = bounds.build(ROOT), bounds.build(ROOT)
        self.assertEqual(first, second)
        metrics = json.loads(first[bounds.ARTIFACTS / "metrics.json"])
        self.assertEqual((metrics["reference_cases"], metrics["issuer_rows"], metrics["overlap_issuers"]), (94, 158, 61))
        self.assertEqual(metrics["candidate"]["candidate_units"], 67)
        rows = bounds.parse_csv(first[Path("data/analysis_inputs/validation_identification_bounds.csv")])
        main = rows[0]
        self.assertEqual([main[f] for f in ("n", "known_positive", "known_negative", "unknown")], ["158", "61", "0", "97"])
        self.assertFalse(metrics["city_platform_union_bounds_reported"])

    def test_reference_rows_all_retained(self):
        audit, _, _ = bounds.audit_overlap(self.data["reference"], self.data["issuers"], self.data["disclosures"])
        ids = [r["reference_case_id"] for r in audit if r["reference_case_id"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(self.refs), len(self.data["reference"]))

    def test_shared_documents_do_not_certify_same_event_pairing(self):
        overlap = [r for r in self.audit if r["reference_case_id"]]
        self.assertEqual(sum(bool(r["shared_reference_screen_document_ids"]) for r in overlap), 41)
        self.assertTrue(all(r["event_time_alignment"] == "not_established" for r in overlap))
        self.assertTrue(all(r["independent_same_event_pairing"] == "not_established" for r in overlap))
        row = bounds.make_bounds(self.audit, self.data["reference"], [])[0]
        self.assertIn("corresponding screen issuer/event", row["assumptions"])

    def test_scope_exclusions_remain_outcome_unknown(self):
        units, counts = bounds.audit_candidate(self.data, self.audit, self.refs)
        self.assertEqual(counts["nonoverlap_scope_counts"], {"eligible": 57, "ineligible": 40})
        row = bounds.make_bounds(self.audit, self.data["reference"], units)[0]
        self.assertEqual((row["known_negative"], row["unknown"]), (0, 97))

    def test_source_document_case_mismatch(self):
        selected = copy.deepcopy(self.selected)
        selected[0]["source_row_id"] = "wrong_case"
        with self.assertRaisesRegex(ValueError, "document case links"):
            bounds.audit_sources(self.data, selected)

    def test_candidate_inconsistent_link(self):
        data = copy.deepcopy(self.data)
        data["origins"][0]["source_row_id"] = "wrong_case"
        with self.assertRaisesRegex(ValueError, "candidate link"):
            bounds.audit_candidate(data, self.audit, self.refs)

    def test_candidate_duplicate_origin_is_not_dropped(self):
        data = copy.deepcopy(self.data)
        data["origins"].append(copy.deepcopy(data["origins"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate origin link"):
            bounds.audit_candidate(data, self.audit, self.refs)

    def test_candidate_design_denominator_mismatch(self):
        data = copy.deepcopy(self.data)
        data["design"][0]["stratum_population_n"] = "999"
        with self.assertRaisesRegex(ValueError, "denominator mismatch"):
            bounds.audit_candidate(data, self.audit, self.refs)


if __name__ == "__main__":
    unittest.main()
