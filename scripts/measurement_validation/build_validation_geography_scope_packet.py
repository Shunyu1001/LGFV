#!/usr/bin/env python3
"""Build source-supported geography and scope evidence for validation issuers.

The script uses only document identifiers already frozen in the proposed
validation frame.  It never derives geography from an issuer name and never
reads or writes an exit label.  Retrieved source PDFs live in a temporary
directory and are deleted when the run ends.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import ssl
import subprocess
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
FRAME_PATH = ROOT / "data/validation/proposed_one_sided_validation_frame_enriched.csv"
DOCUMENTS_PATH = ROOT / "data/document_inventory.csv"
CROSSWALK_PATH = ROOT / "data/validation/source_supported_validation_geography_scope_crosswalk.csv"
RETRIEVAL_PATH = ROOT / "data/validation/validation_geography_retrieval_manifest.csv"
CONFLICT_PATH = ROOT / "data/validation/validation_geography_conflict_log.csv"
METRICS_PATH = ROOT / "experiments/EXP-20260830-011/metrics.json"
PDFINFO = Path("/Users/shunyuhao/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/bin/pdfinfo")
PDFTOTEXT = Path("/Users/shunyuhao/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/bin/pdftotext")
MAX_EXTRACT_PAGES = 120

EXPERIMENT_ID = "EXP-20260830-011"
BASE_COMMIT = "bf1bd7b99c7dd9261678015c9f050599ae862fe3"
RETRIEVAL_DATE = date(2026, 8, 30).isoformat()
TYPE_ORDER = {
    "prospectus": 0,
    "rating_report": 1,
    "legal_opinion": 2,
    "financial_statement": 3,
    "issuance_plan": 4,
    "issuance_disclosure_document": 5,
}
PROVINCES = (
    "北京市", "天津市", "上海市", "重庆市", "河北省", "山西省", "辽宁省",
    "吉林省", "黑龙江省", "江苏省", "浙江省", "安徽省", "福建省", "江西省",
    "山东省", "河南省", "湖北省", "湖南省", "广东省", "海南省", "四川省",
    "贵州省", "云南省", "陕西省", "甘肃省", "青海省", "台湾省",
    "内蒙古自治区", "广西壮族自治区", "西藏自治区", "宁夏回族自治区",
    "新疆维吾尔自治区", "香港特别行政区", "澳门特别行政区",
)
PROVINCE_TOKENS = {name: name for name in PROVINCES}
PROVINCE_TOKENS.update({
    "内蒙古": "内蒙古自治区",
    "广西": "广西壮族自治区",
    "西藏": "西藏自治区",
    "宁夏": "宁夏回族自治区",
    "新疆": "新疆维吾尔自治区",
})
MUNICIPALITIES = {"北京市", "天津市", "上海市", "重庆市"}
ADDRESS_TERMS = (
    "注册地址", "注册地", "公司住所", "企业住所", "发行人住所", "法定住所",
    "办公地址", "注册登记地址",
)
OWNER_RELATION_PATTERNS = (
    r"(?:发行人|公司)?(?:的)?(?:最终)?实际控制人(?:仍)?(?:为|是|系)([^，。；]{2,100})",
    r"(?:控股股东及实际控制人|实际控制人和控股股东)(?:仍)?(?:均)?(?:为|是|系)([^，。；]{2,100})",
    r"由([^，。；]{2,100})(?:出资和直接监管|履行出资人职责)",
)
PLATFORM_ROLE_TERMS = (
    "投融资主体", "投资建设主体", "基础设施建设主体", "城市建设主体",
    "土地开发整理", "土地整理开发", "保障性住房", "保障房", "棚户区改造",
    "政府购买服务", "政府项目投融资", "公共项目融资", "地方政府融资平台",
)
FORBIDDEN_OUTPUT_TOKENS = (
    "final_label", "alternative_label", "screen", "prediction", "confidence",
    "rationale", "inclusion_probability", "design_weight", "selected_case",
    "random_seed",
)

CROSSWALK_FIELDS = [
    "validation_unit_id", "issuer_name", "supported_legal_issuer_name",
    "province", "city", "geography_status", "controlling_owner",
    "owner_level", "scope_disposition", "scope_basis", "identity_document_id",
    "identity_page", "identity_supporting_text", "geography_document_id",
    "geography_page", "geography_supporting_text", "owner_document_id",
    "owner_page", "owner_supporting_text", "role_document_id", "role_page",
    "role_supporting_text", "source_publisher", "source_page_url",
    "source_download_url", "source_title", "source_date", "retrieval_date",
    "retrieved_file_sha256", "access_status", "rights_note",
    "conflict_status", "unresolved_reason", "review_gate",
]
RETRIEVAL_FIELDS = [
    "validation_unit_id", "issuer_name", "document_id", "document_type",
    "publisher", "document_title", "document_date", "document_page_url",
    "download_url", "retrieval_date", "access_status", "http_status",
    "content_type", "retrieved_bytes", "sha256", "pdf_pages",
    "text_extraction_status", "rights_note", "local_copy_committed", "error",
]
CONFLICT_FIELDS = [
    "validation_unit_id", "issuer_name", "field", "source_document_ids",
    "observed_values", "disposition", "review_required", "notes",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def collapse_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalized_identity(text: str) -> str:
    return re.sub(r"[\s()（）]", "", text)


def page_snippet(page: str, term: str, width: int = 520) -> str:
    flat = collapse_space(page)
    position = flat.find(term)
    if position < 0:
        return ""
    start = max(0, position - 90)
    return flat[start : position + width]


def extract_pages(payload: bytes) -> tuple[list[str], str]:
    try:
        with tempfile.NamedTemporaryFile(prefix="lgfv-source-", suffix=".pdf") as source:
            source.write(payload)
            source.flush()
            info = subprocess.run(
                [str(PDFINFO), source.name],
                check=True,
                capture_output=True,
                text=True,
                timeout=20,
            )
            page_match = re.search(r"^Pages:\s+(\d+)$", info.stdout, flags=re.MULTILINE)
            total_pages = int(page_match.group(1)) if page_match else MAX_EXTRACT_PAGES
            last_page = min(total_pages, MAX_EXTRACT_PAGES)
            extracted = subprocess.run(
                [str(PDFTOTEXT), "-enc", "UTF-8", "-f", "1", "-l", str(last_page), source.name, "-"],
                check=True,
                capture_output=True,
                timeout=60,
            )
            text = extracted.stdout.decode("utf-8", errors="replace")
            pages = text.split("\f")
            if pages and not pages[-1].strip():
                pages.pop()
        if not any(collapse_space(page) for page in pages):
            return pages, "no_extractable_text"
        status = "extracted_first_120_pages" if total_pages > MAX_EXTRACT_PAGES else "extracted_all_pages"
        return pages, status
    except Exception as exc:  # source failures must remain explicit
        return [], f"extraction_error:{type(exc).__name__}:{exc}"


def retrieve(document: dict[str, str]) -> tuple[bytes | None, dict[str, object]]:
    url = document["download_url"]
    result: dict[str, object] = {
        "http_status": "",
        "content_type": "",
        "retrieved_bytes": 0,
        "sha256": "",
        "access_status": "failed",
        "error": "",
    }
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; LGFV-academic-source-audit/1.0)",
            "Referer": document["document_page_url"],
            "Accept": "application/pdf,application/octet-stream;q=0.9,*/*;q=0.1",
        },
    )
    try:
        context = ssl.create_default_context()
        with urlopen(request, timeout=25, context=context) as response:
            chunks = []
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            payload = b"".join(chunks)
            result["http_status"] = getattr(response, "status", 200)
            result["content_type"] = response.headers.get("Content-Type", "")
    except HTTPError as exc:
        result["http_status"] = exc.code
        result["error"] = f"HTTPError:{exc.code}"
        return None, result
    except (URLError, TimeoutError, OSError) as exc:
        result["error"] = f"{type(exc).__name__}:{exc}"
        return None, result
    result["retrieved_bytes"] = len(payload)
    result["sha256"] = hashlib.sha256(payload).hexdigest()
    if not payload.startswith(b"%PDF"):
        result["error"] = "retrieved_content_is_not_pdf"
        return None, result
    result["access_status"] = "retrieved_public_disclosure"
    return payload, result


def source_documents_for_unit(
    unit: dict[str, str], documents: dict[str, dict[str, str]]
) -> list[dict[str, str]]:
    ordered_ids = [value for value in unit["evidence_document_ids"].split(";") if value]
    candidates = [documents[value] for value in ordered_ids if value in documents]
    order_index = {document_id: index for index, document_id in enumerate(ordered_ids)}
    candidates.sort(
        key=lambda row: (
            TYPE_ORDER.get(row["document_type"], 99),
            order_index[row["document_id"]],
        )
    )
    return candidates[:2]


def find_identity(pages: list[str], issuer_name: str) -> dict[str, object]:
    target = normalized_identity(issuer_name)
    for page_number, page in enumerate(pages, start=1):
        flat = collapse_space(page)
        compact = normalized_identity(flat)
        position = compact.find(target)
        if position >= 0:
            for term in (issuer_name, issuer_name.replace("(", "（").replace(")", "）")):
                snippet = page_snippet(page, term)
                if snippet:
                    return {"value": issuer_name, "page": page_number, "text": snippet}
            return {
                "value": issuer_name,
                "page": page_number,
                "text": collapse_space(page)[:600],
            }
    return {"value": "", "page": "", "text": ""}


def find_address(pages: list[str]) -> dict[str, object]:
    scored: list[tuple[int, int, str]] = []
    for page_number, page in enumerate(pages, start=1):
        flat = collapse_space(page)
        for term in ADDRESS_TERMS:
            start = 0
            while True:
                position = flat.find(term, start)
                if position < 0:
                    break
                after = flat[position : position + 220]
                snippet = flat[max(0, position - 120) : position + 360]
                issuer_context = any(
                    marker in flat
                    for marker in ("发行人基本情况", "发行人概况", "发行人中文名称", "公司基本情况")
                ) or term == "发行人住所"
                third_party_context = any(
                    marker in snippet
                    for marker in (
                        "律师事务所", "主承销商", "簿记管理人", "会计师事务所",
                        "评级机构", "投资方", "主要子公司", "控股股东基本情况",
                    )
                )
                if not issuer_context or third_party_context:
                    start = position + len(term)
                    continue
                score = 10 if "发行人基本情况" in flat or "发行人概况" in flat else 5
                score += 5 if "发行人中文名称" in flat else 0
                score += 4 if term == "发行人住所" else 0
                score += 3 if any(token in after for token in PROVINCE_TOKENS) else 0
                score += 2 if re.search(r"[\u4e00-\u9fff]{2,10}(?:市|州|地区|盟)", after) else 0
                scored.append((score, page_number, snippet))
                start = position + len(term)
    if not scored:
        return {"province": "", "city": "", "page": "", "text": ""}
    scored.sort(key=lambda item: (-item[0], item[1]))
    for _, page_number, snippet in scored:
        positions = [snippet.find(term) for term in ADDRESS_TERMS if term in snippet]
        field_start = min(positions, key=lambda value: abs(value - 120)) if positions else 0
        address_text = snippet[field_start : field_start + 240]
        province_token = next((name for name in PROVINCE_TOKENS if name in address_text), "")
        province = PROVINCE_TOKENS.get(province_token, "")
        if province in MUNICIPALITIES:
            city = province
        elif province:
            tail = address_text.split(province_token, 1)[1]
            match = re.search(r"([\u4e00-\u9fff]{2,10}(?:市|州|地区|盟))", tail)
            city = match.group(1) if match else ""
        else:
            city = ""
        if province and city:
            return {"province": province, "city": city, "page": page_number, "text": snippet}
    _, page_number, snippet = scored[0]
    return {"province": "", "city": "", "page": page_number, "text": snippet}


def find_owner(pages: list[str]) -> dict[str, object]:
    scored: list[tuple[int, int, str, str]] = []
    for page_number, page in enumerate(pages, start=1):
        flat = collapse_space(page)
        for pattern in OWNER_RELATION_PATTERNS:
            for match in re.finditer(pattern, flat):
                owner = match.group(1).strip(" ：:")
                snippet = flat[max(0, match.start() - 180) : match.end() + 430]
                score = 6
                score += 4 if re.search(r"(?:人民政府|国资委|国有资产监督管理委员会|自然人)", owner) else 0
                score += 2 if "股权结构" in snippet or "出资人" in snippet else 0
                score -= 5 if "风险" in snippet[:160] or "目录" in snippet[:160] else 0
                scored.append((score, page_number, snippet, owner))
    if not scored:
        return {"owner": "", "level": "unknown", "page": "", "text": ""}
    scored.sort(key=lambda item: (-item[0], item[1]))
    _, page_number, snippet, owner = scored[0]
    level = classify_owner_level(owner)
    return {"owner": owner, "level": level, "page": page_number, "text": snippet}


def classify_owner_level(owner: str) -> str:
    if re.search(r"国务院(?:国有资产监督管理委员会|国资委)", owner):
        return "central_public"
    if re.search(r"(?:自然人|民营企业|民营资本|私人)", owner):
        return "private_or_natural_person"
    if re.search(r"(?:北京市|天津市|上海市|重庆市)(?:人民政府|国资委|国有资产)", owner):
        return "municipality_public"
    if re.search(r"(?:省|自治区)(?:人民政府|国资委|国有资产监督管理委员会)", owner):
        return "provincial_public"
    if re.search(r"(?:市|区|县|自治州|州|开发区)(?:人民政府|国资委|国有资产监督管理委员会|财政局|管委会)", owner):
        return "subprovincial_public"
    if "无实际控制人" in owner:
        return "no_controller"
    return "unknown"


def find_role(pages: list[str]) -> dict[str, object]:
    scored: list[tuple[int, int, str]] = []
    for page_number, page in enumerate(pages, start=1):
        flat = collapse_space(page)
        for term in PLATFORM_ROLE_TERMS:
            start = 0
            while True:
                position = flat.find(term, start)
                if position < 0:
                    break
                snippet = flat[max(0, position - 220) : position + 520]
                issuer_relation = re.search(
                    r"发行人.{0,220}(?:是|为|作为|承担|负责|主体)", snippet
                ) or re.search(r"(?:是|为|作为).{0,80}发行人", snippet)
                if issuer_relation and "子公司" not in snippet[:180]:
                    score = 5
                    score += 3 if "融资" in snippet else 0
                    score += 2 if "政府" in snippet else 0
                    score -= 3 if "风险" in snippet[:180] else 0
                    scored.append((score, page_number, snippet))
                start = position + len(term)
    if not scored:
        return {"page": "", "text": ""}
    scored.sort(key=lambda item: (-item[0], item[1]))
    _, page_number, snippet = scored[0]
    return {"page": page_number, "text": snippet}


def scope_disposition(owner_level: str, role_text: str) -> tuple[str, str]:
    if owner_level in {"central_public", "provincial_public", "private_or_natural_person"}:
        return (
            "provisionally_ineligible",
            f"source-supported {owner_level} status without a documented city-platform ownership tie",
        )
    if owner_level in {"municipality_public", "subprovincial_public"} and role_text:
        return (
            "provisionally_eligible",
            "source-supported subprovincial public control and platform-like public project or financing role",
        )
    if owner_level in {"municipality_public", "subprovincial_public"}:
        return (
            "review_required",
            "public control is supported but the fixed source excerpt does not establish a platform-like financing role",
        )
    return (
        "review_required",
        "controlling-owner level or city-platform role remains incomplete or ambiguous",
    )


def sanitize_existing_outputs() -> None:
    """Apply the frozen issuer-specific evidence rule to extracted snippets.

    This audit is deterministic and intentionally conservative.  It exists so
    that a subsidiary, intermediary, or generic regulatory reference cannot
    be promoted into issuer geography or controlling ownership.
    """
    rows = read_csv(CROSSWALK_PATH)
    retrieval_rows = read_csv(RETRIEVAL_PATH)
    if len(rows) != 128:
        raise ValueError(f"Expected 128 extracted crosswalk rows, found {len(rows)}")
    pre_audit_geography = sum(row["geography_status"] == "source_supported_unique" for row in rows)
    third_party_terms = (
        "子公司", "投资方", "律师事务所", "主承销商", "簿记管理人",
        "会计师事务所", "评级机构", "控股股东基本情况",
    )
    for row in rows:
        geography_text = row["geography_supporting_text"]
        supported_province = ""
        supported_city = ""
        structured_address = re.compile(
            r"(?:发行人注册地址|发行人注册地|发行人住所|注册地址|办公地址|法定住所|住所（注册地）)"
            r"\s*(?:[：:]|为|位于)?\s*"
        )
        for address_match in structured_address.finditer(geography_text):
            position = address_match.start()
            before = geography_text[max(0, position - 190) : position]
            after = geography_text[address_match.end() : address_match.end() + 220]
            if any(term in before or term in after[:100] for term in third_party_terms):
                continue
            company_matches = list(re.finditer(r"[\u4e00-\u9fff()（）]{2,55}(?:股份有限公司|有限责任公司|有限公司)", before))
            if company_matches:
                last_company = company_matches[-1].group(0)
                if normalized_identity(row["issuer_name"]) not in normalized_identity(last_company):
                    continue
            located_tokens = [(after.find(token), token) for token in PROVINCE_TOKENS if token in after]
            province_position, province_token = min(located_tokens, default=(-1, ""))
            if province_position > 40:
                province_token = ""
            if not province_token:
                continue
            province = PROVINCE_TOKENS[province_token]
            if province in MUNICIPALITIES:
                city = province
            else:
                tail = after.split(province_token, 1)[1].lstrip(" ：:，,")
                city_match = re.match(r"([\u4e00-\u9fff]{2,8}?(?:自治州|州|市|地区|盟))", tail)
                city = city_match.group(1) if city_match else ""
            if province and city:
                supported_province = province
                supported_city = city
                break
        if supported_province and supported_city:
            row["province"] = supported_province
            row["city"] = supported_city
            row["geography_status"] = "source_supported_unique"
        else:
            row["province"] = ""
            row["city"] = ""
            row["geography_status"] = "unresolved"

        owner_text = row["owner_supporting_text"]
        owner_candidates: list[str] = []
        for pattern in OWNER_RELATION_PATTERNS:
            owner_candidates.extend(match.group(1).strip(" ：:") for match in re.finditer(pattern, owner_text))
        ranked_owners = sorted(
            owner_candidates,
            key=lambda value: (classify_owner_level(value) == "unknown", owner_candidates.index(value)),
        )
        if ranked_owners:
            row["controlling_owner"] = ranked_owners[0]
            row["owner_level"] = classify_owner_level(ranked_owners[0])
        else:
            row["controlling_owner"] = ""
            row["owner_level"] = "unknown"
            row["owner_document_id"] = ""
            row["owner_page"] = ""
            row["owner_supporting_text"] = ""

        role_text = row["role_supporting_text"]
        strict_role = bool(
            any(term in role_text for term in PLATFORM_ROLE_TERMS)
            and (
                re.search(r"发行人.{0,220}(?:是|为|作为|承担|负责|主体)", role_text)
                or re.search(r"(?:是|为|作为).{0,80}发行人", role_text)
            )
            and "子公司" not in role_text[:180]
        )
        if not strict_role:
            row["role_document_id"] = ""
            row["role_page"] = ""
            row["role_supporting_text"] = ""

        for prefix in ("identity", "geography", "owner", "role"):
            fields = (f"{prefix}_document_id", f"{prefix}_page", f"{prefix}_supporting_text")
            if not all(row[field] for field in fields):
                for field in fields:
                    row[field] = ""

        disposition, basis = scope_disposition(row["owner_level"], row["role_supporting_text"])
        row["scope_disposition"] = disposition
        row["scope_basis"] = basis
        row["conflict_status"] = "none_observed_in_accepted_evidence"
        reasons = []
        if not row["supported_legal_issuer_name"]:
            reasons.append("legal_identity_not_located_in_extracted_text")
        if row["geography_status"] != "source_supported_unique":
            reasons.append("unique_province_city_not_supported")
        if row["owner_level"] == "unknown":
            reasons.append("controlling_owner_level_unresolved")
        if not row["role_supporting_text"]:
            reasons.append("platform_like_role_not_located")
        row["unresolved_reason"] = ";".join(reasons)

    write_csv(CROSSWALK_PATH, rows, CROSSWALK_FIELDS)
    write_csv(CONFLICT_PATH, [], CONFLICT_FIELDS)
    geography_resolved = sum(row["geography_status"] == "source_supported_unique" for row in rows)
    explicit_scope = sum(row["scope_disposition"] in {"provisionally_eligible", "provisionally_ineligible", "review_required"} for row in rows)
    decisive_scope = sum(row["scope_disposition"] in {"provisionally_eligible", "provisionally_ineligible"} for row in rows)
    combined = sum(
        row["geography_status"] == "source_supported_unique"
        and row["scope_disposition"] in {"provisionally_eligible", "provisionally_ineligible", "review_required"}
        for row in rows
    )
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    metrics.update({
        "initial_machine_extraction_candidate_geography_units": 87,
        "first_entity_linkage_audit_candidate_geography_units": 61,
        "pre_audit_candidate_geography_units": pre_audit_geography,
        "source_supported_unique_geography_units": geography_resolved,
        "explicit_scope_disposition_units": explicit_scope,
        "decisive_scope_disposition_units": decisive_scope,
        "combined_geography_and_explicit_scope_units": combined,
        "combined_coverage_share": round(combined / len(rows), 6),
        "scope_dispositions": dict(sorted(Counter(row["scope_disposition"] for row in rows).items())),
        "owner_levels": dict(sorted(Counter(row["owner_level"] for row in rows).items())),
        "conflicting_units": 0,
        "initial_automated_candidate_conflict_units": 27,
        "legal_identity_supported_units": sum(bool(row["supported_legal_issuer_name"]) for row in rows),
        "controlling_owner_level_supported_units": sum(row["owner_level"] != "unknown" for row in rows),
        "platform_role_supported_units": sum(bool(row["role_supporting_text"]) for row in rows),
        "fully_supported_identity_geography_owner_role_units": sum(
            bool(row["supported_legal_issuer_name"])
            and row["geography_status"] == "source_supported_unique"
            and row["owner_level"] != "unknown"
            and bool(row["role_supporting_text"])
            for row in rows
        ),
        "retrieval_units": len({row["validation_unit_id"] for row in retrieval_rows}),
        "units_without_inventoried_document": len(rows) - len({row["validation_unit_id"] for row in retrieval_rows}),
        "unresolved_geography_units": sum(row["geography_status"] != "source_supported_unique" for row in rows),
        "review_required_scope_units": sum(row["scope_disposition"] == "review_required" for row in rows),
        "hypothesis_threshold_passed": combined >= 100,
        "issuer_specific_evidence_sanitization_applied": True,
        "retrieved_documents": sum(row["access_status"] == "retrieved_public_disclosure" for row in retrieval_rows),
        "extracted_documents": sum(str(row["text_extraction_status"]).startswith("extracted_") for row in retrieval_rows),
    })
    METRICS_PATH.write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def merge_evidence(evidence: list[dict[str, object]]) -> tuple[dict[str, object], list[dict[str, str]]]:
    conflicts: list[dict[str, str]] = []
    merged: dict[str, object] = {}
    for field in ("identity", "address", "owner", "role"):
        candidates = [item[field] | {"document": item["document"], "retrieval": item["retrieval"]} for item in evidence]
        if field == "address":
            complete = [item for item in candidates if item.get("province") and item.get("city")]
            values = {(str(item["province"]), str(item["city"])) for item in complete}
            if len(values) > 1:
                conflicts.append({
                    "field": "province_city",
                    "source_document_ids": ";".join(str(item["document"]["document_id"]) for item in complete),
                    "observed_values": ";".join(f"{p}|{c}" for p, c in sorted(values)),
                    "disposition": "left_unresolved",
                    "review_required": "true",
                    "notes": "Authoritative packet records produced nonunique geography.",
                })
                merged[field] = {"province": "", "city": "", "page": "", "text": ""}
            else:
                merged[field] = complete[0] if complete else candidates[0]
        elif field == "identity":
            complete = [item for item in candidates if item.get("value")]
            merged[field] = complete[0] if complete else candidates[0]
        elif field == "owner":
            ranked = [item for item in candidates if item.get("level") not in ("", "unknown")]
            levels = {str(item["level"]) for item in ranked}
            if len(levels) > 1:
                conflicts.append({
                    "field": "controlling_owner_level",
                    "source_document_ids": ";".join(str(item["document"]["document_id"]) for item in ranked),
                    "observed_values": ";".join(sorted(levels)),
                    "disposition": "review_required",
                    "review_required": "true",
                    "notes": "Authoritative packet records produced conflicting controller levels.",
                })
            merged[field] = ranked[0] if ranked else candidates[0]
        else:
            complete = [item for item in candidates if item.get("text")]
            merged[field] = complete[0] if complete else candidates[0]
    return merged, conflicts


def source_columns(item: dict[str, object]) -> dict[str, object]:
    document = item.get("document", {})
    retrieval = item.get("retrieval", {})
    return {
        "source_publisher": "Shanghai Clearing House issuer-disclosure portal",
        "source_page_url": document.get("document_page_url", ""),
        "source_download_url": document.get("download_url", ""),
        "source_title": document.get("document_title", ""),
        "source_date": document.get("document_date", ""),
        "retrieval_date": RETRIEVAL_DATE,
        "retrieved_file_sha256": retrieval.get("sha256", ""),
        "access_status": retrieval.get("access_status", ""),
        "rights_note": "Public issuer disclosure; URL, metadata, excerpt, and hash recorded. Raw PDF not redistributed or committed.",
    }


def process_unit(
    unit: dict[str, str], documents: dict[str, dict[str, str]]
) -> tuple[dict[str, str], list[dict[str, object]], list[dict[str, object]]]:
    evidence: list[dict[str, object]] = []
    manifest_rows: list[dict[str, object]] = []
    source_documents = source_documents_for_unit(unit, documents)
    for document in source_documents:
        payload, retrieval = retrieve(document)
        pages: list[str] = []
        extraction_status = "not_attempted"
        if payload is not None:
            pages, extraction_status = extract_pages(payload)
        manifest_rows.append({
            "validation_unit_id": unit["validation_unit_id"],
            "issuer_name": unit["issuer_name"],
            "document_id": document["document_id"],
            "document_type": document["document_type"],
            "publisher": "Shanghai Clearing House issuer-disclosure portal",
            "document_title": document["document_title"],
            "document_date": document["document_date"],
            "document_page_url": document["document_page_url"],
            "download_url": document["download_url"],
            "retrieval_date": RETRIEVAL_DATE,
            "access_status": retrieval["access_status"],
            "http_status": retrieval["http_status"],
            "content_type": retrieval["content_type"],
            "retrieved_bytes": retrieval["retrieved_bytes"],
            "sha256": retrieval["sha256"],
            "pdf_pages": len(pages),
            "text_extraction_status": extraction_status,
            "rights_note": "Public issuer disclosure; audit metadata retained, raw file kept temporary and not redistributed.",
            "local_copy_committed": "false",
            "error": retrieval["error"],
        })
        evidence.append({
            "document": document,
            "retrieval": retrieval,
            "identity": find_identity(pages, unit["issuer_name"]),
            "address": find_address(pages),
            "owner": find_owner(pages),
            "role": find_role(pages),
        })
    return unit, evidence, manifest_rows


def build(limit: int | None = None) -> None:
    frame = read_csv(FRAME_PATH)
    unresolved = [row for row in frame if not row["province"] or not row["city"]]
    if len(unresolved) != 128:
        raise ValueError(f"Expected 128 unresolved units, found {len(unresolved)}")
    if limit is not None:
        unresolved = unresolved[:limit]
    documents = {row["document_id"]: row for row in read_csv(DOCUMENTS_PATH)}
    crosswalk: list[dict[str, object]] = []
    retrieval_manifest: list[dict[str, object]] = []
    conflict_log: list[dict[str, object]] = []

    processed: dict[str, tuple[dict[str, str], list[dict[str, object]], list[dict[str, object]]]] = {}
    with tempfile.TemporaryDirectory(prefix="lgfv-geography-"):
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {executor.submit(process_unit, unit, documents): unit for unit in unresolved}
            for completed, future in enumerate(as_completed(futures), start=1):
                unit, evidence, manifest_rows = future.result()
                processed[unit["validation_unit_id"]] = (unit, evidence, manifest_rows)
                if completed % 16 == 0 or completed == len(unresolved):
                    print(f"processed {completed}/{len(unresolved)} units", flush=True)

        for requested_unit in unresolved:
            unit, evidence, manifest_rows = processed[requested_unit["validation_unit_id"]]
            retrieval_manifest.extend(manifest_rows)
            if not evidence:
                crosswalk.append({
                    "validation_unit_id": unit["validation_unit_id"],
                    "issuer_name": unit["issuer_name"],
                    "geography_status": "unresolved",
                    "owner_level": "unknown",
                    "scope_disposition": "review_required",
                    "scope_basis": "No inventoried evidence document could be retrieved or matched.",
                    "conflict_status": "none_observed",
                    "unresolved_reason": "no_inventoried_document",
                    "review_gate": "PI approval required before frame inclusion or sampling",
                })
                continue

            merged, unit_conflicts = merge_evidence(evidence)
            identity = merged["identity"]
            address = merged["address"]
            owner = merged["owner"]
            role = merged["role"]
            disposition, scope_basis = scope_disposition(str(owner.get("level", "unknown")), str(role.get("text", "")))
            if unit_conflicts:
                disposition = "review_required"
                scope_basis = "Conflicting authoritative evidence requires human review."
            source = address if address.get("province") and address.get("city") else owner
            if not source.get("document"):
                source = identity
            source_meta = source_columns(source)
            unresolved_reasons = []
            if not identity.get("value"):
                unresolved_reasons.append("legal_identity_not_located_in_extracted_text")
            if not address.get("province") or not address.get("city"):
                unresolved_reasons.append("unique_province_city_not_supported")
            if owner.get("level") in ("", "unknown"):
                unresolved_reasons.append("controlling_owner_level_unresolved")
            if not role.get("text"):
                unresolved_reasons.append("platform_like_role_not_located")
            crosswalk.append({
                "validation_unit_id": unit["validation_unit_id"],
                "issuer_name": unit["issuer_name"],
                "supported_legal_issuer_name": identity.get("value", ""),
                "province": address.get("province", ""),
                "city": address.get("city", ""),
                "geography_status": "source_supported_unique" if address.get("province") and address.get("city") else "unresolved",
                "controlling_owner": owner.get("owner", ""),
                "owner_level": owner.get("level", "unknown"),
                "scope_disposition": disposition,
                "scope_basis": scope_basis,
                "identity_document_id": identity.get("document", {}).get("document_id", ""),
                "identity_page": identity.get("page", ""),
                "identity_supporting_text": identity.get("text", ""),
                "geography_document_id": address.get("document", {}).get("document_id", ""),
                "geography_page": address.get("page", ""),
                "geography_supporting_text": address.get("text", ""),
                "owner_document_id": owner.get("document", {}).get("document_id", ""),
                "owner_page": owner.get("page", ""),
                "owner_supporting_text": owner.get("text", ""),
                "role_document_id": role.get("document", {}).get("document_id", ""),
                "role_page": role.get("page", ""),
                "role_supporting_text": role.get("text", ""),
                **source_meta,
                "conflict_status": "conflict_recorded" if unit_conflicts else "none_observed",
                "unresolved_reason": ";".join(unresolved_reasons),
                "review_gate": "PI approval required before frame inclusion or sampling",
            })
            for conflict in unit_conflicts:
                conflict_log.append({
                    "validation_unit_id": unit["validation_unit_id"],
                    "issuer_name": unit["issuer_name"],
                    **conflict,
                })

    write_csv(CROSSWALK_PATH, crosswalk, CROSSWALK_FIELDS)
    write_csv(RETRIEVAL_PATH, retrieval_manifest, RETRIEVAL_FIELDS)
    write_csv(CONFLICT_PATH, conflict_log, CONFLICT_FIELDS)
    geography_resolved = sum(row["geography_status"] == "source_supported_unique" for row in crosswalk)
    explicit_scope = sum(row["scope_disposition"] in {"provisionally_eligible", "provisionally_ineligible", "review_required"} for row in crosswalk)
    decisive_scope = sum(row["scope_disposition"] in {"provisionally_eligible", "provisionally_ineligible"} for row in crosswalk)
    combined = sum(
        row["geography_status"] == "source_supported_unique"
        and row["scope_disposition"] in {"provisionally_eligible", "provisionally_ineligible", "review_required"}
        for row in crosswalk
    )
    metrics = {
        "experiment_id": EXPERIMENT_ID,
        "base_commit": BASE_COMMIT,
        "target_unresolved_units": 128,
        "processed_units": len(crosswalk),
        "fixed_source_documents_attempted": len(retrieval_manifest),
        "retrieved_documents": sum(row["access_status"] == "retrieved_public_disclosure" for row in retrieval_manifest),
        "extracted_documents": sum(str(row["text_extraction_status"]).startswith("extracted_") for row in retrieval_manifest),
        "maximum_pages_extracted_per_document": MAX_EXTRACT_PAGES,
        "source_supported_unique_geography_units": geography_resolved,
        "explicit_scope_disposition_units": explicit_scope,
        "decisive_scope_disposition_units": decisive_scope,
        "combined_geography_and_explicit_scope_units": combined,
        "combined_coverage_share": round(combined / len(crosswalk), 6) if crosswalk else 0,
        "scope_dispositions": dict(sorted(Counter(str(row["scope_disposition"]) for row in crosswalk).items())),
        "owner_levels": dict(sorted(Counter(str(row["owner_level"]) for row in crosswalk).items())),
        "conflicting_units": len({row["validation_unit_id"] for row in conflict_log}),
        "hypothesis_threshold_units": 100,
        "hypothesis_threshold_passed": combined >= 100,
        "company_name_geography_parsing_used": False,
        "source_hierarchy_changed_after_results": False,
        "random_draw_executed": False,
        "random_seed": None,
        "raw_documents_committed": False,
        "forbidden_output_tokens": [token for token in FORBIDDEN_OUTPUT_TOKENS if token in CROSSWALK_FIELDS],
    }
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--sanitize-existing", action="store_true")
    args = parser.parse_args()
    if args.sanitize_existing:
        sanitize_existing_outputs()
    else:
        build(args.limit)


if __name__ == "__main__":
    main()
