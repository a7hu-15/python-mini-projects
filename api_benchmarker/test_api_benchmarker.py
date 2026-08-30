"""
Unit tests for API Benchmarker & Load Tester.
"""

import unittest
from unittest.mock import MagicMock, patch
from api_benchmarker import APIBenchmarker, BenchmarkResult, calculate_percentile


class TestAPIBenchmarker(unittest.TestCase):

    def test_calculate_percentile(self):
        data = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
        self.assertEqual(calculate_percentile(data, 0), 10.0)
        self.assertEqual(calculate_percentile(data, 100), 100.0)
        self.assertAlmostEqual(calculate_percentile(data, 50), 55.0)

    def test_benchmark_result_metrics(self):
        latencies = [10.0, 20.0, 30.0, 40.0, 50.0]
        status_codes = {200: 5}
        res = BenchmarkResult(
            total_requests=5,
            successful_requests=5,
            failed_requests=0,
            total_duration_sec=2.0,
            latencies_ms=latencies,
            status_codes=status_codes,
        )
        d = res.to_dict()
        self.assertEqual(d["total_requests"], 5)
        self.assertEqual(d["requests_per_sec"], 2.5)
        self.assertEqual(d["latency_ms"]["min"], 10.0)
        self.assertEqual(d["latency_ms"]["max"], 50.0)
        self.assertEqual(d["latency_ms"]["mean"], 30.0)

    @patch("urllib.request.urlopen")
    def test_benchmarker_run_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        benchmarker = APIBenchmarker(url="http://example.com")
        res = benchmarker.run(total_requests=10, concurrency=2)

        self.assertEqual(res.total_requests, 10)
        self.assertEqual(res.successful_requests, 10)
        self.assertEqual(res.failed_requests, 0)
        self.assertIn(200, res.status_codes)
        self.assertEqual(res.status_codes[200], 10)


if __name__ == "__main__":
    unittest.main()
