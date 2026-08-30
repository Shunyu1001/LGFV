#!/usr/bin/env python3

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts/measurement_validation/validate_validation_geography_scope_packet.py"
SPEC = importlib.util.spec_from_file_location("validation_geography_validator", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ValidationGeographyScopePacketTest(unittest.TestCase):
    def test_packet_integrity_and_metrics(self) -> None:
        computed = MODULE.validate(check_metrics=True)
        self.assertEqual(computed["processed_units"], 128)
        self.assertEqual(computed["source_supported_unique_geography_units"], 40)
        self.assertEqual(computed["combined_geography_and_explicit_scope_units"], 40)

    def test_crosswalk_has_no_forbidden_design_or_label_fields(self) -> None:
        fields, _ = MODULE.read_csv(MODULE.CROSSWALK_PATH)
        self.assertFalse(MODULE.FORBIDDEN_HEADERS.intersection(fields))


if __name__ == "__main__":
    unittest.main()
