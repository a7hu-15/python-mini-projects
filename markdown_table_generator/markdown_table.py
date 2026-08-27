#!/usr/bin/env python3
"""
Markdown Table Generator & CSV/JSON Converter

A CLI utility for converting CSV, JSON, or list structures into formatted
Markdown and ASCII tables with alignment, sorting, filtering, and export capabilities.
"""

import argparse
import csv
import json
import os
import sys
from typing import List, Dict, Any, Optional, Union

class MarkdownTableGenerator:
    """Generates Markdown and ASCII tables from structured tabular data."""

    def __init__(self, headers: List[str], rows: List[List[Any]]):
        self.headers = [str(h) for h in headers]
        self.rows = [[str(cell) for cell in row] for row in rows]

    @classmethod
    def from_csv_string(cls, csv_text: str, delimiter: str = ",") -> "MarkdownTableGenerator":
        """Construct generator from CSV string data."""
        lines = csv_text.strip().splitlines()
        if not lines:
            return cls([], [])
        reader = csv.reader(lines, delimiter=delimiter)
        data = list(reader)
        if not data:
            return cls([], [])
        return cls(headers=data[0], rows=data[1:])

    @classmethod
    def from_json_string(cls, json_text: str) -> "MarkdownTableGenerator":
        """Construct generator from JSON string containing array of objects."""
        data = json.loads(json_text)
        if not isinstance(data, list) or not data:
            return cls([], [])
        
        # Collect unique keys maintaining insertion order
        headers = []
        for obj in data:
            if isinstance(obj, dict):
                for key in obj.keys():
                    if key not in headers:
                        headers.append(key)
        
        rows = []
        for obj in data:
            if isinstance(obj, dict):
                row = [obj.get(h, "") for h in headers]
                rows.append(row)
        return cls(headers=headers, rows=rows)

    def filter_rows(self, column: str, value: str, case_sensitive: bool = False) -> None:
        """Filter rows where specified column contains given search value."""
        if column not in self.headers:
            return
        idx = self.headers.index(column)
        new_rows = []
        for row in self.rows:
            cell_val = row[idx] if idx < len(row) else ""
            if case_sensitive:
                if value in cell_val:
                    new_rows.append(row)
            else:
                if value.lower() in cell_val.lower():
                    new_rows.append(row)
        self.rows = new_rows

    def sort_rows(self, column: str, reverse: bool = False, numeric: bool = False) -> None:
        """Sort rows by a specified column name."""
        if column not in self.headers:
            return
        idx = self.headers.index(column)

        def key_func(row):
            val = row[idx] if idx < len(row) else ""
            if numeric:
                try:
                    return float(val)
                except ValueError:
                    return float('-inf')
            return val

        self.rows.sort(key=key_func, reverse=reverse)

    def to_markdown(self, align: Optional[Dict[str, str]] = None) -> str:
        """
        Generate GFM Markdown table.
        align can be a dict mapping column name -> 'left' | 'center' | 'right'
        """
        if not self.headers:
            return ""

        align = align or {}
        widths = [len(h) for h in self.headers]
        for row in self.rows:
            for i, cell in enumerate(row):
                if i < len(widths):
                    widths[i] = max(widths[i], len(str(cell)))
                else:
                    widths.append(len(str(cell)))

        # Header line
        header_cells = [self.headers[i].ljust(widths[i]) for i in range(len(self.headers))]
        header_line = "| " + " | ".join(header_cells) + " |"

        # Separator line
        sep_cells = []
        for i, h in enumerate(self.headers):
            col_align = align.get(h, "left").lower()
            w = max(3, widths[i])
            if col_align == "center":
                sep_cells.append(":" + "-" * (w - 2) + ":")
            elif col_align == "right":
                sep_cells.append("-" * (w - 1) + ":")
            else:
                sep_cells.append("-" * w)
        sep_line = "| " + " | ".join(sep_cells) + " |"

        # Data lines
        data_lines = []
        for row in self.rows:
            row_cells = []
            for i in range(len(self.headers)):
                cell_val = row[i] if i < len(row) else ""
                col_align = align.get(self.headers[i], "left").lower()
                w = widths[i]
                if col_align == "right":
                    row_cells.append(cell_val.rjust(w))
                elif col_align == "center":
                    row_cells.append(cell_val.center(w))
                else:
                    row_cells.append(cell_val.ljust(w))
            data_lines.append("| " + " | ".join(row_cells) + " |")

        return "\n".join([header_line, sep_line] + data_lines)


def main():
    parser = argparse.ArgumentParser(description="Convert CSV/JSON data into Markdown tables.")
    parser.add_argument("input_file", nargs="?", help="Path to input CSV or JSON file")
    parser.add_argument("--format", choices=["csv", "json"], help="Input format (autodetected if omitted)")
    parser.add_argument("--sort", help="Column name to sort by")
    parser.add_argument("--reverse", action="store_true", help="Reverse sort order")
    parser.add_argument("--numeric", action="store_true", help="Numeric sort")
    parser.add_argument("--filter-col", help="Column name to filter")
    parser.add_argument("--filter-val", help="Value to match for filter")
    parser.add_argument("--output", "-o", help="Output file path (prints to stdout if omitted)")

    args = parser.parse_args()

    if not args.input_file:
        # Provide interactive demo
        sample_csv = "Name,Age,Role,Salary\nAlice,30,Engineer,95000\nBob,25,Designer,72000\nCharlie,35,Manager,115000"
        generator = MarkdownTableGenerator.from_csv_string(sample_csv)
        print("--- Demo Markdown Table Output ---")
        print(generator.to_markdown())
        return

    if not os.path.exists(args.input_file):
        print(f"Error: File '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(args.input_file, "r", encoding="utf-8") as f:
        content = f.read()

    fmt = args.format
    if not fmt:
        fmt = "json" if args.input_file.endswith(".json") else "csv"

    if fmt == "json":
        gen = MarkdownTableGenerator.from_json_string(content)
    else:
        gen = MarkdownTableGenerator.from_csv_string(content)

    if args.filter_col and args.filter_val:
        gen.filter_rows(args.filter_col, args.filter_val)

    if args.sort:
        gen.sort_rows(args.sort, reverse=args.reverse, numeric=args.numeric)

    table_md = gen.to_markdown()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(table_md + "\n")
        print(f"Markdown table successfully written to {args.output}")
    else:
        print(table_md)

if __name__ == "__main__":
    main()
