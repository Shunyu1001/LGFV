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
EXP = ROOT / "experiments/EXP-20260831-001"
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
    "mv_c4af6b64ad69": "doc_sch_20260630_0003_003",
    "mv_a52ab8f6ce4b": "doc_exp_20260703_0021_005",
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
    "mv_3134f5ad5182": {
        "document_id": "web_chinamoney_jinluling_2025_rating",
        "filename": "web_chinamoney_jinluling_2025_rating.pdf",
        "text_filename": "web_chinamoney_jinluling_2025_rating.txt",
        "document_type": "rating_report",
        "publisher": "China Money; CSCI Pengyuan",
        "document_title": "吉安市井冈山开发区金庐陵经济发展有限公司2025年主体信用评级报告",
        "document_date": "2025-08-13",
        "retrieval_date": "2026-08-31",
        "document_page_url": "https://www.chinamoney.com.cn/dqs/cm-s-notice-query/fileDownLoad.do?contentId=3282967&mode=open&priority=0",
        "download_url": "https://www.chinamoney.com.cn/dqs/cm-s-notice-query/fileDownLoad.do?contentId=3282967&mode=open&priority=0",
        "extraction_profile": "pdfplumber-0.11.10-layout-x2-y3",
    },
    "mv_dc10a1d093cf": {
        "document_id": "web_sse_shanxi_construction_2025_annual",
        "filename": "web_sse_shanxi_construction_2025_annual.pdf",
        "text_filename": "web_sse_shanxi_construction_2025_annual.txt",
        "document_type": "annual_report",
        "publisher": "Shanghai Stock Exchange",
        "document_title": "山西建设投资集团有限公司公司债券年度报告（2025年）",
        "document_date": "2026-04-29",
        "retrieval_date": "2026-08-31",
        "document_page_url": "https://static.sse.com.cn/disclosure/bond/announcement/company/c/new/2026-04-29/244508_20260429_FIHX.pdf",
        "download_url": "https://static.sse.com.cn/disclosure/bond/announcement/company/c/new/2026-04-29/244508_20260429_FIHX.pdf",
        "extraction_profile": "pdfplumber-0.11.10-layout-x2-y3",
    },
    "mv_32559fdf4bd7": {
        "document_id": "web_chinamoney_guizhou_expressway_2024_base",
        "filename": "web_chinamoney_guizhou_expressway_2024_base.pdf",
        "text_filename": "web_chinamoney_guizhou_expressway_2024_base.txt",
        "document_type": "parent_prospectus",
        "publisher": "China Money",
        "document_title": "贵州高速公路集团有限公司2024年度第二期中期票据基础募集说明书",
        "document_date": "2024-05-23",
        "retrieval_date": "2026-08-31",
        "document_page_url": "https://www.chinamoney.com.cn/dqs/cm-s-notice-query/fileDownLoad.do?contentId=2882938&mode=open&priority=0",
        "download_url": "https://www.chinamoney.com.cn/dqs/cm-s-notice-query/fileDownLoad.do?contentId=2882938&mode=open&priority=0",
        "extraction_profile": "pdfplumber-0.11.10-layout-x2-y3",
    },
    "mv_3707ecbfb1f2": {
        "document_id": "web_chinamoney_linyi_2026_rating",
        "filename": "web_chinamoney_linyi_2026_rating.pdf",
        "text_filename": "web_chinamoney_linyi_2026_rating.txt",
        "document_type": "rating_report",
        "publisher": "China Money; Orient Golden Credit",
        "document_title": "临沂投资发展集团有限公司主体及“23临投01/23临沂投发债01”2026年度跟踪评级报告",
        "document_date": "2026-06-23",
        "retrieval_date": "2026-08-31",
        "document_page_url": "https://www.chinamoney.com.cn/dqs/cm-s-notice-query/fileDownLoad.do?contentId=3364219&mode=save&priority=0",
        "download_url": "https://www.chinamoney.com.cn/dqs/cm-s-notice-query/fileDownLoad.do?contentId=3364219&mode=save&priority=0",
        "extraction_profile": "pdfplumber-0.11.10-layout-x2-y3",
    },
}

CONTROLLER_OVERRIDES = {
    "mv_b7aabd80bf01": "中国民用航空局",
}

