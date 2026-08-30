#!/usr/bin/env python3
"""Compile the registered case-by-case source review into auditable CSV files.

The script never reads an outcome field. It operates on the frozen frame, the
EXP-011 retrieval manifest, the registered review decisions, and retrieved
public-source text supplied with ``--source-dir``. Raw sources remain outside
the repository; their URLs and hashes are retained in the successor manifest.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments/EXP-20260830-015"
FRAME = ROOT / "data/validation/proposed_one_sided_validation_frame_enriched.csv"
OLD_CROSSWALK = ROOT / "data/validation/source_supported_validation_geography_scope_crosswalk.csv"
OLD_MANIFEST = ROOT / "data/validation/validation_geography_retrieval_manifest.csv"
DOCUMENTS = ROOT / "data/document_inventory.csv"
DECISIONS = EXP / "review_decisions.csv"
OUT_CROSSWALK = ROOT / "data/validation/probability_validation_geography_scope_crosswalk.csv"
OUT_UNRESOLVED = ROOT / "data/validation/probability_validation_unresolved_log.csv"
OUT_MANIFEST = ROOT / "data/validation/probability_validation_source_manifest.csv"
RETRIEVAL_DATE = "2026-08-30"

WEB_SOURCES = {
    "mv_3707ecbfb1f2": {
        "document_id": "web_linyi_sasac_profile",
        "filename": "web_linyi_sasac_profile.html",
        "document_type": "government_profile",
        "publisher": "Linyi Municipal SASAC",
        "document_title": "临沂投资发展集团有限公司",
        "document_date": "2023-09-07",
        "document_page_url": "https://lysgzw.linyi.gov.cn/info/1023/12434.htm",
        "download_url": "https://lysgzw.linyi.gov.cn/info/1023/12434.htm",
    },
    "mv_3134f5ad5182": {
        "document_id": "web_ndrc_jian_jinluling",
        "filename": "web_ndrc_jian_jinluling.html",
        "document_type": "government_approval",
        "publisher": "National Development and Reform Commission",
        "document_title": "关于江西省吉安市井冈山开发区金庐陵经济发展有限公司发行公司债券核准的批复",
        "document_date": "2020-03-19",
        "document_page_url": "https://www.ndrc.gov.cn/xxgk/zcfb/qt/202003/t20200319_1223642.html",
        "download_url": "https://www.ndrc.gov.cn/xxgk/zcfb/qt/202003/t20200319_1223642.html",
    },
    "mv_dd84e076bf32": {
        "document_id": "web_saac_guiyang_public_transport_current_name",
        "filename": "web_saac_guiyang_public_transport_current_name.html",
        "document_type": "government_profile",
        "publisher": "National Archives Administration of China",
        "document_title": "贵阳市公共交通投资运营集团有限公司通过企业集团数字档案馆（室）建设试点验收",
        "document_date": "2025-06-24",
        "document_page_url": "https://www.saac.gov.cn/daj/qydagz/202506/cecc46d5d46b49a39d3ad19871fc586c.shtml",
        "download_url": "https://www.saac.gov.cn/daj/qydagz/202506/cecc46d5d46b49a39d3ad19871fc586c.shtml",
    },
    "mv_32559fdf4bd7": {
        "document_id": "web_guizhou_transport_guiyang_city_development",
        "filename": "web_guizhou_transport_guiyang_city_development.html",
        "document_type": "government_project_notice",
        "publisher": "Guizhou Provincial Department of Transport",
        "document_title": "贵阳环城高速交通基础设施智慧扩容项目1标中标结果公告",
        "document_date": "2025-06-13",
        "document_page_url": "https://jt.guizhou.gov.cn/zwgk/zdlyxxgk_5948535/zbtb_5948548/zbjggsgg/202506/t20250613_88138895.html",
        "download_url": "https://jt.guizhou.gov.cn/zwgk/zdlyxxgk_5948535/zbtb_5948548/zbjggsgg/202506/t20250613_88138895.html",
    },
    "mv_bbc98d5aa00c": {
        "document_id": "web_shenzhen_sasac_special_zone_development",
        "filename": "web_shenzhen_sasac_special_zone_development.html",
        "document_type": "government_profile",
        "publisher": "Shenzhen Municipal SASAC",
        "document_title": "深圳市特区建设发展集团有限公司",
        "document_date": "2026-01-01",
        "document_page_url": "https://gzw.sz.gov.cn/szgq/content/post_9395752.html",
        "download_url": "https://gzw.sz.gov.cn/szgq/content/post_9395752.html",
    },
    "mv_8c56f4ed9aa0": {
        "document_id": "web_gz_gov_guangzhou_transport_profile",
        "filename": "web_gz_gov_guangzhou_transport_profile.html",
        "document_type": "government_profile",
        "publisher": "Guangzhou Municipal Government; source: Municipal SASAC",
        "document_title": "广州交通投资集团有限公司",
        "document_date": "2025-02-21",
        "document_page_url": "https://www.gz.gov.cn/zwgk/zdly/gqxx/jbxx/content/mpost_7793086.html",
        "download_url": "https://www.gz.gov.cn/zwgk/zdly/gqxx/jbxx/content/mpost_7793086.html",
    },
    "mv_a52ab8f6ce4b": {
        "document_id": "web_gz_gov_guangzhou_industry_profile",
        "filename": "web_gz_gov_guangzhou_industry_profile.html",
        "document_type": "government_profile",
        "publisher": "Guangzhou Municipal Government; source: Municipal SASAC",
        "document_title": "广州产业投资控股集团有限公司",
        "document_date": "2025-12-23",
        "document_page_url": "https://www.gz.gov.cn/zwgk/zdly/gqxx/jbxx/content/post_7796298.html",
        "download_url": "https://www.gz.gov.cn/zwgk/zdly/gqxx/jbxx/content/post_7796298.html",
    },
    "mv_35577ffe2ec5": {
        "document_id": "web_csrc_zunyi_daoqiao_current_name",
        "filename": "doc_csrc_zunyi_daoqiao_2023.html",
        "document_type": "government_enforcement_notice",
        "publisher": "China Securities Regulatory Commission Guizhou Bureau",
        "document_title": "关于对遵义道桥建设（集团）有限公司采取出具警示函措施的决定",
        "document_date": "2023-11-15",
        "document_page_url": "https://www.csrc.gov.cn/guizhou/c104852/c7513192/content.shtml",
        "download_url": "https://www.csrc.gov.cn/guizhou/c104852/c7513192/content.shtml",
    },
}

PREEXISTING_PDFS = {
    "mv_098975f6dda7": "doc_gz_lps_kaitou_2016_bond_prospectus",
    "mv_bbc98d5aa00c": "doc_gd_sz_tqjf_2025_mtn4_001",
    "mv_35577ffe2ec5": "doc_gz_zy_daoqiao_2015_bond_prospectus",
}

EXTERNAL_PDFS = {
    "mv_039c3dde77ab": {
        "document_id": "web_hkex_anhui_transport_controller",
        "filename": "web_hkex_anhui_transport_controller.pdf",
        "text_filename": "web_hkex_anhui_transport_controller.txt",
        "document_type": "exchange_disclosure",
        "publisher": "Hong Kong Exchanges and Clearing",
        "document_title": "Anhui Expressway acquisition disclosure: Anhui Transport Holding controller",
        "document_date": "2023-06-20",
        "document_page_url": "https://www.hkexnews.hk/listedco/listconews/sehk/2023/0620/2023062001130_c.pdf",
        "download_url": "https://www.hkexnews.hk/listedco/listconews/sehk/2023/0620/2023062001130_c.pdf",
    },
    "mv_c4af6b64ad69": {
        "document_id": "web_cninfo_zhuhai_port_controller",
        "filename": "web_cninfo_zhuhai_port_controller.pdf",
        "text_filename": "web_cninfo_zhuhai_port_controller.txt",
        "document_type": "exchange_disclosure",
        "publisher": "CNINFO",
        "document_title": "Zhuhai Port listed-company legal opinion: controller of Zhuhai Port Holding",
        "document_date": "2022-11-25",
        "document_page_url": "https://static.cninfo.com.cn/finalpage/2022-11-25/1215195558.PDF",
        "download_url": "https://static.cninfo.com.cn/finalpage/2022-11-25/1215195558.PDF",
    },
}

CONTROLLER_OVERRIDES = {
    "mv_b7aabd80bf01": "中国民用航空局",
    "mv_940b87861065": "张寓帅",
}

ROLE_ANCHOR_OVERRIDES = {
    "mv_dd32227a7cc7": "海淀区城市基础设施投融资的重要主体",
}

SUPPORTED_NAME_OVERRIDES = {
    "mv_35577ffe2ec5": "遵义道桥建设（集团）有限公司",
}

CROSSWALK_FIELDS = [
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
]

MANIFEST_FIELDS = [
    "validation_unit_id", "issuer_name", "document_id", "document_type",
    "publisher", "document_title", "document_date", "document_page_url",
    "download_url", "retrieval_date", "access_status", "http_status",
    "content_type", "retrieved_bytes", "sha256", "pages",
    "text_extraction_status", "rights_note", "local_copy_committed", "error",
]

UNRESOLVED_FIELDS = [
    "validation_unit_id", "issuer_name", "failed_gate", "observed_values",
    "source_document_ids", "disposition", "reason_code", "notes",
    "review_required",
]

IDENTITY_TERMS = ("发行人基本情况", "发行人概况", "公司基本情况", "企业名称", "名称：")
ADDRESS_TERMS = ("注册地址", "注册地", "公司住所", "企业住所", "发行人住所", "住所：", "办公地址")
OWNER_TERMS = (
    "实际控制人", "控股股东", "出资人", "持有公司100%", "持股100%",
    "国资委", "市属", "市级国有", "省属", "持有",
)
PLATFORM_TERMS = (
    "投融资主体", "投资建设主体", "基础设施建设主体", "城市建设主体",
    "基础设施投资", "基础设施建设", "土地开发整理", "土地整理开发",
    "保障性住房", "棚户区改造", "园区开发", "项目融资", "融资平台",
    "投资、建设、运营", "投资建设运营", "城市更新", "市政工程",
    "投融资的重要主体", "投资运营主体", "城市运营平台", "投资、开发、运营主体",
)
BUSINESS_TERMS = ("主营业务", "经营范围", "业务范围", "主要业务", "核心业务", "业务板块")


@dataclass
class Source:
    unit_id: str
    document_id: str
    pages: list[str]
    manifest: dict[str, str]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalized(text: str) -> str:
    return re.sub(r"[\s()（）·,，。:：]", "", text)


def html_to_text(payload: bytes) -> str:
    decoded = payload.decode("utf-8", errors="replace")
    decoded = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", decoded)
    decoded = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</h[1-6]>", "\n", decoded)
    return collapse(html.unescape(re.sub(r"(?s)<[^>]+>", " ", decoded)))


def snippet(page: str, anchors: tuple[str, ...], width: int = 720) -> str:
    flat = collapse(page)
    position = next((flat.find(anchor) for anchor in anchors if anchor and flat.find(anchor) >= 0), 0)
    start = max(0, position - 180)
    return flat[start : position + width]


def expected_owner_tokens(decision: dict[str, str]) -> tuple[str, ...]:
    province = decision["province"]
    city = decision["city"]
    level = decision["owner_level"]
    if level == "central_public":
        return ("国务院国资委", "国务院国有资产监督管理委员会", "中央企业")
    if level == "provincial_public":
        short = province.removesuffix("省").removesuffix("市").replace("壮族自治区", "").replace("维吾尔自治区", "")
        return (f"{short}省国资委", f"{short}省人民政府", "自治区国资委", "自治区人民政府", "省国资委", "省人民政府")
    if level == "private_or_natural_person":
        return ("自然人", "实际控制人", "民营", "私人")
    if level in {"municipality_public", "subprovincial_public"}:
        short_city = city.removesuffix("市").removesuffix("自治州")
        return (f"{short_city}市国资委", f"{short_city}市人民政府", "区国资委", "区人民政府", "县财政局", "市国资委", "市人民政府", "管委会")
    return ()


def choose_page(
    sources: list[Source],
    required: tuple[str, ...],
    preferred: tuple[str, ...],
    issuer_name: str,
    purpose: str,
) -> tuple[Source | None, int | str, str]:
    ranked: list[tuple[int, int, Source, int, str]] = []
    issuer = normalized(issuer_name)
    for source_order, source in enumerate(sources):
        for page_number, page in enumerate(source.pages, start=1):
            flat = collapse(page)
            compact = normalized(flat)
            if required and not all(any(token in flat for token in group.split("|")) for group in required):
                continue
            score = 0
            if issuer and issuer in compact:
                score += 30
            score += 7 * sum(token in flat for token in preferred)
            if purpose == "geography":
                score += 12 * sum(token in flat for token in ADDRESS_TERMS)
                score += 5 * sum(token in flat for token in IDENTITY_TERMS)
            elif purpose == "owner":
                score += 10 * sum(token in flat for token in OWNER_TERMS)
                score += 4 * ("股权结构" in flat)
                score += 45 * bool(re.search(r"(?:实际控制人|控股股东).{0,45}(?:为|是|系|持有|隶属于)", flat))
                score -= 50 * ("持有人会议" in flat)
            elif purpose == "role":
                score += 9 * sum(token in flat for token in PLATFORM_TERMS)
                score += 4 * ("发行人" in flat)
                score += 35 * bool(re.search(r"(?:发行人|公司).{0,90}(?:作为|是|为|承担|负责).{0,180}(?:主体|基础设施|土地|保障房|棚户区|项目|城市更新|园区)", flat))
                score += 20 * bool(re.search(r"(?:行业地位|主要职责|功能定位|公司定位)", flat))
                score -= 35 * ("募集资金不用于" in flat or "不承担政府融资职能" in flat)
                score -= 12 * ("风险" in flat)
            elif purpose == "business":
                score += 9 * sum(token in flat for token in BUSINESS_TERMS)
                score += 4 * ("发行人" in flat)
            else:
                score += 6 * sum(token in flat for token in IDENTITY_TERMS)
            if "子公司" in flat[:250] and issuer not in compact:
                score -= 30
            ranked.append((score, -source_order, source, page_number, page))
    if not ranked:
        return None, "", ""
    ranked.sort(key=lambda item: (-item[0], -item[1], item[3]))
    _, _, source, page_number, page = ranked[0]
    if purpose == "role":
        relationship_anchors = tuple(
            marker for marker in ("发行人作为", "公司作为", "发行人是", "公司是", "发行人承担", "发行人负责", "主要职责", "行业地位")
            if marker in collapse(page)
        )
        anchors = relationship_anchors + preferred + required + (issuer_name,)
    else:
        anchors = preferred + required + (issuer_name,)
    return source, page_number, snippet(page, anchors, width=1000 if purpose == "owner" else 720)


def owner_name(text: str, decision: dict[str, str]) -> str:
    patterns = (
        r"(?:最终)?实际控制人(?:仍)?(?:均)?(?:为|是|系)([^，。；]{2,100})",
        r"控股股东及实际控制人(?:仍)?(?:均)?(?:为|是|系)([^，。；]{2,100})",
        r"由([^，。；]{2,100})(?:履行出资人职责|直接监管)",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return collapse(match.group(1)).strip(" ：:")
    for token in expected_owner_tokens(decision):
        if token in text and token not in {"省国资委", "省人民政府", "市国资委", "市人民政府", "区国资委", "区人民政府", "自治区国资委", "自治区人民政府", "管委会", "自然人", "实际控制人", "民营", "私人"}:
            return token
    institution = re.search(
        r"([\u4e00-\u9fff（）()·]{2,32}(?:人民政府国有资产监督管理委员会|国有资产监督管理委员会|国有资产管理委员会|国有资产管理中心|国有资产服务中心|国资委|国资办|财政局|人民政府|管委会))",
        text,
    )
    if institution:
        value = institution.group(1)
        for separator in ("。", "；", "，", " "):
            value = value.split(separator)[-1]
        return value
    return ""


def source_manifest_rows(source_dir: Path) -> tuple[list[dict[str, str]], dict[str, list[Source]]]:
    old_manifest = read_csv(OLD_MANIFEST)
    frame = {row["validation_unit_id"]: row for row in read_csv(FRAME)}
    documents = {row["document_id"]: row for row in read_csv(DOCUMENTS)}
    manifest: list[dict[str, str]] = []
    by_unit: dict[str, list[Source]] = {unit_id: [] for unit_id in frame}

    for row in old_manifest:
        converted = dict(row)
        converted["pages"] = converted.pop("pdf_pages", "")
        manifest.append(converted)
        text_path = source_dir / f"{row['document_id']}.txt"
        if text_path.exists():
            pages = text_path.read_text(encoding="utf-8", errors="replace").split("\f")
            by_unit[row["validation_unit_id"]].append(Source(row["validation_unit_id"], row["document_id"], pages, converted))

    for unit_id, document_id in PREEXISTING_PDFS.items():
        document = documents[document_id]
        pdf_path = source_dir / f"{document_id}.pdf"
        text_path = source_dir / f"{document_id}.txt"
        payload = pdf_path.read_bytes()
        pages = text_path.read_text(encoding="utf-8", errors="replace").split("\f")
        row = {
            "validation_unit_id": unit_id,
            "issuer_name": frame[unit_id]["issuer_name"],
            "document_id": document_id,
            "document_type": document["document_type"],
            "publisher": "Public bond issuer-disclosure portal",
            "document_title": document["document_title"],
            "document_date": document["document_date"],
            "document_page_url": document["document_page_url"],
            "download_url": document["download_url"],
            "retrieval_date": RETRIEVAL_DATE,
            "access_status": "retrieved_public_disclosure",
            "http_status": "200",
            "content_type": "application/pdf",
            "retrieved_bytes": str(len(payload)),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "pages": str(len(pages)),
            "text_extraction_status": "extracted_all_pages",
            "rights_note": "Public issuer disclosure; audit metadata and excerpts retained. Raw source not committed.",
            "local_copy_committed": "false",
            "error": "",
        }
        manifest.append(row)
        by_unit[unit_id].append(Source(unit_id, document_id, pages, row))

    for unit_id, metadata in WEB_SOURCES.items():
        payload = (source_dir / metadata["filename"]).read_bytes()
        text = html_to_text(payload)
        row = {
            "validation_unit_id": unit_id,
            "issuer_name": frame[unit_id]["issuer_name"],
            "document_id": metadata["document_id"],
            "document_type": metadata["document_type"],
            "publisher": metadata["publisher"],
            "document_title": metadata["document_title"],
            "document_date": metadata["document_date"],
            "document_page_url": metadata["document_page_url"],
            "download_url": metadata["download_url"],
            "retrieval_date": RETRIEVAL_DATE,
            "access_status": "retrieved_public_webpage",
            "http_status": "200",
            "content_type": "text/html",
            "retrieved_bytes": str(len(payload)),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "pages": "1",
            "text_extraction_status": "extracted_html_text",
            "rights_note": "Public government webpage; URL hash and excerpt retained. Raw page not committed.",
            "local_copy_committed": "false",
            "error": "",
        }
        manifest.append(row)
        by_unit[unit_id].insert(0, Source(unit_id, metadata["document_id"], [text], row))

    for unit_id, metadata in EXTERNAL_PDFS.items():
        payload = (source_dir / metadata["filename"]).read_bytes()
        pages = (source_dir / metadata["text_filename"]).read_text(encoding="utf-8", errors="replace").split("\f")
        row = {
            "validation_unit_id": unit_id,
            "issuer_name": frame[unit_id]["issuer_name"],
            "document_id": metadata["document_id"],
            "document_type": metadata["document_type"],
            "publisher": metadata["publisher"],
            "document_title": metadata["document_title"],
            "document_date": metadata["document_date"],
            "document_page_url": metadata["document_page_url"],
            "download_url": metadata["download_url"],
            "retrieval_date": RETRIEVAL_DATE,
            "access_status": "retrieved_public_disclosure",
            "http_status": "200",
            "content_type": "application/pdf",
            "retrieved_bytes": str(len(payload)),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "pages": str(len(pages)),
            "text_extraction_status": "extracted_all_pages",
            "rights_note": "Public exchange disclosure; audit metadata and excerpts retained. Raw source not committed.",
            "local_copy_committed": "false",
            "error": "",
        }
        manifest.append(row)
        by_unit[unit_id].insert(0, Source(unit_id, metadata["document_id"], pages, row))

    manifest.sort(key=lambda row: (int(next(d["sequence"] for d in read_csv(DECISIONS) if d["validation_unit_id"] == row["validation_unit_id"])), row["document_id"]))
    return manifest, by_unit


def evidence_fields(prefix: str, source: Source | None, page: int | str, text: str) -> dict[str, str]:
    return {
        f"{prefix}_document_id": source.document_id if source else "",
        f"{prefix}_page": str(page),
        f"{prefix}_supporting_text": collapse(text),
    }


def build(source_dir: Path) -> None:
    frame_rows = read_csv(FRAME)
    frame = {row["validation_unit_id"]: row for row in frame_rows}
    old = {row["validation_unit_id"]: row for row in read_csv(OLD_CROSSWALK)}
    decisions = read_csv(DECISIONS)
    manifest, sources_by_unit = source_manifest_rows(source_dir)
    crosswalk: list[dict[str, str]] = []
    unresolved: list[dict[str, str]] = []

    for decision in decisions:
        unit_id = decision["validation_unit_id"]
        issuer_name = decision["issuer_name"]
        sources = sources_by_unit[unit_id]
        prior = old.get(unit_id, {})

        if unit_id == "mv_dd84e076bf32":
            identity_source, identity_page, identity_text = choose_page(
                sources, ("贵阳市公共交通投资运营集团有限公司",), ("贵阳市公共交通投资运营集团有限公司",), issuer_name, "identity"
            )
            supported_name = "贵阳市公共交通投资运营集团有限公司"
        elif unit_id in SUPPORTED_NAME_OVERRIDES:
            supported_name = SUPPORTED_NAME_OVERRIDES[unit_id]
            identity_source, identity_page, identity_text = choose_page(
                sources, (supported_name,), (supported_name,), supported_name, "identity"
            )
        else:
            identity_source, identity_page, identity_text = choose_page(
                sources, (), (issuer_name,), issuer_name, "identity"
            )
            supported_name = issuer_name if identity_source and normalized(issuer_name) in normalized(identity_text) else prior.get("supported_legal_issuer_name", "")
            if not identity_source and prior.get("identity_document_id"):
                identity_source = next((item for item in sources if item.document_id == prior["identity_document_id"]), None)
                identity_page = prior.get("identity_page", "")
                identity_text = prior.get("identity_supporting_text", "")

        if decision["geography_status"] == "source_supported_unique":
            province_tokens = (decision["province"], decision["province"].removesuffix("省"))
            city_tokens = (decision["city"], decision["city"].removesuffix("市"))
            geo_source, geo_page, geo_text = choose_page(
                sources,
                ("|".join(token for token in province_tokens if token), "|".join(token for token in city_tokens if token)),
                ADDRESS_TERMS + IDENTITY_TERMS,
                issuer_name,
                "geography",
            )
            if not geo_source:
                geo_source, geo_page, geo_text = choose_page(
                    sources,
                    ("|".join(token for token in city_tokens if token),),
                    ADDRESS_TERMS + province_tokens + IDENTITY_TERMS,
                    issuer_name,
                    "geography",
                )
            if not geo_source and prior.get("geography_status") == "source_supported_unique":
                geo_source = next((item for item in sources if item.document_id == prior.get("geography_document_id")), None)
                geo_page = prior.get("geography_page", "")
                geo_text = prior.get("geography_supporting_text", "")
            if geo_source and geo_page and not any(token and token in geo_text for token in city_tokens):
                geo_text = snippet(
                    geo_source.pages[int(geo_page) - 1],
                    tuple(token for token in city_tokens if token),
                )
        else:
            geo_source = None
            geo_page = ""
            geo_text = ""

        if decision["owner_level"] != "unknown":
            owner_tokens = expected_owner_tokens(decision)
            owner_source, owner_page, owner_text = choose_page(
                sources, ("|".join(OWNER_TERMS),), owner_tokens + OWNER_TERMS, issuer_name, "owner"
            )
            if prior.get("owner_level") == decision["owner_level"] and prior.get("owner_supporting_text"):
                prior_owner_source = next((item for item in sources if item.document_id == prior.get("owner_document_id")), None)
                if prior_owner_source:
                    owner_source = prior_owner_source
                    owner_page = prior.get("owner_page", "")
                    owner_text = prior.get("owner_supporting_text", "")
            controller = owner_name(owner_text, decision) or prior.get("controlling_owner", "")
        else:
            owner_source = None
            owner_page = ""
            owner_text = ""
            controller = ""

        if decision["scope_reason_code"] == "local_public_platform_role":
            role_anchor = ROLE_ANCHOR_OVERRIDES.get(unit_id, "")
            role_source, role_page, role_text = choose_page(
                sources, (role_anchor,) if role_anchor else (), PLATFORM_TERMS, issuer_name, "role"
            )
            if prior.get("role_supporting_text"):
                prior_role_source = next((item for item in sources if item.document_id == prior.get("role_document_id")), None)
                prior_role_text = prior.get("role_supporting_text", "")
                strict_prior = bool(
                    any(term in prior_role_text for term in PLATFORM_TERMS)
                    and re.search(r"(?:发行人|公司).{0,160}(?:作为|是|为|承担|负责|主体|业务)", prior_role_text)
                    and "募集资金不用于" not in prior_role_text
                )
                if prior_role_source and strict_prior:
                    role_source = prior_role_source
                    role_page = prior.get("role_page", "")
                    role_text = prior_role_text
        elif decision["scope_reason_code"] in {"excluded_commercial_no_platform_role", "unresolved_platform_boundary"}:
            role_source, role_page, role_text = choose_page(
                sources, (), BUSINESS_TERMS + ("不属于地方政府融资平台", "不承担政府融资职能"), issuer_name, "business"
            )
        elif unit_id == "mv_3134f5ad5182":
            role_source, role_page, role_text = choose_page(
                sources, ("标准化厂房|配套设施",), ("发行公司债券", "所筹资金"), issuer_name, "role"
            )
        elif unit_id == "mv_32559fdf4bd7":
            role_source, role_page, role_text = choose_page(
                sources, (issuer_name,), ("交通基础设施", "招标人"), issuer_name, "role"
            )
        else:
            role_source = None
            role_page = ""
            role_text = ""

        controller = CONTROLLER_OVERRIDES.get(unit_id, controller)

        conflict_status = "none_observed"
        unresolved_reason = ""
        if unit_id == "mv_dd84e076bf32":
            conflict_status = "legal_name_conflict_recorded"
            unresolved_reason = "current_authoritative_sources_use_different_legal_name"
        elif decision["scope_reason_code"] == "unresolved_owner_level":
            unresolved_reason = "controlling_owner_level_not_source_supported"
        elif decision["scope_reason_code"] == "unresolved_platform_boundary":
            unresolved_reason = "platform_like_role_remains_ambiguous"

        scope_basis = {
            "local_public_platform_role": "Source-supported local public control and issuer-specific platform-like public financing or project role.",
            "excluded_central_public": "Source-supported central control excludes the issuer from the local-government platform frame.",
            "excluded_provincial_public": "Source-supported provincial control without a city-platform ownership tie excludes the issuer.",
            "excluded_private": "Source-supported private or natural-person control excludes the issuer.",
            "excluded_commercial_no_platform_role": "Local public ownership is documented but the issuer-specific business evidence does not establish a platform-like public financing or project role.",
            "unresolved_owner_level": "Issuer identity geography and public-project evidence are available but controlling-owner level remains unsupported.",
            "unresolved_platform_boundary": "Local public control is supported but the available issuer-specific evidence does not resolve the platform-role boundary.",
            "unresolved_legal_identity": "The frozen frame name cannot be linked uniquely to the current legal issuer named by authoritative sources.",
        }[decision["scope_reason_code"]]

        row = {
            "validation_unit_id": unit_id,
            "issuer_name": issuer_name,
            "supported_legal_issuer_name": supported_name,
            "province": decision["province"],
            "city": decision["city"],
            "geography_status": decision["geography_status"],
            "administrative_level": decision["administrative_level"],
            "controlling_owner": controller,
            "owner_level": decision["owner_level"],
            "scope_disposition": decision["scope_disposition"],
            "scope_reason_code": decision["scope_reason_code"],
            "scope_basis": scope_basis,
            "audit_note": decision["audit_note"],
            **evidence_fields("identity", identity_source, identity_page, identity_text),
            **evidence_fields("geography", geo_source, geo_page, geo_text),
            **evidence_fields("owner", owner_source, owner_page, owner_text),
            **evidence_fields("role", role_source, role_page, role_text),
            "conflict_status": conflict_status,
            "unresolved_reason": unresolved_reason,
            "review_gate": "PI approval required before frame freeze or sampling",
            "baseline_geography_gap": "true" if unit_id in old and old[unit_id].get("geography_status") != "source_supported_unique" else "false",
            "baseline_scope_review": "true" if unit_id in old and old[unit_id].get("scope_disposition") == "review_required" else "false",
        }
        crosswalk.append(row)

        if decision["geography_status"] != "source_supported_unique":
            unresolved.append({
                "validation_unit_id": unit_id,
                "issuer_name": issuer_name,
                "failed_gate": "geography_and_identity",
                "observed_values": supported_name,
                "source_document_ids": row["identity_document_id"],
                "disposition": "unresolved_after_search",
                "reason_code": "unresolved_legal_identity",
                "notes": decision["audit_note"],
                "review_required": "true",
            })
        if decision["scope_disposition"] == "unresolved_after_search":
            unresolved.append({
                "validation_unit_id": unit_id,
                "issuer_name": issuer_name,
                "failed_gate": "scope",
                "observed_values": f"owner_level={decision['owner_level']}; role_document={row['role_document_id']}",
                "source_document_ids": ";".join(dict.fromkeys(filter(None, (row["owner_document_id"], row["role_document_id"], row["identity_document_id"])))),
                "disposition": "unresolved_after_search",
                "reason_code": decision["scope_reason_code"],
                "notes": decision["audit_note"],
                "review_required": "true",
            })

    write_csv(OUT_CROSSWALK, crosswalk, CROSSWALK_FIELDS)
    write_csv(OUT_UNRESOLVED, unresolved, UNRESOLVED_FIELDS)
    write_csv(OUT_MANIFEST, manifest, MANIFEST_FIELDS)
    print(f"wrote {len(crosswalk)} crosswalk rows, {len(unresolved)} failed gates, and {len(manifest)} source rows")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    args = parser.parse_args()
    build(args.source_dir)


if __name__ == "__main__":
    main()
