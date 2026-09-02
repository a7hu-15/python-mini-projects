import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from secret_scanner.secret_scanner import (
    DEFAULT_RULES,
    Finding,
    SecretRule,
    SecretScanner,
    format_text_report,
    mask_secret,
)


class TestSecretScanner(unittest.TestCase):
    """Unit test suite for Secret Scanner mini-project."""

    def setUp(self) -> None:
        self.scanner = SecretScanner()

    def test_mask_secret(self) -> None:
        self.assertEqual(mask_secret("sk_test_1234567890abcdef"), "sk_******************def")
        self.assertEqual(mask_secret("123456"), "******")
        self.assertEqual(mask_secret("123"), "***")

    def test_aws_access_key_detection(self) -> None:
        rule = next(r for r in DEFAULT_RULES if r.rule_id == "AWS-001")
        matches = rule.match("aws_key = 'AKIAIOSFODNN7EXAMPLE'")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].group(0), "AKIAIOSFODNN7EXAMPLE")

    def test_github_token_detection(self) -> None:
        rule = next(r for r in DEFAULT_RULES if r.rule_id == "GH-001")
        matches = rule.match("token = 'ghp_1234567890abcdefghijklmnopqrstuvwxyz'")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].group(0), "ghp_1234567890abcdefghijklmnopqrstuvwxyz")

    def test_stripe_key_detection(self) -> None:
        rule = next(r for r in DEFAULT_RULES if r.rule_id == "STRIPE-001")
        matches = rule.match("stripe_key = 'sk_test_51abcdefghijklmnopqrstuvw'")
        self.assertEqual(len(matches), 1)

    def test_rsa_key_detection(self) -> None:
        rule = next(r for r in DEFAULT_RULES if r.rule_id == "KEY-001")
        matches = rule.match("-----BEGIN RSA PRIVATE KEY-----")
        self.assertEqual(len(matches), 1)

    def test_file_scanning(self) -> None:
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".py") as tf:
            tf.write("# Test file\n")
            tf.write("AWS_KEY = 'AKIAIOSFODNN7EXAMPLE'\n")
            tf.write("print('hello world')\n")
            tf_path = tf.name

        try:
            findings = self.scanner.scan_file(tf_path)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].rule_id, "AWS-001")
            self.assertEqual(findings[0].line_number, 2)
        finally:
            os.remove(tf_path)

    def test_directory_scanning_and_ignoring(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir)

            # Create clean file
            clean_file = dir_path / "app.py"
            clean_file.write_text("print('Clean file')")

            # Create file with secret
            secret_file = dir_path / "config.py"
            secret_file.write_text("OPENAI_KEY = 'sk-1234567890abcdef1234567890abcdef12345678'")

            # Create ignored directory with secret
            venv_dir = dir_path / ".venv"
            venv_dir.mkdir()
            (venv_dir / "lib.py").write_text("AKIAIOSFODNN7EXAMPLE")

            findings = self.scanner.scan_directory(dir_path)
            # Should detect secret_file but ignore .venv
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].rule_id, "OPENAI-001")

    def test_report_formatting(self) -> None:
        findings = [
            Finding(
                rule_id="AWS-001",
                rule_name="AWS Access Key ID",
                severity="HIGH",
                file_path="config.py",
                line_number=5,
                matched_text="AKIAIOSFODNN7EXAMPLE",
                snippet="AWS_KEY = 'AKIAIOSFODNN7EXAMPLE'",
            )
        ]
        report = format_text_report(findings, mask=True)
        self.assertIn("HIGH", report)
        self.assertIn("AWS-001", report)
        self.assertIn("AKI**************PLE", report)

    def test_empty_findings_report(self) -> None:
        report = format_text_report([])
        self.assertIn("No secrets or sensitive data detected", report)


if __name__ == "__main__":
    unittest.main()
