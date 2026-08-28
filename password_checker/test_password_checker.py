import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from password_checker import check_password_strength, generate_strong_password


class TestPasswordChecker(unittest.TestCase):
    def test_weak_passwords(self):
        res = check_password_strength("12345")
        self.assertIn(res["strength"], ["Very Weak", "Weak"])

    def test_strong_passwords(self):
        res = check_password_strength("K9#m$P2!xL8@qW1z")
        self.assertIn(res["strength"], ["Strong", "Very Strong"])

    def test_generate_password(self):
        pwd = generate_strong_password(20)
        self.assertEqual(len(pwd), 20)
        res = check_password_strength(pwd)
        self.assertGreaterEqual(res["score"], 6)


if __name__ == "__main__":
    unittest.main()
