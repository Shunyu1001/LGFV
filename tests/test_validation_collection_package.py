from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_validation_collection_package as package


class ValidationCollectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.hashes = package.load_inputs()
        cls.outputs = package.build_outputs(cls.data, cls.hashes)

    def rows(self, name):
        return package.parse_csv(self.outputs[name])

    def test_deterministic_complete_current_frame(self):
        self.assertEqual(self.outputs, package.build_outputs(self.data, self.hashes))
        packets = self.rows("blinded_packets.csv")
        ids = [r["packet_case_id"] for r in packets]
        self.assertEqual(len(ids), 67)
        self.assertEqual(len(set(ids)), 67)
        self.assertEqual(set(ids), {r["validation_unit_id"] for r in self.data["candidate"]})
        for name in ("blinded_coder_1_entry.csv", "blinded_coder_2_entry.csv", "adjudication_entry.csv"):
            self.assertEqual([r["packet_case_id"] for r in self.rows(name)], ids)

    def test_complete_exact_origin_document_and_manifest_links(self):
        sources = self.rows("blinded_sources.csv")
        observed = {(r["packet_case_id"], r["document_id"]) for r in sources if r["document_id"]}
        ids = {r["validation_unit_id"] for r in self.data["candidate"]}
        expected = {(r["validation_unit_id"], d) for r in self.data["origins"]
                    if r["validation_unit_id"] in ids for d in package.split_ids(r["evidence_document_ids"])}
        expected |= {(r["validation_unit_id"], r["document_id"]) for r in self.data["manifest"]
                     if r["validation_unit_id"] in ids}
        self.assertEqual(observed, expected)
        self.assertEqual(len({r["source_record_id"] for r in sources}), len(sources))
        self.assertTrue(all(r["document_page_url"] or r["download_url"] for r in sources))
        lookup = {r["source_record_id"]: r for r in sources}
        for packet in self.rows("blinded_packets.csv"):
            for record_id in package.split_ids(packet["source_record_ids"]):
                self.assertEqual(lookup[record_id]["packet_case_id"], packet["packet_case_id"])

    def test_blinded_allowlists_and_blank_forms(self):
        for name, fields, blanks in (
            ("blinded_packets.csv", package.PACKET_FIELDS, []),
            ("blinded_sources.csv", package.SOURCE_FIELDS, []),
            ("blinded_coder_1_entry.csv", package.PACKET_FIELDS + package.ENTRY_FIELDS, package.ENTRY_FIELDS),
            ("blinded_coder_2_entry.csv", package.PACKET_FIELDS + package.ENTRY_FIELDS, package.ENTRY_FIELDS),
            ("adjudication_entry.csv", package.ADJUDICATION_FIELDS, package.ADJUDICATION_FIELDS[1:]),
        ):
            package.validate_blinded(self.outputs[name], fields, blanks)
            self.assertFalse(any(token in field for field in fields
                                 for token in ("surrogate", "capacity", "debt", "old_label", "screen_status")))

    def test_schema_column_added_removed_renamed_reordered_duplicated(self):
        raw = self.outputs["blinded_packets.csv"]
        first, rest = raw.split(b"\n", 1)
        columns = first.split(b",")
        variants = [first + b",screen_status", b",".join(columns[:-1]),
                    b",".join([b"issuer_alias", *columns[1:]]),
                    b",".join(reversed(columns)), b",".join([columns[0], *columns[1:-1], columns[0]])]
        for mutated_header in variants:
            with self.subTest(header=mutated_header), self.assertRaises(ValueError):
                package.validate_blinded(mutated_header + b"\n" + rest, package.PACKET_FIELDS, [])

    def test_label_status_signature_date_and_score_leakage_rejected(self):
        rows = self.rows("blinded_coder_1_entry.csv")
        for field in package.ENTRY_FIELDS:
            altered = copy.deepcopy(rows)
            altered[0][field] = "nominal_exit" if field == "final_label" else "MUTATION"
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "leaked"):
                package.validate_blinded(package.csv_bytes(altered), package.PACKET_FIELDS + package.ENTRY_FIELDS,
                                         package.ENTRY_FIELDS)
        for value in ("screen_positive_nominal", "screened_no_direct_formal_event", "codex_surrogate"):
            altered = self.rows("blinded_packets.csv")
            altered[0]["issuer_name"] = value
            with self.assertRaisesRegex(ValueError, "leaked"):
                package.validate_blinded(package.csv_bytes(altered), package.PACKET_FIELDS, [])

    def test_all_94_authorized_labels_and_6298_pairs(self):
        scope = self.rows("coordinator_reference_report_scope.csv")
        self.assertEqual(len(scope), 94)
        self.assertEqual({r["case_id"]: r["confirmed_label"] for r in scope},
                         {r["case_id"]: r["final_label"] for r in self.data["reference"]})
        self.assertTrue(all(r["reviewer_identity"] == r["review_completed_on"] == "" for r in scope))
        self.assertTrue(all(r["blinding_status"] == "not_reported" for r in scope))
        pairs = self.rows("coordinator_reference_pair_audit.csv")
        self.assertEqual(len(pairs), 67 * 94)
        self.assertEqual(len({(r["packet_case_id"], r["reference_case_id"]) for r in pairs}), 67 * 94)
        mappings = self.rows("coordinator_reference_mappings.csv")
        self.assertEqual(len(mappings), 67)
        self.assertTrue(all(r["confirmed_reference_label"] == "" for r in mappings))
        self.assertTrue(all(r["reason"] == "no_exact_issuer_in_report_scope" for r in mappings))

    def test_issuer_event_mapping_is_conjunctive_no_city_or_alias(self):
        ref = self.data["reference"][0]
        unit = {"validation_unit_id": "test_unit", "issuer_name": ref["company_name"],
                "city": ref["city"], "historical_capacity_source_case_ids": ref["case_id"]}
        origin = {"source_row_id": ref["case_id"], "evidence_document_ids": ref["primary_evidence_doc"]}
        exact = package.match_reference(unit, [origin], ref)
        self.assertEqual(exact["mapping_status"], "exact_historical_reference")
        for changed_unit, changed_origin in (
            ({**unit, "issuer_name": "different issuer"}, origin),
            ({**unit, "issuer_name": unit["issuer_name"] + " "}, origin),
            (unit, {**origin, "source_row_id": "different_event"}),
            (unit, {**origin, "evidence_document_ids": "other_document"}),
            (unit, {**origin, "evidence_document_ids": ""}),
        ):
            result = package.match_reference(changed_unit, [changed_origin], ref)
            self.assertEqual(result["mapping_status"], "unmatched")
        self.assertEqual(package.match_reference(unit, [origin], {**ref, "official_exit_event": ""})[
            "mapping_status"], "unmatched")

    def test_ambiguous_event_does_not_carry_label(self):
        scope = package.authorized_reference_rows(self.data)
        pairs = [{"reference_case_id": r["case_id"], "mapping_status": "exact_historical_reference",
                  "issuer_exact_match": "true"} for r in scope[:2]]
        result = package.historical_mapping("unit", pairs, scope)
        self.assertEqual(result["confirmed_reference_label"], "")
        self.assertEqual(result["reason"], "ambiguous_multiple_reference_events")

    def test_reference_and_report_mutations_rejected(self):
        for key, field, value in (
            ("register", "confirmed_label", "liquidation"),
            ("register", "reviewer_identity", "invented"),
            ("reference", "final_label", "liquidation"),
            ("reference", "case_id", "new_candidate"),
        ):
            altered = copy.deepcopy(self.data)
            altered[key][0][field] = value
            with self.subTest(key=key, field=field), self.assertRaises(ValueError):
                package.authorized_reference_rows(altered)
        altered = copy.deepcopy(self.data)
        altered["report"]["case_count"] = 161
        with self.assertRaises(ValueError):
            package.authorized_reference_rows(altered)

    def test_input_hashes_and_schema_mutations(self):
        for item in self.hashes:
            raw = (ROOT / item["path"]).read_bytes()
            self.assertEqual(package.sha256(raw), item["sha256"])
            self.assertEqual(len(raw), item["bytes"])
            with self.subTest(path=item["path"]), self.assertRaisesRegex(ValueError, "hash mismatch"):
                package.verify_payload(item["path"], raw + b"\n", raw)
        raw = (ROOT / package.INPUTS["candidate"]).read_bytes()
        with self.assertRaisesRegex(ValueError, "schema"):
            package.verify_payload(package.INPUTS["candidate"], raw.replace(b"screen_status", b"other_status", 1), raw)

    def test_coordinator_state_updates_do_not_change_collection_snapshot(self):
        original = Path.read_bytes

        def changed_state(path):
            if path == ROOT / package.INPUTS["state"]:
                raise AssertionError("Live coordinator state must not be consumed")
            return original(path)

        with patch.object(Path, "read_bytes", changed_state):
            data, hashes = package.load_inputs()
        self.assertEqual(data, self.data)
        self.assertEqual(hashes, self.hashes)
        state = next(r for r in hashes if r["path"] == package.INPUTS["state"])
        self.assertEqual(state["pin_policy"], "baseline_snapshot_only")
        self.assertTrue(all(r["pin_policy"] == "strict_current_scientific_input"
                            for r in hashes if r["path"] != package.INPUTS["state"]))

    def test_output_hashes_cover_every_other_output(self):
        hashes = json.loads(self.outputs["output_hashes.json"])
        self.assertEqual(set(hashes), set(self.outputs) - {"output_hashes.json"})
        for name, digest in hashes.items():
            self.assertEqual(package.sha256(self.outputs[name]), digest)

    def test_duplicates_and_malformed_rows_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            package.unique([{"id": "x"}, {"id": "x"}], ("id",))
        for value in ("x;x", "x;", ";x"):
            with self.assertRaises(ValueError):
                package.split_ids(value)
        for raw in (b"a,a\n1,2\n", b"a,b\n1,2,3\n", b"a,b\n1\n"):
            with self.assertRaises(ValueError):
                package.parse_csv(raw)
        for table in ("candidate", "origins", "documents", "sources", "manifest", "historical"):
            altered = copy.deepcopy(self.data)
            altered[table].append(copy.deepcopy(altered[table][0]))
            with self.subTest(table=table), self.assertRaisesRegex(ValueError, "Duplicate"):
                package.build_outputs(altered, self.hashes)

    def test_candidate_schema_and_design_mutations_rejected(self):
        for field, value in (("eligibility_flag", "false"), ("random_draw_executed", "true"),
                             ("inclusion_probability", "0.5"), ("issuer_name", "other issuer")):
            altered = copy.deepcopy(self.data)
            altered["candidate"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                package.build_outputs(altered, self.hashes)

    def test_platform_scope_is_not_exit_eligibility_or_negative_outcome(self):
        readiness = json.loads(self.outputs["realized_input_readiness.json"])["units"]
        self.assertEqual(len(readiness), 67)
        for row in readiness:
            self.assertEqual(row["platform_scope_eligibility"], "eligible")
            for field in ("codebook_exit_eligibility", "formal_event_human_decision", "post_event_evidence_human_decision",
                          "coder_1_label", "coder_2_label", "adjudicated_label", "realized_validation_outcome",
                          "realized_inclusion_probability", "reviewer_identity", "actual_review_date", "signature"):
                self.assertIsNone(row[field])
        design = self.rows("coordinator_design_sidecar.csv")
        self.assertEqual(sum(r["screen_status"] == "screened_no_direct_formal_event" for r in design), 10)
        self.assertTrue(all(r["realized_inclusion_probability"] == r["freeze_authorization_id"] == "" for r in design))
        self.assertTrue(all(r["inclusion_probability"] == "1" for r in design))

    def test_exact_outcome_mapping_missing_and_unresolved_not_zero(self):
        self.assertEqual(package.map_outcome("nominal_exit"), 0)
        self.assertEqual(package.map_outcome("substantive_exit"), 1)
        self.assertEqual(package.map_outcome("functional_transfer"), 1)
        for label in (None, "", "liquidation"):
            self.assertIsNone(package.map_outcome(label))
        for label in ("unclear", "unresolved", "ineligible", "Nominal", "false", "0", False, 0):
            with self.subTest(label=label), self.assertRaises(ValueError):
                package.map_outcome(label)
        for eligibility in ("", "unresolved", "ineligible"):
            state = package.human_entry_state({"exit_case_eligibility": eligibility})
            self.assertIsNone(state["label"])
            self.assertIsNone(state["realized_validation_outcome"])
        with self.assertRaisesRegex(ValueError, "Label requires"):
            package.human_entry_state({"final_label": "nominal_exit"})
        with self.assertRaisesRegex(ValueError, "lacks formal/post-event"):
            package.human_entry_state({"exit_case_eligibility": "eligible", "formal_event_found": "yes"})
        full = {"exit_case_eligibility": "eligible", "formal_event_found": "yes", "post_event_evidence_found": "yes",
                "formal_event_summary": "test event", "formal_event_source_references": "test:1",
                "post_event_function": "test function", "post_event_source_references": "test:2",
                "final_label": "nominal_exit"}
        self.assertIsNone(package.human_entry_state(full)["realized_validation_outcome"])

    def test_missing_guiyang_origin_and_old_shenzhen_not_hidden(self):
        readiness = {r["packet_case_id"]: r for r in json.loads(self.outputs["realized_input_readiness.json"])["units"]}
        self.assertEqual(readiness["mv_dd84e076bf32"]["origins_without_document_ids"], ["pilot_gz_001_alt_rail"])
        self.assertGreater(readiness["mv_dd84e076bf32"]["manifest_verified_raw_documents"], 0)
        records = self.rows("coordinator_source_audit.csv")
        old = next(r for r in records if r["source_record_id"].endswith(":web_shenzhen_sasac_special_zone_development"))
        renewed = next(r for r in records if r["source_record_id"].endswith(":web_shenzhen_sasac_special_zone_development_20260910"))
        self.assertEqual(old["raw_archive_state"], "missing_file")
        self.assertEqual(renewed["raw_archive_state"], "verified")

    def test_historical_comparison_matches_exact_current_and_old_id_sets(self):
        rows = self.rows("historical_packet_comparison.csv")
        current = {r["validation_unit_id"] for r in self.data["candidate"]}
        historical = {r["packet_case_id"] for r in self.data["historical"]}
        self.assertEqual({r["packet_case_id"] for r in rows if r["historical_packet_membership"] == "present"},
                         current & historical)
        self.assertEqual({r["packet_case_id"] for r in rows if r["historical_packet_membership"] == "absent"},
                         current - historical)
        metrics = json.loads(self.outputs["metrics.json"])
        self.assertEqual(set(metrics["historical_only_units"]), historical - current)
        self.assertEqual((len(current & historical), len(current - historical), len(historical - current)), (3, 64, 1))
        self.assertTrue(all(not r["historical_only_document_ids"] for r in rows))

    def test_local_file_hashes_and_missing_are_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source"
            self.assertEqual(package.audit_file(str(path), "", {})["state"], "missing_file")
            path.write_bytes(b"source bytes")
            digest = package.sha256(path.read_bytes())
            self.assertEqual(package.audit_file(str(path), digest, {})["state"], "verified")
            self.assertEqual(package.audit_file(str(path), "0" * 64, {})["state"], "hash_mismatch")
            self.assertEqual(package.audit_file(str(path), "", {})["state"], "present_unanchored")
            self.assertEqual(package.audit_file("", "", {})["state"], "missing_locator")
        with self.assertRaises(ValueError):
            package.archive_path(Path("/tmp"), "../escape")

    def test_writer_is_idempotent_and_never_overwrites_human_forms(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp)
            package.write_outputs(self.outputs, destination)
            package.write_outputs(self.outputs, destination)
            package.write_outputs(self.outputs, destination, check=True)
            form = destination / "blinded_coder_1_entry.csv"
            changed = form.read_bytes() + b"human-entered data\n"
            form.write_bytes(changed)
            with self.assertRaisesRegex(ValueError, "Refusing to overwrite"):
                package.write_outputs(self.outputs, destination)
            with self.assertRaisesRegex(ValueError, "Stale/changed"):
                package.write_outputs(self.outputs, destination, check=True)
            self.assertEqual(form.read_bytes(), changed)


if __name__ == "__main__":
    unittest.main()
