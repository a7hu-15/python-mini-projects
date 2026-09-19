#!/usr/bin/env python3
"""
CLI Nginx & Web Server Config Security Linter.

Audits Nginx configuration files (.conf) for security risks, weak TLS settings,
missing security headers, unsafe root/alias directives, and directory listing vulnerabilities.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Union


def audit_nginx_config(config_input: Union[str, Path]) -> Dict[str, Any]:
    """
    Audits Nginx config string or file path for security issues and anti-patterns.
    """
    if isinstance(config_input, Path) or (isinstance(config_input, str) and "\n" not in config_input and Path(config_input).is_file()):
        file_path = Path(config_input)
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            return {
                "valid": False,
                "file": str(file_path),
                "errors": [f"Failed to read file: {e}"],
                "warnings": [],
                "recommendations": []
            }
        file_name = str(file_path)
    else:
        content = str(config_input)
        file_name = "<inline_config>"

    errors: List[str] = []
    warnings: List[str] = []
    recommendations: List[str] = []

    lines = content.splitlines()

    # 1. Server tokens check
    if re.search(r"server_tokens\s+on\s*;", content, re.IGNORECASE):
        errors.append("`server_tokens on;` is enabled. Set `server_tokens off;` to prevent server version exposure.")

    # 2. Directory index / autoindex check
    if re.search(r"autoindex\s+on\s*;", content, re.IGNORECASE):
        errors.append("`autoindex on;` is enabled. Disable directory index listing (`autoindex off;`) to avoid data leakage.")

    # 3. Weak SSL/TLS Protocols
    insecure_protocols = {"SSLV2", "SSLV3", "TLSV1", "TLSV1.1"}
    ssl_proto_match = re.search(r"ssl_protocols\s+([^;]+);", content, re.IGNORECASE)
    if ssl_proto_match:
        protocols_str = ssl_proto_match.group(1)
        tokens = [p.strip().upper() for p in protocols_str.split()]
        found_insecure = [p for p in tokens if p in insecure_protocols]
        if found_insecure:
            errors.append(f"Insecure SSL/TLS protocols detected: {', '.join(found_insecure)}. Use `TLSv1.2 TLSv1.3` only.")

    # 4. Missing Security Headers
    security_headers = {
        "X-Frame-Options": r"add_header\s+X-Frame-Options",
        "X-Content-Type-Options": r"add_header\s+X-Content-Type-Options",
        "Content-Security-Policy": r"add_header\s+Content-Security-Policy",
        "Strict-Transport-Security": r"add_header\s+Strict-Transport-Security",
        "Referrer-Policy": r"add_header\s+Referrer-Policy",
    }

    for header_name, pattern in security_headers.items():
        if not re.search(pattern, content, re.IGNORECASE):
            warnings.append(f"Missing security header: `{header_name}`.")

    # 5. SSL client certificate verification turned off explicitly
    if re.search(r"ssl_verify_client\s+off\s*;", content, re.IGNORECASE):
        warnings.append("`ssl_verify_client off;` is explicitly defined. Ensure mTLS / client auth is not required.")

    # 6. Alias trailing slash mismatch check
    # Location ending with / with alias not ending with /
    alias_matches = re.finditer(r"location\s+([^\s{]+)\s*\{[^}]*alias\s+([^;]+);", content, re.DOTALL | re.IGNORECASE)
    for m in alias_matches:
        loc = m.group(1).strip()
        alias = m.group(2).strip()
        if loc.endswith("/") and not alias.endswith("/"):
            errors.append(f"Location `{loc}` has trailing slash but `alias {alias}` does not. This causes path traversal vulnerabilities.")

    # 7. SSL session caching recommendation
    if "ssl_certificate" in content.lower() and "ssl_session_cache" not in content.lower():
        recommendations.append("HTTPS is configured without `ssl_session_cache`. Add `ssl_session_cache shared:SSL:10m;` for better performance.")

    # 8. Check gzip on sensitive endpoints
    if re.search(r"gzip\s+on\s*;", content, re.IGNORECASE) and "ssl_certificate" in content.lower():
        recommendations.append("Gzip compression enabled over SSL/TLS. Beware of BREACH side-channel attacks on sensitive endpoints.")

    valid = len(errors) == 0

    return {
        "valid": valid,
        "file": file_name,
        "errors": errors,
        "warnings": warnings,
        "recommendations": recommendations,
    }


def main():
    parser = argparse.ArgumentParser(description="CLI Nginx & Web Server Security Linter")
    parser.add_argument("config_file", type=str, help="Path to Nginx config file (.conf)")
    parser.add_argument("--json", action="store_true", help="Output audit report in JSON format")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")

    args = parser.parse_args()

    report = audit_nginx_config(Path(args.config_file))

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"\n🔍 Nginx Config Audit: {report['file']}")
        print("=" * 60)
        print(f"Status: {'✅ PASSED' if report['valid'] else '❌ FAILED'}\n")

        if report["errors"]:
            print("🚨 ERRORS:")
            for err in report["errors"]:
                print(f"  - {err}")
            print()

        if report["warnings"]:
            print("⚠️ WARNINGS:")
            for warn in report["warnings"]:
                print(f"  - {warn}")
            print()

        if report["recommendations"]:
            print("💡 RECOMMENDATIONS:")
            for rec in report["recommendations"]:
                print(f"  - {rec}")
            print()

    if not report["valid"] or (args.strict and report["warnings"]):
        sys.exit(1)


if __name__ == "__main__":
    main()
