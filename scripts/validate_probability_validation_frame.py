#!/usr/bin/env python3
"""Validate the completed source review and probability-frame candidate."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRAME = ROOT / "data/validation/proposed_one_sided_validation_frame_enriched.csv"
OLD_CROSSWALK = ROOT / "data/validation/source_supported_validation_geography_scope_crosswalk.csv"
DECISIONS = ROOT / "experiments/EXP-20260831-001/review_decisions.csv"
CROSSWALK = ROOT / "data/validation/probability_validation_geography_scope_crosswalk.csv"
UNRESOLVED = ROOT / "data/validation/probability_validation_unresolved_log.csv"
SOURCE_MANIFEST = ROOT / "data/validation/probability_validation_source_manifest.csv"
CANDIDATE = ROOT / "data/validation/probability_validation_frame_candidate.csv"
ORIGINS = ROOT / "data/validation/probability_validation_frame_origin_rows.csv"
FLOW = ROOT / "data/validation/probability_validation_frame_flow.csv"
DESIGN = ROOT / "data/validation/probability_validation_sampling_design.csv"
METRICS = ROOT / "experiments/EXP-20260831-001/metrics.json"
SURROGATE = ROOT / "data/analysis_inputs/codex_surrogate_labels_2026_07_03_expanded.csv"
DOCUMENTS = ROOT / "data/document_inventory.csv"
HISTORICAL = ROOT / "data/analysis_inputs/candidate_city_historical_capacity.csv"
CONTROLS = ROOT / "data/analysis_inputs/contemporary_city_controls.csv"
DEFAULT_SOURCE_DIR = Path("/tmp/lgfv-exp015-sources")

ALLOWED_GEOGRAPHY = {"source_supported_unique", "source_supported_multiple", "unresolved_after_search"}
ALLOWED_SCOPE = {"eligible", "ineligible", "unresolved_after_search"}
LOCAL_OWNER = {"municipality_public", "subprovincial_public"}
EXCLUDED_OWNER = {"central_public", "provincial_public", "private_or_natural_person"}
ALLOWED_ADMIN = {"central", "provincial", "municipality", "prefecture", "district", "county", "development_zone", "private", "unresolved"}
ALLOWED_SCREEN = {"screen_positive_nominal", "screened_no_direct_formal_event"}
FORBIDDEN_OUTPUT_HEADERS = {
    "exit_type", "formal_event_found", "formal_event_summary",
    "continued_function_found", "continued_function_summary", "alternative_label",
    "classification_rationale", "confidence", "selected_case", "selection_order",
}
EXPECTED_OUTPUT_SCHEMAS = {
    CROSSWALK: (
        "validation_unit_id", "issuer_name", "supported_legal_issuer_name",
        "province", "city", "geography_status", "administrative_level",
        "controlling_owner", "owner_level", "scope_disposition",
        "scope_reason_code", "scope_basis", "audit_note",
        "identity_document_id", "identity_page", "identity_supporting_text",
        "geography_document_id", "geography_page", "geography_supporting_text",
        "owner_document_id", "owner_page", "owner_supporting_text",
        "role_document_id", "role_page", "role_supporting_text",
        "conflict_status", "unresolved_reason", "review_gate",
        "baseline_geography_gap", "baseline_scope_review",
    ),
    UNRESOLVED: (
        "validation_unit_id", "issuer_name", "failed_gate", "observed_values",
        "source_document_ids", "disposition", "reason_code", "notes",
        "review_required",
    ),
    SOURCE_MANIFEST: (
        "validation_unit_id", "issuer_name", "document_id", "document_type",
        "publisher", "document_title", "document_date", "document_page_url",
        "download_url", "retrieval_date", "access_status", "http_status",
        "content_type", "retrieved_bytes", "sha256", "pages",
        "text_extraction_status", "source_text_sha256", "extraction_profile",
        "cache_verification_status", "raw_cache_filename",
        "text_cache_filename", "rights_note", "local_copy_committed", "error",
    ),
    CANDIDATE: (
        "validation_unit_id", "issuer_key", "issuer_name",
        "normalized_legal_issuer_key", "scope_disposition", "eligibility_flag",
        "province", "city", "administrative_level", "geography_status",
        "screen_status", "source_coverage_score", "source_coverage_bin",
        "historical_capacity_bin", "historical_capacity_join_status",
        "historical_capacity_source_case_ids", "debt_pressure_availability",
        "debt_pressure_control_unit_id", "frozen_stratum_id",
        "stratum_population_n", "proposed_stratum_sample_n",
        "inclusion_probability", "proposed_design_weight",
        "deterministic_random_seed", "random_draw_executed",
    ),
    ORIGINS: (
        "validation_unit_id", "issuer_name", "scope_disposition",
        "eligibility_flag", "screen_status", "origin_position", "source_row_id",
        "pool_id", "evidence_document_ids",
    ),
    FLOW: (
        "stage", "disposition", "issuer_unit_count",
        "originating_disclosure_row_count", "notes",
    ),
    DESIGN: (
        "frozen_stratum_id", "screen_status", "source_coverage_bin",
        "historical_capacity_bin", "debt_pressure_availability",
        "administrative_level", "stratum_population_n",
        "proposed_stratum_sample_n", "inclusion_probability",
        "deterministic_random_seed", "random_draw_executed", "approval_status",
    ),
}
PREFECTURE_ROLLUPS = {
    "太仓市": "苏州市",
    "如皋市": "南通市",
}
HISTORICAL_ENGLISH_JOIN = {
    "乌鲁木齐市": ("Xinjiang", "Urumqi"),
    "福州市": ("Fujian", "Fuzhou"),
}
REPAIRED_GEOGRAPHY_EVIDENCE = {
    "mv_3c17f10ab84f": (
        "doc_exp2_20260703_0002_009",
        "251",
        "北京市",
        (
            "发行人： 北控水务集团有限公司",
            "联系地址：北京市朝阳区望京东园七区保利国际广场 T3 北控水务大厦",
        ),
    ),
    "mv_b14a65482fac": (
        "doc_sch_20260630_0168_006",
        "40",
        "重庆市",
        (
            "注册名称 西部（重庆）科学城江津园区开发建设集团有限公司",
            "住所（注册地） 重庆市江津区双福街道南北大道390号",
        ),
    ),
    "mv_3707ecbfb1f2": (
        "web_linyi_sasac_profile",
        "1",
        "临沂市",
        (
            "企业名称 临沂投资发展集团有限公司",
            "注册地址 山东省临沂市兰山区北城新区临沂商会大厦1号楼701",
        ),
    ),
    "mv_3134f5ad5182": (
        "web_chinamoney_jinluling_2025_rating",
        "6",
        "吉安市",
        (
            "公司原名为“吉安市金庐陵经济开发有限公司”",
            "公司实际控制人变更为吉安市国资委",
        ),
    ),
    "mv_6c405c7c4748": (
        "doc_sch_20260630_0012_012",
        "32",
        "济南市",
        (
            "注册名称 山东金曰交通发展集团有限公司",
            "住所（注册地） 山东省济南市章丘区圣井高科技工业园",
        ),
    ),
    "mv_a1ed5dac069a": (
        "doc_sch_20260630_0062_002",
        "205",
        "太原市",
        (
            "一、发行人 名称：山西交通控股集团有限公司",
            "住所：山西省示范区太原学府园区南中环街 529 号 B 座 24-25 层",
        ),
    ),
    "mv_a84c738293b5": (
        "doc_sch_20260630_0065_001",
        "27",
        "广州市",
        (
            "注册名称：广东省铁路建设投资集团有限公司",
            "注册地址：广东省广州市天河区黄埔大道中 668 号",
        ),
    ),
    "mv_457ad56917e5": (
        "doc_exp9_20260704_0141_007",
        "56",
        "南京市",
        (
            "一、发行人 江苏省国信集团有限公司",
            "联系地址：南京市玄武区长江路 88 号",
        ),
    ),
    "mv_58bf202441a9": (
        "doc_exp8_20260703_0009_003",
        "37",
        "深圳市",
        (
            "注册名称：深圳市地铁集团有限公司",
            "住所：深圳市福田区莲花街道福中一路1016号地铁大厦",
        ),
    ),
    "mv_bbc98d5aa00c": (
        "web_shenzhen_sasac_special_zone_development",
        "1",
        "深圳市",
        (
            "特区建发集团按照市委、市政府和市国资委的决策部署及要求",
            "地址：深圳市福田区福华一路大中华国际交易广场裙楼7楼",
        ),
    ),
    "mv_4aa0191176be": (
        "doc_exp10_20260704_0192_002",
        "240",
        "武汉市",
        (
            "一、发行人 发行人：湖北楚天智能交通股份有限公司",
            "联系地址：武汉市汉阳区湖北国展中心东塔",
        ),
    ),
    "mv_bce7a88198f3": (
        "doc_exp8_20260703_0087_004",
        "37",
        "荆门市",
        (
            "中文注册名称： 荆门高新技术产业开发有限责任公司",
            "住所： 湖北省荆门市高新区·掇刀区凤袁路 1 号",
        ),
    ),
    "mv_35577ffe2ec5": (
        "doc_gz_zy_daoqiao_2015_bond_prospectus",
        "22",
        "遵义市",
        (
            "名称：遵义市道路桥梁工程有限责任公司",
            "住所：遵义市汇川区苏州路中段公路枢纽组织管理中心",
        ),
    ),
    "mv_707d013abcbe": (
        "doc_sch_20260630_0114_001",
        "30",
        "西宁市",
        (
            "（一）注册名称：青海省国有资产投资管理有限公司",
            "（八）住所：青海省西宁市城中区创业路 128 号中小企业创业园 5 楼 501 室",
        ),
    ),
}
COURT_VENUE_GEOGRAPHY_PATTERN = re.compile(
    r"(?:住所地|注册地)[^。；]{0,80}(?:人民法院|法院)"
)
THIRD_PARTY_GEOGRAPHY_MARKERS = (
    "主承销商", "联席主承销商", "律师事务所", "会计师事务所",
    "评级机构", "召集人", "承销机构", "托管人", "登记结算机构",
)
THIRD_PARTY_ADDRESS_PATTERN = re.compile(
    r"(?:住所|注册地址|办公地址|联系地址|地址)\s*(?:[:：]|为|位于)?"
)
ADDRESS_VALUE_STOP_PATTERN = re.compile(
    r"\s+(?:(?:法定代表人|授权代表|负责人|联系人|电话|传真|邮政编码|网址|"
    r"统一社会信用代码|企业类型|经营范围|名称|住所|注册地址|注册地|办公地址|"
    r"联系地址|地址)\s*[:：]|[一二三四五六七八九十]+、)"
)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def validate_output_schemas(observed_schemas: dict[Path, list[str]]) -> None:
    for path, expected_fields in EXPECTED_OUTPUT_SCHEMAS.items():
        if tuple(observed_schemas[path]) != expected_fields:
            raise ValueError(
                f"Output schema mismatch for {path}: "
                f"{observed_schemas[path]} != {list(expected_fields)}"
            )
    for path, fields in observed_schemas.items():
        forbidden = sorted(FORBIDDEN_OUTPUT_HEADERS.intersection(fields))
        if forbidden:
            raise ValueError(f"Outcome or selection fields appear in {path}: {forbidden}")


def normalize(value: str) -> str:
    return re.sub(r"[\s()（）·,，。]", "", value).casefold()


def collapse_evidence(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def address_value_after(text: str, match: re.Match[str], width: int = 300) -> str:
    """Return only the current address field, bounded before the next labeled field."""
    value = text[match.end() : match.end() + width]
    stop = ADDRESS_VALUE_STOP_PATTERN.search(value)
    return value[: stop.start()] if stop else value


def geography_evidence_is_obviously_third_party_only(
    text: str,
    city: str,
    issuer_name: str = "",
) -> bool:
    """Identify venue boilerplate or an address explicitly assigned to an intermediary."""
    collapsed = collapse_evidence(text)
    if COURT_VENUE_GEOGRAPHY_PATTERN.search(collapsed):
        return True
    city_tokens = tuple(filter(None, (city, city.removesuffix("市").removesuffix("自治州"))))
    for address_match in THIRD_PARTY_ADDRESS_PATTERN.finditer(collapsed):
        address_segment = address_value_after(collapsed, address_match)
        if not any(token in address_segment for token in city_tokens):
            continue
        relation_prefix = collapsed[max(0, address_match.start() - 700) : address_match.start()]
        focal_positions = [relation_prefix.rfind("发行人")]
        if issuer_name:
            focal_positions.append(relation_prefix.rfind(issuer_name))
        third_party_positions = [
            relation_prefix.rfind(marker) for marker in THIRD_PARTY_GEOGRAPHY_MARKERS
        ]
        if max(focal_positions) >= 0 and max(focal_positions) > max(third_party_positions):
            return False
    for marker in THIRD_PARTY_GEOGRAPHY_MARKERS:
        start = 0
        while True:
            position = collapsed.find(marker, start)
            if position < 0:
                break
            segment = collapsed[position : position + 500]
            address_match = THIRD_PARTY_ADDRESS_PATTERN.search(segment)
            if address_match and any(
                token in address_value_after(segment, address_match) for token in city_tokens
            ):
                return True
            start = position + len(marker)
    return False


def validate_repaired_geography_row(row: dict[str, str]) -> None:
    """Independently require the registered focal-issuer/location pair for one repair."""
    unit_id = row["validation_unit_id"]
    expected = REPAIRED_GEOGRAPHY_EVIDENCE.get(unit_id)
    if expected is None:
        return
    document_id, page, city, anchors = expected
    if row["geography_status"] != "source_supported_unique":
        raise ValueError(f"Repaired geography is no longer uniquely resolved: {unit_id}")
    if row["city"] != city:
        raise ValueError(f"Repaired geography city mismatch: {unit_id}")
    if (row["geography_document_id"], row["geography_page"]) != (document_id, page):
        raise ValueError(f"Repaired geography locator mismatch: {unit_id}")
    evidence = row["geography_supporting_text"]
    if geography_evidence_is_obviously_third_party_only(
        evidence, city, row.get("issuer_name", "")
    ):
        raise ValueError(f"Repaired geography uses court-venue or third-party-only evidence: {unit_id}")
    compact = normalize(evidence)
    missing = [anchor for anchor in anchors if normalize(anchor) not in compact]
    if missing:
        raise ValueError(f"Repaired geography lacks its direct focal/location anchors: {unit_id}")
    anchor_positions = [compact.find(normalize(anchor)) for anchor in anchors]
    if anchor_positions != sorted(anchor_positions):
        raise ValueError(f"Repaired geography reverses its focal/location relation: {unit_id}")


def validate_repaired_geography_evidence(crosswalk_rows: list[dict[str, str]]) -> None:
    rows = {row["validation_unit_id"]: row for row in crosswalk_rows}
    missing = sorted(set(REPAIRED_GEOGRAPHY_EVIDENCE).difference(rows))
    if missing:
        raise ValueError(f"Registered geography repairs are absent from the crosswalk: {missing}")
    for unit_id in REPAIRED_GEOGRAPHY_EVIDENCE:
        validate_repaired_geography_row(rows[unit_id])


def read_extracted_pages(path: Path) -> list[str]:
    pages = path.read_text(encoding="utf-8", errors="replace").split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return pages


def html_to_text(payload: bytes) -> str:
    decoded = payload.decode("utf-8", errors="replace")
    decoded = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", decoded)
    decoded = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</h[1-6]>", "\n", decoded)
    return collapse_evidence(html.unescape(re.sub(r"(?s)<[^>]+>", " ", decoded)))


def verify_cited_source_cache(
    crosswalk_rows: list[dict[str, str]],
    manifest: dict[tuple[str, str], dict[str, str]],
    source_dir: Path,
) -> int:
    """Recompute raw/text hashes and excerpt containment from the source cache."""
    if not source_dir.is_dir():
        raise ValueError(f"Source cache directory is unavailable: {source_dir}")
    cached_content: dict[tuple[str, str], tuple[bytes, bytes, list[str]]] = {}
    verified = 0
    for row in crosswalk_rows:
        unit_id = row["validation_unit_id"]
        for prefix in ("identity", "geography", "owner", "role"):
            document_id = row[f"{prefix}_document_id"]
            if not document_id:
                continue
            source = manifest[(unit_id, document_id)]
            raw_filename = source["raw_cache_filename"]
            text_filename = source["text_cache_filename"]
            if not raw_filename:
                raise ValueError(f"Cited source lacks a raw-cache filename: {unit_id} {prefix}")
            cache_key = (raw_filename, text_filename)
            if cache_key not in cached_content:
                raw_path = source_dir / raw_filename
                if not raw_path.is_file():
                    raise ValueError(f"Cited raw source is absent: {raw_path}")
                raw_payload = raw_path.read_bytes()
                if text_filename:
                    text_path = source_dir / text_filename
                    if not text_path.is_file():
                        raise ValueError(f"Cited extracted text is absent: {text_path}")
                    text_payload = text_path.read_bytes()
                    pages = read_extracted_pages(text_path)
                else:
                    extracted_text = html_to_text(raw_payload)
                    text_payload = extracted_text.encode("utf-8")
                    pages = [extracted_text]
                cached_content[cache_key] = (raw_payload, text_payload, pages)
            raw_payload, text_payload, pages = cached_content[cache_key]
            if hashlib.sha256(raw_payload).hexdigest() != source["sha256"]:
                raise ValueError(f"Cited raw-source hash mismatch: {unit_id} {document_id}")
            if len(raw_payload) != int(source["retrieved_bytes"]):
                raise ValueError(f"Cited raw-source byte count mismatch: {unit_id} {document_id}")
            if hashlib.sha256(text_payload).hexdigest() != source["source_text_sha256"]:
                raise ValueError(f"Cited extracted-text hash mismatch: {unit_id} {document_id}")
            if len(pages) != int(source["pages"]):
                raise ValueError(f"Cited extracted-page count mismatch: {unit_id} {document_id}")
            page_number = int(row[f"{prefix}_page"])
            excerpt = collapse_evidence(row[f"{prefix}_supporting_text"])
            if excerpt not in collapse_evidence(pages[page_number - 1]):
                raise ValueError(
                    f"Cited excerpt is absent from the hash-verified page: "
                    f"{unit_id} {prefix} {document_id} page {page_number}"
                )
            verified += 1
    return verified


def surrogate_origin_lookup() -> tuple[dict[str, set[str]], dict[tuple[str, str], float]]:
    """Read only the safe identifier and source-coverage columns."""
    with SURROGATE.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        source_index = header.index("source_row_id")
        pool_index = header.index("pool_id")
        coverage_index = header.index("source_coverage_score")
        pools: dict[str, set[str]] = defaultdict(set)
        coverage: dict[tuple[str, str], float] = {}
        for values in reader:
            source_row_id = values[source_index]
            pool_id = values[pool_index]
            score = float(values[coverage_index])
            pools[source_row_id].add(pool_id)
            pair = (source_row_id, pool_id)
            if pair in coverage and coverage[pair] != score:
                raise ValueError(f"Conflicting source coverage for origin pair: {pair}")
            coverage[pair] = score
    return dict(pools), coverage


def resolve_origin_pairs(
    source_row_ids: list[str],
    declared_pool_ids: list[str],
    surrogate_pools: dict[str, set[str]],
    context: str,
) -> list[tuple[str, str]]:
    """Independently reconstruct each frozen source-to-pool pairing."""
    missing_origins = [source_id for source_id in source_row_ids if source_id not in surrogate_pools]
    if missing_origins:
        raise ValueError(f"Frozen-frame origin is absent from the safe surrogate lookup: {context} {missing_origins}")
    declared_pool_set = set(declared_pool_ids)
    pool_choices = [surrogate_pools[source_id].intersection(declared_pool_set) for source_id in source_row_ids]
    if any(len(choices) != 1 for choices in pool_choices):
        raise ValueError(f"Frozen-frame origin pairs are not uniquely identified: {context}")
    resolved_pool_ids = [next(iter(choices)) for choices in pool_choices]
    if Counter(resolved_pool_ids) != Counter(declared_pool_ids):
        raise ValueError(f"Frozen frame pool-ID membership mismatch: {context}")
    return list(zip(source_row_ids, resolved_pool_ids))


def coverage_for_origin_pairs(
    origin_pairs: list[tuple[str, str]],
    coverage: dict[tuple[str, str], float],
    context: str,
) -> float:
    """Reconstruct coverage from resolved pairs without borrowing another pool's score."""
    missing_pairs = [pair for pair in origin_pairs if pair not in coverage]
    if missing_pairs:
        raise ValueError(f"Candidate source coverage cannot be reconstructed: {context} {missing_pairs}")
    return max(coverage[pair] for pair in origin_pairs)


