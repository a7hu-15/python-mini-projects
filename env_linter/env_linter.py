#!/usr/bin/env python3
"""
CLI Environment Variables (.env) Linter & Secret Leak Inspector

Parses .env files to check syntax, key formatting, missing keys compared to .env.example,
and scans for hardcoded sensitive credentials/tokens before committing code.
"""

import argparse
import os
import re
import sys
from typing import List, Dict, Tuple, Set


SECRET_KEY_PATTERNS = [
    r"AKIA[0-9A-Z]{16}",  # AWS Access Key ID
    r"EAACEdEose0cBA[0-9A-Za-z]+",  # Facebook Access Token
    r"ghp_[0-9a-zA-Z]{36}",  # GitHub Personal Access Token
    r"sk_live_[0-9a-zA-Z]{24}",  # Stripe Live Key
    r"-----BEGIN PRIVATE KEY-----",  # RSA/PEM Private Key
]


class EnvLinter:
    """Handles parsing and linting of .env files."""

    @staticmethod
    def parse_env_file(filepath: str) -> Dict[str, str]:
        """Parse .env file into key-value pairs."""
        env_vars = {}
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    env_vars[key.strip()] = val.strip().strip("'\"")
        return env_vars

    @staticmethod
    def check_syntax_and_secrets(filepath: str) -> Tuple[List[str], List[str]]:
        """Check .env file for formatting issues and hardcoded secrets."""
        warnings = []
        errors = []

        with open(filepath, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f, start=1):
                raw_line = line.strip()
                if not raw_line or raw_line.startswith("#"):
                    continue

                if "=" not in raw_line:
                    errors.append(f"Line {idx}: Missing '=' operator in '{raw_line}'")
                    continue

                key, val = raw_line.split("=", 1)
                key = key.strip()
                val = val.strip()

                # Key casing check
                if not re.match(r"^[A-Z0-9_]+$", key):
                    warnings.append(f"Line {idx}: Key '{key}' should be UPPERCASE_WITH_UNDERSCORES")

                # Secret check
                for pattern in SECRET_KEY_PATTERNS:
                    if re.search(pattern, val):
                        errors.append(f"Line {idx}: Hardcoded secret pattern detected in key '{key}'")

        return warnings, errors

    @staticmethod
    def compare_example(env_path: str, example_path: str) -> List[str]:
        """Compare .env keys against .env.example keys to find missing variables."""
        env_keys = set(EnvLinter.parse_env_file(env_path).keys())
        example_keys = set(EnvLinter.parse_env_file(example_path).keys())

        missing = example_keys - env_keys
        return [f"Missing variable defined in {example_path}: '{k}'" for k in sorted(missing)]


def main():
    parser = argparse.ArgumentParser(description="Lint .env files and scan for hardcoded secrets.")
    parser.add_argument("env_file", nargs="?", default=".env", help="Path to .env file")
    parser.add_argument("--example", help="Path to .env.example file for key comparison")

    args = parser.parse_args()

    if not os.path.exists(args.env_file):
        print(f"Error: File '{args.env_file}' not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Linting environment file: '{args.env_file}'...")
    warnings, errors = EnvLinter.check_syntax_and_secrets(args.env_file)

    if args.example:
        if os.path.exists(args.example):
            missing = EnvLinter.compare_example(args.env_file, args.example)
            errors.extend(missing)
        else:
            print(f"Warning: Example file '{args.example}' not found.", file=sys.stderr)

    if warnings:
        print("\n⚠️  Warnings:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print("\n❌ Errors:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("✅ Environment file passed all checks!")


if __name__ == "__main__":
    main()
