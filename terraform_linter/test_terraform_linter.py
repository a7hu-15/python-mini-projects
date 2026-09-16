import unittest
import tempfile
import os
from terraform_linter.terraform_linter import audit_tf_manifest, audit_tf_content


class TestTerraformLinter(unittest.TestCase):
    def test_open_ingress_rule_detection(self):
        content = """
resource "aws_security_group" "web" {
  name = "web-sg"
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
"""
        issues = audit_tf_content(content)
        open_ingress = [i for i in issues if i["rule"] == "OpenIngressSecurityGroup"]
        self.assertEqual(len(open_ingress), 1)
        self.assertEqual(open_ingress[0]["severity"], "HIGH")

    def test_unencrypted_s3_bucket(self):
        content = """
resource "aws_s3_bucket" "my_bucket" {
  bucket = "my-company-data-bucket"
}
"""
        issues = audit_tf_content(content)
        s3_issues = [i for i in issues if i["rule"] == "UnencryptedS3Bucket"]
        self.assertEqual(len(s3_issues), 1)

    def test_hardcoded_secret_key(self):
        content = 'provider "aws" {\n  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"\n}\n'
        issues = audit_tf_content(content)
        secret_issues = [i for i in issues if i["rule"] == "Hardcoded AWS Secret Key"]
        self.assertEqual(len(secret_issues), 1)

    def test_audit_tf_manifest_file(self):
        content = 'resource "aws_s3_bucket" "test" {\n  bucket = "test"\n}\n'
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".tf") as f:
            f.write(content)
            temp_path = f.name

        try:
            report = audit_tf_manifest(temp_path)
            self.assertFalse(report["valid"])
            self.assertEqual(report["error_count"], 1)
        finally:
            os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
