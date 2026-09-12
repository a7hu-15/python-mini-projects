import unittest
import tempfile
import os
from yaml_env_validator.yaml_env_validator import audit_config_file, detect_secrets, audit_env_content


class TestYamlEnvValidator(unittest.TestCase):
    def test_detect_secrets(self):
        line_secret = "AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        findings = detect_secrets(line_secret, 1)
        self.assertTrue(len(findings) > 0)
        self.assertEqual(findings[0]["rule"], "AWS Secret Access Key")

    def test_valid_env_content(self):
        env_content = "PORT=8080\nNODE_ENV=production\nDATABASE_URL=${DB_URL}\n"
        errors, warnings = audit_env_content(env_content)
        self.assertEqual(len(errors), 0)

    def test_invalid_env_syntax(self):
        env_content = "PORT 8080\nINVALID LINE WITHOUT EQUALS\n"
        errors, warnings = audit_env_content(env_content)
        self.assertTrue(len(errors) >= 2)
        self.assertEqual(errors[0]["rule"], "SyntaxError")

    def test_empty_value_warning(self):
        env_content = "API_KEY=\n"
        errors, warnings = audit_env_content(env_content)
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0]["rule"], "EmptyValue")

    def test_audit_config_file(self):
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".env") as f:
            f.write("APP_NAME=MyApp\nPORT=3000\nSECRET_KEY=12345\n")
            temp_path = f.name

        try:
            report = audit_config_file(temp_path)
            self.assertIn("valid", report)
            self.assertTrue(report["valid"])
        finally:
            os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
