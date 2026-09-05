"""
CLI Dockerfile Linter & Security Auditor.

Parses Dockerfiles and checks against container security best practices and optimization rules.
"""

import argparse
import re
import sys
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class LintViolation:
    rule_id: str
    severity: str  # 'ERROR', 'WARNING', 'INFO'
    line_number: int
    message: str
    line_content: str


class DockerfileLinter:
    """Linter engine for analyzing Dockerfiles."""

    SECRET_PATTERN = re.compile(
        r"(?i)(api[_-]?key|secret|password|passwd|token|aws[_-]?secret|access[_-]?key|private[_-]?key)\s*[:=]\s*['\"]?[A-Za-z0-9/+=_-]{8,}['\"]?"
    )

    def __init__(self):
        self.violations: List[LintViolation] = []

    def lint_content(self, content: str) -> List[LintViolation]:
        self.violations = []
        lines = content.splitlines()

        has_user = False
        has_healthcheck = False

        for idx, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            # Check DL002: Base image using latest or unpinned tag
            if line.startswith("FROM"):
                parts = line.split()
                if len(parts) >= 2:
                    image = parts[1]
                    if ":" not in image or image.endswith(":latest"):
                        self.violations.append(
                            LintViolation(
                                rule_id="DL002",
                                severity="WARNING",
                                line_number=idx,
                                message=f"Base image '{image}' uses ':latest' or unpinned version tag.",
                                line_content=raw_line,
                            )
                        )

            # Check DL001: USER directive tracking
            if line.startswith("USER") and not line.startswith("USER root"):
                has_user = True

            # Check DL005: HEALTHCHECK directive tracking
            if line.startswith("HEALTHCHECK"):
                has_healthcheck = True

            # Check DL004: Prefer COPY over ADD for local resources
            if line.startswith("ADD"):
                parts = line.split()
                if len(parts) >= 3 and not (parts[1].startswith("http://") or parts[1].startswith("https://")):
                    self.violations.append(
                        LintViolation(
                            rule_id="DL004",
                            severity="WARNING",
                            line_number=idx,
                            message="Use COPY instead of ADD for copying local files and directories.",
                            line_content=raw_line,
                        )
                    )

            # Check DL003: apt-get update without cleanup in same layer
            if "apt-get update" in line and "rm -rf /var/lib/apt/lists/*" not in line:
                self.violations.append(
                    LintViolation(
                        rule_id="DL003",
                        severity="WARNING",
                        line_number=idx,
                        message="'apt-get update' should be paired with 'rm -rf /var/lib/apt/lists/*' in the same RUN layer.",
                        line_content=raw_line,
                    )
                )

            # Check DL008: Using sudo inside RUN
            if line.startswith("RUN") and "sudo " in line:
                self.violations.append(
                    LintViolation(
                        rule_id="DL008",
                        severity="ERROR",
                        line_number=idx,
                        message="Avoid using 'sudo' in RUN instructions. Run commands as root directly or use appropriate permissions.",
                        line_content=raw_line,
                    )
                )

            # Check DL007: Hardcoded secrets in ENV or ARG
            if (line.startswith("ENV") or line.startswith("ARG")) and self.SECRET_PATTERN.search(line):
                self.violations.append(
                    LintViolation(
                        rule_id="DL007",
                        severity="ERROR",
                        line_number=idx,
                        message="Potential hardcoded secret or API credential detected in ENV/ARG directive.",
                        line_content=raw_line,
                    )
                )

        if not has_user:
            self.violations.append(
                LintViolation(
                    rule_id="DL001",
                    severity="ERROR",
                    line_number=len(lines),
                    message="Missing non-root USER instruction. Containers should not run as root by default.",
                    line_content="",
                )
            )

        if not has_healthcheck:
            self.violations.append(
                LintViolation(
                    rule_id="DL005",
                    severity="INFO",
                    line_number=len(lines),
                    message="Missing HEALTHCHECK instruction for container health monitoring.",
                    line_content="",
                )
            )

        return self.violations

    def lint_file(self, filepath: str) -> List[LintViolation]:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return self.lint_content(content)


def main():
    parser = argparse.ArgumentParser(description="CLI Dockerfile Security & Best Practices Linter")
    parser.add_argument("file", help="Path to Dockerfile")
    args = parser.parse_args()

    linter = DockerfileLinter()
    violations = linter.lint_file(args.file)

    if not violations:
        print("✅ Dockerfile passed all security and quality checks!")
        sys.exit(0)

    print(f"🔍 Found {len(violations)} issue(s) in {args.file}:\n")
    for v in violations:
        symbol = "❌" if v.severity == "ERROR" else ("⚠️" if v.severity == "WARNING" else "ℹ️")
        line_str = f"Line {v.line_number}: " if v.line_number > 0 else ""
        print(f"{symbol} [{v.severity}] [{v.rule_id}] {line_str}{v.message}")
        if v.line_content:
            print(f"   > {v.line_content.strip()}")

    errors = [v for v in violations if v.severity == "ERROR"]
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
