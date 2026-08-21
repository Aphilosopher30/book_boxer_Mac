#!/usr/bin/env python3
"""
add_photo_column.py

Reads a CSV file, looks up each value in the "collection" column against
files in a given folder, and writes a new "photo" column containing the
matching file's path (or blank if no match is found).

Usage:
    python add_photo_column.py --csv <path/to/file.csv> --folder <path/to/photos>

Optional flags:
    --output <path/to/output.csv>   Where to save the result (default: overwrites input file)
    --recursive                     Search subfolders as well as the top-level folder
    --case-insensitive              Match filenames without regard to letter case
"""

import argparse
import csv
import os
import sys


def build_file_map(folder: str, recursive: bool, case_insensitive: bool) -> dict:
    """
    Walk the folder and return a dict mapping filename-without-extension
    (and optionally lowercased) → full file path.

    If two files share the same stem, the last one found wins and a
    warning is printed.
    """
    file_map = {}

    if recursive:
        walker = (
            (dirpath, filenames)
            for dirpath, _, filenames in os.walk(folder)
        )
    else:
        try:
            entries = os.listdir(folder)
        except FileNotFoundError:
            sys.exit(f"ERROR: Folder not found: {folder}")

        walker = [(folder, [e for e in entries if os.path.isfile(os.path.join(folder, e))])]

    for dirpath, filenames in walker:
        for filename in filenames:
            stem, _ = os.path.splitext(filename)
            key = stem.lower() if case_insensitive else stem
            full_path = os.path.join(dirpath, filename)

            if key in file_map:
                print(f"WARNING: Duplicate match for '{stem}' — "
                      f"keeping '{full_path}', ignoring '{file_map[key]}'")

            file_map[key] = full_path

    return file_map


def process_csv(csv_path: str, folder: str, output_path: str,
                recursive: bool, case_insensitive: bool) -> None:

    # ── Validate inputs ───────────────────────────────────────────────────────
    if not os.path.isfile(csv_path):
        sys.exit(f"ERROR: CSV file not found: {csv_path}")

    if not os.path.isdir(folder):
        sys.exit(f"ERROR: Photos folder not found: {folder}")

    # ── Build lookup map ──────────────────────────────────────────────────────
    print(f"Scanning folder: {folder}" + (" (recursive)" if recursive else ""))
    file_map = build_file_map(folder, recursive, case_insensitive)
    print(f"  → {len(file_map)} file(s) indexed.\n")

    # ── Read CSV ──────────────────────────────────────────────────────────────
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            sys.exit("ERROR: The CSV file appears to be empty.")

        if "collection" not in reader.fieldnames:
            sys.exit(
                f"ERROR: No 'collection' column found.\n"
                f"       Columns present: {', '.join(reader.fieldnames)}"
            )

        rows = list(reader)
        fieldnames = list(reader.fieldnames)

    # Add "photo" column if it doesn't already exist
    if "photo" not in fieldnames:
        fieldnames.append("photo")

    # ── Match & annotate ──────────────────────────────────────────────────────
    matched = 0
    for row in rows:
        collection_value = row.get("collection", "").strip()
        lookup_key = collection_value.lower() if case_insensitive else collection_value

        photo_path = file_map.get(lookup_key, "")
        row["photo"] = photo_path

        if photo_path:
            matched += 1

    print(f"Rows processed : {len(rows)}")
    print(f"Matches found  : {matched}")
    print(f"No match       : {len(rows) - matched}\n")

    # ── Write output ──────────────────────────────────────────────────────────
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Output saved to: {output_path}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Add a 'photo' column to a CSV by matching the 'collection' "
                    "column against filenames in a folder."
    )
    parser.add_argument("--csv",    required=True,  help="Path to the input CSV file")
    parser.add_argument("--folder", required=True,  help="Path to the folder containing photo files")
    parser.add_argument("--output", default=None,
                        help="Path for the output CSV (default: overwrites the input file)")
    parser.add_argument("--recursive",        action="store_true",
                        help="Search subfolders recursively")
    parser.add_argument("--case-insensitive", action="store_true",
                        help="Match filenames without regard to case")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    output = args.output if args.output else args.csv
    process_csv(
        csv_path=args.csv,
        folder=args.folder,
        output_path=output,
        recursive=args.recursive,
        case_insensitive=args.case_insensitive,
    )