OWNER_EVIDENCE_OVERRIDES = {
    "mv_b2459f067a2b": ("doc_sch_20260630_0159_004", 49, ("控股股东和实际控制人是新乡市人民政府",), "新乡市人民政府"),
    "mv_982774a1383c": ("doc_sch_20260630_0098_006", 31, ("实际控制人 为江苏省人民政府",), "江苏省人民政府"),
    "mv_006dcea75bdc": ("doc_exp5_20260703_0007_004", 27, ("实际控制人仍为 宁波市海曙区国有资产管理中心",), "宁波市海曙区国有资产管理中心"),
    "mv_976b6b4ba9e3": ("doc_exp8_20260703_0163_006", 37, ("发行人实际控制人为宁波市镇海区国有资产管理服务中心",), "宁波市镇海区国有资产管理服务中心"),
    "mv_159990d28253": ("doc_sch_20260630_0094_001", 47, ("发行人控股股东和实 际控制人为重庆市江津区国有资产监督管理委员会",), "重庆市江津区国有资产监督管理委员会"),
    "mv_339f72153d34": ("doc_sch_20260630_0167_006", 46, ("实际控制人为重庆市江津区国有资产监督管理委员会",), "重庆市江津区国有资产监督管理委员会"),
    "mv_337e721d68ed": ("doc_sch_20260630_0145_004", 55, ("最终控制方为中国-上海合作组织地方经 贸合作示范区管理委员会",), "中国-上海合作组织地方经贸合作示范区管理委员会"),
    "mv_7c33183335cb": ("doc_sch_20260630_0009_007", 51, ("实际控制人为武汉东湖新技术开发区管理委员会",), "武汉东湖新技术开发区管理委员会"),
    "mv_17e532a3b4ee": ("doc_sch_20260630_0001_007", 5, ("公司实际控制 人为四川省政府国有资产监督管理委员会",), "四川省政府国有资产监督管理委员会"),
    "mv_a84c738293b5": ("doc_sch_20260630_0065_004", 5, ("广 东省人民政府国有资产监督管理委员会",), "广东省人民政府国有资产监督管理委员会"),
    "mv_337bebdb56b3": ("doc_sch_20260630_0026_009", 41, ("实际控制人为广西壮族自治区人民政府国 有资产监督管理委员会",), "广西壮族自治区人民政府国有资产监督管理委员会"),
    "mv_4f02e2b3b4ef": ("doc_exp8_20260703_0037_007", 41, ("南京江宁经济技术开发区管理委员会持有公司93.88%的股权",), "南京江宁经济技术开发区管理委员会"),
    "mv_32814f16ef6f": ("doc_sch_20260630_0061_008", 8, ("发行人实际控制人为安徽省人民政府国有资产监督管理委员会",), "安徽省人民政府国有资产监督管理委员会"),
    "mv_b08ea3f69614": ("doc_exp_20260703_0004_006", 35, ("发行人控股股东及实际控制人均为成都市国有资产监督管理委员会",), "成都市国有资产监督管理委员会"),
    "mv_ce9b4a51f177": ("doc_exp4_20260703_0049_008", 47, ("发行人的实际控制人为自治区国资委",), "广西壮族自治区人民政府国有资产监督管理委员会"),
    "mv_6bdc75acec44": ("doc_sch_20260630_0081_004", 35, ("发行人控股股东及实际控制人均为张毓强",), "张毓强"),
    "mv_5d511bd5ada9": ("doc_sch_20260630_0131_019", 40, ("李水荣持有发行人股份63.523%，为发行人控股 股东和实际控制人",), "李水荣"),
    "mv_dda0f3c66afa": ("doc_sch_20260630_0084_005", 32, ("发行人控股股东及实际控制人为自然人陈邦先生",), "陈邦"),
    "mv_1d97639f04bd": ("doc_sch_20260630_0063_002", 54, ("发行人实际控制人为苏州市人民政府国有资产监督管 理委员会",), "苏州市人民政府国有资产监督管理委员会"),
    "mv_bbe1de049afe": ("doc_sch_20260630_0119_002", 43, ("实 际控制人为重庆市永川区国有资产管理中心",), "重庆市永川区国有资产管理中心"),
    "mv_02c9115b037c": ("doc_sch_20260630_0041_003", 36, ("发行人控股股东和实际控制人均为西宁市政府国有资产监督管理委员会",), "西宁市政府国有资产监督管理委员会"),
    "mv_3134f5ad5182": ("web_chinamoney_jinluling_2025_rating", 6, ("公司实际控制人变更为吉安市国资委",), "吉安市国有资产监督管理委员会"),
    "mv_32559fdf4bd7": ("web_chinamoney_guizhou_expressway_2024_base", 157, ("贵阳市城市发展投资集团股份有限公", "贵州省国资委持有发行人"), "贵州省人民政府国有资产监督管理委员会"),
    "mv_3707ecbfb1f2": ("web_chinamoney_linyi_2026_rating", 3, ("临沂市人民政府国有资产监督管理委员会", "控股股东和实际控制人"), "临沂市人民政府国有资产监督管理委员会"),
    "mv_c4af6b64ad69": ("doc_sch_20260630_0003_003", 6, ("公司实际控制 人仍为珠海市国资委",), "珠海市国资委"),
    "mv_940b87861065": ("doc_sch_20260630_0135_010", 39, ("本公司实际控制人由张寓帅先生、郭梅兰女士变更为张寓帅先生",), "张寓帅"),
}

