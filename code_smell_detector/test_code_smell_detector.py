import unittest
from code_smell_detector.code_smell_detector import analyze_code_smells


class TestCodeSmellDetector(unittest.TestCase):

    def test_clean_python_code(self):
        code = """
def calculate_total(price: float, tax_rate: float) -> float:
    return price * (1 + tax_rate)

class SimpleCalculator:
    def add(self, a, b):
        return a + b
"""
        report = analyze_code_smells(code)
        self.assertTrue(report["valid"])
        self.assertEqual(report["smell_count"], 0)

    def test_wildcard_and_bare_except(self):
        code = """
from math import *

def process():
    try:
        x = 10 / 0
    except:
        pass
"""
        report = analyze_code_smells(code)
        self.assertFalse(report["valid"])
        smell_types = [s["type"] for s in report["smells"]]
        self.assertIn("wildcard_import", smell_types)
        self.assertIn("bare_except", smell_types)

    def test_too_many_parameters_and_deep_loops(self):
        code = """
def complex_function(a, b, c, d, e, f, g):
    for i in range(10):
        for j in range(10):
            for k in range(10):
                print(i, j, k)
"""
        report = analyze_code_smells(code)
        smell_types = [s["type"] for s in report["smells"]]
        self.assertIn("too_many_parameters", smell_types)
        self.assertIn("deeply_nested_loop", smell_types)


if __name__ == "__main__":
    unittest.main()
