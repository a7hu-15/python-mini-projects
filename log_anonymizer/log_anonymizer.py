#!/usr/bin/env python3
"""
Log Anonymizer & PII Masker CLI

A CLI tool and Python utility for detecting and redacting Personally Identifiable Information (PII)
and credentials from application logs, data streams, and text files.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from typing import Callable, Dict, List, Pattern

# Regular expressions for common PII patterns
PII_PATTERNS: Dict[str, str] = {
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "IPV4": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
    "IPV6": r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b",
    "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "PHONE": r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "JWT_TOKEN": r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b",
    "API_KEY": r"\b(?:sk_live|sk_test|api_key|secret_key|access_token)=['\"]?[A-Za-z0-9._\-]{16,}['\"]?\b",
}


def hash_replacement(match: str, pii_type: str) -> str:
    """Generate deterministic SHA256 prefix hash replacement for anonymized data."""
    digest = hashlib.sha256(match.encode("utf-8")).hexdigest()[:8]
    return f"[{pii_type}:{digest}]"


def anonymize_text(
    text: str,
    strategy: str = "placeholder",
    enabled_rules: List[str] | None = None,
) -> str:
    """
    Anonymize PII occurrences within text string.

    Args:
        text: Input string or log content.
        strategy: 'placeholder' ([EMAIL]), 'hash' ([EMAIL:a1b2c3d4]), or 'redact' (***).
        enabled_rules: List of PII pattern keys to enable. Default enables all.

    Returns:
        Anonymized text string.
    """
    if enabled_rules is None:
        enabled_rules = list(PII_PATTERNS.keys())

    anonymized = text

    for rule_name in enabled_rules:
        if rule_name not in PII_PATTERNS:
            continue

        pattern_str = PII_PATTERNS[rule_name]
        compiled = re.compile(pattern_str)

        if strategy == "hash":
            anonymized = compiled.sub(
                lambda m: hash_replacement(m.group(0), rule_name), anonymized
            )
        elif strategy == "redact":
            anonymized = compiled.sub("████████", anonymized)
        else:  # default 'placeholder'
            anonymized = compiled.sub(f"[{rule_name}]", anonymized)

    return anonymized


def main() -> None:
    parser = argparse.ArgumentParser(description="Log Anonymizer & PII Masker CLI")
    parser.add_argument("file", nargs="?", type=argparse.FileType("r"), default=sys.stdin, help="Input file (defaults to stdin)")
    parser.add_argument("-s", "--strategy", choices=["placeholder", "hash", "redact"], default="placeholder", help="Masking strategy")
    parser.add_argument("-o", "--output", type=argparse.FileType("w"), default=sys.stdout, help="Output file (defaults to stdout)")
    args = parser.parse_args()

    content = args.file.read()
    result = anonymize_text(content, strategy=args.strategy)
    args.output.write(result)


if __name__ == "__main__":
    main()
