"""Recover cited caches without changing their registered hashes or raw inputs."""

import csv
import hashlib
import json
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
CACHE = Path("/tmp/lgfv-exp015-sources")
LOCAL = Path("/Users/shunyuhao/Documents/LGFV/data")
NATIVE_PDFTOTEXT = Path("/Users/shunyuhao/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/bin/pdftotext")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def recover(row):
    result = {"document_id": row["document_id"], "raw_status": "missing", "text_status": "missing"}
    try:
        raw_target = CACHE / row["raw_cache_filename"]
        raw = None
        for source in [raw_target, *LOCAL.rglob(row["raw_cache_filename"])]:
            if source.is_file():
                payload = source.read_bytes()
                if digest(payload) == row["sha256"]:
                    raw = payload
                    result["raw_origin"] = str(source)
                    break
        if raw is None:
            with tempfile.TemporaryDirectory() as tmp:
                download = Path(tmp) / "source"
                command = ["curl", "--fail", "--location", "--silent", "--show-error", "--max-time", "40", "--output", str(download), row["download_url"]]
                proc = subprocess.run(command, capture_output=True, text=True)
                if proc.returncode != 0:
                    result["download_error"] = proc.stderr[:500]
                    return result
                payload = download.read_bytes()
                result["retrieved_raw_sha256"] = digest(payload)
                if digest(payload) != row["sha256"]:
                    result["raw_status"] = "retrieved_hash_mismatch"
                    return result
                raw = payload
                result["raw_origin"] = row["download_url"]
        if not raw_target.exists():
            raw_target.write_bytes(raw)
        elif digest(raw_target.read_bytes()) != row["sha256"]:
            raise ValueError("existing cache differs; refusing overwrite")
        result["raw_status"] = "verified"
        text_name = row["text_cache_filename"]
        if not text_name:
            result["text_status"] = "verify_html_in_validator"
            return result
        text_target = CACHE / text_name
        text = None
        for source in [text_target, *LOCAL.rglob(text_name)]:
            if source.is_file():
                payload = source.read_bytes()
                if digest(payload) == row["source_text_sha256"]:
                    text = payload
                    result["text_origin"] = str(source)
                    break
        if text is None:
            if row["document_id"] == "web_guiyang_2022_midyear_bond_report":
                import pdfplumber
                with pdfplumber.open(raw_target) as pdf:
                    chunks = []
                    for page in pdf.pages:
                        value = (page.extract_text() or "").replace("\r\n", "\n").replace("\r", "\n")
                        chunks.append("\n".join(line.rstrip() for line in value.split("\n")).strip() + "\n\f")
                text = "".join(chunks).encode()
                result["text_origin"] = "pdfplumber normalized complete pages"
            else:
                for binary in (str(NATIVE_PDFTOTEXT), "pdftotext"):
                    for options in (["-layout"], []):
                        proc = subprocess.run([binary, *options, str(raw_target), "-"], capture_output=True)
                        if proc.returncode == 0 and digest(proc.stdout) == row["source_text_sha256"]:
                            text = proc.stdout
                            result["text_origin"] = binary + " " + " ".join(options)
                            break
                    if text is not None:
                        break
                if text is None and row["extraction_profile"] == "pdfplumber-0.11.10-layout-x2-y3":
                    import pdfplumber
                    with pdfplumber.open(raw_target) as pdf:
                        chunks = [page.extract_text(layout=True, x_tolerance=2, y_tolerance=3) or "" for page in pdf.pages]
                    for separator in ("\f", "\n\f\n", "\n\f"):
                        for ending in ("", "\f", "\n", "\n\f"):
                            payload = (separator.join(chunks) + ending).encode()
                            if digest(payload) == row["source_text_sha256"]:
                                text = payload
                                result["text_origin"] = f"pdfplumber {pdfplumber.__version__} layout=True x_tolerance=2 y_tolerance=3 separator={separator!r} ending={ending!r}"
                                break
                        if text is not None:
                            break
        if text is None or digest(text) != row["source_text_sha256"]:
            result["text_status"] = "extraction_hash_unrecovered"
            if text is not None:
                result["retrieved_text_sha256"] = digest(text)
            return result
        if not text_target.exists():
            text_target.write_bytes(text)
        elif digest(text_target.read_bytes()) != row["source_text_sha256"]:
            raise ValueError("existing text differs; refusing overwrite")
        result["text_status"] = "verified"
    except Exception as error:
        result["error"] = str(error)
    return result


def main():
    CACHE.mkdir(exist_ok=True)
    crosswalk = rows(ROOT / "data/validation/probability_validation_geography_scope_crosswalk.csv")
    used = {(row["validation_unit_id"], row[f"{prefix}_document_id"]) for row in crosswalk for prefix in ("identity", "geography", "owner", "role")}
    sources = [row for row in rows(ROOT / "data/validation/probability_validation_source_manifest.csv") if (row["validation_unit_id"], row["document_id"]) in used]
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(recover, sources))
    report = {"sources": len(sources), "results": results}
    attempt = 1
    report_path = OUT / "cache_recovery.json"
    while report_path.exists():
        attempt += 1
        report_path = OUT / f"cache_recovery_attempt_{attempt}.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    incomplete = [row for row in results if row["raw_status"] != "verified" or row["text_status"] not in {"verified", "verify_html_in_validator"}]
    print(json.dumps({"sources": len(sources), "incomplete": incomplete}, ensure_ascii=False))
    return bool(incomplete)


if __name__ == "__main__":
    raise SystemExit(main())
