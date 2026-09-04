from datetime import datetime, timedelta, timezone
import unittest
from ssl_cert_inspector.ssl_cert_inspector import parse_cert_date, parse_certificate, format_report


class TestSSLCertInspector(unittest.TestCase):
    def test_parse_cert_date(self):
        date_str = "May 20 23:59:59 2026 GMT"
        dt = parse_cert_date(date_str)
        self.assertEqual(dt.year, 2026)
        self.assertEqual(dt.month, 5)
        self.assertEqual(dt.day, 20)
        self.assertEqual(dt.tzinfo, timezone.utc)

    def test_parse_certificate_healthy(self):
        future_date = datetime.now(timezone.utc) + timedelta(days=60)
        future_str = future_date.strftime("%b %d %H:%M:%S %Y GMT")
        past_date = datetime.now(timezone.utc) - timedelta(days=30)
        past_str = past_date.strftime("%b %d %H:%M:%S %Y GMT")

        mock_cert = {
            "subject": ((("commonName", "example.com"),),),
            "issuer": ((("commonName", "DigiCert Global Root CA"),), (("organizationName", "DigiCert Inc"),)),
            "subjectAltName": (("DNS", "example.com"), ("DNS", "www.example.com")),
            "notBefore": past_str,
            "notAfter": future_str,
            "serialNumber": "0123456789ABCDEF",
            "version": 3,
        }

        result = parse_certificate(mock_cert, "example.com")
        self.assertEqual(result["hostname"], "example.com")
        self.assertEqual(result["subject_cn"], "example.com")
        self.assertEqual(result["issuer_cn"], "DigiCert Global Root CA")
        self.assertEqual(result["issuer_org"], "DigiCert Inc")
        self.assertEqual(result["status"], "HEALTHY")
        self.assertGreaterEqual(result["days_remaining"], 59)
        self.assertEqual(result["subject_alt_names"], ["example.com", "www.example.com"])

    def test_parse_certificate_expired(self):
        past_date = datetime.now(timezone.utc) - timedelta(days=5)
        past_str = past_date.strftime("%b %d %H:%M:%S %Y GMT")
        older_past_date = datetime.now(timezone.utc) - timedelta(days=365)
        older_past_str = older_past_date.strftime("%b %d %H:%M:%S %Y GMT")

        mock_cert = {
            "subject": ((("commonName", "expired.com"),),),
            "issuer": ((("commonName", "Test CA"),),),
            "subjectAltName": (("DNS", "expired.com"),),
            "notBefore": older_past_str,
            "notAfter": past_str,
            "serialNumber": "9999",
            "version": 3,
        }

        result = parse_certificate(mock_cert, "expired.com")
        self.assertEqual(result["status"], "EXPIRED")
        self.assertLess(result["days_remaining"], 0)

    def test_format_report(self):
        info = {
            "hostname": "test.com",
            "status": "HEALTHY",
            "subject_cn": "test.com",
            "issuer_cn": "Test CA",
            "issuer_org": "Test Org",
            "valid_from": "2026-01-01T00:00:00+00:00",
            "valid_until": "2026-12-31T23:59:59+00:00",
            "days_remaining": 120,
            "serial_number": "1234",
            "subject_alt_names": ["test.com"],
        }
        report = format_report(info)
        self.assertIn("SSL/TLS Certificate Report: test.com", report)
        self.assertIn("HEALTHY", report)
        self.assertIn("Days Remaining   : 120 days", report)


if __name__ == "__main__":
    unittest.main()
