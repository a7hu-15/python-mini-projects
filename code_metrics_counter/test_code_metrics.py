import os
import tempfile
import unittest
from code_metrics_counter.code_metrics import CodeMetricsCounter

class TestCodeMetricsCounter(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_analyze_python_file(self):
        py_content = """# Header comment
def hello():
    # Print greeting
    print("Hello World")

# End of file
"""
        file_path = os.path.join(self.temp_dir.name, "sample.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(py_content)

        counter = CodeMetricsCounter(self.temp_dir.name)
        metrics = counter.analyze_file(file_path)

        self.assertEqual(metrics["total"], 6)
        self.assertEqual(metrics["blank"], 1)
        self.assertEqual(metrics["comment"], 3)
        self.assertEqual(metrics["code"], 2)

    def test_scan_directory(self):
        py_file = os.path.join(self.temp_dir.name, "test.py")
        js_file = os.path.join(self.temp_dir.name, "test.js")

        with open(py_file, "w", encoding="utf-8") as f:
            f.write("# comment\nx = 10\n")
        with open(js_file, "w", encoding="utf-8") as f:
            f.write("// JS comment\nconsole.log('hi');\n")

        counter = CodeMetricsCounter(self.temp_dir.name)
        results = counter.scan()

        self.assertEqual(results["total_files"], 2)
        self.assertIn(".py", results["by_extension"])
        self.assertIn(".js", results["by_extension"])
        self.assertEqual(results["summary"]["total_lines"], 4)

    def test_format_report(self):
        counter = CodeMetricsCounter(self.temp_dir.name)
        results = counter.scan()
        report = counter.format_report(results)
        self.assertIn("Code Metrics Report", report)
        self.assertIn("TOTALS", report)

if __name__ == "__main__":
    unittest.main()