def document_ids_by_source_row() -> tuple[dict[str, list[str]], set[str]]:
    _, rows = read_csv(DOCUMENTS)
    by_source: dict[str, list[str]] = defaultdict(list)
    valid_ids: set[str] = set()
    for row in rows:
        document_id = row["document_id"]
        if not document_id:
            continue
        valid_ids.add(document_id)
        if row["usable_for_labeling"] == "yes":
            by_source[row["case_id"]].append(document_id)
    return dict(by_source), valid_ids


def expected_origin_documents(
    source_row_id: str,
    aggregate_ids: str,
    by_source: dict[str, list[str]],
    valid_ids: set[str],
) -> str:
    direct = by_source.get(source_row_id, [])
    if direct:
        return ";".join(dict.fromkeys(direct))
    fallback = [value for value in aggregate_ids.split(";") if value in valid_ids]
    return ";".join(dict.fromkeys(fallback))


def analysis_prefecture_city(city: str) -> str:
    return PREFECTURE_ROLLUPS.get(city, city)


def canonical_control_city(city: str) -> str:
    if city in {"北京", "天津", "上海", "重庆"}:
        return f"{city}市"
    return city


def historical_lookup() -> dict[str, dict[str, str]]:
    _, rows = read_csv(HISTORICAL)
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        capacity_bin = row["historical_capacity_bin"]
        if not capacity_bin:
            continue
        keys = [value for value in row["capacity_prefecture_name_chn"].split("|") if value]
        for chinese_city, english_pair in HISTORICAL_ENGLISH_JOIN.items():
            if (row["province"], row["city"]) == english_pair:
                keys.append(chinese_city)
        for key in keys:
            existing = result.get(key)
            if existing and existing["historical_capacity_bin"] != capacity_bin:
                raise ValueError(f"Conflicting historical-capacity bins for {key}")
            if existing:
                case_ids = sorted(set(existing["case_ids"].split(";") + [row["case_id"]]))
                existing["case_ids"] = ";".join(case_ids)
            else:
                result[key] = {
                    "historical_capacity_bin": capacity_bin,
                    "case_ids": row["case_id"],
                }
    return result


