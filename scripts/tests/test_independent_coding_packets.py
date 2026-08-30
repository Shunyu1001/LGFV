#!/usr/bin/env python3

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts/measurement_validation/validate_independent_coding_packets.py"
SPEC = importlib.util.spec_from_file_location("independent_packet_validator", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class IndependentCodingPacketTest(unittest.TestCase):
    def test_blinding_source_and_metrics_gates(self) -> None:
        computed = MODULE.validate(check_metrics=True)
        self.assertEqual(computed["gold_packet_rows"], 94)
        self.assertEqual(computed["candidate_packet_rows"], 4)
        self.assertEqual(computed["adjudication_template_rows"], 94)
        self.assertEqual(computed["populated_coder_entry_cells"], 0)
        self.assertEqual(computed["populated_adjudication_entry_cells"], 0)

    def test_forbidden_fields_are_absent(self) -> None:
        gold_fields, _ = MODULE.read_csv(MODULE.GOLD_PACKET)
        candidate_fields, _ = MODULE.read_csv(MODULE.CANDIDATE_PACKET)
        adjudication_fields, _ = MODULE.read_csv(MODULE.ADJUDICATION_PACKET)
        fields = set(gold_fields) | set(candidate_fields) | set(adjudication_fields)
        self.assertFalse(MODULE.FORBIDDEN_PACKET_HEADERS.intersection(fields))


if __name__ == "__main__":
    unittest.main()
