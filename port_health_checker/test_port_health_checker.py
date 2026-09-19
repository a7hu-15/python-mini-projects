import unittest
from port_health_checker.port_health_checker import check_tcp_port, audit_port_health


class TestPortHealthChecker(unittest.TestCase):

    def test_check_tcp_port_failure(self):
        # Port 59999 should not be listening locally
        is_ok, latency, err = check_tcp_port("127.0.0.1", 59999, timeout=0.1)
        self.assertFalse(is_ok)
        self.assertIsNotNone(err)

    def test_audit_port_health_mixed(self):
        targets = [
            {"host": "127.0.0.1", "port": 59999}
        ]
        report = audit_port_health(targets, timeout=0.1)
        self.assertFalse(report["valid"])
        self.assertEqual(report["summary"]["healthy"], 0)
        self.assertEqual(report["summary"]["unhealthy"], 1)


if __name__ == "__main__":
    unittest.main()