def debt_lookup() -> dict[str, tuple[str, str]]:
    _, rows = read_csv(CONTROLS)
    result: dict[str, tuple[str, str]] = {}
    for row in rows:
        city = canonical_control_city(row["control_city_chn"])
        if not city:
            continue
        status = row["debt_pressure_status"]
        availability = "available" if status.startswith("source_backed") or status.startswith("latest_source_backed") else "not_available"
        value = (row["control_unit_id"], availability)
        if city in result and result[city] != value:
            raise ValueError(f"Conflicting contemporary-control rows for {city}")
        result[city] = value
    return result


def coverage_bin(score: float) -> str:
    if score >= 4:
        return "high_4_plus"
    if score >= 2:
        return "moderate_2_3"
    return "low_0_1"


def expected_stratum(row: dict[str, str]) -> str:
    return "__".join((
        row["screen_status"],
        row["source_coverage_bin"],
        f"historical_{row['historical_capacity_bin']}",
        f"debt_{row['debt_pressure_availability']}",
        f"admin_{row['administrative_level']}",
    ))


def validate_member_design_consistency(
    member: dict[str, str],
    design_row: dict[str, str],
) -> None:
    """Require every unit-level sampling value to match its stratum proposal."""
    unit_id = member["validation_unit_id"]
    probability = float(design_row["inclusion_probability"])
    if not math.isclose(
        float(member["inclusion_probability"]), probability, rel_tol=0, abs_tol=1e-12
    ):
        raise ValueError(f"Unit-level inclusion probability mismatch: {unit_id}")
    if not math.isclose(
        float(member["proposed_design_weight"]), 1 / probability, rel_tol=1e-10
    ):
        raise ValueError(f"Unit-level proposed design weight mismatch: {unit_id}")
    if member["deterministic_random_seed"] != design_row["deterministic_random_seed"]:
        raise ValueError(f"Unit-level deterministic random seed mismatch: {unit_id}")
    if member["random_draw_executed"] != design_row["random_draw_executed"]:
        raise ValueError(f"Unit-level random-draw state mismatch: {unit_id}")