ROLE_EVIDENCE_OVERRIDES = {
    "mv_0076d521190d": ("doc_exp9_20260704_0111_009", 70, ("公司主要通过境内外融资筹措资金并进行投资", "古雷管委会")),
    "mv_4f36112eaaff": ("doc_exp5_20260703_0025_007", 34, ("作为全面负责牛首山景区建设和运营的 单一项目公司", "所有的融资均服务于项目 建设")),
    "mv_3134f5ad5182": ("web_chinamoney_jinluling_2025_rating", 6, ("公司作为井开区和青原区工业园重要的基础设施建设及园区开发主体",)),
    "mv_02c9115b037c": ("doc_sch_20260630_0041_003", 17, ("根据西宁市政府安排", "西宁市教育布局调整一期项目已竣工验收")),
    "mv_7c33183335cb": ("doc_sch_20260630_0009_007", 113, ("建设投资是东湖高新区管委会赋予公司的重要职责之一",)),
    "mv_1d97639f04bd": ("doc_sch_20260630_0063_002", 7, ("发行人主要从事轨道交通项目的建设和运营", "为了满足持续增加的轨道交通建设资金需求")),
    "mv_dea7fe1c1704": ("doc_exp5_20260703_0004_008", 49, ("发行人作为椒江区重要的交通基础建设与社会事业运营主体", "承担椒江区内交通基础设施建设")),
    "mv_17100b41e197": ("doc_sch_20260630_0144_005", 92, ("部分项目由发行人子公司江宁交发通过委托代建模式承接", "建设过程中的工程款及江宁交发先行垫付产生的资金成本")),
    "mv_18c49cc8c4cc": ("doc_sch_20260630_0024_009", 54, ("发行人作为长沙市天心区区级平台公司", "发行人主要负责天心区内的城市建设")),
    "mv_b6a587c44bcf": ("doc_exp2_20260703_0022_003", 105, ("亦庄控股主要负责北京经开区的基础设施建设和土地一级开发", "亦庄国投则更多地围绕资本运作构建产业投资服务平台")),
    "mv_989edd5e627b": ("doc_exp_20260703_0005_010", 44, ("作为天津市国有资本投资运营公司", "主要从事化工板块业务、能源板块业务")),
    "mv_0e2553f13e14": ("doc_exp9_20260704_0084_002", 27, ("发行人现有经营范围为", "企业自有资金投资")),
    "mv_3b9c491fbf5a": ("doc_sch_20260630_0149_002", 68, ("发行人营业收入来源主要包括建筑安装、房地产业、小额贷款", "发行人建筑施工主业依托于控股子公司江苏华建和江苏扬建")),
    "mv_83fa1cb2dc9e": ("doc_sch_20260630_0066_003", 82, ("主营业务无涉及政府工程代建、土地整理、保障房建设等城建类业务", "未参与PPP项目、政府投资基金、BT、回购其他主体项目的业务")),
    "mv_c4af6b64ad69": ("doc_sch_20260630_0003_003", 24, ("公司作为珠海交控集团下属产业类平台", "拥有着市内港口码头、机场等核心交通类资产")),
    "mv_46a8889cdc37": ("doc_exp8_20260703_0017_003", 51, ("城乡重大基础设施项目投资建设与运营", "政府重大公益项目的投资建设与运营")),
    "mv_072dc57cd561": ("doc_sch_20260630_0160_003", 51, ("发行人主营业务主要为政府授权范围内的基础设施及民生保障类项目的投融资", "建设、运营、管理")),
    "mv_46f0d1b309fc": ("doc_sch_20260630_0127_002", 131, ("城交投公司作为社会资本方参与公共交通类 PPP 项目投资", "负责项目的投融资、建设和运营维护管理")),
    "mv_c9485f13755e": ("doc_exp8_20260703_0012_004", 60, ("新孟河延伸拓浚（新北区）及综合配套整治项目采取“政府购买服务”的方式实施", "计划总投资 97.12 亿元，截至 2026 年 3 月末已投资 94.48 亿元")),
    "mv_2547f5fbc2e2": ("doc_exp10_20260704_0013_006", 57, ("发行人的主要业务划分为物流业务和收费公路及大环保业务两个板块", "发行人不涉及城投业务")),
    "mv_5e15d9346287": ("doc_sch_20260630_0074_002", 172, ("公司是南通市苏锡通园区最重要的基础设施开发建设主体", "主要根据政府意图承担苏锡通园区的基础设施建设投融资任务")),
    "mv_b08ea3f69614": ("doc_exp_20260703_0004_006", 141, ("成都市财政局", "产业园区配套", "项目建设资金", "资金来源为自有资金")),
    "mv_a52ab8f6ce4b": ("doc_exp_20260703_0021_005", 22, ("促进广州市重大基础设施项目的落地实施", "基础设施、城市更新改造及战略性新兴产业")),
    "mv_0590d5f9c3fa": ("doc_sch_20260630_0170_009", 107, ("发行人主要采取自有资金加社会配套资金相结合的融资模式", "需北京市政投入负债性资金 68.97 亿元")),
    "mv_8508178f07a5": ("doc_exp5_20260703_0001_009", 95, ("与济南市章丘区人民政府签订《济南市章丘区委托建设协议》", "建设投资成本（包括融资成本）的 20-30%加成")),
    "mv_bc74862def53": ("doc_sch_20260630_0031_005", 105, ("市政府指定我集团作为片区开发主体", "总投资约为 150,000.00 万元")),
    "mv_3c17f10ab84f": ("doc_exp2_20260703_0002_009", 82, ("主要以政府购买服务方式产生收益", "由政府提供缺口补助")),
    "mv_bf399debd218": ("doc_exp2_20260703_0021_005", 88, ("发行人工程设计业务经营主体为永麒科技集团有限公司", "通过招投标获取项目，主要客户为各地政府及平台公司")),
}

ROLE_ANCHOR_OVERRIDES = {
    "mv_dd32227a7cc7": "海淀区城市基础设施投融资的重要主体",
}

SUPPORTED_NAME_OVERRIDES = {
    "mv_35577ffe2ec5": "遵义道桥建设（集团）有限公司",
}

