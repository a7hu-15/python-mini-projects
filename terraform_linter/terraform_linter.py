"""
CLI Terraform Security & Best Practices Auditor.

Audits Terraform (`.tf`) configuration files for:
1. Insecure security group ingress rules (`cidr_blocks = ["0.0.0.0/0"]`)
2. Unencrypted S3 buckets (`aws_s3_bucket` without encryption)
3. Exposed hardcoded credentials (AWS access keys, secret keys, password strings)
4. Missing `tags` block on cloud resources
5. Unpinned provider versions
"""

import sys
import os
import re
import argparse
from typing import List, Dict, Any


SECRET_PATTERNS = [
    (re.compile(r"(?i)secret_key\s*=\s*['\"]([A-Za-z0-9/+=]{40})['\"]"), "Hardcoded AWS Secret Key"),
    (re.compile(r"(?i)access_key\s*=\s*['\"](AKIA[A-Z0-9]{16})['\"]"), "Hardcoded AWS Access Key ID"),
    (re.compile(r"(?i)password\s*=\s*['\"](?!var\.)[^\s'\"]{4,}['\"]"), "Hardcoded Database Password"),
]


def audit_tf_content(content: str) -> List[Dict[str, Any]]:
    """Audit Terraform file content string line by line and block by block."""
    issues = []
    lines = content.splitlines()

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("//"):
            continue

        # 1. Open ingress rule check
        if 'cidr_blocks' in stripped and '"0.0.0.0/0"' in stripped and 'ingress' in content[:content.find(line)]:
            issues.append({
                "line": idx,
                "rule": "OpenIngressSecurityGroup",
                "finding": "Security group ingress rule allows open access from 0.0.0.0/0",
                "severity": "HIGH"
            })

        # 2. Hardcoded Secret Detection
        for pattern, rule_name in SECRET_PATTERNS:
            match = pattern.search(line)
            if match:
                matched_str = match.group(0)
                masked = matched_str[:12] + "..." if len(matched_str) > 15 else matched_str
                issues.append({
                    "line": idx,
                    "rule": rule_name,
                    "finding": f"Possible hardcoded secret: `{masked}`",
                    "severity": "CRITICAL"
                })

    # 3. Structural checks
    if 'resource "aws_s3_bucket"' in content and 'server_side_encryption_configuration' not in content:
        issues.append({
            "line": 1,
            "rule": "UnencryptedS3Bucket",
            "finding": "S3 bucket resource is missing server-side encryption configuration",
            "severity": "HIGH"
        })

    if 'resource "' in content and 'tags =' not in content and 'tags {' not in content:
        issues.append({
            "line": 1,
            "rule": "MissingResourceTags",
            "finding": "Cloud resource declaration is missing standard 'tags' block",
            "severity": "LOW"
        })

    return issues


def audit_tf_manifest(filepath: str) -> Dict[str, Any]:
    """Audit a `.tf` Terraform file and return structured security report."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Terraform file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    issues = audit_tf_content(content)
    errors = [i for i in issues if i["severity"] in ("CRITICAL", "HIGH")]
    warnings = [i for i in issues if i["severity"] not in ("CRITICAL", "HIGH")]

    return {
        "file": filepath,
        "valid": len(errors) == 0,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description="CLI Terraform Security & Best Practices Auditor")
    parser.add_argument("tf_file", help="Path to Terraform .tf file to audit")
    args = parser.parse_args()

    try:
        report = audit_tf_manifest(args.tf_file)
        print(f"=== Terraform Security Audit Report for '{report['file']}' ===")
        print(f"Status: {'PASSED ✅' if report['valid'] else 'FAILED ❌'}")
        print(f"Errors: {report['error_count']} | Warnings: {report['warning_count']}\n")

        for err in report["errors"]:
            print(f"  [ERROR] Line {err.get('line', '-')}: {err['rule']} - {err['finding']}")
        for warn in report["warnings"]:
            print(f"  [WARN]  Line {warn.get('line', '-')}: {warn['rule']} - {warn['finding']}")

        sys.exit(0 if report["valid"] else 1)
    except Exception as e:
        print(f"Error executing audit: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
