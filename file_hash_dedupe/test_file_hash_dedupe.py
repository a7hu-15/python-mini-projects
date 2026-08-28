import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from file_hash_dedupe import FileHashDedupe


class TestFileHashDedupe(unittest.TestCase):
    def test_file_hashing(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("Hello Hash World")
            f_path = f.name

        try:
            h = FileHashDedupe.get_file_hash(f_path, "sha256")
            self.assertEqual(len(h), 64)
        finally:
            if os.path.exists(f_path):
                os.remove(f_path)

    def test_find_duplicates(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = os.path.join(tmpdir, "a.txt")
            file2 = os.path.join(tmpdir, "b.txt")
            file3 = os.path.join(tmpdir, "c.txt")

            with open(file1, "w") as f:
                f.write("Duplicate Content")
            with open(file2, "w") as f:
                f.write("Duplicate Content")
            with open(file3, "w") as f:
                f.write("Unique Content")

            dupes = FileHashDedupe.find_duplicates(tmpdir, "sha256")
            self.assertEqual(len(dupes), 1)
            paths = list(dupes.values())[0]
            self.assertEqual(len(paths), 2)


if __name__ == "__main__":
    unittest.main()