GEOGRAPHY_EVIDENCE_OVERRIDES = {
    "mv_3c17f10ab84f": (
        "doc_exp2_20260703_0002_009",
        251,
        (
            "发行人： 北控水务集团有限公司",
            "联系地址：北京市朝阳区望京东园七区保利国际广场 T3 北控水务大厦",
        ),
    ),
    "mv_b14a65482fac": (
        "doc_sch_20260630_0168_006",
        40,
        (
            "注册名称 西部（重庆）科学城江津园区开发建设集团有限公司",
            "住所（注册地） 重庆市江津区双福街道南北大道390号",
        ),
    ),
    "mv_3707ecbfb1f2": (
        "web_linyi_sasac_profile",
        1,
        (
            "企业名称 临沂投资发展集团有限公司",
            "注册地址 山东省临沂市兰山区北城新区临沂商会大厦1号楼701",
        ),
    ),
    "mv_3134f5ad5182": (
        "web_chinamoney_jinluling_2025_rating",
        6,
        (
            "公司原名为“吉安市金庐陵经济开发有限公司”",
            "公司实际控制人变更为吉安市国资委",
        ),
    ),
    "mv_6c405c7c4748": (
        "doc_sch_20260630_0012_012",
        32,
        (
            "注册名称 山东金曰交通发展集团有限公司",
            "住所（注册地） 山东省济南市章丘区圣井高科技工业园",
        ),
    ),
    "mv_a1ed5dac069a": (
        "doc_sch_20260630_0062_002",
        205,
        (
            "一、发行人 名称：山西交通控股集团有限公司",
            "住所：山西省示范区太原学府园区南中环街 529 号 B 座 24-25 层",
        ),
    ),
    "mv_a84c738293b5": (
        "doc_sch_20260630_0065_001",
        27,
        (
            "注册名称：广东省铁路建设投资集团有限公司",
            "注册地址：广东省广州市天河区黄埔大道中 668 号",
        ),
    ),
    "mv_457ad56917e5": (
        "doc_exp9_20260704_0141_007",
        56,
        (
            "一、发行人 江苏省国信集团有限公司",
            "联系地址：南京市玄武区长江路 88 号",
        ),
    ),
    "mv_58bf202441a9": (
        "doc_exp8_20260703_0009_003",
        37,
        (
            "注册名称：深圳市地铁集团有限公司",
            "住所：深圳市福田区莲花街道福中一路1016号地铁大厦",
        ),
    ),
    "mv_bbc98d5aa00c": (
        "web_shenzhen_sasac_special_zone_development",
        1,
        (
            "特区建发集团按照市委、市政府和市国资委的决策部署及要求",
            "地址：深圳市福田区福华一路大中华国际交易广场裙楼7楼",
        ),
    ),
    "mv_4aa0191176be": (
        "doc_exp10_20260704_0192_002",
        240,
        (
            "一、发行人 发行人：湖北楚天智能交通股份有限公司",
            "联系地址：武汉市汉阳区湖北国展中心东塔",
        ),
    ),
    "mv_bce7a88198f3": (
        "doc_exp8_20260703_0087_004",
        37,
        (
            "中文注册名称： 荆门高新技术产业开发有限责任公司",
            "住所： 湖北省荆门市高新区·掇刀区凤袁路 1 号",
        ),
    ),
    "mv_35577ffe2ec5": (
        "doc_gz_zy_daoqiao_2015_bond_prospectus",
        22,
        (
            "名称：遵义市道路桥梁工程有限责任公司",
            "住所：遵义市汇川区苏州路中段公路枢纽组织管理中心",
        ),
    ),
    "mv_707d013abcbe": (
        "doc_sch_20260630_0114_001",
        30,
        (
            "（一）注册名称：青海省国有资产投资管理有限公司",
            "（八）住所：青海省西宁市城中区创业路 128 号中小企业创业园 5 楼 501 室",
        ),
    ),
    "mv_588a5cfdd852": ("doc_sch_20260630_0161_008", 36),
    "mv_e2b7b3bbc9d5": ("doc_sch_20260630_0078_004", 33),
    "mv_46f0d1b309fc": ("doc_sch_20260630_0127_002", 39),
    "mv_2f9f77975978": ("doc_exp9_20260704_0182_004", 25),
    "mv_29bec224b1af": ("doc_exp9_20260704_0247_001", 16),
    "mv_17100b41e197": ("doc_sch_20260630_0144_005", 33),
    "mv_f26b7d84a6c5": ("doc_sch_20260630_0075_003", 36),
    "mv_4f02e2b3b4ef": ("doc_exp8_20260703_0037_007", 37),
    "mv_48ea3687a4e1": ("doc_exp8_20260703_0042_004", 32),
    "mv_4f36112eaaff": ("doc_exp5_20260703_0025_007", 36),
    "mv_072dc57cd561": ("doc_sch_20260630_0160_003", 33),
    "mv_aef21d6695b2": ("doc_sch_20260630_0089_002", 34),
    "mv_dea7fe1c1704": ("doc_exp5_20260703_0004_008", 29),
    "mv_dc10a1d093cf": ("web_sse_shanxi_construction_2025_annual", 6),
    "mv_0e2553f13e14": ("doc_exp9_20260704_0084_005", 19),
    "mv_312664814132": ("doc_sch_20260630_0128_005", 37),
    "mv_337bebdb56b3": ("doc_sch_20260630_0026_009", 31),
    "mv_3b9c491fbf5a": ("doc_sch_20260630_0149_002", 33),
    "mv_e4cd1cefc02b": ("doc_sch_20260630_0121_005", 33),
    "mv_81aed909eaf3": ("doc_sch_20260630_0088_005", 23),
    "mv_974b8c867433": ("doc_sch_20260630_0059_004", 37),
    "mv_31dd4fd107b5": ("doc_exp_20260703_0003_007", 36),
    "mv_0ba8eaa09fa0": ("doc_exp10_20260704_0156_004", 31),
    "mv_ed1f2e005d13": ("doc_exp2_20260703_0003_005", 32),
    "mv_df87c57ef59b": ("doc_exp10_20260704_0064_007", 32),
    "mv_dda0f3c66afa": ("doc_sch_20260630_0084_005", 30),
    "mv_c4af6b64ad69": ("doc_sch_20260630_0003_003", 6),
    "mv_14353a22e4cf": ("doc_exp5_20260703_0034_004", 36),
    "mv_ea3d4bb7e80e": ("doc_exp6_20260703_0025_004", 31),
    "mv_1d97639f04bd": ("doc_sch_20260630_0063_002", 44),
    "mv_349e0a09a9ca": ("doc_exp10_20260704_0071_006", 36),
    "mv_bbe1de049afe": ("doc_sch_20260630_0119_002", 37),
    "mv_fdbd697a93bc": ("doc_exp8_20260703_0088_007", 37),
    "mv_46a8889cdc37": ("doc_exp8_20260703_0017_003", 28),
    "mv_2547f5fbc2e2": ("doc_exp10_20260704_0013_006", 25),
    "mv_940b87861065": ("doc_sch_20260630_0135_010", 33),
}

