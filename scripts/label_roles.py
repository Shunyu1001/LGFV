"""Canonical label roles for generated LGFV research artifacts.

Some legacy input columns and status values predate the distinction between
Codex source-packet review and independent human confirmation. Builders may
read those values for backward compatibility, but they must emit the canonical
roles below.
"""

from __future__ import annotations


WORKING_REFERENCE_ANALYTIC_ROLE = "working_reference_outcome"
WORKING_REFERENCE_LABEL_SOURCE = "codex_source_packet_working_reference"
WORKING_REFERENCE_SCREENING_STATUS = "working_reference_exit_type"
WORKING_REFERENCE_POOL_STATUS = "working_reference"
WORKING_REFERENCE_BOUNDARY_SOURCE = "codex_source_packet_boundary_review"
WORKING_REFERENCE_BOUNDARY_STATUS = "working_reference_boundary"
WORKING_REFERENCE_PRODUCER = "Codex source-packet review on behalf of Shunyu Hao"
INDEPENDENT_CONFIRMATION_NOTICE = "Working reference labels await independent human confirmation."

LLM_SURROGATE_LABEL_SOURCE = "codex_surrogate"

LEGACY_WORKING_REFERENCE_STATUSES = frozenset(
    {
        "human_validated",
        "gold_standard",
        WORKING_REFERENCE_POOL_STATUS,
    }
)
LEGACY_WORKING_REFERENCE_SOURCES = frozenset(
    {
        "human_gold_standard",
        WORKING_REFERENCE_LABEL_SOURCE,
    }
)
LEGACY_BOUNDARY_SOURCES = frozenset(
    {
        "human_reviewed_boundary",
        WORKING_REFERENCE_BOUNDARY_SOURCE,
    }
)


def is_working_reference_status(value: object) -> bool:
    return str(value or "").strip() in LEGACY_WORKING_REFERENCE_STATUSES


def is_working_reference_source(value: object) -> bool:
    return str(value or "").strip() in LEGACY_WORKING_REFERENCE_SOURCES


def is_boundary_source(value: object) -> bool:
    return str(value or "").strip() in LEGACY_BOUNDARY_SOURCES
