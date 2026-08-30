from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "build_dsl_surrogate_adjustment.py"
AUTHORITATIVE_ISSUERS = (
    ROOT
    / "data"
    / "analysis_inputs"
    / "codex_surrogate_issuer_summary_2026_07_03_expanded.csv"
)


def diagnostic_values(path: Path) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["quantity"]: row["value"] for row in csv.DictReader(handle)}


class DslSurrogateAdjustmentDefaultTest(unittest.TestCase):
    def run_adjustment(
        self, output_dir: Path, stem: str, issuers: Path | None = None
    ) -> tuple[subprocess.CompletedProcess[str], list[Path]]:
        diagnostics = output_dir / f"{stem}_diagnostics.csv"
        augmented = output_dir / f"{stem}_augmented.csv"
        tex = output_dir / f"{stem}.tex"
        command = [
            sys.executable,
            str(SCRIPT),
            "--diagnostics",
            str(diagnostics),
            "--augmented",
            str(augmented),
            "--tex",
            str(tex),
        ]
        if issuers is not None:
            command.extend(["--issuers", str(issuers)])
        completed = subprocess.run(
            command,
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return completed, [diagnostics, augmented, tex]

    def test_default_matches_authoritative_expanded_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            default_run, default_outputs = self.run_adjustment(output_dir, "default")
            explicit_run, explicit_outputs = self.run_adjustment(
                output_dir, "explicit", AUTHORITATIVE_ISSUERS
            )

            values = diagnostic_values(default_outputs[0])
            self.assertEqual(values["surrogate_unique_issuers"], "158")
            self.assertEqual(values["surrogate_gold_overlap_issuers"], "61")
            self.assertEqual(values["nonoverlap_surrogate_issuers"], "97")
            self.assertIn("validation_overlap=61", default_run.stdout)
            self.assertIn("nonoverlap_surrogate_issuers=97", default_run.stdout)
            self.assertEqual(default_run.stdout, explicit_run.stdout)

            for default_path, explicit_path in zip(default_outputs, explicit_outputs):
                self.assertEqual(default_path.read_bytes(), explicit_path.read_bytes())


if __name__ == "__main__":
    unittest.main()