GEOGRAPHY_RELATION_ALIASES = {
    "mv_3134f5ad5182": "吉安市金庐陵经济开发有限公司",
    "mv_bbc98d5aa00c": "特区建发集团",
    "mv_35577ffe2ec5": "遵义市道路桥梁工程有限责任公司",
    "mv_c4af6b64ad69": "珠海港集团",
}

MULTIPLE_LOCATION_TERMS = {
    "mv_2547f5fbc2e2": (("百慕大",), ("香港",), ("深圳",)),
    "mv_940b87861065": (("深圳",), ("东莞",)),
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
    "text_extraction_status", "source_text_sha256", "extraction_profile",
    "cache_verification_status", "raw_cache_filename", "text_cache_filename",
    "rights_note", "local_copy_committed", "error",
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
GENERIC_ISSUER_GEOGRAPHY_TERMS = (
    "发行人基本情况", "发行人概况", "发行人住所", "发行人注册地址",
    "发行人注册地", "发行人办公地址", "发行人名称",
)
THIRD_PARTY_GEOGRAPHY_MARKERS = (
    "主承销商", "联席主承销商", "律师事务所", "法律顾问", "会计师事务所",
    "审计机构", "评级机构", "承销机构", "托管人", "登记结算机构",
)
STRUCTURED_ADDRESS_PATTERN = re.compile(
    r"(发行人注册地址|发行人办公地址|发行人住所(?!地)|注册地址|注册地|"
    r"公司住所|企业住所|办公地址|法定住所|公司地址|(?<!联系)地址)"
    r"\s*(?:[:：]|为|位于|由)\s*([^。；]{0,260})"
)
ADDRESS_VALUE_STOP_PATTERN = re.compile(
    r"\s+(?:(?:法定代表人|授权代表|负责人|联系人|电话|传真|邮政编码|网址|"
    r"统一社会信用代码|企业类型|经营范围|名称|住所|注册地址|注册地|办公地址|"
    r"联系地址|地址)\s*[:：]|[一二三四五六七八九十]+、)"
)


def structured_address_value(match: re.Match[str]) -> str:
    """Keep one address field from absorbing later entities or fields on the page."""
    value = match.group(2)
    stop = ADDRESS_VALUE_STOP_PATTERN.search(value)
    return value[: stop.start()] if stop else value


def issuer_relation_block(prefix: str) -> str:
    """Keep only issuer relation text after the last intermediary marker."""
    block = prefix[-650:]
    positions = [
        block.rfind(marker)
        for marker in THIRD_PARTY_GEOGRAPHY_MARKERS
        if block.rfind(marker) >= 0
    ]
    if not positions:
        return block
    return block[max(positions) :]


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


def read_extracted_pages(path: Path) -> list[str]:
    """Read a form-feed-delimited cache without counting its terminal marker."""
    pages = path.read_text(encoding="utf-8", errors="replace").split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return pages


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


def anchor_covering_snippet(page: str, anchors: tuple[str, ...], width: int = 1000) -> str:
    """Return one contiguous page excerpt that retains every registered anchor."""
    flat = collapse(page)
    normalized_flat_chars: list[str] = []
    flat_positions: list[int] = []
    for position, character in enumerate(flat):
        retained = normalized(character)
        for normalized_character in retained:
            normalized_flat_chars.append(normalized_character)
            flat_positions.append(position)
    normalized_flat = "".join(normalized_flat_chars)
    spans: list[tuple[int, int]] = []
    for anchor in anchors:
        normalized_anchor = normalized(anchor)
        anchor_position = normalized_flat.find(normalized_anchor)
        if anchor_position < 0:
            raise ValueError(f"registered evidence anchor is absent from page: {anchor}")
        start_position = flat_positions[anchor_position]
        end_position = flat_positions[anchor_position + len(normalized_anchor) - 1] + 1
        spans.append((start_position, end_position))
    start = max(0, min(span[0] for span in spans) - 180)
    end = min(len(flat), max(span[1] for span in spans) + width)
    excerpt = flat[start:end]
    if not all(normalized(anchor) in normalized(excerpt) for anchor in anchors):
        raise ValueError("registered evidence anchors could not be retained in one excerpt")
    return excerpt


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
        converted["raw_cache_filename"] = f"{row['document_id']}.pdf"
        converted["text_cache_filename"] = f"{row['document_id']}.txt"
        text_path = source_dir / f"{row['document_id']}.txt"
        if text_path.exists():
            pdf_path = source_dir / f"{row['document_id']}.pdf"
            if not pdf_path.exists():
                raise ValueError(f"raw source is missing for extracted text: {row['document_id']}")
            raw_sha256 = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
            if raw_sha256 != row["sha256"]:
                raise ValueError(f"raw source hash mismatch: {row['document_id']}")
            text_payload = text_path.read_bytes()
            converted["source_text_sha256"] = hashlib.sha256(text_payload).hexdigest()
            converted["extraction_profile"] = "inherited_EXP-011_cache_tool_version_unrecorded"
            converted["cache_verification_status"] = "raw_hash_verified_against_EXP-011_manifest_and_text_present"
            pages = read_extracted_pages(text_path)
            converted["pages"] = str(len(pages))
            converted["text_extraction_status"] = "cached_extracted_pages_available"
            by_unit[row["validation_unit_id"]].append(Source(row["validation_unit_id"], row["document_id"], pages, converted))
        else:
            converted["source_text_sha256"] = ""
            converted["extraction_profile"] = "inherited_EXP-011_cache_tool_version_unrecorded"
            converted["cache_verification_status"] = "source_cache_missing_at_ultra_audit"
        manifest.append(converted)

    for unit_id, document_id in PREEXISTING_PDFS.items():
        document = documents[document_id]
        pdf_path = source_dir / f"{document_id}.pdf"
        text_path = source_dir / f"{document_id}.txt"
        payload = pdf_path.read_bytes()
        pages = read_extracted_pages(text_path)
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
            "text_extraction_status": "cached_extracted_pages_available",
            "source_text_sha256": hashlib.sha256(text_path.read_bytes()).hexdigest(),
            "extraction_profile": "inherited_cache_tool_version_unrecorded",
            "cache_verification_status": "raw_hash_recorded_and_text_present",
            "raw_cache_filename": f"{document_id}.pdf",
            "text_cache_filename": f"{document_id}.txt",
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
            "retrieval_date": metadata.get("retrieval_date", RETRIEVAL_DATE),
            "access_status": "retrieved_public_webpage",
            "http_status": "200",
            "content_type": "text/html",
            "retrieved_bytes": str(len(payload)),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "pages": "1",
            "text_extraction_status": "extracted_html_text",
            "source_text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "extraction_profile": "builtin_html_to_text_v1",
            "cache_verification_status": "raw_hash_recorded_and_text_present",
            "raw_cache_filename": metadata["filename"],
            "text_cache_filename": "",
            "rights_note": "Public government webpage; URL hash and excerpt retained. Raw page not committed.",
            "local_copy_committed": "false",
            "error": "",
        }
        manifest.append(row)
        by_unit[unit_id].insert(0, Source(unit_id, metadata["document_id"], [text], row))

    for unit_id, metadata in EXTERNAL_PDFS.items():
        payload = (source_dir / metadata["filename"]).read_bytes()
        pages = read_extracted_pages(source_dir / metadata["text_filename"])
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
            "retrieval_date": metadata.get("retrieval_date", RETRIEVAL_DATE),
            "access_status": "retrieved_public_disclosure",
            "http_status": "200",
            "content_type": "application/pdf",
            "retrieved_bytes": str(len(payload)),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "pages": str(len(pages)),
            "text_extraction_status": "cached_extracted_pages_available",
            "source_text_sha256": hashlib.sha256((source_dir / metadata["text_filename"]).read_bytes()).hexdigest(),
            "extraction_profile": metadata.get("extraction_profile", "inherited_cache_tool_version_unrecorded"),
            "cache_verification_status": "raw_hash_recorded_and_text_present",
            "raw_cache_filename": metadata["filename"],
            "text_cache_filename": metadata["text_filename"],
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


