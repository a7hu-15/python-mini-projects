"""
Unit tests for SQL Schema & Query Static Linter.
"""

import unittest
from sql_linter import SQLLinter, LintIssue


class TestSQLLinter(unittest.TestCase):

    def setUp(self):
        self.linter = SQLLinter(check_keywords=True)

    def test_select_star_error(self):
        sql = "SELECT * FROM users;"
        issues = self.linter.lint_query(sql)
        codes = [i.code for i in issues]
        self.assertIn("ERR001", codes)

    def test_missing_where_update_delete_error(self):
        sql_update = "UPDATE users SET active = 0;"
        issues = self.linter.lint_query(sql_update)
        codes = [i.code for i in issues]
        self.assertIn("ERR002", codes)

        sql_delete = "DELETE FROM orders;"
        issues_delete = self.linter.lint_query(sql_delete)
        codes_delete = [i.code for i in issues_delete]
        self.assertIn("ERR002", codes_delete)

    def test_keyword_lowercase_warning(self):
        sql = "select id, name from users where active = 1;"
        issues = self.linter.lint_query(sql)
        codes = [i.code for i in issues]
        self.assertIn("WARN001", codes)

    def test_leading_wildcard_like_warning(self):
        sql = "SELECT id FROM users WHERE email LIKE '%@gmail.com';"
        issues = self.linter.lint_query(sql)
        codes = [i.code for i in issues]
        self.assertIn("WARN002", codes)

    def test_join_missing_on_clause(self):
        sql = "SELECT u.id, o.total FROM users u JOIN orders o;"
        issues = self.linter.lint_query(sql)
        codes = [i.code for i in issues]
        self.assertIn("WARN003", codes)

    def test_clean_query_no_errors(self):
        sql = "SELECT id, email FROM users WHERE id = 10 LIMIT 1;"
        issues = self.linter.lint_query(sql)
        errors = [i for i in issues if i.severity == "ERROR"]
        self.assertEqual(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
