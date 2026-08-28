import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env_linter import EnvLinter


class TestEnvLinter(unittest.TestCase):
    def test_parse_env_file(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("PORT=8080\n# Comment\nDB_HOST='localhost'\n")
            f_path = f.name

        try:
            vars = EnvLinter.parse_env_file(f_path)
            self.assertEqual(vars["PORT"], "8080")
            self.assertEqual(vars["DB_HOST"], "localhost")
        finally:
            if os.path.exists(f_path):
                os.remove(f_path)

    def test_compare_example(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as f1, tempfile.NamedTemporaryFile("w", delete=False) as f2:
            f1.write("PORT=8080\n")
            f2.write("PORT=8080\nSECRET_KEY=abc\n")
            p1, p2 = f1.name, f2.name

        try:
            missing = EnvLinter.compare_example(p1, p2)
            self.assertEqual(len(missing), 1)
            self.assertIn("SECRET_KEY", missing[0])
        finally:
            for p in (p1, p2):
                if os.path.exists(p):
                    os.remove(p)


if __name__ == "__main__":
    unittest.main()
