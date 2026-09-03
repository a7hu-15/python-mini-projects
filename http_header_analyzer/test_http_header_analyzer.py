#!/usr/bin/env python3
"""Unit test suite for HTTP Security Header Analyzer."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from http_header_analyzer import (
    analyze_headers,
    calculate_grade,
    format_report,
    normalize_headers,
)


class TestHTTPHeaderAnalyzer(unittest.TestCase):
    """Test cases for HTTP security header evaluation."""

    def test_normalize_headers(self) -> None:
        raw = {"Content-Type": "application/json", "STRICT-TRANSPORT-SECURITY": "max-age=3600"}
        norm = normalize_headers(raw)
        self.assertEqual(norm["content-type"], "application/json")
        self.assertEqual(norm["strict-transport-security"], "max-age=3600")

    def test_calculate_grade(self) -> None:
        self.assertEqual(calculate_grade(98), "A+")
        self.assertEqual(calculate_grade(88), "A")
        self.assertEqual(calculate_grade(78), "B")
        self.assertEqual(calculate_grade(65), "C")
        self.assertEqual(calculate_grade(50), "D")
        self.assertEqual(calculate_grade(30), "F")

    def test_perfect_headers(self) -> None:
        perfect_headers = {
            "Strict-Transport-Security": "max-age=31536000",
            "Content-Security-Policy": "default-src 'self'",
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "no-referrer",
            "Permissions-Policy": "geolocation=()",
            "X-XSS-Protection": "0",
        }
        res = analyze_headers(perfect_headers)
        self.assertEqual(res["score"], 100)
        self.assertEqual(res["grade"], "A+")
        self.assertEqual(res["passed_count"], 7)
        self.assertEqual(res["missing_count"], 0)
        self.assertEqual(len(res["warnings"]), 0)

    def test_missing_headers_and_server_leak(self) -> None:
        headers = {
            "X-Frame-Options": "SAMEORIGIN",
            "Server": "nginx/1.18.0",
            "X-Powered-By": "Express",
        }
        res = analyze_headers(headers)
        self.assertLess(res["score"], 50)
        self.assertEqual(res["passed_count"], 1)
        self.assertGreater(res["missing_count"], 4)
        self.assertEqual(len(res["warnings"]), 2)

    def test_format_report(self) -> None:
        headers = {"X-Frame-Options": "DENY"}
        res = analyze_headers(headers)
        report = format_report(res)
        self.assertIn("HTTP SECURITY HEADER AUDIT REPORT", report)
        self.assertIn("X-Frame-Options", report)


if __name__ == "__main__":
    unittest.main()
