#!/usr/bin/env python3
"""
CLI Dependency & License Compliance Auditor
Parses project dependency specs (requirements.txt, pyproject.toml, package.json)
to audit for unpinned versions, insecure repository URLs, and restrictive licenses.
"""

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class AuditIssue:
    file: str
    package: str
    rule_id: str
    severity: str  # 'HIGH', 'MEDIUM', 'LOW', 'INFO'
    message: str


class DependencyAuditor:
    """Auditor for project dependency files."""

    RESTRICTIVE_LICENSES = {"GPL-2.0", "GPL-3.0", "AGPL-3.0", "SSPL"}
    KNOWN_DEPRECATED = {"urllib3-legacy", "python-dateutil-old", "request", "babel-core"}

    def audit_requirements_txt(self, content: str, filename: str) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Check unpinned/wildcard dependency
            pkg_name = re.split(r"[=<>]", line)[0].strip()

            if "http://" in line:
                issues.append(
                    AuditIssue(
                        file=filename,
                        package=pkg_name,
                        rule_id="DEP001",
                        severity="HIGH",
                        message="Insecure HTTP dependency source URL detected",
                    )
                )

            if "==" not in line and "~=" not in line and "===" not in line:
                issues.append(
                    AuditIssue(
                        file=filename,
                        package=pkg_name,
                        rule_id="DEP002",
                        severity="MEDIUM",
                        message="Unpinned dependency version (missing explicit '==' pin)",
                    )
                )

            if pkg_name.lower() in self.KNOWN_DEPRECATED:
                issues.append(
                    AuditIssue(
                        file=filename,
                        package=pkg_name,
                        rule_id="DEP003",
                        severity="HIGH",
                        message="Deprecated or unmaintained package detected",
                    )
                )

        return issues

    def audit_package_json(self, content: str, filename: str) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            return [
                AuditIssue(
                    file=filename,
                    package="N/A",
                    rule_id="DEP000",
                    severity="HIGH",
                    message=f"Invalid JSON syntax: {e}",
                )
            ]

        license_field = data.get("license", "UNKNOWN")
        if isinstance(license_field, str) and license_field in self.RESTRICTIVE_LICENSES:
            issues.append(
                AuditIssue(
                    file=filename,
                    package=data.get("name", "root"),
                    rule_id="LIC001",
                    severity="HIGH",
                    message=f"Package uses restrictive copyleft license: {license_field}",
                )
            )

        deps = data.get("dependencies", {})
        dev_deps = data.get("devDependencies", {})
        all_deps = {**deps, **dev_deps}

        for pkg, ver in all_deps.items():
            if ver in ("*", "latest") or ver.startswith("^") or ver.startswith("~"):
                issues.append(
                    AuditIssue(
                        file=filename,
                        package=pkg,
                        rule_id="DEP002",
                        severity="LOW",
                        message=f"Loose / unpinned npm version constraint: '{ver}'",
                    )
                )
            if pkg.lower() in self.KNOWN_DEPRECATED:
                issues.append(
                    AuditIssue(
                        file=filename,
                        package=pkg,
                        rule_id="DEP003",
                        severity="HIGH",
                        message="Deprecated npm package detected",
                    )
                )

        return issues

    def audit_file(self, filepath: Path) -> List[AuditIssue]:
        if not filepath.exists():
            return [
                AuditIssue(
                    file=str(filepath),
                    package="N/A",
                    rule_id="DEP000",
                    severity="HIGH",
                    message="File not found",
                )
            ]

        content = filepath.read_text(encoding="utf-8")
        name = filepath.name.lower()

        if "requirements" in name or name.endswith(".txt"):
            return self.audit_requirements_txt(content, filepath.name)
        elif name == "package.json":
            return self.audit_package_json(content, filepath.name)
        else:
            return self.audit_requirements_txt(content, filepath.name)


def main():
    parser = argparse.ArgumentParser(description="CLI Dependency & License Compliance Auditor")
    parser.add_argument("files", nargs="+", type=Path, help="Paths to dependency files (requirements.txt, package.json)")
    parser.add_argument("--json", action="store_true", help="Output audit results in JSON format")
    args = parser.parse_args()

    auditor = DependencyAuditor()
    all_issues = []

    for file_path in args.files:
        issues = auditor.audit_file(file_path)
        all_issues.extend(issues)

    if args.json:
        print(json.dumps([asdict(i) for i in all_issues], indent=2))
    else:
        if not all_issues:
            print("✅ All dependencies audited cleanly!")
            sys.exit(0)

        print(f"\n🔍 Audit Summary ({len(all_issues)} issues found):")
        for issue in all_issues:
            print(f"  [{issue['severity']:6s}] {issue['file']} -> {issue['package']} ({issue['rule_id']}): {issue['message']}")

    sys.exit(1 if all_issues else 0)


if __name__ == "__main__":
    main()
