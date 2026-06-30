#!/usr/bin/env python3
"""Search Shanghai Clearing static disclosure pages for issuer names.

This script is a source-discovery helper. It reads public list pages in
selected disclosure categories and prints matched announcement pages. It does
not download documents or assign labels.
"""

from __future__ import annotations

import argparse
import csv
import html
import re
import sys
import time
import urllib.request
from urllib.parse import urljoin


BASE = "https://www.shclearing.com.cn/xxpl/fxpl/"
CATEGORIES = ("mtn", "cp", "scp", "ppn")
ITEM_RE = re.compile(
    r'<a href="(?P<href>[^"]+)" target="_blank">\s*<p>\s*(?P<title>.*?)\s*</p>\s*<span>\s*(?P<date>.*?)\s*</span>',
    re.S,
)


def page_url(category: str, page_index: int) -> str:
    suffix = "index.html" if page_index == 0 else f"index_{page_index}.html"
    return urljoin(BASE, f"{category}/{suffix}")


def fetch(url: str, timeout: float) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def normalize(text: str) -> str:
    text = re.sub(r"<.*?>", "", text, flags=re.S)
    return re.sub(r"\s+", "", html.unescape(text))


def iter_items(category: str, pages: int, sleep: float, timeout: float):
    for page_index in range(pages):
        url = page_url(category, page_index)
        try:
            text = fetch(url, timeout)
        except Exception as exc:  # pragma: no cover - network helper
            print(f"warning: failed {url}: {exc}", file=sys.stderr)
            continue
        for match in ITEM_RE.finditer(text):
            title = normalize(match.group("title"))
            date = normalize(match.group("date"))
            href = match.group("href")
            yield category, date, title, urljoin(url, href)
        if sleep:
            time.sleep(sleep)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("terms", nargs="+", help="Issuer names or keywords to match")
    parser.add_argument("--categories", default=",".join(CATEGORIES))
    parser.add_argument("--pages", type=int, default=40)
    parser.add_argument("--sleep", type=float, default=0.1)
    parser.add_argument("--timeout", type=float, default=8)
    args = parser.parse_args()

    categories = [item.strip() for item in args.categories.split(",") if item.strip()]
    terms = [term.strip() for term in args.terms if term.strip()]

    writer = csv.writer(sys.stdout)
    writer.writerow(["term", "category", "publish_date", "title", "url"])
    seen: set[tuple[str, str, str]] = set()
    for category in categories:
        for category_name, date, title, url in iter_items(
            category, args.pages, args.sleep, args.timeout
        ):
            for term in terms:
                if term in title:
                    key = (term, title, url)
                    if key in seen:
                        continue
                    seen.add(key)
                    writer.writerow([term, category_name, date, title, url])
                    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
