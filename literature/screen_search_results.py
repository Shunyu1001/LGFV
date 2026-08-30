#!/usr/bin/env python3
"""Deduplicate and conservatively screen literature-search metadata."""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
from collections import Counter


SPACE = re.compile(r"\s+")
NONWORD = re.compile(r"[^a-z0-9\u3400-\u9fff]+")


def normalize(value: str) -> str:
    return SPACE.sub(" ", value or "").strip()


def title_key(title: str) -> str:
    return NONWORD.sub("", normalize(title).lower())


def dedupe_key(row: dict) -> str:
    doi = normalize(row.get("doi", "")).lower()
    return "doi:" + doi if doi else "title:" + title_key(row.get("title", ""))


def screen(literature: str, text: str) -> tuple[str, str]:
    value = text.lower()
    if literature == "lgfv_exit_transformation":
        lgfv = any(term in value for term in [
            "local government financing vehicle", "local government financing platform",
            "lgfv", "地方政府融资平台", "地方融资平台", "城投",
        ])
        change = any(term in value for term in [
            "exit", "transform", "restructur", "market-oriented", "marketization",
            "withdraw", "liquidat", "退出", "转型", "重组", "市场化", "清算",
        ])
        if lgfv and change:
            return "manual_review", "lgfv_and_institutional_change_terms"
        if not lgfv:
            return "excluded_title_abstract", "not_lgfv"
        return "excluded_title_abstract", "lgfv_without_exit_or_transformation_outcome"

    if literature == "debt_resolution_recentralization":
        china = any(term in value for term in ["china", "chinese", "中国"])
        local = any(term in value for term in [
            "local government", "subnational", "municipal", "lgfv",
            "地方政府", "地方债", "融资平台", "城投",
        ])
        resolution = any(term in value for term in [
            "debt", "fiscal", "swap", "restructur", "resolution", "recentral",
            "债务", "财政", "置换", "化债", "重组", "再集中",
        ])
        if china and local and resolution:
            return "manual_review", "china_local_debt_resolution_terms"
        if not china:
            return "excluded_title_abstract", "not_china"
        if not local:
            return "excluded_title_abstract", "not_local_or_subnational_debt"
        return "excluded_title_abstract", "no_debt_resolution_or_fiscal_governance_link"

    if literature == "compliance_functional_substitution":
        organization = any(term in value for term in [
            "organization", "organisation", "corporate", "firm", "regulat",
            "institution", "bureaucr", "agency", "组织", "企业", "监管", "机构",
        ])
        compliance = any(term in value for term in [
            "compliance", "decoupl", "recoupl", "symbolic", "substantive",
            "implementation", "law in action", "合规", "脱钩", "执行",
        ])
        if organization and compliance:
            return "manual_review", "organizational_compliance_or_decoupling_terms"
        if not organization:
            return "excluded_title_abstract", "not_organizational_or_regulatory"
        return "excluded_title_abstract", "no_formal_substantive_compliance_link"

    if literature == "text_measurement_error":
        text_measure = any(term in value for term in [
            "text", "language model", "llm", "annotation", "classification", "coding",
            "data-mined", "document", "文本", "语言模型", "标注", "分类",
        ])
        validity = any(term in value for term in [
            "measurement", "error", "valid", "inference", "surrogate", "accuracy",
            "reliab", "bias", "测量", "误差", "验证", "推断", "偏差",
        ])
        if text_measure and validity:
            return "manual_review", "text_or_llm_measurement_validity_terms"
        if not text_measure:
            return "excluded_title_abstract", "generic_measurement_error_without_text_or_llm"
        return "excluded_title_abstract", "text_method_without_validation_or_inference_link"

    raise ValueError(f"Unknown literature: {literature}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = list(csv.DictReader(open(args.candidates, newline="")))
    grouped: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        grouped.setdefault((row["literature"], dedupe_key(row)), []).append(row)

    screened = []
    for (literature, key), versions in grouped.items():
        versions.sort(key=lambda row: (bool(row.get("abstract")), bool(row.get("doi"))), reverse=True)
        row = dict(versions[0])
        title_abstract = normalize(row.get("title", "") + " " + row.get("abstract", ""))
        status, reason = screen(literature, title_abstract)
        row.update({
            "dedupe_key": key,
            "query_ids": ";".join(sorted({item["query_id"] for item in versions})),
            "databases": ";".join(sorted({item["database"] for item in versions})),
            "duplicate_rows": len(versions),
            "screen_status": status,
            "screen_reason": reason,
        })
        screened.append(row)

    screened.sort(key=lambda row: (row["literature"], row["screen_status"], row["title"].lower()))
    output = pathlib.Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "literature", "dedupe_key", "query_ids", "databases", "duplicate_rows",
        "screen_status", "screen_reason", "title", "authors", "year", "venue",
        "doi", "record_url", "work_type", "abstract",
    ]
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(screened)

    summary = {
        "candidate_rows": len(rows),
        "deduplicated_works": len(screened),
        "counts_by_literature_and_status": {
            f"{literature}:{status}": count
            for (literature, status), count in sorted(
                Counter((row["literature"], row["screen_status"]) for row in screened).items()
            )
        },
        "method": "conservative deterministic title-and-abstract metadata screen",
        "note": "Manual full-text inclusion decisions are recorded separately; this screen does not treat metadata as evidence.",
    }
    output.with_suffix(".summary.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
