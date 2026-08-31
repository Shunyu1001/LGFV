from __future__ import annotations

import csv
import io
import unittest

from scripts.sync_master_case_pool_label_provenance import synchronize


class ProvenanceSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.columns = [
            "case_id",
            "validation_status",
            "exit_type",
            "human_reviewer",
            "validation_date",
        ]
        self.rows = [
            {
                "case_id": "reference_case",
                "validation_status": "human_validated",
                "exit_type": "nominal_exit",
                "human_reviewer": "Shunyu Hao / Codex-assisted review",
                "validation_date": "2026-06-20",
            },
            {
                "case_id": "candidate_case",
                "validation_status": "llm_coded",
                "exit_type": "",
                "human_reviewer": "",
                "validation_date": "",
            },
        ]
        self.references = [
            {
                "case_id": "reference_case",
                "reference_label_producer": (
                    "Codex source-packet review on behalf of Shunyu Hao"
                ),
            }
        ]

    def test_adds_only_producer_metadata(self) -> None:
        columns, rows = synchronize(self.columns, self.rows, self.references)
        self.assertEqual(columns[-3], "reference_label_producer")
        self.assertEqual(
            rows[0]["reference_label_producer"],
            "Codex source-packet review on behalf of Shunyu Hao",
        )
        self.assertEqual(rows[1]["reference_label_producer"], "")
        for original, output in zip(self.rows, rows):
            for key, value in original.items():
                self.assertEqual(output[key], value)

    def test_rejects_case_set_mismatch(self) -> None:
        with self.assertRaisesRegex(ValueError, "case mismatch"):
            synchronize(self.columns, self.rows, [])

    def test_rejects_conflicting_existing_value(self) -> None:
        columns = self.columns + ["reference_label_producer"]
        rows = [dict(self.rows[0], reference_label_producer="Independent human")]
        with self.assertRaisesRegex(ValueError, "conflicting producer"):
            synchronize(columns, rows, self.references)


if __name__ == "__main__":
    unittest.main()
