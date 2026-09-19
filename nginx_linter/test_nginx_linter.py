import unittest
from nginx_linter.nginx_linter import audit_nginx_config


class TestNginxLinter(unittest.TestCase):

    def test_clean_config(self):
        config = """
        server {
            listen 443 ssl;
            server_name example.com;
            server_tokens off;
            autoindex off;
            ssl_protocols TLSv1.2 TLSv1.3;

            add_header X-Frame-Options "DENY";
            add_header X-Content-Type-Options "nosniff";
            add_header Content-Security-Policy "default-src 'self'";
            add_header Strict-Transport-Security "max-age=31536000";
            add_header Referrer-Policy "strict-origin-when-cross-origin";

            location /static/ {
                alias /var/www/static/;
            }
        }
        """
        report = audit_nginx_config(config)
        self.assertTrue(report["valid"])
        self.assertEqual(len(report["errors"]), 0)
        self.assertEqual(len(report["warnings"]), 0)

    def test_insecure_directives(self):
        config = """
        server {
            listen 80;
            server_tokens on;
            autoindex on;
            ssl_protocols SSLv3 TLSv1 TLSv1.2;

            location /files/ {
                alias /var/www/files;
            }
        }
        """
        report = audit_nginx_config(config)
        self.assertFalse(report["valid"])
        self.assertTrue(any("server_tokens" in e for e in report["errors"]))
        self.assertTrue(any("autoindex" in e for e in report["errors"]))
        self.assertTrue(any("Insecure SSL/TLS protocols" in e for e in report["errors"]))
        self.assertTrue(any("trailing slash" in e for e in report["errors"]))

    def test_missing_security_headers(self):
        config = """
        server {
            listen 80;
            server_tokens off;
        }
        """
        report = audit_nginx_config(config)
        self.assertTrue(report["valid"])
        self.assertTrue(len(report["warnings"]) >= 4)


if __name__ == "__main__":
    unittest.main()
