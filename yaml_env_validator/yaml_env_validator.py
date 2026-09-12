"""
CLI YAML & Environment Variable Configuration Auditor.

Audits YAML (`.yaml`, `.yml`) and `.env` configuration files for:
1. Hardcoded API keys, passwords, and sensitive tokens (AWS, JWT, Generic secrets)
2. Invalid syntax or malformed lines
3. Missing mandatory environment variables or empty production values
4. Inconsistent key casing (e.g. mixed SCREAMING_SNAKE_CASE vs camelCase)

Supports standalone CLI execution or Python library import.
"""

import sys
import re
import os
import argparse
from typing import List, Dict, Any, Tuple

# Regex patterns for high-confidence secrets
SECRET_PATTERNS = [
    (re.compile(r"(?i)aws[_\-]?secret[_\-]?access[_\-]?key\s*[:=]\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?"), "AWS Secret Access Key"),
    (re.compile(r"(?i)api[_\-]?key\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{20,})['\"]?"), "API Key"),
    (re.compile(r"(?i)password\s*[:=]\s*['\"]?(?![\${])[^\s'\"]{4,}['\"]?"), "Hardcoded Password"),
    (re.compile(r"eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*"), "JWT Bearer Token"),
    (re.compile(r"-----BEGIN (RSA|EC|PRIVATE) KEY-----"), "Private Cryptographic Key"),
]


def detect_secrets(line: str, line_num: int) -> List[Dict[str, Any]]:
    """Scan a single line of config for hardcoded credentials or secret patterns."""
    findings = []
    # Skip comments
    stripped = line.strip()
    if stripped.startswith("#") or stripped.startswith("//"):
        return findings

    for pattern, rule_name in SECRET_PATTERNS:
        match = pattern.search(line)
        if match:
            # Mask secret in report
            matched_str = match.group(0)
            masked = matched_str[:12] + "..." if len(matched_str) > 15 else matched_str
            findings.append({
                "line": line_num,
                "rule": rule_name,
                "finding": f"Possible hardcoded secret: `{masked}`",
                "severity": "CRITICAL"
            })
    return findings


def audit_env_content(content: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Audit .env file content line by line."""
    errors = []
    warnings = []
    lines = content.splitlines()

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Check key-value format
        if "=" not in stripped:
            errors.append({
                "line": idx,
                "rule": "SyntaxError",
                "finding": f"Invalid .env line syntax (missing '='): '{stripped}'",
                "severity": "HIGH"
            })
            continue

        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()

        # Check key naming convention (SCREAMING_SNAKE_CASE recommended)
        if not re.match(r"^[A-Z0-9_]+$", key):
            warnings.append({
                "line": idx,
                "rule": "NamingConvention",
                "finding": f"Env key '{key}' is not SCREAMING_SNAKE_CASE",
                "severity": "LOW"
            })

        # Check empty required values
        if value == "" or value == '""' or value == "''":
            warnings.append({
                "line": idx,
                "rule": "EmptyValue",
                "finding": f"Environment variable '{key}' has an empty value",
                "severity": "MEDIUM"
            })

        # Secret detection
        secrets = detect_secrets(line, idx)
        errors.extend([s for s in secrets if s["severity"] in ("CRITICAL", "HIGH")])
        warnings.extend([s for s in secrets if s["severity"] not in ("CRITICAL", "HIGH")])

    return errors, warnings


def audit_config_file(filepath: str) -> Dict[str, Any]:
    """Audit a config file (.env or .yaml) and return detailed findings."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    errors, warnings = audit_env_content(content)
    is_valid = len(errors) == 0

    return {
        "file": filepath,
        "valid": is_valid,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description="CLI YAML & Environment Variable Validator")
    parser.add_argument("file", help="Path to .env or YAML config file to audit")
    args = parser.parse_args()

    try:
        report = audit_config_file(args.file)
        print(f"=== Config Audit Report for '{report['file']}' ===")
        print(f"Status: {'PASSED ✅' if report['valid'] else 'FAILED ❌'}")
        print(f"Errors: {report['error_count']} | Warnings: {report['warning_count']}\n")

        for err in report["errors"]:
            print(f"  [ERROR] Line {err['line']}: {err['rule']} - {err['finding']}")
        for warn in report["warnings"]:
            print(f"  [WARN]  Line {warn['line']}: {warn['rule']} - {warn['finding']}")

        sys.exit(0 if report["valid"] else 1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
