"""
Unit tests for Git Commit History & Contributor Analyzer.
"""

import unittest
from git_analyzer import GitLogParser


class TestGitLogParser(unittest.TestCase):
    def setUp(self):
        self.sample_log = """
COMMIT|Alice Developer|alice@example.com|2026-08-28|Thursday
10\t2\tmain.py
5\t0\tREADME.md

COMMIT|Bob Smith|bob@example.com|2026-08-28|Thursday
20\t5\tutils.py

COMMIT|Alice Developer|alice@example.com|2026-08-29|Friday
3\t1\tmain.py
"""

    def test_parse_log_statistics(self):
        parser = GitLogParser()
        summary = parser.parse_log(self.sample_log)

        self.assertEqual(summary["total_commits"], 3)
        self.assertEqual(summary["total_authors"], 2)

        # Check Alice stats
        alice = next(a for a in summary["authors"] if a["name"] == "Alice Developer")
        self.assertEqual(alice["commits"], 2)
        self.assertEqual(alice["additions"], 18)
        self.assertEqual(alice["deletions"], 3)

        # Check Bob stats
        bob = next(a for a in summary["authors"] if a["name"] == "Bob Smith")
        self.assertEqual(bob["commits"], 1)
        self.assertEqual(bob["additions"], 20)

        # Check top changed files
        self.assertEqual(summary["top_files"][0]["file"], "main.py")
        self.assertEqual(summary["top_files"][0]["changes"], 2)

    def test_markdown_format(self):
        parser = GitLogParser()
        parser.parse_log(self.sample_log)
        md = parser.format_markdown()

        self.assertIn("# 📊 Git Repository Analytics Report", md)
        self.assertIn("Alice Developer", md)
        self.assertIn("`main.py`", md)


if __name__ == "__main__":
    unittest.main()
