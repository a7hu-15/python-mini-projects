import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from json_converter import DataConverter


class TestDataConverter(unittest.TestCase):
    def test_dict_to_xml(self):
        data = {"user": {"name": "Alice", "role": "admin"}}
        xml_str = DataConverter.dict_to_xml(data, root_name="config")
        self.assertIn("<config>", xml_str)
        self.assertIn("<name>Alice</name>", xml_str)

    def test_xml_to_dict(self):
        xml_str = "<root><title>Test</title></root>"
        res = DataConverter.xml_to_dict(xml_str)
        self.assertEqual(res, {"root": {"title": "Test"}})


if __name__ == "__main__":
    unittest.main()
