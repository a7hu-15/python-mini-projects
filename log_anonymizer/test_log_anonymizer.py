#!/usr/bin/env python3
"""Unit test suite for Log Anonymizer & PII Masker."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from log_anonymizer import anonymize_text, hash_replacement


class TestLogAnonymizer(unittest.TestCase):
    """Test cases for PII log masking and redaction."""

    def test_anonymize_email(self) -> None:
        log = "User alice@example.com logged in successfully."
        res = anonymize_text(log, strategy="placeholder")
        self.assertEqual(res, "User [EMAIL] logged in successfully.")

    def test_anonymize_ip_address(self) -> None:
        log = "Failed login attempt from 192.168.1.50 at port 443."
        res = anonymize_text(log, strategy="placeholder")
        self.assertEqual(res, "Failed login attempt from [IPV4] at port 443.")

    def test_anonymize_hash_strategy(self) -> None:
        log = "Contact john.doe@company.org for support."
        res = anonymize_text(log, strategy="hash")
        self.assertIn("[EMAIL:", res)

    def test_anonymize_redact_strategy(self) -> None:
        log = "Credit card: 4532-1234-5678-9012"
        res = anonymize_text(log, strategy="redact")
        self.assertIn("████████", res)

    def test_multiple_pii_in_single_line(self) -> None:
        log = "User john@test.com from 10.0.0.1 used SSN 123-45-6789"
        res = anonymize_text(log, strategy="placeholder")
        self.assertEqual(res, "User [EMAIL] from [IPV4] used SSN [SSN]")


if __name__ == "__main__":
    unittest.main()
