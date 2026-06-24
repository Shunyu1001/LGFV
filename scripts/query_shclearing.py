#!/usr/bin/env python3
"""Query selected Shanghai Clearing disclosure endpoints.

This script is for source discovery. It does not assign labels.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.parse
import urllib.request


APP_ROOT = "https://www.shclearing.com.cn/shchapp/web/"
OUT = csv.writer(sys.stdout)


def join_values(values: object) -> str:
    if not values:
        return ""
    if isinstance(values, str):
        return values
    if isinstance(values, list):
        out: list[str] = []
        for value in values:
            if isinstance(value, str):
                out.append(value)
            elif isinstance(value, dict):
                out.extend(str(item) for item in value.values() if item)
            elif value:
                out.append(str(value))
        return ";".join(out)
    return str(values)


def post_json(endpoint: str, data: dict[str, object]) -> dict:
    payload = urllib.parse.urlencode(data, doseq=True).encode("utf-8")
    req = urllib.request.Request(
        APP_ROOT + endpoint,
        data=payload,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.shclearing.com.cn/sy/qwjs/",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def org_search(name: str, limit: int) -> None:
    result = post_json(
        "clientDisclosureQuery/orgSearch",
        {"orgName": name, "limit": limit, "start": 0},
    )
    OUT.writerow(["org_name", "org_id", "org_type", "used_name"])
    for item in result.get("root", []):
        org_type = join_values(item.get("orgType"))
        used_name = join_values(item.get("usedName"))
        OUT.writerow([item.get("orgFullName") or "", item.get("id") or "", org_type, used_name])


def bond_list(org_id: str, limit: int) -> None:
    result = post_json(
        "clientDisclosureQuery/queryBondFullNameByOrg",
        {"id": org_id, "limit": limit, "start": 0},
    )
    OUT.writerow(["bond_full_name", "publish_date"])
    seen: set[tuple[str, str]] = set()
    for item in result.get("root", []):
        row = (item.get("bondFullName") or "", item.get("docpubdate") or "")
        if row in seen:
            continue
        seen.add(row)
        OUT.writerow(row)


def bulletin_list(bond_name: str, limit: int) -> None:
    result = post_json(
        "clientDisclosureQuery/queryNewBulletinList",
        {"bondName": bond_name, "limit": limit, "start": 0},
    )
    OUT.writerow(["publish_date", "title", "url"])
    for item in result.get("root", []):
        OUT.writerow([item.get("publishDate") or "", item.get("title") or "", item.get("url") or ""])


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    org = sub.add_parser("org")
    org.add_argument("name")
    org.add_argument("--limit", type=int, default=10)

    bonds = sub.add_parser("bonds")
    bonds.add_argument("org_id")
    bonds.add_argument("--limit", type=int, default=20)

    bulletins = sub.add_parser("bulletins")
    bulletins.add_argument("bond_name")
    bulletins.add_argument("--limit", type=int, default=20)

    args = parser.parse_args()
    if args.command == "org":
        org_search(args.name, args.limit)
    elif args.command == "bonds":
        bond_list(args.org_id, args.limit)
    elif args.command == "bulletins":
        bulletin_list(args.bond_name, args.limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
