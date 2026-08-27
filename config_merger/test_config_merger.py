import os
import unittest
from config_merger.config_merger import ConfigMerger

class TestConfigMerger(unittest.TestCase):

    def test_deep_merge(self):
        base = {"a": 1, "b": {"x": 10, "y": 20}}
        override = {"b": {"y": 99, "z": 30}, "c": 3}
        merged = ConfigMerger.deep_merge(base, override)

        self.assertEqual(merged["a"], 1)
        self.assertEqual(merged["b"]["x"], 10)
        self.assertEqual(merged["b"]["y"], 99)
        self.assertEqual(merged["b"]["z"], 30)
        self.assertEqual(merged["c"], 3)

    def test_substitute_env_vars(self):
        os.environ["TEST_HOST"] = "127.0.0.1"
        data = {
            "host": "${TEST_HOST:localhost}",
            "port": "${TEST_PORT:8080}",
            "db": "postgresql://${TEST_HOST}:${TEST_PORT:5432}/db"
        }
        res = ConfigMerger.substitute_env_vars(data)
        self.assertEqual(res["host"], "127.0.0.1")
        self.assertEqual(res["port"], "8080")
        self.assertEqual(res["db"], "postgresql://127.0.0.1:5432/db")

    def test_compute_diff(self):
        d1 = {"server": {"port": 80, "host": "0.0.0.0"}, "active": True}
        d2 = {"server": {"port": 443, "host": "0.0.0.0"}, "ssl": True}

        diffs = ConfigMerger.compute_diff(d1, d2)
        diff_types = {d["path"]: d["type"] for d in diffs}

        self.assertEqual(diff_types.get("server.port"), "MODIFIED")
        self.assertEqual(diff_types.get("active"), "REMOVED")
        self.assertEqual(diff_types.get("ssl"), "ADDED")

if __name__ == "__main__":
    unittest.main()
