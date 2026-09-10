"""Register a new dated source and direct excerpts, retaining the old snapshot record."""

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
from validate_probability_validation_frame import html_to_text, canonical_row_hash

UNIT = "mv_bbc98d5aa00c"
OLD_ID = "web_shenzhen_sasac_special_zone_development"
NEW_ID = OLD_ID + "_20260910"
RAW = Path("/tmp/lgfv-exp015-sources") / (OLD_ID + ".retrieved_20260910.html")
EXPECTED_RAW = "2d13b660ee1b469483ca81f79e7843140cce78814e8fc77b7f22c6aa7acb9550"
EXPECTED_TEXT = "c70b2a1924488b4fd503b9bad3e0ce3c3dbdb999a1144d362779b295fb159747"


def main():
    raw = RAW.read_bytes()
    text = html_to_text(raw)
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_RAW
    assert hashlib.sha256(text.encode()).hexdigest() == EXPECTED_TEXT
    assert "发布时间：2026-08-03 10:54:43" in text
    with (ROOT / "data/validation/probability_validation_source_manifest.csv").open() as handle:
        old = next(row for row in csv.DictReader(handle) if row["document_id"] == OLD_ID)
    source = dict(old)
    source.update(document_id=NEW_ID, document_date="2026-08-03", retrieval_date="2026-09-10",
                  retrieved_bytes=str(len(raw)), sha256=EXPECTED_RAW,
                  source_text_sha256=EXPECTED_TEXT, raw_cache_filename=RAW.name,
                  cache_verification_status="new_dated_retrieval_raw_and_text_verified",
                  rights_note="Public government profile re-retrieved on 2026-09-10. Previous raw snapshot unavailable; old manifest retained unchanged. Metadata and evidence only; raw page not redistributed.")
    start = text.index(old["issuer_name"] + "（简称")
    geo_end = text.index(" 邮编：518048", start)
    owner_end = text.index(" 基础设施投资建设运营平台。", start)
    role_end = text.index("骨干国企之一。", start) + len("骨干国企之一。")
    excerpts = {"geography": text[start:geo_end], "owner": text[start:owner_end], "role": text[start:role_end]}
    for prefix, excerpt in excerpts.items():
        assert old["issuer_name"] in excerpt and excerpt in text
        assert "市属综合性投融资平台公司" in excerpt
    assert "市国资委的决策部署及要求" in excerpts["owner"]
    assert "地址：深圳市福田区福华一路大中华国际交易广场裙楼7楼" in excerpts["geography"]
    patch = {}
    for prefix, excerpt in excerpts.items():
        patch.update({f"{prefix}_document_id": NEW_ID, f"{prefix}_page": "1", f"{prefix}_supporting_text": excerpt})
    source_path = OUT / "renewed_source_manifest.csv"
    with source_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(source), lineterminator="\n")
        writer.writeheader()
        writer.writerow(source)
    (OUT / "crosswalk_evidence_patch.json").write_text(json.dumps(patch, ensure_ascii=False, indent=2) + "\n")
    with (ROOT / "data/validation/probability_validation_geography_scope_crosswalk.csv").open() as handle:
        previous = next(row for row in csv.DictReader(handle) if row["validation_unit_id"] == UNIT)
    renewed = {**previous, **patch}
    record = {
        "old_source_id": OLD_ID, "new_source_id": NEW_ID,
        "old_raw_snapshot_recovered": False,
        "old_raw_sha256": old["sha256"], "new_raw_sha256": EXPECTED_RAW,
        "old_text_sha256": old["source_text_sha256"], "new_text_sha256": EXPECTED_TEXT,
        "source_canonical_hash": canonical_row_hash(source),
        "crosswalk_canonical_hash": canonical_row_hash(renewed),
        "source_manifest_file_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        "evidence_patch_file_sha256": hashlib.sha256((OUT / "crosswalk_evidence_patch.json").read_bytes()).hexdigest(),
        "changed_fields": [field for field in previous if previous[field] != renewed[field]],
        "scope_or_outcome_decisions_changed": False,
        "publication_date_correction_on_new_record_only": [old["document_date"], source["document_date"]],
        "owner_evidence_limitation": "Municipal public status and SASAC oversight, not an ownership percentage or post-exit financing-function finding.",
    }
    (OUT / "source_review.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(record, ensure_ascii=False))


if __name__ == "__main__":
    main()
