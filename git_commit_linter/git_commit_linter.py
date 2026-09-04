"""CLI Git Commit Message Linter & Hook Validator.

Validates commit messages against Conventional Commits specification rules.
Checks type, scope, subject casing, header character length, and breaking change indicators.
"""

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Optional, Set

DEFAULT_TYPES = {
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "perf",
    "test",
    "build",
    "ci",
    "chore",
    "revert",
}

# Regex pattern for Conventional Commits header: type(scope)!: subject
HEADER_REGEX = re.compile(
    r"^(?P<type>[a-z0-9-]+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s+(?P<subject>.+)$"
)


def lint_commit_message(
    message: str,
    allowed_types: Optional[Set[str]] = None,
    max_header_len: int = 72,
) -> Dict[str, Any]:
    """Lints a commit message string against Conventional Commits rules.

    Args:
        message: Raw commit message text (header + optional body)
        allowed_types: Set of allowed commit type strings
        max_header_len: Maximum character length for first line (default 72)

    Returns:
        Dictionary containing 'valid' boolean, parsed fields, and list of error messages.
    """
    if allowed_types is None:
        allowed_types = DEFAULT_TYPES

    errors: List[str] = []
    lines = [line.strip() for line in message.strip().splitlines() if not line.startswith("#")]

    if not lines or not lines[0]:
        return {
            "valid": False,
            "errors": ["Commit message cannot be empty"],
            "parsed": None,
        }

    header = lines[0]

    # Rule 1: Header character length limit
    if len(header) > max_header_len:
        errors.append(f"Header length ({len(header)}) exceeds maximum limit of {max_header_len} characters")

    # Rule 2: Header format match
    match = HEADER_REGEX.match(header)
    if not match:
        errors.append(
            "Header does not match Conventional Commits format: '<type>[(scope)][!]: <subject>'"
        )
        return {
            "valid": False,
            "errors": errors,
            "parsed": {"header": header},
        }

    commit_type = match.group("type")
    scope = match.group("scope")
    is_breaking = bool(match.group("breaking"))
    subject = match.group("subject")

    # Rule 3: Valid commit type check
    if commit_type not in allowed_types:
        errors.append(
            f"Invalid commit type '{commit_type}'. Allowed types: {', '.join(sorted(allowed_types))}"
        )

    # Rule 4: Subject start casing check (should start with letter/number, not capital unless proper noun)
    if subject and subject[0].isupper() and not subject[:3].isupper():
        errors.append("Subject line should start with lower case letter (e.g. 'add feature' not 'Add feature')")

    # Rule 5: Subject trailing period check
    if subject.endswith("."):
        errors.append("Subject line must not end with a period '.'")

    # Rule 6: Check for blank line between header and body if body exists
    if len(lines) > 1 and len(message.strip().splitlines()) > 1:
        raw_lines = message.strip().splitlines()
        if raw_lines[1].strip() != "":
            errors.append("Must separate commit header and body with a blank line")

    # Check for BREAKING CHANGE in body/footer
    if "BREAKING CHANGE:" in message or "BREAKING-CHANGE:" in message:
        is_breaking = True

    parsed_info = {
        "header": header,
        "type": commit_type,
        "scope": scope,
        "is_breaking": is_breaking,
        "subject": subject,
    }

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "parsed": parsed_info,
    }


def main():
    parser = argparse.ArgumentParser(description="CLI Git Commit Message Linter")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-m", "--message", help="Commit message string to lint")
    group.add_argument("-f", "--file", help="Path to commit message file (e.g. .git/COMMIT_EDITMSG)")

    parser.add_argument("--max-header-length", type=int, default=72, help="Max header character length (default: 72)")
    parser.add_argument("--json", action="store_true", help="Output validation result in JSON format")

    args = parser.parse_args()

    message_content = ""
    if args.message:
        message_content = args.message
    elif args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                message_content = f.read()
        except Exception as e:
            print(f"Error reading file '{args.file}': {e}", file=sys.stderr)
            sys.exit(2)

    result = lint_commit_message(message_content, max_header_len=args.max_header_length)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["valid"]:
            print("✅ Commit message complies with Conventional Commits specification!")
            if result["parsed"]:
                p = result["parsed"]
                print(f"   Type    : {p['type']}")
                print(f"   Scope   : {p['scope'] or 'none'}")
                print(f"   Breaking: {p['is_breaking']}")
                print(f"   Subject : {p['subject']}")
        else:
            print("❌ Commit message failed validation rules:", file=sys.stderr)
            for err in result["errors"]:
                print(f"  - {err}", file=sys.stderr)

    if not result["valid"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
