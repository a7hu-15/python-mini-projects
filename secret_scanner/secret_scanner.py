#!/usr/bin/env python3
"""
CLI Secret Scanner & Sensitive Data Detector

A zero-dependency Python CLI tool that scans codebases and files for leaked
API keys, credentials, tokens, and private keys using regular expression pattern matching.

Features:
- Detects AWS keys, GitHub tokens, Stripe API keys, OpenAI keys, Slack webhooks/tokens, RSA keys, JWTs, and Bearer tokens.
- Supports directory recursion with default and custom ignore patterns (.git, node_modules, .venv, binary files).
- Option to redact/mask discovered secrets for safe log output.
- Text (table format) and JSON export outputs.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class SecretRule:
    rule_id: str
    name: str
    pattern: str
    severity: str  # HIGH, MEDIUM, LOW

    def match(self, content: str) -> List[re.Match]:
        return list(re.finditer(self.pattern, content))


DEFAULT_RULES: List[SecretRule] = [
    SecretRule(
        rule_id="AWS-001",
        name="AWS Access Key ID",
        pattern=r"\b(AKIA|ASIA|ABIA|ACCA)[0-9A-Z]{16}\b",
        severity="HIGH",
    ),
    SecretRule(
        rule_id="AWS-002",
        name="AWS Secret Access Key Assignment",
        pattern=r"(?i)(aws_secret_access_key|aws_secret_key)\s*[:=]\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?",
        severity="HIGH",
    ),
    SecretRule(
        rule_id="GH-001",
        name="GitHub Personal Access Token",
        pattern=r"\b(ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{82})\b",
        severity="HIGH",
    ),
    SecretRule(
        rule_id="STRIPE-001",
        name="Stripe API Key",
        pattern=r"\b(sk_test_[0-9a-zA-Z]{24,34})\b",
        severity="HIGH",
    ),
    SecretRule(
        rule_id="OPENAI-001",
        name="OpenAI API Key",
        pattern=r"\b(sk-[a-zA-Z0-9]{32,48})\b",
        severity="HIGH",
    ),
    SecretRule(
        rule_id="SLACK-001",
        name="Slack Bot or Webhook Token",
        pattern=r"(xox[baprs]-[0-9a-zA-Z]{10,48}|https://hooks\.slack\.com/services/T[a-zA-Z0-9_]+/B[a-zA-Z0-9_]+/[a-zA-Z0-9_]+)",
        severity="HIGH",
    ),
    SecretRule(
        rule_id="KEY-001",
        name="RSA / Private Key Header",
        pattern=r"-----BEGIN\s+(EC|DSA|RSA|OPENSSH)?\s*PRIVATE KEY-----",
        severity="HIGH",
    ),
    SecretRule(
        rule_id="JWT-001",
        name="JSON Web Token (JWT)",
        pattern=r"\beyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*\b",
        severity="MEDIUM",
    ),
    SecretRule(
        rule_id="BEARER-001",
        name="Generic Bearer Token Assignment",
        pattern=r"(?i)bearer\s+([a-zA-Z0-9_\-\.=]{20,})",
        severity="MEDIUM",
    ),
]

DEFAULT_IGNORED_DIRS: Set[str] = {
    ".git",
    ".svn",
    ".hg",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".idea",
    ".vscode",
    "dist",
    "build",
}

DEFAULT_IGNORED_EXTENSIONS: Set[str] = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".svg",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".7z",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".pyc",
    ".pyo",
    ".bin",
    ".db",
    ".sqlite",
    ".woff",
    ".woff2",
}


@dataclass
class Finding:
    rule_id: str
    rule_name: str
    severity: str
    file_path: str
    line_number: int
    matched_text: str
    snippet: str

    def to_dict(self, mask: bool = False) -> Dict[str, str | int]:
        d = asdict(self)
        if mask:
            d["matched_text"] = mask_secret(self.matched_text)
            d["snippet"] = d["snippet"].replace(self.matched_text, mask_secret(self.matched_text))
        return d


def mask_secret(secret: str) -> str:
    """Mask sensitive string leaving only first 3 and last 3 characters visible."""
    if len(secret) <= 6:
        return "*" * len(secret)
    return secret[:3] + "*" * (len(secret) - 6) + secret[-3:]


class SecretScanner:
    """Core engine for scanning files and directories for secrets."""

    def __init__(
        self,
        rules: Optional[List[SecretRule]] = None,
        ignored_dirs: Optional[Set[str]] = None,
        ignored_exts: Optional[Set[str]] = None,
    ) -> None:
        self.rules = rules if rules is not None else DEFAULT_RULES
        self.ignored_dirs = ignored_dirs if ignored_dirs is not None else DEFAULT_IGNORED_DIRS
        self.ignored_exts = ignored_exts if ignored_exts is not None else DEFAULT_IGNORED_EXTENSIONS

    def scan_file(self, file_path: str | Path) -> List[Finding]:
        """Scan a single file for secret matches."""
        path = Path(file_path)
        if not path.is_file() or path.suffix.lower() in self.ignored_exts:
            return []

        findings: List[Finding] = []
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception:
            return []

        for line_idx, line in enumerate(lines, start=1):
            for rule in self.rules:
                for match in rule.match(line):
                    matched_str = match.group(0)
                    snippet = line.strip()
                    findings.append(
                        Finding(
                            rule_id=rule.rule_id,
                            rule_name=rule.name,
                            severity=rule.severity,
                            file_path=str(path),
                            line_number=line_idx,
                            matched_text=matched_str,
                            snippet=snippet,
                        )
                    )

        return findings

    def scan_directory(self, dir_path: str | Path) -> List[Finding]:
        """Recursively scan a directory for secret matches."""
        root_path = Path(dir_path)
        all_findings: List[Finding] = []

        if not root_path.exists():
            return []

        if root_path.is_file():
            return self.scan_file(root_path)

        for root, dirs, files in os.walk(root_path):
            # Prune ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs and not d.startswith(".")]

            for file in files:
                file_p = Path(root) / file
                all_findings.extend(self.scan_file(file_p))

        return all_findings


def format_text_report(findings: List[Finding], mask: bool = True) -> str:
    """Format findings list as a readable terminal text report."""
    if not findings:
        return "✅ No secrets or sensitive data detected!"

    lines = []
    lines.append(f"🚨 Found {len(findings)} potential secret(s):\n")
    lines.append(f"{'SEVERITY':<10} | {'RULE ID':<10} | {'FILE:LINE':<40} | {'SECRET':<25}")
    lines.append("-" * 90)

    for f in findings:
        loc = f"{f.file_path}:{f.line_number}"
        secret_disp = mask_secret(f.matched_text) if mask else f.matched_text
        if len(loc) > 40:
            loc = "..." + loc[-37:]
        lines.append(f"{f.severity:<10} | {f.rule_id:<10} | {loc:<40} | {secret_disp:<25}")
        lines.append(f"   └─ Snippet: {f.snippet}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI Secret & Sensitive Data Scanner")
    parser.add_argument("target", nargs="?", default=".", help="Path to file or directory to scan (default: current dir)")
    parser.add_argument("--json", action="store_true", help="Output findings as JSON")
    parser.add_argument("--unmask", action="store_true", help="Do not mask sensitive matches in output")
    parser.add_argument("--severity", choices=["HIGH", "MEDIUM", "LOW"], help="Filter findings by minimum severity")

    args = parser.parse_args()

    scanner = SecretScanner()
    findings = scanner.scan_directory(args.target)

    if args.severity:
        severities = ["LOW", "MEDIUM", "HIGH"]
        min_idx = severities.index(args.severity)
        findings = [f for f in findings if severities.index(f.severity) >= min_idx]

    mask = not args.unmask

    if args.json:
        out = [f.to_dict(mask=mask) for f in findings]
        print(json.dumps(out, indent=2))
    else:
        print(format_text_report(findings, mask=mask))

    if findings:
        sys.exit(1)


if __name__ == "__main__":
    main()
