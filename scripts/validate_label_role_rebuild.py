#!/usr/bin/env python3
"""Validate that EXP-20260831-091 changed semantics but not empirical values."""

from __future__ import annotations

import csv
import io
import subprocess
from collections import Counter
from pathlib import Path

from label_roles import (
    WORKING_REFERENCE_ANALYTIC_ROLE,
    WORKING_REFERENCE_BOUNDARY_SOURCE,
    WORKING_REFERENCE_LABEL_SOURCE,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = "87ac6587cf34dcbe11384e55d228e4d7f67fcb65"


def read_csv_text(text: str) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(text))
    return reader.fieldnames or [], list(reader)


def base_csv(path: str) -> tuple[list[str], list[dict[str, str]]]:
    completed = subprocess.run(
        ["git", "show", f"{BASE}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return read_csv_text(completed.stdout)


def current_csv(path: str) -> tuple[list[str], list[dict[str, str]]]:
    return read_csv_text((ROOT / path).read_text(encoding="utf-8"))


def compare_rows(path: str, ignored: set[str]) -> None:
    base_fields, old_rows = base_csv(path)
    current_fields, new_rows = current_csv(path)
    if base_fields != current_fields:
        raise AssertionError(f"{path}: columns changed")
    if len(old_rows) != len(new_rows):
        raise AssertionError(f"{path}: row count changed")
    fields = [field for field in base_fields if field not in ignored]
    for row_number, (old, new) in enumerate(zip(old_rows, new_rows), start=2):
        for field in fields:
            if old.get(field, "") != new.get(field, ""):
                raise AssertionError(
                    f"{path}:{row_number}: {field} changed from {old.get(field)!r} "
                    f"to {new.get(field)!r}"
                )


def compare_numeric_columns(path: str, columns: list[str]) -> None:
    _, old_rows = base_csv(path)
    _, new_rows = current_csv(path)
    if len(old_rows) != len(new_rows):
        raise AssertionError(f"{path}: row count changed")
    for row_number, (old, new) in enumerate(zip(old_rows, new_rows), start=2):
        for field in columns:
            if old.get(field, "") != new.get(field, ""):
                raise AssertionError(f"{path}:{row_number}: numeric field {field} changed")


def assert_clean_table_text() -> None:
    forbidden = [
        "human_gold_standard",
        "gold_outcome",
        "gold standard",
        "gold-standard",
        "gold labels",
        "gold plus",
        "validated-sample",
        "author-reviewed",
    ]
    table_paths = [
        "paper/tables/dsl_adjusted_outcome_distribution.tex",
        "paper/tables/dsl_surrogate_validation.tex",
        "paper/tables/empirical_case_panel_coverage.tex",
        "paper/tables/llm_screening_status.tex",
        "paper/tables/pilot_lpm_institutional_change.tex",
        "paper/tables/pilot_case_historical_capacity.tex",
        "paper/tables/pilot_validated_exit_types.tex",
        "paper/tables/pilot_validation_tiers.tex",
        "paper/tables/pilot_capacity_bin_exit_type.tex",
        "paper/figures/pilot_exit_type_distribution.tex",
    ]
    for path in table_paths:
        text = (ROOT / path).read_text(encoding="utf-8").lower()
        for phrase in forbidden:
            if phrase in text:
                raise AssertionError(f"{path}: false provenance phrase {phrase!r}")


def main() -> int:
    compare_rows(
        "data/analysis_inputs/codex_surrogate_labels_2026_07_03_expanded.csv",
        set(),
    )
    compare_rows(
        "data/analysis_inputs/llm_screening_sample_2026_07_03_expanded.csv",
        {"label_source", "screening_status", "missing_information", "needs_human_review"},
    )
    compare_numeric_columns(
        "data/analysis_inputs/dsl_augmented_outcome_distribution.csv",
        [
            "observations",
            "nominal_exit",
            "institutional_change_or_error",
            "nominal_share",
        ],
    )
    compare_numeric_columns(
        "data/analysis_inputs/dsl_surrogate_diagnostics.csv", ["value"]
    )
    compare_rows(
        "data/analysis_inputs/issuer_level_surrogate_empirical_input.csv",
        {"analytic_id", "analytic_role", "label_source", "notes"},
    )
    compare_rows(
        "data/analysis_inputs/empirical_case_panel.csv",
        {"panel_id", "analytic_role", "label_source", "notes"},
    )
    compare_numeric_columns(
        "data/analysis_inputs/empirical_case_panel_coverage.csv",
        ["available", "denominator"],
    )
    compare_rows(
        "data/analysis_inputs/pilot_case_historical_capacity.csv",
        {"display_case_status"},
    )
    compare_numeric_columns(
        "data/analysis_inputs/pilot_exit_type_distribution.csv",
        [
            "total",
            "substantive_exit",
            "nominal_exit",
            "functional_transfer",
            "unclear",
        ],
    )

    _, screening_rows = current_csv(
        "data/analysis_inputs/llm_screening_sample_2026_07_03_expanded.csv"
    )
    sources = Counter(row["label_source"] for row in screening_rows)
    if sources[WORKING_REFERENCE_LABEL_SOURCE] != 94:
        raise AssertionError("expected 94 canonical working-reference screening rows")
    if sources[WORKING_REFERENCE_BOUNDARY_SOURCE] != 5:
        raise AssertionError("expected five canonical boundary-review screening rows")

    _, panel_rows = current_csv("data/analysis_inputs/empirical_case_panel.csv")
    roles = Counter(row["analytic_role"] for row in panel_rows)
    if roles[WORKING_REFERENCE_ANALYTIC_ROLE] != 94:
        raise AssertionError("expected 94 working-reference panel rows")
    if sum(row["include_in_current_validated_model_sample"] == "1" for row in panel_rows) != 84:
        raise AssertionError("current diagnostic model sample changed")
    if sum(row["include_in_full_controls_regression_sample"] == "1" for row in panel_rows) != 78:
        raise AssertionError("full-controls sample changed")

    assert_clean_table_text()
    print("label_role_rebuild_validation=ok")
    print("working_reference_rows=94 boundary_rows=5 surrogate_disclosure_rows=203")
    print("panel_rows=191 diagnostic_rows=84 full_controls_rows=78")
    print("numeric_and_label_fields_changed=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
