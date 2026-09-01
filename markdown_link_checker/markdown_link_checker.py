#!/usr/bin/env python3
"""
CLI Markdown Link & Anchor Checker

A lightweight CLI tool to validate relative file paths, image references, and heading anchors (#anchor-name)
within Markdown files across a project repository.

Features:
- Validates local file references (images, relative markdown files, code snippets).
- Validates Markdown heading anchors (#heading-slug-name) within target files.
- Generates clean CLI reports with line numbers and status codes.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Regex to match Markdown links: [link text](url_or_path "optional title")
LINK_REGEX = re.compile(r'\[([^\]]+)\]\(([^"\'\s\)]+)(?:\s+["\'][^"\']*["\'])?\)')
# Regex to match Markdown headings: # Heading Title
HEADING_REGEX = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)


def slugify_heading(heading_text: str) -> str:
    """
    Converts a Markdown heading title into GitHub-style anchor slug.

    >>> slugify_heading("Hello World!")
    'hello-world'
    >>> slugify_heading("Section 1.2: Deep Dive (Advanced)")
    'section-12-deep-dive-advanced'
    """
    text = heading_text.lower().strip()
    # Remove markdown inline formatting (bold, italic, code ticks)
    text = re.sub(r'[`*_~]', '', text)
    # Replace non-alphanumeric chars with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace whitespace with single hyphen
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')


def extract_headings(file_path: Path) -> Set[str]:
    """Extracts all heading anchor slugs from a markdown file."""
    if not file_path.exists() or not file_path.is_file():
        return set()

    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return set()

    anchors = set()
    for match in HEADING_REGEX.finditer(content):
        heading_title = match.group(2).strip()
        slug = slugify_heading(heading_title)
        if slug:
            anchors.add(slug)
    return anchors


class MarkdownLinkChecker:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir.resolve()
        self.heading_cache: Dict[Path, Set[str]] = {}

    def check_file(self, file_path: Path) -> List[Tuple[int, str, str]]:
        """
        Inspects a single markdown file for broken local links.
        Returns list of tuples: (line_number, target_link, error_message)
        """
        file_path = file_path.resolve()
        if not file_path.exists():
            return [(0, str(file_path), "File does not exist")]

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as err:
            return [(0, str(file_path), f"Failed to read file: {err}")]

        broken_links: List[Tuple[int, str, str]] = []
        lines = content.splitlines()

        for line_idx, line in enumerate(lines, start=1):
            for match in LINK_REGEX.finditer(line):
                target = match.group(2).strip()

                # Skip web URLs, mailto, and empty targets
                if target.startswith(("http://", "https://", "mailto:", "ftp://", "javascript:")) or not target:
                    continue

                # Handle anchor-only links: #my-heading
                if target.startswith("#"):
                    anchor = target[1:]
                    if file_path not in self.heading_cache:
                        self.heading_cache[file_path] = extract_headings(file_path)

                    if anchor and anchor not in self.heading_cache[file_path]:
                        broken_links.append((line_idx, target, f"Anchor '{anchor}' not found in current file"))
                    continue

                # Handle relative path with optional anchor: relative/file.md#anchor
                if "#" in target:
                    path_part, anchor_part = target.split("#", 1)
                else:
                    path_part, anchor_part = target, ""

                resolved_path = (file_path.parent / path_part).resolve()

                if not resolved_path.exists():
                    broken_links.append((line_idx, target, f"Referenced path '{path_part}' does not exist"))
                elif anchor_part and resolved_path.suffix == ".md":
                    if resolved_path not in self.heading_cache:
                        self.heading_cache[resolved_path] = extract_headings(resolved_path)

                    if anchor_part not in self.heading_cache[resolved_path]:
                        broken_links.append((line_idx, target, f"Anchor '{anchor_part}' not found in '{path_part}'"))

        return broken_links

    def check_directory(self, target_dir: Path) -> Dict[Path, List[Tuple[int, str, str]]]:
        """Recursively checks all markdown files in target directory."""
        results: Dict[Path, List[Tuple[int, str, str]]] = {}
        for path in target_dir.rglob("*.md"):
            if ".git" in path.parts or "node_modules" in path.parts:
                continue
            errors = self.check_file(path)
            if errors:
                results[path] = errors
        return results


def main() -> int:
    parser = argparse.ArgumentParser(description="CLI Markdown Link & Anchor Checker")
    parser.add_argument("path", nargs="?", default=".", help="File or directory path to check")
    args = parser.parse_args()

    target_path = Path(args.path).resolve()
    checker = MarkdownLinkChecker(target_path if target_path.is_dir() else target_path.parent)

    total_errors = 0

    if target_path.is_file():
        errors = checker.check_file(target_path)
        if errors:
            print(f"❌ {target_path.name}:")
            for line_no, link, msg in errors:
                print(f"  Line {line_no}: [{link}] -> {msg}")
            total_errors += len(errors)
        else:
            print(f"✅ {target_path.name}: All local links valid!")

    elif target_path.is_dir():
        results = checker.check_directory(target_path)
        if results:
            for file_path, errors in results.items():
                rel_path = file_path.relative_to(target_path)
                print(f"❌ {rel_path}:")
                for line_no, link, msg in errors:
                    print(f"  Line {line_no}: [{link}] -> {msg}")
                total_errors += len(errors)
        else:
            print(f"✅ All markdown files in '{target_path.name}' have valid local links!")

    else:
        print(f"Error: Path '{args.path}' does not exist.")
        return 1

    if total_errors > 0:
        print(f"\nSummary: Found {total_errors} broken link(s).")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