def cited_page(
    sources: list[Source],
    document_id: str,
    page_number: int,
    anchors: tuple[str, ...],
    *,
    width: int = 1000,
) -> tuple[Source, int, str]:
    source = next((item for item in sources if item.document_id == document_id), None)
    if source is None:
        raise ValueError(f"registered evidence document is unavailable: {document_id}")
    if page_number < 1 or page_number > len(source.pages):
        raise ValueError(f"registered evidence page is unavailable: {document_id} page {page_number}")
    page = source.pages[page_number - 1]
    flat = collapse(page)
    if not all(normalized(anchor) in normalized(flat) for anchor in anchors):
        missing = [anchor for anchor in anchors if normalized(anchor) not in normalized(flat)]
        raise ValueError(f"registered evidence anchors absent from {document_id} page {page_number}: {missing}")
    return source, page_number, anchor_covering_snippet(page, anchors, width=width)


def geography_evidence_page(
    sources: list[Source],
    document_id: str,
    page_number: int,
    decision: dict[str, str],
) -> tuple[Source, int, str]:
    """Retain a same-page issuer/location excerpt, not a third-party address hit."""
    source = next((item for item in sources if item.document_id == document_id), None)
    if source is None:
        raise ValueError(f"registered geography document is unavailable: {document_id}")
    if page_number < 1 or page_number > len(source.pages):
        raise ValueError(f"registered geography page is unavailable: {document_id} page {page_number}")
    flat = collapse(source.pages[page_number - 1])
    unit_id = decision["validation_unit_id"]
    issuer_name = decision["issuer_name"]
    alias = GEOGRAPHY_RELATION_ALIASES.get(unit_id, "")
    relation_candidates = tuple(dict.fromkeys(filter(None, (
        alias,
        issuer_name,
        re.split(r"[(（]", issuer_name, maxsplit=1)[0],
        issuer_name[:8],
    ))))
    relation = next((candidate for candidate in relation_candidates if candidate in flat), "")
    if not relation and normalized(alias or issuer_name) not in normalized(flat):
        raise ValueError(f"{unit_id} geography page does not identify the focal issuer")

    required_groups: tuple[tuple[str, ...], ...]
    if decision["geography_status"] == "source_supported_multiple":
        required_groups = MULTIPLE_LOCATION_TERMS[unit_id]
    else:
        city = decision["city"]
        required_groups = ((city, city.removesuffix("市").removesuffix("自治州")),)
    positions = [flat.find(relation)] if relation else [0]
    for group in required_groups:
        token_positions = [(flat.find(token), token) for token in group if token and flat.find(token) >= 0]
        if not token_positions:
            raise ValueError(f"{unit_id} geography page lacks required location group {group}")
        positions.append(min(token_positions)[0])
    start = max(0, min(positions) - 180)
    end = min(len(flat), max(positions) + 1200)
    return source, page_number, flat[start:end]


