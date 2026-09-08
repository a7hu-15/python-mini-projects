#!/usr/bin/env python3
"""
CLI Shell Script Linter & Security Auditor
Parses Bash / Shell scripts to identify security risks, missing safety flags, unquoted variables, and anti-patterns.
"""

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class LintIssue:
    line_number: int
    rule_id: str
    severity: str  # 'HIGH', 'MEDIUM', 'LOW', 'INFO'
    message: str
    line_content: str


class ShellLinter:
    """Linter for Shell / Bash scripts."""

    def __init__(self, check_bashisms: bool = True):
        self.check_bashisms = check_bashisms

    def lint_content(self, content: str, filename: str = "script.sh") -> List[LintIssue]:
        issues: List[LintIssue] = []
        lines = content.splitlines()

        if not lines:
            issues.append(
                LintIssue(
                    line_number=1,
                    rule_id="SH001",
                    severity="MEDIUM",
                    message="Empty script file",
                    line_content="",
                )
            )
            return issues

        # Rule SH002: Check Shebang
        first_line = lines[0].strip()
        if not first_line.startswith("#!"):
            issues.append(
                LintIssue(
                    line_number=1,
                    rule_id="SH002",
                    severity="HIGH",
                    message="Missing shebang (e.g., #!/bin/bash or #!/usr/bin/env bash)",
                    line_content=first_line,
                )
            )

        # Safety mode check (set -e, set -u, set -o pipefail)
        has_set_e = any(re.search(r"\bset\s+-[^#]*e", line) for line in lines)
        has_pipefail = any("pipefail" in line for line in lines)

        if not has_set_e:
            issues.append(
                LintIssue(
                    line_number=1,
                    rule_id="SH003",
                    severity="MEDIUM",
                    message="Script does not enable exit-on-error ('set -e' or 'set -eo pipefail')",
                    line_content=first_line,
                )
            )

        if not has_pipefail:
            issues.append(
                LintIssue(
                    line_number=1,
                    rule_id="SH004",
                    severity="LOW",
                    message="Script does not set 'pipefail' (pipe failures may be ignored)",
                    line_content=first_line,
                )
            )

        # Line by line checks
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            # Skip pure comments
            if stripped.startswith("#"):
                continue

            # Rule SH005: Unchecked rm -rf with variable
            if re.search(r"\brm\s+-[a-zA-Z]*rf\b", line):
                if re.search(r"\$([A-Za-z0-9_]+|\{[A-Za-z0-9_]+\})", line):
                    issues.append(
                        LintIssue(
                            line_number=idx,
                            rule_id="SH005",
                            severity="HIGH",
                            message="Potentially dangerous 'rm -rf' with variable expansion. Ensure variable is non-empty.",
                            line_content=stripped,
                        )
                    )

            # Rule SH006: Dangerous eval usage
            if re.search(r"\beval\b", line):
                issues.append(
                    LintIssue(
                        line_number=idx,
                        rule_id="SH006",
                        severity="HIGH",
                        message="Use of 'eval' can lead to arbitrary code execution vulnerability",
                        line_content=stripped,
                    )
                )

            # Rule SH007: Unquoted variable expansion in cd or echo or paths
            if re.search(r"\bcd\s+\$[A-Za-z0-9_]+\b", line):
                issues.append(
                    LintIssue(
                        line_number=idx,
                        rule_id="SH007",
                        severity="MEDIUM",
                        message="Unquoted variable in 'cd' command; space in path will cause failure",
                        line_content=stripped,
                    )
                )

            # Rule SH008: Hardcoded secret assignment
            if re.search(r"\b[A-Za-z0-9_]*(PASSWORD|SECRET|API_KEY|PRIVATE_KEY|TOKEN)[A-Za-z0-9_]*\s*=\s*['\"][^'\"]+['\"]", line, re.IGNORECASE):
                issues.append(
                    LintIssue(
                        line_number=idx,
                        rule_id="SH008",
                        severity="HIGH",
                        message="Possible hardcoded secret or API key detected in script variable assignment",
                        line_content=stripped,
                    )
                )

            # Rule SH009: Backtick command substitution preference
            if re.search(r"`[^`]+`", line):
                issues.append(
                    LintIssue(
                        line_number=idx,
                        rule_id="SH009",
                        severity="LOW",
                        message="Legacy backticks used for command substitution; prefer $(...) syntax",
                        line_content=stripped,
                    )
                )

            # Rule SH010: Use of single-bracket test in bash script
            if self.check_bashisms and "bash" in first_line:
                if re.search(r"\bif\s+\[\s+[^\]]+\s+\]", line):
                    issues.append(
                        LintIssue(
                            line_number=idx,
                            rule_id="SH010",
                            severity="INFO",
                            message="Single bracket '[' test used in Bash script; consider using '[[' for improved safety",
                            line_content=stripped,
                        )
                    )

        return issues

    def lint_file(self, filepath: Path) -> List[LintIssue]:
        try:
            content = filepath.read_text(encoding="utf-8")
            return self.lint_content(content, filename=filepath.name)
        except Exception as e:
            return [
                LintIssue(
                    line_number=0,
                    rule_id="SH000",
                    severity="HIGH",
                    message=f"Failed to read file: {e}",
                    line_content="",
                )
            ]


def main():
    parser = argparse.ArgumentParser(description="CLI Shell Script Linter & Security Auditor")
    parser.add_argument("files", nargs="+", type=Path, help="Paths to shell scripts to audit")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument(
        "--min-severity",
        choices=["INFO", "LOW", "MEDIUM", "HIGH"],
        default="INFO",
        help="Minimum severity level to display",
    )
    args = parser.parse_args()

    severity_order = {"INFO": 1, "LOW": 2, "MEDIUM": 3, "HIGH": 4}
    min_level = severity_order[args.min_severity]

    linter = ShellLinter()
    all_results = {}
    total_issues = 0

    for file_path in args.files:
        issues = linter.lint_file(file_path)
        filtered = [i for i in issues if severity_order.get(i.severity, 1) >= min_level]
        if filtered:
            all_results[str(file_path)] = [asdict(i) for i in filtered]
            total_issues += len(filtered)

    if args.json:
        print(json.dumps(all_results, indent=2))
    else:
        if not all_results:
            print("✅ No shell linting issues detected!")
            sys.exit(0)

        for filepath, issue_list in all_results.items():
            print(f"\n📄 File: {filepath}")
            for issue in issue_list:
                sev = issue["severity"]
                print(f"  Line {issue['line_number']:3d} [{sev:6s}] ({issue['rule_id']}): {issue['message']}")
                if issue["line_content"]:
                    print(f"           > {issue['line_content']}")

        print(f"\nTotal issues found: {total_issues}")

    sys.exit(1 if total_issues > 0 else 0)


if __name__ == "__main__":
    main()
