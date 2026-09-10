#!/usr/bin/env python3
"""Build or check the case register without changing original outcome records."""

from __future__ import annotations

import argparse
import csv
import io

from human_confirmation import REGISTER, confirmed_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows = confirmed_rows()
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    expected = output.getvalue()
    if args.check:
        if REGISTER.read_text(encoding="utf-8") != expected:
            raise SystemExit("human_confirmation_register=stale_or_invalid")
    else:
        REGISTER.write_text(expected, encoding="utf-8")
    print(f"human_checked_reference_cases={len(rows)}")
    print("basis=author_report; label_revisions=0; blind_double_coding=not_documented")


if __name__ == "__main__":
    main()
