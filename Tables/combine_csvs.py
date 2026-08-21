#!/usr/bin/env python3
"""
combine_csvs.py — Merge multiple CSV files into a single output CSV.

Usage:
    python combine_csvs.py file1.csv file2.csv file3.csv
    python combine_csvs.py *.csv
    python combine_csvs.py file1.csv file2.csv --output merged.csv
    python combine_csvs.py /path/to/folder/*.csv --output combined.csv --no-dedup-headers
"""

import csv
import sys
import argparse
from pathlib import Path


def combine_csvs(input_files: list[Path], output_file: Path, dedup_headers: bool = True) -> None:
    if not input_files:
        print("Error: No input files provided.", file=sys.stderr)
        sys.exit(1)

    header_written = False
    expected_header = None
    total_rows = 0

    with output_file.open("w", newline="", encoding="utf-8") as out_f:
        writer = None

        for csv_path in input_files:
            if not csv_path.exists():
                print(f"Warning: '{csv_path}' not found — skipping.", file=sys.stderr)
                continue
            if csv_path.resolve() == output_file.resolve():
                print(f"Warning: '{csv_path}' is the output file — skipping.", file=sys.stderr)
                continue

            with csv_path.open("r", newline="", encoding="utf-8-sig") as in_f:
                reader = csv.DictReader(in_f)

                if reader.fieldnames is None:
                    print(f"Warning: '{csv_path}' appears empty — skipping.", file=sys.stderr)
                    continue

                current_header = list(reader.fieldnames)

                # First file sets the canonical header
                if expected_header is None:
                    expected_header = current_header
                    writer = csv.DictWriter(out_f, fieldnames=expected_header, extrasaction="ignore")
                    writer.writeheader()
                    header_written = True
                    print(f"Header columns ({len(expected_header)}): {', '.join(expected_header)}")
                elif dedup_headers and current_header != expected_header:
                    print(
                        f"Warning: '{csv_path}' has different columns — "
                        "rows will be aligned to the first file's header.",
                        file=sys.stderr,
                    )

                rows_in_file = 0
                for row in reader:
                    writer.writerow(row)
                    rows_in_file += 1

                total_rows += rows_in_file
                print(f"  ✓ {csv_path.name}  ({rows_in_file} rows)")

    if not header_written:
        print("Error: No valid input files were processed.", file=sys.stderr)
        sys.exit(1)

    print(f"\nDone! {total_rows} total rows written to '{output_file}'.")


def main():
    parser = argparse.ArgumentParser(
        description="Combine multiple CSV files into one."
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="CSV files to combine (supports glob patterns when quoted).",
    )
    parser.add_argument(
        "--output", "-o",
        default="combined.csv",
        metavar="OUTPUT",
        help="Name of the output file (default: combined.csv).",
    )
    parser.add_argument(
        "--no-dedup-headers",
        action="store_false",
        dest="dedup_headers",
        help="Disable column-mismatch warnings.",
    )

    args = parser.parse_args()

    input_paths = [Path(f) for f in args.files]
    output_path = Path(args.output)

    print(f"Combining {len(input_paths)} file(s) → '{output_path}'\n")
    combine_csvs(input_paths, output_path, dedup_headers=args.dedup_headers)


if __name__ == "__main__":
    main()