def validate(source_dir: Path = DEFAULT_SOURCE_DIR) -> dict[str, object]:
    frame_fields, frame_rows = read_csv(FRAME)
    old_fields, old_rows = read_csv(OLD_CROSSWALK)
    decision_fields, decisions = read_csv(DECISIONS)
    crosswalk_fields, crosswalk_rows = read_csv(CROSSWALK)
    unresolved_fields, unresolved_rows = read_csv(UNRESOLVED)
    manifest_fields, manifest_rows = read_csv(SOURCE_MANIFEST)
    candidate_fields, candidate_rows = read_csv(CANDIDATE)
    origin_fields, origin_rows = read_csv(ORIGINS)
    flow_fields, flow_rows = read_csv(FLOW)
    design_fields, design_rows = read_csv(DESIGN)
    del frame_fields, old_fields, decision_fields

    surrogate_pools, surrogate_coverage = surrogate_origin_lookup()
    documents_by_source, valid_document_ids = document_ids_by_source_row()
    historical = historical_lookup()
    debt = debt_lookup()

    observed_schemas = {
        CROSSWALK: crosswalk_fields,
        UNRESOLVED: unresolved_fields,
        SOURCE_MANIFEST: manifest_fields,
        CANDIDATE: candidate_fields,
        ORIGINS: origin_fields,
        FLOW: flow_fields,
        DESIGN: design_fields,
    }
    validate_output_schemas(observed_schemas)

    frame = {row["validation_unit_id"]: row for row in frame_rows}
    old = {row["validation_unit_id"]: row for row in old_rows}
    decision = {row["validation_unit_id"]: row for row in decisions}
    crosswalk = {row["validation_unit_id"]: row for row in crosswalk_rows}
    if any(len(rows) != len({row["validation_unit_id"] for row in rows}) for rows in (frame_rows, decisions, crosswalk_rows)):
        raise ValueError("Duplicate validation_unit_id in a unit-level input")
    if len(frame_rows) != 133 or len(decisions) != 133 or len(crosswalk_rows) != 133:
        raise ValueError("Frame, decisions, and completed crosswalk must each contain 133 units")
    if set(frame) != set(decision) or set(frame) != set(crosswalk):
        raise ValueError("Unit IDs differ across frame, decisions, and completed crosswalk")

    manifest = {(row["validation_unit_id"], row["document_id"]): row for row in manifest_rows}
    if len(manifest) != len(manifest_rows):
        raise ValueError("Duplicate unit-document pair in source manifest")
    required_manifest_fields = {"source_text_sha256", "extraction_profile", "cache_verification_status"}
    if not required_manifest_fields.issubset(manifest_fields):
        raise ValueError("Source manifest lacks extracted-text provenance fields")
    for row in manifest_rows:
        if row["local_copy_committed"] != "false":
            raise ValueError(f"Raw source marked committed: {row['document_id']}")
        if not row["rights_note"]:
            raise ValueError(f"Missing rights note: {row['document_id']}")
        if row["access_status"].startswith("retrieved_"):
            if len(row["sha256"]) != 64 or not row["document_page_url"] or not row["download_url"] or not row["retrieval_date"]:
                raise ValueError(f"Retrieved source lacks traceability: {row['document_id']}")

    baseline_geography_ids = {unit_id for unit_id, row in old.items() if row["geography_status"] != "source_supported_unique"}
    baseline_scope_ids = {unit_id for unit_id, row in old.items() if row["scope_disposition"] == "review_required"}
    if len(baseline_geography_ids) != 88 or len(baseline_scope_ids) != 98:
        raise ValueError("The quarantined 88-geography and 98-scope baselines were not reproduced")

    for unit_id, row in crosswalk.items():
        if row["issuer_name"] != frame[unit_id]["issuer_name"] or row["issuer_name"] != decision[unit_id]["issuer_name"]:
            raise ValueError(f"Issuer identity drift: {unit_id}")
        if row["geography_status"] not in ALLOWED_GEOGRAPHY:
            raise ValueError(f"Invalid geography disposition: {unit_id}")
        if row["scope_disposition"] not in ALLOWED_SCOPE:
            raise ValueError(f"Invalid scope disposition: {unit_id}")
        if row["administrative_level"] not in ALLOWED_ADMIN:
            raise ValueError(f"Invalid administrative level: {unit_id}")
        for field in ("geography_status", "administrative_level", "owner_level", "scope_disposition", "scope_reason_code", "audit_note"):
            if row[field] != decision[unit_id][field]:
                raise ValueError(f"Completed review diverges from registered decision {field}: {unit_id}")
        for field in ("province", "city"):
            if row[field] != decision[unit_id][field]:
                raise ValueError(f"Geography diverges from registered decision: {unit_id}")
        expected_baseline_geography = "true" if unit_id in baseline_geography_ids else "false"
        expected_baseline_scope = "true" if unit_id in baseline_scope_ids else "false"
        if row["baseline_geography_gap"] != expected_baseline_geography or row["baseline_scope_review"] != expected_baseline_scope:
            raise ValueError(f"Baseline audit flag mismatch: {unit_id}")
        if row["review_gate"] != "PI approval required before frame freeze or sampling":
            raise ValueError(f"Missing review gate: {unit_id}")

        if not row["identity_document_id"] or not row["identity_page"] or not row["identity_supporting_text"]:
            raise ValueError(f"Identity evidence is incomplete: {unit_id}")
        if row["geography_status"] == "source_supported_unique":
            required = ("supported_legal_issuer_name", "province", "city", "geography_document_id", "geography_page", "geography_supporting_text")
            if any(not row[field] for field in required):
                raise ValueError(f"Resolved geography lacks evidence: {unit_id}")
            city_token = row["city"].removesuffix("市")
            if city_token and city_token not in row["geography_supporting_text"]:
                raise ValueError(f"Geography excerpt does not contain city token: {unit_id}")
            if geography_evidence_is_obviously_third_party_only(
                row["geography_supporting_text"], row["city"], row["issuer_name"]
            ):
                raise ValueError(f"Resolved geography uses court-venue or third-party-only evidence: {unit_id}")
        elif row["geography_status"] == "source_supported_multiple":
            if row["province"] or row["city"]:
                raise ValueError(f"Multiple-location geography retains a coerced unique place: {unit_id}")
            required = (
                "geography_document_id", "geography_page", "geography_supporting_text",
                "conflict_status", "unresolved_reason",
            )
            if any(not row[field] for field in required) or row["conflict_status"] == "none_observed":
                raise ValueError(f"Multiple-location geography lacks conflict evidence: {unit_id}")
        elif row["province"] or row["city"]:
            raise ValueError(f"Unresolved geography retains a coerced place: {unit_id}")

        if row["scope_disposition"] == "eligible":
            if row["owner_level"] not in LOCAL_OWNER:
                raise ValueError(f"Eligible unit lacks local public control: {unit_id}")
            if not row["owner_document_id"] or not row["owner_supporting_text"] or not row["role_document_id"] or not row["role_supporting_text"]:
                raise ValueError(f"Eligible unit lacks owner or platform-role evidence: {unit_id}")
        elif row["scope_reason_code"] in {"excluded_central_public", "excluded_provincial_public", "excluded_private"}:
            if row["owner_level"] not in EXCLUDED_OWNER or not row["owner_document_id"] or not row["owner_supporting_text"]:
                raise ValueError(f"Owner-based exclusion lacks evidence: {unit_id}")
        elif row["scope_reason_code"] == "excluded_commercial_no_platform_role":
            if row["owner_level"] not in LOCAL_OWNER or not row["owner_document_id"] or not row["role_document_id"] or not row["role_supporting_text"]:
                raise ValueError(f"Commercial-function exclusion lacks owner/business evidence: {unit_id}")

        for prefix in ("identity", "geography", "owner", "role"):
            document_id = row[f"{prefix}_document_id"]
            if not document_id:
                continue
            source = manifest.get((unit_id, document_id))
            if not source or not source["access_status"].startswith("retrieved_"):
                raise ValueError(f"Evidence source does not join to a retrieved manifest row: {unit_id} {prefix}")
            if (
                len(source["source_text_sha256"]) != 64
                or not source["extraction_profile"]
                or source["cache_verification_status"].startswith("source_cache_missing")
            ):
                raise ValueError(f"Cited source lacks verified extraction provenance: {unit_id} {prefix}")
            if not row[f"{prefix}_page"] or not row[f"{prefix}_supporting_text"]:
                raise ValueError(f"Evidence locator is incomplete: {unit_id} {prefix}")
            try:
                cited_page = int(row[f"{prefix}_page"])
                available_pages = int(source["pages"])
            except ValueError as error:
                raise ValueError(f"Evidence or manifest page count is invalid: {unit_id} {prefix}") from error
            if cited_page < 1 or available_pages < cited_page:
                raise ValueError(
                    f"Evidence page exceeds the manifest extraction bound: {unit_id} {prefix} "
                    f"{cited_page}>{available_pages}"
                )

    validate_repaired_geography_evidence(crosswalk_rows)
    verified_cited_evidence = verify_cited_source_cache(
        crosswalk_rows, manifest, source_dir
    )

    baseline_geography_unique = sum(crosswalk[unit_id]["geography_status"] == "source_supported_unique" for unit_id in baseline_geography_ids)
    baseline_geography_multiple = sum(crosswalk[unit_id]["geography_status"] == "source_supported_multiple" for unit_id in baseline_geography_ids)
    baseline_geography_unresolved = sum(crosswalk[unit_id]["geography_status"] == "unresolved_after_search" for unit_id in baseline_geography_ids)
    if (baseline_geography_unique, baseline_geography_multiple, baseline_geography_unresolved) != (86, 2, 0):
        raise ValueError(
            "Unexpected disposition of 88 baseline geography gaps: "
            f"{(baseline_geography_unique, baseline_geography_multiple, baseline_geography_unresolved)}"
        )
    baseline_scope_resolved = sum(crosswalk[unit_id]["scope_disposition"] in {"eligible", "ineligible"} for unit_id in baseline_scope_ids)
    baseline_scope_unresolved = sum(crosswalk[unit_id]["scope_disposition"] == "unresolved_after_search" for unit_id in baseline_scope_ids)
    if (baseline_scope_resolved, baseline_scope_unresolved) != (98, 0):
        raise ValueError(f"Unexpected resolution of 98 baseline scope reviews: {(baseline_scope_resolved, baseline_scope_unresolved)}")

    expected_failed_gates = Counter()
    for row in crosswalk_rows:
        if row["geography_status"] == "source_supported_multiple":
            expected_failed_gates[(row["validation_unit_id"], "geography_unique_assignment")] += 1
        elif row["geography_status"] == "unresolved_after_search":
            expected_failed_gates[(row["validation_unit_id"], "geography_and_identity")] += 1
        if row["scope_disposition"] == "unresolved_after_search":
            expected_failed_gates[(row["validation_unit_id"], "scope")] += 1
    observed_failed_gates = Counter((row["validation_unit_id"], row["failed_gate"]) for row in unresolved_rows)
    if expected_failed_gates != observed_failed_gates:
        raise ValueError(f"Unresolved log does not contain one row per failed gate: {observed_failed_gates}")
    for row in unresolved_rows:
        expected_disposition = "source_supported_multiple" if row["failed_gate"] == "geography_unique_assignment" else "unresolved_after_search"
        if row["review_required"] != "true" or row["disposition"] != expected_disposition or not row["source_document_ids"]:
            raise ValueError("An unresolved-log row lacks traceability or an explicit review gate")

    eligible_ids = {unit_id for unit_id, row in crosswalk.items() if row["scope_disposition"] == "eligible"}
    candidate_ids = [row["validation_unit_id"] for row in candidate_rows]
    if len(candidate_ids) != len(set(candidate_ids)) or set(candidate_ids) != eligible_ids:
        raise ValueError("Candidate units are not the unique eligible crosswalk units")
    legal_keys = [row["normalized_legal_issuer_key"] for row in candidate_rows]
    if any(not key for key in legal_keys) or len(legal_keys) != len(set(legal_keys)):
        raise ValueError("Candidate legal-issuer keys are blank or duplicated")

    members_by_stratum: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in candidate_rows:
        unit_id = row["validation_unit_id"]
        frame_row = frame[unit_id]
        review = crosswalk[unit_id]
        if row["eligibility_flag"] != "true" or row["scope_disposition"] != "eligible":
            raise ValueError(f"Candidate contains a noneligible unit: {unit_id}")
        if row["normalized_legal_issuer_key"] != normalize(review["supported_legal_issuer_name"]):
            raise ValueError(f"Candidate legal-name key does not match the supported legal name: {unit_id}")
        for field in ("province", "city", "administrative_level", "geography_status"):
            if row[field] != review[field]:
                raise ValueError(f"Candidate {field} diverges from the completed review: {unit_id}")
        if row["screen_status"] != frame_row["design_stratum"]:
            raise ValueError(f"Candidate screen status diverges from the frozen frame: {unit_id}")
        if row["screen_status"] not in ALLOWED_SCREEN:
            raise ValueError(f"Invalid screen stratum: {unit_id}")

        source_row_ids = [value for value in frame_row["source_row_ids"].split(";") if value]
        declared_pool_ids = [value for value in frame_row["pool_ids"].split(";") if value]
        if len(source_row_ids) != len(declared_pool_ids) or len(source_row_ids) != int(frame_row["disclosure_rows"]):
            raise ValueError(f"Frozen frame has an origin-row count mismatch: {unit_id}")
        resolved_origin_pairs = resolve_origin_pairs(
            source_row_ids, declared_pool_ids, surrogate_pools, unit_id
        )
        expected_coverage = coverage_for_origin_pairs(
            resolved_origin_pairs, surrogate_coverage, unit_id
        )
        if not math.isclose(float(row["source_coverage_score"]), expected_coverage, rel_tol=0, abs_tol=1e-12):
            raise ValueError(f"Candidate source coverage is incorrect: {unit_id}")
        if row["source_coverage_bin"] != coverage_bin(expected_coverage):
            raise ValueError(f"Candidate source-coverage bin is incorrect: {unit_id}")

        prefecture_city = analysis_prefecture_city(review["city"])
        historical_match = historical.get(prefecture_city)
        expected_historical_bin = historical_match["historical_capacity_bin"] if historical_match else "not_available"
        expected_historical_status = "source_backed_match" if historical_match else "not_available"
        expected_historical_cases = historical_match["case_ids"] if historical_match else ""
        if (
            row["historical_capacity_bin"] != expected_historical_bin
            or row["historical_capacity_join_status"] != expected_historical_status
            or row["historical_capacity_source_case_ids"] != expected_historical_cases
        ):
            raise ValueError(f"Candidate historical-capacity join is incorrect: {unit_id}")

        expected_control_id, expected_debt_status = debt.get(prefecture_city, ("", "not_available"))
        if (
            row["debt_pressure_control_unit_id"] != expected_control_id
            or row["debt_pressure_availability"] != expected_debt_status
        ):
            raise ValueError(f"Candidate debt-pressure join is incorrect: {unit_id}")
        if row["frozen_stratum_id"] != expected_stratum(row):
            raise ValueError(f"Frozen stratum contains a disallowed or inconsistent component: {unit_id}")
        probability = float(row["inclusion_probability"])
        if not 0 < probability <= 1 or not math.isclose(float(row["proposed_design_weight"]), 1 / probability, rel_tol=1e-10):
            raise ValueError(f"Invalid probability or design weight: {unit_id}")
        if row["random_draw_executed"] != "false" or not row["deterministic_random_seed"]:
            raise ValueError(f"Random draw state is invalid: {unit_id}")
        members_by_stratum[row["frozen_stratum_id"]].append(row)
    if {row["screen_status"] for row in candidate_rows} != ALLOWED_SCREEN:
        raise ValueError("Eligible candidate does not retain both screen strata")

    design = {row["frozen_stratum_id"]: row for row in design_rows}
    if len(design) != len(design_rows) or set(design) != set(members_by_stratum):
        raise ValueError("Sampling design does not have one row per frozen stratum")
    for stratum_id, members in members_by_stratum.items():
        row = design[stratum_id]
        population_n = len(members)
        target_n = int(row["proposed_stratum_sample_n"])
        probability = target_n / population_n
        if int(row["stratum_population_n"]) != population_n or not 0 < target_n <= population_n:
            raise ValueError(f"Invalid sampling allocation: {stratum_id}")
        if not math.isclose(float(row["inclusion_probability"]), probability, rel_tol=1e-12):
            raise ValueError(f"Sampling probability mismatch: {stratum_id}")
        if row["random_draw_executed"] != "false" or row["approval_status"] != "proposal_only_PI_approval_required":
            raise ValueError(f"Sampling proposal was executed or lacks approval gate: {stratum_id}")
        for field in ("screen_status", "source_coverage_bin", "historical_capacity_bin", "debt_pressure_availability", "administrative_level"):
            if row[field] != members[0][field]:
                raise ValueError(f"Sampling-design {field} does not match its members: {stratum_id}")
        for member in members:
            if int(member["stratum_population_n"]) != population_n or int(member["proposed_stratum_sample_n"]) != target_n:
                raise ValueError(f"Unit-level stratum allocation mismatch: {member['validation_unit_id']}")
            validate_member_design_consistency(member, row)

    expected_origins: list[tuple[str, str, str, str, str]] = []
    for row in frame_rows:
        source_rows = [value for value in row["source_row_ids"].split(";") if value]
        declared_pool_ids = [value for value in row["pool_ids"].split(";") if value]
        if len(source_rows) != len(declared_pool_ids) or len(source_rows) != int(row["disclosure_rows"]):
            raise ValueError(f"Frozen frame has an origin-row count mismatch: {row['validation_unit_id']}")
        resolved_origin_pairs = resolve_origin_pairs(
            source_rows, declared_pool_ids, surrogate_pools, row["validation_unit_id"]
        )
        for position, (source_row_id, pool_id) in enumerate(resolved_origin_pairs, start=1):
            evidence_ids = expected_origin_documents(
                source_row_id,
                row["evidence_document_ids"],
                documents_by_source,
                valid_document_ids,
            )
            expected_origins.append((row["validation_unit_id"], str(position), source_row_id, pool_id, evidence_ids))
    observed_origins = [
        (
            row["validation_unit_id"], row["origin_position"], row["source_row_id"],
            row["pool_id"], row["evidence_document_ids"],
        )
        for row in origin_rows
    ]
    if len(expected_origins) != 157 or observed_origins != expected_origins:
        raise ValueError("All 157 originating disclosure rows were not retained in stable order")
    for row in origin_rows:
        invalid_documents = [
            document_id for document_id in row["evidence_document_ids"].split(";")
            if document_id and document_id not in valid_document_ids
        ]
        if invalid_documents:
            raise ValueError(f"Origin row contains invalid evidence document IDs: {row['source_row_id']} {invalid_documents}")

    scope_counts = Counter(row["scope_disposition"] for row in crosswalk_rows)
    geography_counts = Counter(row["geography_status"] for row in crosswalk_rows)
    if geography_counts != Counter({"source_supported_unique": 130, "source_supported_multiple": 2, "unresolved_after_search": 1}):
        raise ValueError(f"Unexpected full-frame geography dispositions: {geography_counts}")
    if scope_counts != Counter({"eligible": 66, "ineligible": 66, "unresolved_after_search": 1}):
        raise ValueError(f"Unexpected full-frame scope dispositions: {scope_counts}")
    screen_counts = Counter(row["screen_status"] for row in candidate_rows)
    metrics = json.loads(METRICS.read_text(encoding="utf-8"))
    expected_metrics = {
        "proposed_issuer_units": 133,
        "originating_disclosure_rows": 157,
        "baseline_geography_gaps": 88,
        "baseline_geography_resolved": 86,
        "baseline_geography_multiple": 2,
        "baseline_geography_unresolved": 0,
        "baseline_scope_reviews": 98,
        "baseline_scope_resolved": 98,
        "baseline_scope_unresolved": 0,
        "all_geography_statuses": dict(sorted(geography_counts.items())),
        "all_scope_dispositions": dict(sorted(scope_counts.items())),
        "eligible_candidate_units": len(candidate_rows),
        "candidate_originating_disclosure_rows": sum(
            int(row["originating_disclosure_row_count"])
            for row in flow_rows
            if row["stage"] == "scope_gate" and row["disposition"] == "eligible"
        ),
        "eligible_screen_statuses": dict(sorted(screen_counts.items())),
        "frozen_strata": len(design_rows),
        "deterministic_random_seed": "20260830015",
        "all_eligible_units_have_nonzero_probability": True,
        "random_draw_executed": False,
        "frame_ready_to_freeze": False,
    }
    mismatches = {key: (metrics.get(key), value) for key, value in expected_metrics.items() if metrics.get(key) != value}
    if mismatches:
        raise ValueError(f"Metrics mismatch: {mismatches}")
    if set(metrics) != set(expected_metrics):
        raise ValueError(
            f"Metrics schema mismatch: {sorted(metrics)} != {sorted(expected_metrics)}"
        )

    flow_keys = {(row["stage"], row["disposition"]): int(row["issuer_unit_count"]) for row in flow_rows}
    if flow_keys.get(("proposed_frame", "all_legal_issuer_units")) != 133:
        raise ValueError("Frame-flow table does not start from 133 units")
    for disposition, count in scope_counts.items():
        if flow_keys.get(("scope_gate", disposition)) != count:
            raise ValueError(f"Frame-flow scope count mismatch: {disposition}")

    return {
        "baseline_geography_resolved": 86,
        "baseline_geography_multiple": 2,
        "baseline_geography_unresolved": 0,
        "baseline_scope_resolved": 98,
        "baseline_scope_unresolved": 0,
        "all_geography_statuses": dict(sorted(geography_counts.items())),
        "all_scope_dispositions": dict(sorted(scope_counts.items())),
        "candidate_units": len(candidate_rows),
        "originating_disclosure_rows": len(origin_rows),
        "frozen_strata": len(design_rows),
        "random_draw_executed": False,
        "verified_cited_evidence": verified_cited_evidence,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    args = parser.parse_args()
    print(json.dumps(validate(args.source_dir), ensure_ascii=False, sort_keys=True))