def generic_geography_evidence_page(
    sources: list[Source],
    decision: dict[str, str],
) -> tuple[Source | None, int | str, str]:
    """Find a page that links the focal issuer and reviewed city in one excerpt."""
    unit_id = decision["validation_unit_id"]
    issuer_name = decision["issuer_name"]
    city_candidates = tuple(dict.fromkeys(filter(None, (
        decision["city"], decision["city"].removesuffix("市").removesuffix("自治州"),
    ))))
    province_candidates = tuple(dict.fromkeys(filter(None, (
        decision["province"], decision["province"].removesuffix("省").removesuffix("市"),
    ))))
    ranked: list[tuple[int, int, int, Source, int, str, str, str, str]] = []
    for source_order, source in enumerate(sources):
        for page_number, page in enumerate(source.pages, start=1):
            flat = collapse(page)
            for match in STRUCTURED_ADDRESS_PATTERN.finditer(flat):
                fact = match.group(1)
                address_value = structured_address_value(match)
                city = next((candidate for candidate in city_candidates if candidate in address_value), "")
                if not city:
                    continue
                prefix = flat[max(0, match.start() - 900):match.start()]
                registered_block = issuer_relation_block(prefix)
                near_prefix = registered_block[-260:]
                relation = ""
                if fact.startswith("发行人"):
                    relation = fact
                elif normalized(issuer_name) in normalized(near_prefix):
                    relation = issuer_name
                else:
                    if "注册名称" in registered_block and normalized(issuer_name) in normalized(registered_block):
                        relation = issuer_name
                    else:
                        relation = next(
                            (
                                candidate for candidate in GENERIC_ISSUER_GEOGRAPHY_TERMS
                                if candidate in registered_block
                            ),
                            "",
                        )
                if not relation:
                    continue
                province = next(
                    (candidate for candidate in province_candidates if candidate in address_value),
                    "",
                )
                score = 140 if normalized(issuer_name) in normalized(near_prefix) else 100
                score += 20 if fact.startswith("发行人") else 0
                score += 10 if province else 0
                ranked.append(
                    (
                        score, -source_order, -page_number, source, page_number,
                        relation, fact, city, province,
                    )
                )
    if not ranked:
        return None, "", ""
    _, _, _, source, page_number, relation, fact, city, province = max(ranked)
    anchors = tuple(filter(None, (relation, fact, city, province)))
    excerpt = anchor_covering_snippet(source.pages[page_number - 1], anchors, width=720)
    return source, page_number, excerpt


def excerpt_has_issuer_geography_relation(unit_id: str, issuer_name: str, excerpt: str) -> bool:
    candidates = tuple(filter(None, (
        GEOGRAPHY_RELATION_ALIASES.get(unit_id, ""),
        issuer_name,
        re.split(r"[(（]", issuer_name, maxsplit=1)[0],
        *GENERIC_ISSUER_GEOGRAPHY_TERMS,
    )))
    compact = normalized(excerpt)
    return any(normalized(candidate) in compact for candidate in candidates)


def generic_geography_excerpt_is_direct(
    unit_id: str,
    issuer_name: str,
    city: str,
    excerpt: str,
) -> bool:
    city_candidates = tuple(filter(None, (city, city.removesuffix("市").removesuffix("自治州"))))
    for match in STRUCTURED_ADDRESS_PATTERN.finditer(excerpt):
        if not any(candidate in structured_address_value(match) for candidate in city_candidates):
            continue
        if match.group(1).startswith("发行人"):
            return True
        prefix = excerpt[max(0, match.start() - 900):match.start()]
        registered_block = issuer_relation_block(prefix)
        if normalized(issuer_name) in normalized(registered_block[-260:]):
            return True
        if "注册名称" in registered_block and normalized(issuer_name) in normalized(registered_block):
            return True
        if any(term in registered_block for term in GENERIC_ISSUER_GEOGRAPHY_TERMS):
            return True
    return False


