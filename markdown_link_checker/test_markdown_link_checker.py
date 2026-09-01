"""
Unit tests for CLI Markdown Link & Anchor Checker
"""

import tempfile
import unittest
from pathlib import Path

from markdown_link_checker import MarkdownLinkChecker, slugify_heading


class TestMarkdownLinkChecker(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_path = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_slugify_heading(self) -> None:
        self.assertEqual(slugify_heading("Introduction"), "introduction")
        self.assertEqual(slugify_heading("Section 1.2: Advanced Usage!"), "section-12-advanced-usage")
        self.assertEqual(slugify_heading("`code_block` & **bold**"), "codeblock-bold")

    def test_valid_file_and_anchor_links(self) -> None:
        target_file = self.root_path / "target.md"
        target_file.write_text("# Target Section\n\nSome target content.")

        index_file = self.root_path / "index.md"
        index_content = """# Main Header

- [Target Doc](./target.md)
- [Target Section](./target.md#target-section)
- [Internal Anchor](#main-header)
"""
        index_file.write_text(index_content)

        checker = MarkdownLinkChecker(self.root_path)
        errors = checker.check_file(index_file)
        self.assertEqual(len(errors), 0)

    def test_broken_file_and_anchor_links(self) -> None:
        target_file = self.root_path / "target.md"
        target_file.write_text("# Existing Header\n\nContent.")

        index_file = self.root_path / "index.md"
        index_content = """# Main Header

- [Missing File](./missing.md)
- [Missing Anchor](./target.md#non-existent-header)
- [Broken Local Anchor](#wrong-anchor)
"""
        index_file.write_text(index_content)

        checker = MarkdownLinkChecker(self.root_path)
        errors = checker.check_file(index_file)
        self.assertEqual(len(errors), 3)

        error_msgs = [e[2] for e in errors]
        self.assertTrue(any("does not exist" in msg for msg in error_msgs))
        self.assertTrue(any("not found in './target.md'" in msg for msg in error_msgs))
        self.assertTrue(any("not found in current file" in msg for msg in error_msgs))

    def test_directory_check(self) -> None:
        doc1 = self.root_path / "doc1.md"
        doc1.write_text("# Doc One\n[Doc 2](./doc2.md)")

        doc2 = self.root_path / "doc2.md"
        doc2.write_text("# Doc Two\n[Valid](./doc1.md)")

        checker = MarkdownLinkChecker(self.root_path)
        results = checker.check_directory(self.root_path)
        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main()
