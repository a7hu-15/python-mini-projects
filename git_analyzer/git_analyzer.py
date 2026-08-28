"""
CLI Git Commit History & Contributor Statistics Analyzer in Python.

Parses git repository logs to compile author statistics, commit frequencies,
line additions/deletions (churn), file modification hotspots, and peak activity timing.

Supports output export formats:
- Plain Text / ASCII Summary
- JSON Summary
- Markdown Table Report
"""

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from typing import Dict, List, Any, Optional


class GitLogParser:
    """Parses raw git log output into structured statistics."""

    def __init__(self):
        self.authors: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"commits": 0, "additions": 0, "deletions": 0}
        )
        self.file_churn: Dict[str, int] = defaultdict(int)
        self.day_activity: Dict[str, int] = defaultdict(int)
        self.total_commits = 0

    def parse_log(self, log_output: str) -> Dict[str, Any]:
        """
        Parse raw git log text formatted with numstat and author info.

        Expected record header format:
        COMMIT|<author_name>|<author_email>|<date_iso>|<day_of_week>
        followed by numstat lines:
        <added> \t <deleted> \t <filename>
        """
        current_author = None
        lines = log_output.strip().splitlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("COMMIT|"):
                parts = line.split("|")
                if len(parts) >= 5:
                    current_author = parts[1].strip()
                    day_of_week = parts[4].strip()
                    self.authors[current_author]["commits"] += 1
                    self.day_activity[day_of_week] += 1
                    self.total_commits += 1
            elif current_author and "\t" in line:
                parts = line.split("\t")
                if len(parts) == 3:
                    added_str, deleted_str, filename = parts[0], parts[1], parts[2]
                    added = int(added_str) if added_str.isdigit() else 0
                    deleted = int(deleted_str) if deleted_str.isdigit() else 0

                    self.authors[current_author]["additions"] += added
                    self.authors[current_author]["deletions"] += deleted
                    self.file_churn[filename] += 1

        return self.get_summary()

    def get_summary(self) -> Dict[str, Any]:
        """Compile and return structured statistics dictionary."""
        sorted_authors = sorted(
            [{"name": k, **v} for k, v in self.authors.items()],
            key=lambda x: x["commits"],
            reverse=True,
        )

        top_files = sorted(
            [{"file": k, "changes": v} for k, v in self.file_churn.items()],
            key=lambda x: x["changes"],
            reverse=True,
        )[:10]

        return {
            "total_commits": self.total_commits,
            "total_authors": len(self.authors),
            "authors": sorted_authors,
            "top_files": top_files,
            "day_activity": dict(self.day_activity),
        }

    def format_markdown(self) -> str:
        """Format summary into Markdown report."""
        summary = self.get_summary()
        md = []
        md.append("# 📊 Git Repository Analytics Report\n")
        md.append(f"- **Total Commits**: {summary['total_commits']}")
        md.append(f"- **Total Contributors**: {summary['total_authors']}\n")

        md.append("## 👥 Contributor Statistics\n")
        md.append("| Author | Commits | Additions | Deletions | Net Lines |")
        md.append("| :--- | :---: | :---: | :---: | :---: |")
        for a in summary["authors"]:
            net = a["additions"] - a["deletions"]
            md.append(f"| {a['name']} | {a['commits']} | +{a['additions']} | -{a['deletions']} | {net:+d} |")

        if summary["top_files"]:
            md.append("\n## 🔥 Top Changed Files (Hotspots)\n")
            md.append("| File Path | Revisions |")
            md.append("| :--- | :---: |")
            for f in summary["top_files"]:
                md.append(f"| `{f['file']}` | {f['changes']} |")

        return "\n".join(md)


def run_git_log(repo_path: str = ".") -> str:
    """Execute git command to retrieve log data for parsing."""
    cmd = [
        "git",
        "-C",
        repo_path,
        "log",
        "--format=COMMIT|%an|%ae|%ad|%aA",
        "--numstat",
        "--date=iso",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description="CLI Git Repository & Contributor Statistics Analyzer")
    parser.add_argument("--repo", default=".", help="Path to Git repository target (default: .)")
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text", help="Output format")
    args = parser.parse_args()

    try:
        raw_log = run_git_log(args.repo)
        parser_obj = GitLogParser()
        summary = parser_obj.parse_log(raw_log)

        if args.format == "json":
            print(json.dumps(summary, indent=2))
        elif args.format == "markdown":
            print(parser_obj.format_markdown())
        else:
            print("=== Git Repository Analytics ===")
            print(f"Total Commits: {summary['total_commits']}")
            print(f"Total Contributors: {summary['total_authors']}\n")
            print("Contributors:")
            for a in summary["authors"]:
                print(f"  - {a['name']}: {a['commits']} commits (+{a['additions']}/-{a['deletions']})")
    except Exception as e:
        print(f"Error analyzing git repository: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
