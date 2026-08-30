import csv
import hashlib
import importlib.util
import tempfile
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


def load_builder():
    path = ROOT / "scripts/build_probability_validation_frame.py"
    spec = importlib.util.spec_from_file_location("probability_frame_builder", path)
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
        cls.builder = load_builder()
        cls.validator = load_validator()
        cls.summary = cls.validator.validate()
        cls.candidate = read_csv("data/validation/probability_validation_frame_candidate.csv")
        cls.design = read_csv("data/validation/probability_validation_sampling_design.csv")
        cls.origins = read_csv("data/validation/probability_validation_frame_origin_rows.csv")
        cls.crosswalk = read_csv("data/validation/probability_validation_geography_scope_crosswalk.csv")

    def test_registered_gaps_have_honest_dispositions(self):
        self.assertEqual(self.summary["baseline_geography_resolved"], 86)
        self.assertEqual(self.summary["baseline_geography_multiple"], 2)
        self.assertEqual(self.summary["baseline_geography_unresolved"], 0)
        self.assertEqual(self.summary["baseline_scope_resolved"], 98)
        self.assertEqual(self.summary["baseline_scope_unresolved"], 0)
        self.assertEqual(
            self.summary["all_scope_dispositions"],
            {"eligible": 66, "ineligible": 66, "unresolved_after_search": 1},
        )

    def test_multiple_geographies_preserve_the_unique_assignment_failure(self):
        multiple = [row for row in self.crosswalk if row["geography_status"] == "source_supported_multiple"]
        self.assertEqual(len(multiple), 2)
        for row in multiple:
            self.assertEqual((row["province"], row["city"]), ("", ""))
            self.assertNotEqual(row["conflict_status"], "none_observed")
            self.assertTrue(row["geography_document_id"])
            self.assertTrue(row["geography_supporting_text"])
        unresolved = read_csv("data/validation/probability_validation_unresolved_log.csv")
        logged = {
            row["validation_unit_id"]
            for row in unresolved
            if row["failed_gate"] == "geography_unique_assignment"
            and row["disposition"] == "source_supported_multiple"
        }
        self.assertEqual(logged, {row["validation_unit_id"] for row in multiple})

    def test_candidate_is_unique_and_eligible(self):
        unit_ids = [row["validation_unit_id"] for row in self.candidate]
        legal_keys = [row["normalized_legal_issuer_key"] for row in self.candidate]
        self.assertEqual(len(unit_ids), len(set(unit_ids)))
        self.assertEqual(len(legal_keys), len(set(legal_keys)))
        self.assertEqual(len(unit_ids), 66)
        self.assertTrue(all(row["scope_disposition"] == "eligible" for row in self.candidate))

    def test_final_candidate_design_counts(self):
        self.assertEqual(self.summary["candidate_units"], 66)
        self.assertEqual(self.summary["frozen_strata"], 23)
        self.assertEqual(
            {status: sum(row["screen_status"] == status for row in self.candidate) for status in {
                "screen_positive_nominal", "screened_no_direct_formal_event"
            }},
            {"screen_positive_nominal": 57, "screened_no_direct_formal_event": 9},
        )
        self.assertEqual(sum(row["historical_capacity_join_status"] == "source_backed_match" for row in self.candidate), 32)
        self.assertEqual(sum(row["debt_pressure_availability"] == "available" for row in self.candidate), 39)
        self.assertTrue(all(row["inclusion_probability"] == "1" for row in self.candidate))

    def test_every_origin_row_is_retained(self):
        self.assertEqual(len(self.origins), 157)
        self.assertEqual(len({(row["validation_unit_id"], row["origin_position"]) for row in self.origins}), 157)

    def test_origin_pairs_use_the_safe_surrogate_mapping(self):
        expected_repairs = {
            "exp4_20260703_0009": "harvest_0199",
            "sch_20260630_0050": "harvest_0050",
            "sch_20260630_0106": "harvest_0106",
            "exp3_20260703_0006": "harvest_0197",
            "sch_20260630_0114": "harvest_0114",
        }
        observed = {row["source_row_id"]: row["pool_id"] for row in self.origins}
        self.assertEqual({source_id: observed[source_id] for source_id in expected_repairs}, expected_repairs)

    def test_resolved_pair_coverage_does_not_borrow_another_pool_score(self):
        coverage = {
            ("source", "declared_pool"): 2.0,
            ("source", "other_pool"): 4.0,
        }
        pools = {"source": {"declared_pool", "other_pool"}}
        for module in (self.builder, self.validator):
            with self.subTest(module=module.__name__):
                pairs = module.resolve_origin_pairs(
                    ["source"], ["declared_pool"], pools, "regression"
                )
                self.assertEqual(pairs, [("source", "declared_pool")])
                self.assertEqual(
                    module.coverage_for_origin_pairs(pairs, coverage, "regression"),
                    2.0,
                )

    def test_all_origin_evidence_document_ids_are_valid(self):
        documents = read_csv("data/document_inventory.csv")
        valid_document_ids = {row["document_id"] for row in documents}
        for origin in self.origins:
            for document_id in filter(None, origin["evidence_document_ids"].split(";")):
                self.assertIn(document_id, valid_document_ids)

    def test_every_cited_source_has_extracted_text_provenance(self):
        manifest = {
            (row["validation_unit_id"], row["document_id"]): row
            for row in read_csv("data/validation/probability_validation_source_manifest.csv")
        }
        for row in self.crosswalk:
            for prefix in ("identity", "geography", "owner", "role"):
                document_id = row[f"{prefix}_document_id"]
                if not document_id:
                    continue
                source = manifest[(row["validation_unit_id"], document_id)]
                self.assertEqual(len(source["source_text_sha256"]), 64)
                self.assertTrue(source["extraction_profile"])
                self.assertFalse(source["cache_verification_status"].startswith("source_cache_missing"))
                self.assertLessEqual(int(row[f"{prefix}_page"]), int(source["pages"]))

    def test_registered_geography_repairs_require_direct_focal_location_anchors(self):
        self.assertEqual(len(self.validator.REPAIRED_GEOGRAPHY_EVIDENCE), 14)
        for unit_id, (document_id, page, city, anchors) in self.validator.REPAIRED_GEOGRAPHY_EVIDENCE.items():
            with self.subTest(unit_id=unit_id):
                row = {
                    "validation_unit_id": unit_id,
                    "geography_status": "source_supported_unique",
                    "city": city,
                    "geography_document_id": document_id,
                    "geography_page": page,
                    "geography_supporting_text": " ".join(anchors),
                }
                self.validator.validate_repaired_geography_row(row)

    def test_geography_repair_rejects_court_venue_boilerplate(self):
        unit_id = "mv_3134f5ad5182"
        document_id, page, city, _ = self.validator.REPAIRED_GEOGRAPHY_EVIDENCE[unit_id]
        row = {
            "validation_unit_id": unit_id,
            "geography_status": "source_supported_unique",
            "city": city,
            "geography_document_id": document_id,
            "geography_page": page,
            "geography_supporting_text": "发行人住所地有管辖权的人民法院为吉安市中级人民法院",
        }
        with self.assertRaisesRegex(ValueError, "court-venue or third-party-only"):
            self.validator.validate_repaired_geography_row(row)

    def test_geography_repair_rejects_third_party_address(self):
        unit_id = "mv_457ad56917e5"
        document_id, page, city, _ = self.validator.REPAIRED_GEOGRAPHY_EVIDENCE[unit_id]
        row = {
            "validation_unit_id": unit_id,
            "geography_status": "source_supported_unique",
            "city": city,
            "geography_document_id": document_id,
            "geography_page": page,
            "geography_supporting_text": (
                "江苏省国信集团有限公司债券文件。主承销商：某银行；"
                "联系地址：南京市建邺区示例路 1 号。"
            ),
        }
        with self.assertRaisesRegex(ValueError, "court-venue or third-party-only"):
            self.validator.validate_repaired_geography_row(row)

    def test_exact_output_schemas_reject_added_outcome_fields(self):
        observed = {
            path: list(fields)
            for path, fields in self.validator.EXPECTED_OUTPUT_SCHEMAS.items()
        }
        observed[self.validator.FLOW].append("outcome")
        with self.assertRaisesRegex(ValueError, "Output schema mismatch"):
            self.validator.validate_output_schemas(observed)

    def test_source_cache_hash_mutation_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source_dir = Path(directory)
            raw_path = source_dir / "example.html"
            raw_payload = b"<html><p>Issuer evidence</p></html>"
            raw_path.write_bytes(raw_payload)
            extracted = self.validator.html_to_text(raw_payload).encode("utf-8")
            manifest = {
                ("unit", "example"): {
                    "raw_cache_filename": "example.html",
                    "text_cache_filename": "",
                    "sha256": hashlib.sha256(raw_payload).hexdigest(),
                    "retrieved_bytes": str(len(raw_payload)),
                    "source_text_sha256": hashlib.sha256(extracted).hexdigest(),
                    "pages": "1",
                }
            }
            row = {
                "validation_unit_id": "unit",
                "identity_document_id": "example",
                "identity_page": "1",
                "identity_supporting_text": "Issuer evidence",
                "geography_document_id": "",
                "owner_document_id": "",
                "role_document_id": "",
            }
            self.assertEqual(
                self.validator.verify_cited_source_cache([row], manifest, source_dir),
                1,
            )
            raw_path.write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "raw-source hash mismatch"):
                self.validator.verify_cited_source_cache([row], manifest, source_dir)

    def test_default_source_cache_verification_is_required(self):
        self.assertEqual(self.validator.DEFAULT_SOURCE_DIR, Path("/tmp/lgfv-exp015-sources"))
        self.assertEqual(self.summary["verified_cited_evidence"], 485)

    def test_candidate_sampling_values_must_match_design_row(self):
        design = {row["frozen_stratum_id"]: row for row in self.design}
        member = self.candidate[0]
        design_row = design[member["frozen_stratum_id"]]
        self.validator.validate_member_design_consistency(member, design_row)
        mutations = {
            "inclusion_probability": ("0.5", "inclusion probability mismatch"),
            "proposed_design_weight": ("2", "proposed design weight mismatch"),
            "deterministic_random_seed": ("different", "random seed mismatch"),
            "random_draw_executed": ("true", "random-draw state mismatch"),
        }
        for field, (value, message) in mutations.items():
            with self.subTest(field=field):
                mutated = dict(member)
                mutated[field] = value
                with self.assertRaisesRegex(ValueError, message):
                    self.validator.validate_member_design_consistency(mutated, design_row)

    def test_both_screen_strata_and_nonzero_probabilities(self):
        self.assertEqual(
            {row["screen_status"] for row in self.candidate},
            {"screen_positive_nominal", "screened_no_direct_formal_event"},
        )
        self.assertTrue(all(float(row["inclusion_probability"]) > 0 for row in self.candidate))

    def test_prefecture_and_taizhou_control_joins(self):
        candidate = {row["validation_unit_id"]: row for row in self.candidate}
        expected = {
            "mv_dea7fe1c1704": ("not_available", "zhejiang_taizhou", "available"),
            "mv_e6fd4cae85c0": ("high", "jiangsu_suzhou", "available"),
            "mv_7964f4b4fada": ("middle", "jiangsu_nantong", "available"),
        }
        for unit_id, (historical_bin, control_id, debt_status) in expected.items():
            self.assertEqual(candidate[unit_id]["historical_capacity_bin"], historical_bin)
            self.assertEqual(candidate[unit_id]["debt_pressure_control_unit_id"], control_id)
            self.assertEqual(candidate[unit_id]["debt_pressure_availability"], debt_status)

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
