"""
CLI SQL Query & Schema Static Linter in Python.

Performs static analysis on SQL files and raw query strings to detect anti-patterns,
syntax risks, performance bottlenecks, and formatting style guidelines.

Lint Rules:
- ERR001: Usage of `SELECT *` anti-pattern.
- ERR002: Missing `WHERE` clause in `UPDATE` or `DELETE` statements.
- WARN001: SQL keywords not capitalized (e.g. `select` vs `SELECT`).
- WARN002: Leading wildcard in `LIKE` condition (e.g., `LIKE '%term'`) prevents index scans.
- WARN003: `JOIN` query missing explicit `ON` or `USING` join condition.
- INFO001: `ORDER BY` clause without `LIMIT` restriction.
"""

import argparse
import re
import sys
from typing import Dict, List, NamedTuple


class LintIssue(NamedTuple):
    code: str
    severity: str  # ERROR, WARNING, INFO
    line_number: int
    message: str
    query_snippet: str


class SQLLinter:
    """
    SQL Static Analysis Engine.
    """

    SQL_KEYWORDS = {
        "SELECT", "FROM", "WHERE", "INSERT", "INTO", "UPDATE", "DELETE",
        "JOIN", "LEFT", "RIGHT", "INNER", "OUTER", "CROSS", "ON", "GROUP",
        "BY", "HAVING", "ORDER", "LIMIT", "OFFSET", "UNION", "ALL", "AS",
        "CREATE", "TABLE", "ALTER", "DROP", "INDEX", "VALUES", "SET",
    }

    def __init__(self, check_keywords: bool = True):
        self.check_keywords = check_keywords

    def lint_query(self, sql_text: str) -> List[LintIssue]:
        """
        Analyze SQL string and return list of LintIssues.

        :param sql_text: Raw SQL queries or script file content.
        :return: List of LintIssue tuples.
        """
        issues: List[LintIssue] = []
        lines = sql_text.splitlines()

        # Remove single-line comments (-- ...) and block comments (/* ... */) for rule checks
        cleaned_text = re.sub(r"--.*$", "", sql_text, flags=re.MULTILINE)
        cleaned_text = re.sub(r"/\*.*?\*/", "", cleaned_text, flags=re.DOTALL)

        queries = [q.strip() for q in cleaned_text.split(";") if q.strip()]

        for query_idx, query in enumerate(queries, start=1):
            query_upper = query.upper()
            line_no = self._find_line_number(lines, query)

            # Rule ERR001: SELECT *
            if re.search(r"\bSELECT\s+\*", query, re.IGNORECASE):
                issues.append(
                    LintIssue(
                        code="ERR001",
                        severity="ERROR",
                        line_number=line_no,
                        message="Anti-pattern: Use explicit column names instead of 'SELECT *'.",
                        query_snippet=query[:60],
                    )
                )

            # Rule ERR002: Missing WHERE in UPDATE / DELETE
            if re.search(r"\b(UPDATE|DELETE)\b", query_upper):
                if "WHERE" not in query_upper:
                    action = "UPDATE" if "UPDATE" in query_upper else "DELETE"
                    issues.append(
                        LintIssue(
                            code="ERR002",
                            severity="ERROR",
                            line_number=line_no,
                            message=f"Critical Risk: Dangerous {action} statement without WHERE clause.",
                            query_snippet=query[:60],
                        )
                    )

            # Rule WARN001: Keyword capitalization
            if self.check_keywords:
                words = re.findall(r"\b[a-zA-Z]+\b", query)
                for w in words:
                    if w.upper() in self.SQL_KEYWORDS and not w.isupper():
                        issues.append(
                            LintIssue(
                                code="WARN001",
                                severity="WARNING",
                                line_number=line_no,
                                message=f"Style: SQL keyword '{w}' should be UPPERCASE '{w.upper()}'.",
                                query_snippet=query[:60],
                            )
                        )
                        break  # Report once per query snippet for brevity

            # Rule WARN002: Leading wildcard in LIKE
            if re.search(r"\bLIKE\s+['\"]%[^\s'\"]+['\"]", query, re.IGNORECASE):
                issues.append(
                    LintIssue(
                        code="WARN002",
                        severity="WARNING",
                        line_number=line_no,
                        message="Performance: Leading wildcard in LIKE '%...' prevents index scan.",
                        query_snippet=query[:60],
                    )
                )

            # Rule WARN003: JOIN missing ON / USING
            if re.search(r"\b(INNER|LEFT|RIGHT|FULL)?\s*JOIN\b", query_upper):
                if not re.search(r"\bCROSS\s+JOIN\b", query_upper):
                    if " ON " not in query_upper and " USING " not in query_upper:
                        issues.append(
                            LintIssue(
                                code="WARN003",
                                severity="WARNING",
                                line_number=line_no,
                                message="Performance/Correctness: JOIN missing ON or USING clause.",
                                query_snippet=query[:60],
                            )
                        )

            # Rule INFO001: ORDER BY without LIMIT
            if "ORDER BY" in query_upper and "LIMIT" not in query_upper:
                issues.append(
                    LintIssue(
                        code="INFO001",
                        severity="INFO",
                        line_number=line_no,
                        message="Advice: ORDER BY without LIMIT may cause high memory overhead on large tables.",
                        query_snippet=query[:60],
                    )
                )

        return issues

    def _find_line_number(self, lines: List[str], query_snippet: str) -> int:
        first_line = query_snippet.splitlines()[0] if query_snippet else ""
        for idx, line in enumerate(lines, start=1):
            if first_line and first_line in line:
                return idx
        return 1


def main():
    parser = argparse.ArgumentParser(description="CLI SQL Schema & Query Static Linter")
    parser.add_argument("file", type=str, nargs="?", help="SQL file to lint")
    parser.add_argument("-q", "--query", type=str, help="Raw SQL query string to lint directly")
    parser.add_argument("--ignore-style", action="store_true", help="Ignore keyword capitalization style warnings")

    args = parser.parse_args()

    if not args.file and not args.query:
        parser.print_help()
        sys.exit(1)

    sql_content = ""
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            sql_content = f.read()
    elif args.query:
        sql_content = args.query

    linter = SQLLinter(check_keywords=not args.ignore_style)
    issues = linter.lint_query(sql_content)

    print(f"🔍 Linting SQL input ({len(issues)} issue(s) found)...\n")

    if not issues:
        print("✅ No SQL issues or anti-patterns detected!")
        sys.exit(0)

    errors = 0
    warnings = 0
    info = 0

    for issue in issues:
        if issue.severity == "ERROR":
            errors += 1
            icon = "❌"
        elif issue.severity == "WARNING":
            warnings += 1
            icon = "⚠️"
        else:
            info += 1
            icon = "ℹ️"

        print(f"{icon} [{issue.code}] Line {issue.line_number}: {issue.message}")
        print(f"   Snippet: {issue.query_snippet.strip()}\n")

    print(f"Summary: {errors} Error(s), {warnings} Warning(s), {info} Info note(s)")
    if errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
