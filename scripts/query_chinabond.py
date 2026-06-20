#!/usr/bin/env python3
"""Query ChinaBond's public bond metadata endpoint.

This script is for pilot source discovery. It queries bond abbreviations and
prints a compact CSV-like table to stdout. It does not assign exit labels.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request


ENDPOINT = "https://www.chinabond.com.cn/cbiw/GetBase/bondSimpleQueryForChinese"


def query(keyword: str, page_size: int) -> dict:
    payload = {
        "bondCode": "",
        "bondNameAbbr": keyword,
        "bondFeatureNo": "",
        "issueDate": "",
        "sortInfo": [],
        "pageSize": page_size,
        "pageNum": 1,
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Referer": "https://www.chinabond.com.cn/xxwsy/gtyw/gtyw_cxgz/cxgz_zqxx/",
            "User-Agent": "Mozilla/5.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("keywords", nargs="+")
    parser.add_argument("--page-size", type=int, default=20)
    args = parser.parse_args()

    print("keyword,bond_name_abbr,bond_code,issuer,issue_date,bond_feature,bond_rating,issuer_rating")
    for keyword in args.keywords:
        result = query(keyword, args.page_size)
        for item in result.get("data", {}).get("list", []):
            if item.get("bondNameAbbr") == "合计":
                continue
            fields = [
                keyword,
                item.get("bondNameAbbr") or "",
                item.get("bondCode") or "",
                item.get("issuer") or "",
                item.get("issueDate") or "",
                item.get("bondFeatureDesc") or "",
                item.get("bondCredRateDesc") or "",
                item.get("subjCredRateDesc") or "",
            ]
            print(",".join(str(x).replace(",", " ") for x in fields))
    return 0


if __name__ == "__main__":
    sys.exit(main())
