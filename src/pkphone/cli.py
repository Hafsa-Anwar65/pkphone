"""Command line interface: pkphone 0300-1234567 or pkphone --csv leads.csv --column phone"""

from __future__ import annotations

import argparse
import csv
import sys

from .core import normalize, parse


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="pkphone", description="Normalize Pakistani phone numbers.")
    ap.add_argument("numbers", nargs="*", help="phone numbers to check")
    ap.add_argument("--format", "-f", default="e164", choices=["e164", "local", "whatsapp"])
    ap.add_argument("--csv", help="CSV file to clean")
    ap.add_argument("--column", default="phone", help="CSV column holding numbers")
    ap.add_argument("--out", help="output CSV path (default: stdout)")
    args = ap.parse_args(argv)

    if args.csv:
        with open(args.csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if args.column not in (reader.fieldnames or []):
                print(f"column '{args.column}' not found", file=sys.stderr)
                return 2
            fields = list(reader.fieldnames) + ["phone_clean", "phone_valid"]
            out = open(args.out, "w", newline="", encoding="utf-8") if args.out else sys.stdout
            w = csv.DictWriter(out, fieldnames=fields)
            w.writeheader()
            for row in reader:
                clean = normalize(row[args.column] or "", args.format)
                row["phone_clean"] = clean or ""
                row["phone_valid"] = "yes" if clean else "no"
                w.writerow(row)
            if args.out:
                out.close()
        return 0

    if not args.numbers:
        ap.print_help()
        return 1

    for raw in args.numbers:
        p = parse(raw)
        if p is None:
            print(f"{raw!r:24} -> invalid")
        else:
            extra = p.operator or p.city or ""
            print(f"{raw!r:24} -> {getattr(p, args.format):16} {p.kind:9} {extra}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
