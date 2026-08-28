import os
import unittest
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from url_shortener import URLShortener


class TestURLShortener(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_url_store.json"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.shortener = URLShortener(storage_file=self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_shorten_and_resolve(self):
        url = "https://example.org/test"
        code = self.shortener.shorten(url)
        self.assertEqual(len(code), 6)
        resolved = self.shortener.resolve(code)
        self.assertEqual(resolved, url)

    def test_click_tracking(self):
        url = "https://example.com"
        code = self.shortener.shorten(url)
        self.assertEqual(self.shortener.get_stats()["total_clicks"], 0)
        self.shortener.resolve(code)
        self.assertEqual(self.shortener.get_stats()["total_clicks"], 1)

    def test_delete(self):
        url = "https://example.com/delete"
        code = self.shortener.shorten(url)
        self.assertTrue(self.shortener.delete(code))
        self.assertIsNone(self.shortener.resolve(code))


if __name__ == "__main__":
    unittest.main()
