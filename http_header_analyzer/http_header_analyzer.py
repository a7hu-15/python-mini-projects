#!/usr/bin/env python3
"""
HTTP Security Header Analyzer

A CLI tool and library for auditing HTTP response headers against web security best practices
(OWASP recommendations, HSTS, CSP, X-Frame-Options, Referrer-Policy, etc.).
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List, Tuple

# Security header evaluation definitions
SECURITY_CHECKS: Dict[str, Dict[str, Any]] = {
    "Strict-Transport-Security": {
        "title": "HTTP Strict Transport Security (HSTS)",
        "weight": 20,
        "recommendation": "Set 'Strict-Transport-Security: max-age=31536000; includeSubDomains; preload'",
    },
    "Content-Security-Policy": {
        "title": "Content Security Policy (CSP)",
        "weight": 25,
        "recommendation": "Set a robust Content-Security-Policy header to prevent XSS and data injection.",
    },
    "X-Frame-Options": {
        "title": "Clickjacking Protection (X-Frame-Options)",
        "weight": 15,
        "recommendation": "Set 'X-Frame-Options: DENY' or 'SAMEORIGIN' to prevent clickjacking.",
    },
    "X-Content-Type-Options": {
        "title": "MIME-Sniffing Protection (X-Content-Type-Options)",
        "weight": 15,
        "recommendation": "Set 'X-Content-Type-Options: nosniff' to prevent MIME sniffing.",
    },
    "Referrer-Policy": {
        "title": "Referrer Policy",
        "weight": 10,
        "recommendation": "Set 'Referrer-Policy: strict-origin-when-cross-origin' or 'no-referrer'.",
    },
    "Permissions-Policy": {
        "title": "Permissions Policy (Feature Policy)",
        "weight": 10,
        "recommendation": "Set 'Permissions-Policy' to restrict browser features (geolocation, camera, etc.).",
    },
    "X-XSS-Protection": {
        "title": "Legacy XSS Protection Filter",
        "weight": 5,
        "recommendation": "Set 'X-XSS-Protection: 0' (disabled in favor of CSP) or '1; mode=block'.",
    },
}

INFORMATION_LEAK_HEADERS = ["Server", "X-Powered-By", "X-AspNet-Version", "X-Runtime"]


def normalize_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """Normalize dictionary header keys to case-insensitive lower case mapping."""
    return {k.lower(): v for k, v in headers.items()}


def calculate_grade(score: int) -> str:
    """Calculate security grade letter from numerical score (0-100)."""
    if score >= 95:
        return "A+"
    elif score >= 85:
        return "A"
    elif score >= 75:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 45:
        return "D"
    else:
        return "F"


def analyze_headers(headers: Dict[str, str]) -> Dict[str, Any]:
    """
    Analyze given HTTP headers for security best practices.

    Args:
        headers: Dictionary of header key-value pairs.

    Returns:
        Structured evaluation containing total score, grade, checks, and warnings.
    """
    norm = normalize_headers(headers)
    passed_checks: List[Dict[str, Any]] = []
    missing_checks: List[Dict[str, Any]] = []
    total_weight = sum(cfg["weight"] for cfg in SECURITY_CHECKS.values())
    earned_score = 0

    for header_name, cfg in SECURITY_CHECKS.items():
        key = header_name.lower()
        if key in norm and norm[key].strip():
            earned_score += cfg["weight"]
            passed_checks.append({
                "header": header_name,
                "title": cfg["title"],
                "value": norm[key],
                "points": cfg["weight"],
            })
        else:
            missing_checks.append({
                "header": header_name,
                "title": cfg["title"],
                "recommendation": cfg["recommendation"],
                "points": cfg["weight"],
            })

    # Information leakage penalties
    warnings: List[str] = []
    for leak_hdr in INFORMATION_LEAK_HEADERS:
        lkey = leak_hdr.lower()
        if lkey in norm:
            warnings.append(f"Header '{leak_hdr}: {norm[lkey]}' exposes server technology details.")
            earned_score = max(0, earned_score - 5)

    final_score = min(100, int((earned_score / total_weight) * 100))
    grade = calculate_grade(final_score)

    return {
        "score": final_score,
        "grade": grade,
        "passed_count": len(passed_checks),
        "missing_count": len(missing_checks),
        "passed_checks": passed_checks,
        "missing_checks": missing_checks,
        "warnings": warnings,
    }


def format_report(result: Dict[str, Any]) -> str:
    """Format analysis result into a terminal summary report."""
    lines: List[str] = []
    lines.append("=" * 60)
    lines.append("           HTTP SECURITY HEADER AUDIT REPORT           ")
    lines.append("=" * 60)
    lines.append(f" Overall Security Score : {result['score']} / 100")
    lines.append(f" Security Grade         : {result['grade']}")
    lines.append(f" Checks Passed          : {result['passed_count']}")
    lines.append(f" Checks Missing         : {result['missing_count']}")
    lines.append("-" * 60)

    if result["passed_checks"]:
        lines.append("✅ PRESENT SECURITY HEADERS:")
        for chk in result["passed_checks"]:
            lines.append(f"  • {chk['header']}: {chk['value']}")

    if result["missing_checks"]:
        lines.append("\n⚠️ MISSING SECURITY HEADERS & RECOMMENDATIONS:")
        for chk in result["missing_checks"]:
            lines.append(f"  • [{chk['header']}] ({chk['title']})")
            lines.append(f"    👉 {chk['recommendation']}")

    if result["warnings"]:
        lines.append("\n🚨 INFORMATION LEAKAGE WARNINGS:")
        for w in result["warnings"]:
            lines.append(f"  • {w}")

    lines.append("=" * 60)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="HTTP Security Header Analyzer CLI")
    parser.add_argument("--json", help="Input JSON string containing HTTP headers")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    args = parser.parse_args()

    if args.json:
        try:
            headers = json.loads(args.json)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON input: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Sample headers for demonstration CLI run
        headers = {
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "Server": "Apache/2.4.41 (Ubuntu)",
        }

    res = analyze_headers(headers)
    if args.format == "json":
        print(json.dumps(res, indent=2))
    else:
        print(format_report(res))


if __name__ == "__main__":
    main()
