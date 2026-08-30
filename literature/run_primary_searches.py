#!/usr/bin/env python3
"""Run and preserve predeclared Crossref and OpenAlex literature searches."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import json
import pathlib
import platform
import time
import urllib.parse
import urllib.request

USER_AGENT = "LGFV-auditable-literature-search/1.0"


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.load(response)


def crossref_url(query: str, rows: int, mail_to: str | None) -> str:
    params = {
        "query.bibliographic": query,
        "rows": rows,
        "select": "DOI,title,author,published,container-title,type,URL,abstract",
    }
    if mail_to:
        params["mailto"] = mail_to
    return "https://api.crossref.org/works?" + urllib.parse.urlencode(params)


def openalex_url(query: str, rows: int) -> str:
    params = {"search": query, "per-page": rows}
    return "https://api.openalex.org/works?" + urllib.parse.urlencode(params)


def first(value, default=""):
    if isinstance(value, list):
        return value[0] if value else default
    return value if value is not None else default


def crossref_rows(item: dict, query: dict) -> dict:
    authors = []
    for author in item.get("author", []):
        name = " ".join(x for x in [author.get("given"), author.get("family")] if x)
        if name:
            authors.append(name)
    date_parts = first(item.get("published", {}).get("date-parts", []), [])
    return {
        "query_id": query["query_id"],
        "literature": query["literature"],
        "database": "crossref",
        "title": first(item.get("title")),
        "authors": "; ".join(authors),
        "year": first(date_parts),
        "venue": first(item.get("container-title")),
        "doi": item.get("DOI", ""),
        "record_url": item.get("URL", ""),
        "work_type": item.get("type", ""),
        "abstract": item.get("abstract", ""),
    }


def openalex_rows(item: dict, query: dict) -> dict:
    primary = item.get("primary_location") or {}
    source = primary.get("source") or {}
    return {
        "query_id": query["query_id"],
        "literature": query["literature"],
        "database": "openalex",
        "title": item.get("display_name", ""),
        "authors": "; ".join(
            entry.get("author", {}).get("display_name", "")
            for entry in item.get("authorships", [])
            if entry.get("author", {}).get("display_name")
        ),
        "year": item.get("publication_year", ""),
        "venue": source.get("display_name", ""),
        "doi": (item.get("doi") or "").removeprefix("https://doi.org/"),
        "record_url": primary.get("landing_page_url") or item.get("id", ""),
        "work_type": item.get("type", ""),
        "abstract": "",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    plan_path = pathlib.Path(args.plan)
    output = pathlib.Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    # JSON is a strict subset of YAML, so the predeclared `.yaml` plan remains
    # both YAML-compatible and readable without a non-standard Python module.
    plan = json.loads(plan_path.read_text())
    rows_per_query = int(plan["rows_per_query"])
    normalized = []
    requests = []

    for query in plan["queries"]:
        for database in plan["databases"]:
            if database == "crossref":
                url = crossref_url(query["query"], rows_per_query, plan.get("mail_to"))
            elif database == "openalex":
                url = openalex_url(query["query"], rows_per_query)
            else:
                raise ValueError(f"Unsupported database: {database}")

            retrieved_at = dt.datetime.now(dt.timezone.utc).isoformat()
            error = ""
            payload = None
            for attempt in range(2):
                try:
                    payload = fetch_json(url)
                    break
                except Exception as exc:  # preserve one permitted retry
                    error = f"{type(exc).__name__}: {exc}"
                    if attempt == 0:
                        time.sleep(2)
            requests.append(
                {
                    "query_id": query["query_id"],
                    "literature": query["literature"],
                    "database": database,
                    "query": query["query"],
                    "url": url,
                    "retrieved_at_utc": retrieved_at,
                    "status": "ok" if payload is not None else "error",
                    "error": error if payload is None else "",
                }
            )
            if payload is None:
                continue

            raw_path = output / f"{query['query_id']}_{database}.json.gz"
            with gzip.open(raw_path, "wt", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
            if database == "crossref":
                items = payload.get("message", {}).get("items", [])
                normalized.extend(crossref_rows(item, query) for item in items)
            else:
                items = payload.get("results", [])
                normalized.extend(openalex_rows(item, query) for item in items)

    fields = [
        "query_id", "literature", "database", "title", "authors", "year",
        "venue", "doi", "record_url", "work_type", "abstract",
    ]
    with (output / "candidates.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(normalized)
    with (output / "requests.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=requests[0].keys())
        writer.writeheader()
        writer.writerows(requests)
    manifest = {
        "experiment_id": plan["experiment_id"],
        "plan": str(plan_path),
        "python": platform.python_version(),
        "script_version": USER_AGENT.rsplit("/", 1)[-1],
        "requests": len(requests),
        "successful_requests": sum(row["status"] == "ok" for row in requests),
        "candidate_rows": len(normalized),
        "completed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