def validate_cited_evidence(crosswalk: list[dict[str, str]], sources_by_unit: dict[str, list[Source]]) -> int:
    """Require every retained excerpt to occur on its cited extracted page."""
    verified = 0
    for row in crosswalk:
        unit_id = row["validation_unit_id"]
        by_document = {source.document_id: source for source in sources_by_unit[unit_id]}
        for prefix in ("identity", "geography", "owner", "role"):
            document_id = row[f"{prefix}_document_id"]
            page_text = row[f"{prefix}_supporting_text"]
            page_value = row[f"{prefix}_page"]
            if not document_id:
                if page_value or page_text:
                    raise ValueError(f"{unit_id} has partial {prefix} evidence")
                continue
            source = by_document.get(document_id)
            if source is None:
                raise ValueError(f"{unit_id} cites unavailable {prefix} document {document_id}")
            try:
                page_number = int(page_value)
            except ValueError as error:
                raise ValueError(f"{unit_id} has invalid {prefix} page {page_value!r}") from error
            if page_number < 1 or page_number > len(source.pages):
                raise ValueError(f"{unit_id} cites unavailable {prefix} page {page_number}")
            if collapse(page_text) not in collapse(source.pages[page_number - 1]):
                raise ValueError(
                    f"{unit_id} {prefix} excerpt is not contained in {document_id} page {page_number}"
                )
            if prefix == "geography":
                geography_override = GEOGRAPHY_EVIDENCE_OVERRIDES.get(unit_id)
                if geography_override and len(geography_override) == 3:
                    required_anchors = geography_override[2]
                    if not all(normalized(anchor) in normalized(page_text) for anchor in required_anchors):
                        raise ValueError(f"{unit_id} geography excerpt omits a registered direct-evidence anchor")
                if (
                    unit_id in GEOGRAPHY_EVIDENCE_OVERRIDES
                    and not excerpt_has_issuer_geography_relation(unit_id, row["issuer_name"], page_text)
                ):
                    raise ValueError(f"{unit_id} geography excerpt is not related to the focal issuer")
                if (
                    unit_id not in GEOGRAPHY_EVIDENCE_OVERRIDES
                    and row["geography_status"] == "source_supported_unique"
                    and not generic_geography_excerpt_is_direct(
                        unit_id, row["issuer_name"], row["city"], page_text
                    )
                ):
                    raise ValueError(f"{unit_id} generic geography excerpt lacks a focal address fact")
                if row["geography_status"] == "source_supported_unique":
                    city = row["city"]
                    city_tokens = (city, city.removesuffix("市").removesuffix("自治州"))
                    if not any(token and token in page_text for token in city_tokens):
                        raise ValueError(f"{unit_id} geography excerpt does not retain the reviewed city")
                elif row["geography_status"] == "source_supported_multiple":
                    for group in MULTIPLE_LOCATION_TERMS[unit_id]:
                        if not any(token in page_text for token in group):
                            raise ValueError(f"{unit_id} geography excerpt omits a recorded location group")
            elif prefix == "owner" and unit_id in OWNER_EVIDENCE_OVERRIDES:
                required_anchors = OWNER_EVIDENCE_OVERRIDES[unit_id][2]
                if not all(normalized(anchor) in normalized(page_text) for anchor in required_anchors):
                    raise ValueError(f"{unit_id} owner excerpt omits a registered anchor")
            elif prefix == "role" and unit_id in ROLE_EVIDENCE_OVERRIDES:
                required_anchors = ROLE_EVIDENCE_OVERRIDES[unit_id][2]
                if not all(normalized(anchor) in normalized(page_text) for anchor in required_anchors):
                    raise ValueError(f"{unit_id} role excerpt omits a registered anchor")
            verified += 1
    return verified


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
                if identity_source and identity_page:
                    identity_text = snippet(
                        identity_source.pages[int(identity_page) - 1],
                        (issuer_name,),
                    )

        if unit_id in GEOGRAPHY_EVIDENCE_OVERRIDES:
            geography_override = GEOGRAPHY_EVIDENCE_OVERRIDES[unit_id]
            document_id, page_number = geography_override[:2]
            if len(geography_override) == 3:
                geo_source, geo_page, geo_text = cited_page(
                    sources, document_id, page_number, geography_override[2], width=720
                )
            else:
                geo_source, geo_page, geo_text = geography_evidence_page(
                    sources, document_id, page_number, decision
                )
        elif decision["geography_status"] == "source_supported_unique":
            geo_source, geo_page, geo_text = generic_geography_evidence_page(sources, decision)
        else:
            geo_source = None
            geo_page = ""
            geo_text = ""

        if decision["owner_level"] != "unknown" and unit_id in OWNER_EVIDENCE_OVERRIDES:
            document_id, page_number, anchors, controller = OWNER_EVIDENCE_OVERRIDES[unit_id]
            owner_source, owner_page, owner_text = cited_page(
                sources, document_id, page_number, anchors
            )
        elif decision["owner_level"] != "unknown":
            owner_tokens = expected_owner_tokens(decision)
            owner_source, owner_page, owner_text = choose_page(
                sources, ("|".join(OWNER_TERMS),), owner_tokens + OWNER_TERMS, issuer_name, "owner"
            )
            if prior.get("owner_level") == decision["owner_level"] and prior.get("owner_supporting_text"):
                prior_owner_source = next((item for item in sources if item.document_id == prior.get("owner_document_id")), None)
                if prior_owner_source:
                    owner_source = prior_owner_source
                    owner_page = prior.get("owner_page", "")
                    if owner_page:
                        owner_text = snippet(
                            owner_source.pages[int(owner_page) - 1],
                            owner_tokens + OWNER_TERMS + (issuer_name,),
                            width=1000,
                        )
            controller = owner_name(owner_text, decision) or prior.get("controlling_owner", "")
        else:
            owner_source = None
            owner_page = ""
            owner_text = ""
            controller = ""

        if unit_id in ROLE_EVIDENCE_OVERRIDES:
            document_id, page_number, anchors = ROLE_EVIDENCE_OVERRIDES[unit_id]
            role_source, role_page, role_text = cited_page(
                sources, document_id, page_number, anchors
            )
        elif decision["scope_reason_code"] == "local_public_platform_role":
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
                    if role_page:
                        role_text = snippet(
                            role_source.pages[int(role_page) - 1],
                            ((role_anchor,) if role_anchor else ()) + PLATFORM_TERMS + (issuer_name,),
                            width=1000,
                        )
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
        elif unit_id == "mv_02c9115b037c":
            conflict_status = "temporal_platform_role_tension_recorded"
        elif decision["geography_status"] == "source_supported_multiple":
            conflict_status = "multiple_issuer_locations_recorded"
            unresolved_reason = "unique_province_city_requires_unregistered_location_precedence_rule"
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

        if decision["geography_status"] == "source_supported_multiple":
            unresolved.append({
                "validation_unit_id": unit_id,
                "issuer_name": issuer_name,
                "failed_gate": "geography_unique_assignment",
                "observed_values": decision["audit_note"],
                "source_document_ids": row["geography_document_id"],
                "disposition": "source_supported_multiple",
                "reason_code": "multiple_issuer_locations_recorded",
                "notes": "No unique province-city was assigned without a preregistered location-precedence rule.",
                "review_required": "true",
            })
        elif decision["geography_status"] != "source_supported_unique":
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

    verified_evidence = validate_cited_evidence(crosswalk, sources_by_unit)
    write_csv(OUT_CROSSWALK, crosswalk, CROSSWALK_FIELDS)
    write_csv(OUT_UNRESOLVED, unresolved, UNRESOLVED_FIELDS)
    write_csv(OUT_MANIFEST, manifest, MANIFEST_FIELDS)
    print(
        f"wrote {len(crosswalk)} crosswalk rows, {len(unresolved)} failed gates, "
        f"and {len(manifest)} source rows; verified {verified_evidence} cited excerpts"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    args = parser.parse_args()
    build(args.source_dir)


if __name__ == "__main__":
    main()
