import unittest
from git_commit_linter.git_commit_linter import lint_commit_message


class TestGitCommitLinter(unittest.TestCase):
    def test_valid_commit_messages(self):
        valid_cases = [
            "feat: add SSL inspector CLI tool",
            "fix(api): handle connection timeout error",
            "docs: update installation instructions",
            "chore!: drop support for Python 3.7",
            "style(ui): format code according to PEP 8",
        ]
        for msg in valid_cases:
            res = lint_commit_message(msg)
            self.assertTrue(res["valid"], f"Failed for valid message: {msg}")

    def test_invalid_type(self):
        res = lint_commit_message("invalidtype: add feature")
        self.assertFalse(res["valid"])
        self.assertTrue(any("Invalid commit type" in err for err in res["errors"]))

    def test_uppercase_subject(self):
        res = lint_commit_message("feat: Add new feature")
        self.assertFalse(res["valid"])
        self.assertTrue(any("Subject line should start with lower case" in err for err in res["errors"]))

    def test_trailing_period(self):
        res = lint_commit_message("fix: resolve login bug.")
        self.assertFalse(res["valid"])
        self.assertTrue(any("must not end with a period" in err for err in res["errors"]))

    def test_header_too_long(self):
        long_msg = "feat(core): " + "a" * 70
        res = lint_commit_message(long_msg, max_header_len=50)
        self.assertFalse(res["valid"])
        self.assertTrue(any("exceeds maximum limit" in err for err in res["errors"]))

    def test_missing_blank_line_before_body(self):
        msg = "feat: add feature\nThis is body line without blank line separator"
        res = lint_commit_message(msg)
        self.assertFalse(res["valid"])
        self.assertTrue(any("blank line" in err for err in res["errors"]))

    def test_empty_message(self):
        res = lint_commit_message("")
        self.assertFalse(res["valid"])
        self.assertEqual(res["errors"], ["Commit message cannot be empty"])


if __name__ == "__main__":
    unittest.main()
