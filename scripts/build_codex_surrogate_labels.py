#!/usr/bin/env python3
"""Build Codex surrogate labels for the LLM candidate pool.

The output is a screening artifact, not a human-validated label file. It keeps
gold-standard human labels separate from Codex-generated surrogate labels and
marks cases without usable source packets as unresolved.
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import re
from datetime import date


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_SEED = ROOT / "data" / "analysis_inputs" / "llm_candidate_pool_seed_2026_06_30.csv"
DEFAULT_MASTER = ROOT / "data" / "analysis_inputs" / "master_case_pool.csv"
DEFAULT_HUMAN = ROOT / "data" / "processed" / "human_validated_labels.csv"
DEFAULT_DOCS = ROOT / "data" / "document_inventory.csv"
DEFAULT_SOURCES = ROOT / "data" / "source_inventory.csv"
DEFAULT_OUTPUT = ROOT / "data" / "analysis_inputs" / f"codex_surrogate_labels_{date.today():%Y_%m_%d}.csv"

DIRECT_COMPLIANCE_TERMS = [
    "退出\\s*融资平台",
    "退出.*融资平台",
    "不\\s*承担\\s*政府\\s*融资",
    "不\\s*从事\\s*政府\\s*融资",
    "不\\s*再\\s*承担\\s*政府\\s*融资",
    "不\\s*再\\s*从事\\s*政府\\s*融资",
    "无\\s*政府\\s*融资\\s*职能",
    "市场化\\s*转型",
    "经营性\\s*转型",
]

TRANSFER_EVENT_TERMS = [
    "整体划转",
    "无偿划转",
    "资产重组",
    "重大资产重组",
    "债务承继",
    "整合重组",
]

LIQUIDATION_TERMS = [
    "注销",
    "清算",
    "破产",
    "撤销",
]

CONTINUED_TERMS = [
    "基础设施",
    "城市建设",
    "土地开发",
    "土地整理",
    "棚户区",
    "保障房",
    "安置房",
    "委托代建",
    "代建",
    "BT",
    "PPP",
    "政府购买",
    "财政补贴",
    "财政拨款",
    "财政资金",
    "财政返还",
    "应收.*政府",
    "政府支持",
    "政府性基金",
    "公益性项目",
    "公用事业",
    "项目回购",
    "还本付息",
]

TRANSFER_TERMS = [
    "划转",
    "整合",
    "合并",
    "并入",
    "重组",
    "承继",
    "转让",
    "新设",
    "设立",
    "注入",
    "股权变更",
]

NEGATED_EVENT_PATTERNS = [
    "不涉及 MQ.4",
    "无新增涉及 MQ.4",
    "不涉及.*重大资产重组",
    "无新增涉及.*重大资产重组",
    "城投公司信用风险结构性分化",
    "国发【2021】5 号文提出",
    "国发\\[2021\\]5 号文提出",
]

FIELDS = [
    "pool_id",
    "source_row_id",
    "province",
    "city",
    "issuer_name",
    "validation_status",
    "label_source",
    "surrogate_status",
    "formal_event_found",
    "formal_event_summary",
    "continued_function_found",
    "continued_function_summary",
    "exit_type",
    "confidence",
    "source_coverage_score",
    "continued_function_evidence_score",
    "alternative_label",
    "missing_information",
    "classification_rationale",
    "evidence_basis",
    "needs_human_review",
    "labeler",
]


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def norm(value: object) -> str:
    if value is None:
        return ""
    text = str(value)
    if text == "nan":
        return ""
    return text.strip()


def any_term(text: str, terms: list[str]) -> bool:
    return any(re.search(term, text, flags=re.IGNORECASE) for term in terms)


def scrub_negated_event_context(text: str) -> str:
    scrubbed = text
    for pattern in NEGATED_EVENT_PATTERNS:
        scrubbed = re.sub(pattern, "", scrubbed, flags=re.IGNORECASE)
    return scrubbed


def first_snippet(text: str, terms: list[str], width: int = 80) -> str:
    for term in terms:
        match = re.search(term, text, flags=re.IGNORECASE)
        if match:
            start = max(0, match.start() - width)
            end = min(len(text), match.end() + width)
            return re.sub(r"\s+", " ", text[start:end]).strip()
    return ""


def processed_text(case_id: str, docs: list[dict[str, str]]) -> tuple[str, list[str]]:
    parts: list[str] = []
    used: list[str] = []
    for row in docs:
        if row.get("case_id") != case_id:
            continue
        local = norm(row.get("local_file_path"))
        if not local:
            continue
        txt_path = ROOT / "data" / "processed" / case_id / f"{pathlib.Path(local).stem}.txt"
        if not txt_path.exists():
            continue
        text = txt_path.read_text(encoding="utf-8", errors="ignore")
        if len(text.strip()) < 200:
            continue
        parts.append(text)
        used.append(row.get("document_id", ""))
    return "\n".join(parts), used


def human_row(seed_row: dict[str, str], human_by_case: dict[str, dict[str, str]]) -> dict[str, str]:
    case_id = seed_row["source_row_id"]
    human = human_by_case.get(case_id, {})
    label = norm(human.get("final_label"))
    return {
        "pool_id": seed_row["pool_id"],
        "source_row_id": case_id,
        "province": seed_row.get("province", ""),
        "city": seed_row.get("city", ""),
        "issuer_name": seed_row.get("issuer_name", ""),
        "validation_status": seed_row.get("validation_status", ""),
        "label_source": "human_gold_standard",
        "surrogate_status": "not_surrogate",
        "formal_event_found": "true",
        "formal_event_summary": norm(human.get("official_exit_event")),
        "continued_function_found": "true" if label in {"nominal_exit", "functional_transfer"} else "",
        "continued_function_summary": norm(human.get("final_rationale")),
        "exit_type": label,
        "confidence": norm(human.get("final_confidence")),
        "source_coverage_score": norm(human.get("source_coverage_score")),
        "continued_function_evidence_score": "",
        "alternative_label": norm(human.get("alternative_label")),
        "missing_information": norm(human.get("caveat")),
        "classification_rationale": norm(human.get("final_rationale")),
        "evidence_basis": "; ".join(
            x for x in [norm(human.get("primary_evidence_doc")), norm(human.get("secondary_evidence_doc"))] if x
        ),
        "needs_human_review": "false",
        "labeler": "human",
    }


def unresolved(seed_row: dict[str, str], reason: str, source_coverage: str = "1") -> dict[str, str]:
    return {
        "pool_id": seed_row["pool_id"],
        "source_row_id": seed_row["source_row_id"],
        "province": seed_row.get("province", ""),
        "city": seed_row.get("city", ""),
        "issuer_name": seed_row.get("issuer_name", ""),
        "validation_status": seed_row.get("validation_status", ""),
        "label_source": "codex_surrogate",
        "surrogate_status": "unresolved",
        "formal_event_found": "false",
        "formal_event_summary": "",
        "continued_function_found": "",
        "continued_function_summary": "",
        "exit_type": "unclear",
        "confidence": "low",
        "source_coverage_score": source_coverage,
        "continued_function_evidence_score": "0",
        "alternative_label": "",
        "missing_information": reason,
        "classification_rationale": "The available screening record is insufficient for an exit-type label under the frozen codebook.",
        "evidence_basis": norm(seed_row.get("source_url")) or norm(seed_row.get("announcement_title")),
        "needs_human_review": "true",
        "labeler": "Codex GPT-5; conservative source-packet screening",
    }


def surrogate_row(
    seed_row: dict[str, str],
    master_row: dict[str, str],
    docs: list[dict[str, str]],
    sources_by_case: dict[str, list[dict[str, str]]],
) -> dict[str, str]:
    case_id = seed_row["source_row_id"]
    text, used_docs = processed_text(case_id, docs)
    source_notes = " ".join(norm(r.get("notes")) for r in sources_by_case.get(case_id, []))
    combined = "\n".join([text, source_notes, norm(master_row.get("source_doc_types"))])

    if not combined.strip():
        return unresolved(seed_row, "No usable source text or source notes have been collected for this candidate.", "0")

    event_text = scrub_negated_event_context(combined)
    direct_compliance = any_term(event_text, DIRECT_COMPLIANCE_TERMS)
    # Transfers are kept as evidence, but they do not create a surrogate label
    # without direct exit or compliance language. This avoids treating ordinary
    # historical equity transfers in prospectuses as LGFV exit events.
    transfer_event = False
    liquidation = False
    formal = direct_compliance
    continued = any_term(combined, CONTINUED_TERMS)
    transfer = transfer_event and any_term(event_text, TRANSFER_TERMS)

    formal_snip = first_snippet(event_text, DIRECT_COMPLIANCE_TERMS)
    continued_snip = first_snippet(combined, CONTINUED_TERMS)

    if not formal:
        row = unresolved(
            seed_row,
            "Usable source text exists, but Codex did not find a direct formal exit, compliance, transfer, or liquidation event.",
            "2" if used_docs else "1",
        )
        row["continued_function_found"] = "true" if continued else "false"
        row["continued_function_summary"] = continued_snip
        row["evidence_basis"] = "; ".join(used_docs) or source_notes[:200]
        return row

    if liquidation and not continued:
        label = "liquidation"
        alt = ""
    elif transfer and continued and not direct_compliance:
        label = "functional_transfer"
        alt = "nominal_exit"
    elif continued:
        label = "nominal_exit"
        alt = "substantive_exit"
    else:
        label = "substantive_exit"
        alt = "unclear"

    coverage = "3" if len(used_docs) >= 2 else ("2" if used_docs else "1")
    function_score = "3" if continued and re.search("融资|债|BT|PPP|回购|财政|政府", continued_snip) else ("2" if continued else "0")
    return {
        "pool_id": seed_row["pool_id"],
        "source_row_id": case_id,
        "province": seed_row.get("province", ""),
        "city": seed_row.get("city", ""),
        "issuer_name": seed_row.get("issuer_name", ""),
        "validation_status": seed_row.get("validation_status", ""),
        "label_source": "codex_surrogate",
        "surrogate_status": "labeled",
        "formal_event_found": "true",
        "formal_event_summary": formal_snip,
        "continued_function_found": "true" if continued else "false",
        "continued_function_summary": continued_snip,
        "exit_type": label,
        "confidence": "medium" if coverage == "3" and continued else "low",
        "source_coverage_score": coverage,
        "continued_function_evidence_score": function_score,
        "alternative_label": alt,
        "missing_information": "Requires human validation against original PDF line references before entering the gold-standard label file.",
        "classification_rationale": (
            "Codex applied the frozen codebook to collected source text and notes. "
            f"Formal event found={formal}; continued function found={continued}; transfer signal={transfer}; liquidation signal={liquidation}."
        ),
        "evidence_basis": "; ".join(used_docs) or source_notes[:200],
        "needs_human_review": "true",
        "labeler": "Codex GPT-5; conservative source-packet screening",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=pathlib.Path, default=DEFAULT_SEED)
    parser.add_argument("--master", type=pathlib.Path, default=DEFAULT_MASTER)
    parser.add_argument("--human", type=pathlib.Path, default=DEFAULT_HUMAN)
    parser.add_argument("--docs", type=pathlib.Path, default=DEFAULT_DOCS)
    parser.add_argument("--sources", type=pathlib.Path, default=DEFAULT_SOURCES)
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    seed = read_csv(args.seed)
    master_by_case = {row["case_id"]: row for row in read_csv(args.master)}
    human_by_case = {row["case_id"]: row for row in read_csv(args.human)}
    docs = read_csv(args.docs)
    sources_by_case: dict[str, list[dict[str, str]]] = {}
    for row in read_csv(args.sources):
        sources_by_case.setdefault(row.get("case_id", ""), []).append(row)

    output: list[dict[str, str]] = []
    for row in seed:
        if row.get("llm_label_status") == "gold_standard":
            output.append(human_row(row, human_by_case))
            continue
        master = master_by_case.get(row.get("source_row_id", ""), {})
        output.append(surrogate_row(row, master, docs, sources_by_case))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    counts: dict[tuple[str, str], int] = {}
    for row in output:
        key = (row["label_source"], row["exit_type"])
        counts[key] = counts.get(key, 0) + 1

    print(f"wrote {len(output)} rows to {args.output}")
    for (source, label), count in sorted(counts.items()):
        print(f"{source},{label},{count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
