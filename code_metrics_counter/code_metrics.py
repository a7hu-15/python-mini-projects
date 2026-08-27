#!/usr/bin/env python3
"""
CLI Code Metrics & Lines of Code (LOC) Counter

Scans directory paths, measures source code lines, blank lines, and comment lines
categorized by file extension, and produces formatted reports or JSON output.
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Any, Optional

# Comment tokens by file extension
COMMENT_MAP = {
    ".py": ["#"],
    ".js": ["//", "/*"],
    ".ts": ["//", "/*"],
    ".jsx": ["//", "/*"],
    ".tsx": ["//", "/*"],
    ".java": ["//", "/*"],
    ".c": ["//", "/*"],
    ".cpp": ["//", "/*"],
    ".h": ["//", "/*"],
    ".hpp": ["//", "/*"],
    ".go": ["//", "/*"],
    ".rs": ["//", "/*"],
    ".sh": ["#"],
    ".bash": ["#"],
    ".yaml": ["#"],
    ".yml": ["#"],
    ".html": ["<!--"],
    ".css": ["/*"],
}

class CodeMetricsCounter:
    """Scans and analyzes source code metrics for directory trees."""

    def __init__(self, target_dir: str, exclude_dirs: Optional[List[str]] = None):
        self.target_dir = os.path.abspath(target_dir)
        self.exclude_dirs = exclude_dirs or [".git", "__pycache__", "node_modules", ".venv", "env", "build", "dist"]

    def analyze_file(self, file_path: str) -> Dict[str, int]:
        """Analyze a single file for total, code, comment, and blank lines."""
        ext = os.path.splitext(file_path)[1].lower()
        comment_prefixes = COMMENT_MAP.get(ext, ["#", "//"])

        total = 0
        blank = 0
        comment = 0
        code = 0

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                in_multiline_comment = False
                for line in f:
                    total += 1
                    stripped = line.strip()

                    if not stripped:
                        blank += 1
                        continue

                    # Multi-line comment simple tracking for /* ... */
                    if "/*" in comment_prefixes and "*/" not in comment_prefixes:
                        if "/*" in stripped and "*/" not in stripped:
                            in_multiline_comment = True
                            comment += 1
                            continue
                        if in_multiline_comment:
                            comment += 1
                            if "*/" in stripped:
                                in_multiline_comment = False
                            continue

                    # Single line comment
                    is_comment = False
                    for prefix in comment_prefixes:
                        if stripped.startswith(prefix):
                            comment += 1
                            is_comment = True
                            break

                    if not is_comment and not in_multiline_comment:
                        code += 1

        except OSError:
            pass

        return {
            "total": total,
            "code": code,
            "comment": comment,
            "blank": blank
        }

    def scan(self) -> Dict[str, Any]:
        """Recursively scan target directory and aggregate metrics by extension."""
        stats_by_ext: Dict[str, Dict[str, int]] = {}
        total_files = 0

        for root, dirs, files in os.walk(self.target_dir):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if not ext:
                    ext = "[no ext]"

                file_path = os.path.join(root, file)
                metrics = self.analyze_file(file_path)

                total_files += 1
                if ext not in stats_by_ext:
                    stats_by_ext[ext] = {"files": 0, "total": 0, "code": 0, "comment": 0, "blank": 0}

                stats_by_ext[ext]["files"] += 1
                stats_by_ext[ext]["total"] += metrics["total"]
                stats_by_ext[ext]["code"] += metrics["code"]
                stats_by_ext[ext]["comment"] += metrics["comment"]
                stats_by_ext[ext]["blank"] += metrics["blank"]

        # Aggregate global totals
        global_total = sum(s["total"] for s in stats_by_ext.values())
        global_code = sum(s["code"] for s in stats_by_ext.values())
        global_comment = sum(s["comment"] for s in stats_by_ext.values())
        global_blank = sum(s["blank"] for s in stats_by_ext.values())

        return {
            "target_directory": self.target_dir,
            "total_files": total_files,
            "summary": {
                "total_lines": global_total,
                "code_lines": global_code,
                "comment_lines": global_comment,
                "blank_lines": global_blank,
                "comment_ratio_pct": round((global_comment / global_total * 100), 2) if global_total > 0 else 0.0
            },
            "by_extension": stats_by_ext
        }

    @staticmethod
    def format_report(results: Dict[str, Any]) -> str:
        """Format scan results as a CLI ASCII report table."""
        lines = []
        lines.append(f"Code Metrics Report: {results['target_directory']}")
        lines.append(f"Total Files Scanned: {results['total_files']}\n")

        header = f"{'Extension':<12} | {'Files':<6} | {'Code':<8} | {'Comments':<8} | {'Blank':<8} | {'Total':<8}"
        sep = "-" * len(header)
        lines.append(header)
        lines.append(sep)

        for ext, s in sorted(results["by_extension"].items(), key=lambda x: x[1]["code"], reverse=True):
            lines.append(f"{ext:<12} | {s['files']:<6} | {s['code']:<8} | {s['comment']:<8} | {s['blank']:<8} | {s['total']:<8}")

        lines.append(sep)
        summary = results["summary"]
        lines.append(
            f"{'TOTALS':<12} | {results['total_files']:<6} | {summary['code_lines']:<8} | "
            f"{summary['comment_lines']:<8} | {summary['blank_lines']:<8} | {summary['total_lines']:<8}"
        )
        lines.append(f"\nComment Density: {summary['comment_ratio_pct']}%")
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze Code Metrics & Lines of Code (LOC) for source repositories.")
    parser.add_argument("path", nargs="?", default=".", help="Target directory path to scan (default: current dir)")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--exclude", nargs="*", help="Directories to exclude from scanning")

    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    counter = CodeMetricsCounter(args.path, exclude_dirs=args.exclude)
    results = counter.scan()

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(counter.format_report(results))

if __name__ == "__main__":
    main()
