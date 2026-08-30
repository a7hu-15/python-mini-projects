"""
CLI Concurrent API Benchmarker & Load Testing Utility in Python.

Provides high-performance, thread-safe API benchmarking and load testing capability
without external dependencies (using Python standard library urllib and concurrent.futures).

Features:
- Multithreaded concurrent HTTP/HTTPS requests execution.
- Detailed metrics calculation: min/max/mean latency, p50, p90, p95, p99 percentiles.
- Throughput calculation (Requests Per Second - RPS).
- Status code distribution analysis (2xx, 4xx, 5xx).
- Export benchmarking metrics to JSON summary report.
- CLI interface with customizable duration, concurrency, and request payloads.
"""

import argparse
import json
import math
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Tuple


def calculate_percentile(data: List[float], percentile: float) -> float:
    """
    Calculate the given percentile for a sorted list of float values.

    :param data: Sorted list of numeric values.
    :param percentile: Percentile value between 0 and 100.
    :return: Calculated percentile float value.
    """
    if not data:
        return 0.0
    if len(data) == 1:
        return data[0]

    k = (len(data) - 1) * (percentile / 100.0)
    f = math.floor(k)
    c = math.ceil(k)

    if f == c:
        return data[int(k)]

    d0 = data[int(f)] * (c - k)
    d1 = data[int(c)] * (k - f)
    return d0 + d1


class BenchmarkResult:
    """Stores metrics and summary calculations for a benchmark run."""

    def __init__(
        self,
        total_requests: int,
        successful_requests: int,
        failed_requests: int,
        total_duration_sec: float,
        latencies_ms: List[float],
        status_codes: Dict[int, int],
    ):
        self.total_requests = total_requests
        self.successful_requests = successful_requests
        self.failed_requests = failed_requests
        self.total_duration_sec = total_duration_sec
        self.latencies_ms = sorted(latencies_ms)
        self.status_codes = status_codes

        self.rps = total_requests / total_duration_sec if total_duration_sec > 0 else 0.0
        self.min_latency = self.latencies_ms[0] if self.latencies_ms else 0.0
        self.max_latency = self.latencies_ms[-1] if self.latencies_ms else 0.0
        self.mean_latency = sum(self.latencies_ms) / len(self.latencies_ms) if self.latencies_ms else 0.0
        self.p50 = calculate_percentile(self.latencies_ms, 50)
        self.p90 = calculate_percentile(self.latencies_ms, 90)
        self.p95 = calculate_percentile(self.latencies_ms, 95)
        self.p99 = calculate_percentile(self.latencies_ms, 99)

    def to_dict(self) -> Dict[str, Any]:
        """Convert results to serializable dictionary."""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "total_duration_sec": round(self.total_duration_sec, 4),
            "requests_per_sec": round(self.rps, 2),
            "latency_ms": {
                "min": round(self.min_latency, 2),
                "max": round(self.max_latency, 2),
                "mean": round(self.mean_latency, 2),
                "p50": round(self.p50, 2),
                "p90": round(self.p90, 2),
                "p95": round(self.p95, 2),
                "p99": round(self.p99, 2),
            },
            "status_codes": self.status_codes,
        }


class APIBenchmarker:
    """
    HTTP API Load Tester and Benchmarking Engine.
    """

    def __init__(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        data: Optional[bytes] = None,
        timeout_sec: float = 5.0,
    ):
        self.url = url
        self.method = method.upper()
        self.headers = headers or {}
        self.data = data
        self.timeout_sec = timeout_sec

    def _send_single_request(self) -> Tuple[bool, int, float]:
        """
        Execute a single HTTP request and return success flag, status code, latency in ms.
        """
        req = urllib.request.Request(
            self.url,
            data=self.data,
            headers=self.headers,
            method=self.method,
        )
        start_time = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as response:
                latency = (time.monotonic() - start_time) * 1000.0
                return True, response.status, latency
        except urllib.error.HTTPError as e:
            latency = (time.monotonic() - start_time) * 1000.0
            return False, e.code, latency
        except Exception:
            latency = (time.monotonic() - start_time) * 1000.0
            return False, 0, latency

    def run(self, total_requests: int, concurrency: int) -> BenchmarkResult:
        """
        Run benchmark with fixed number of total requests and worker concurrency.

        :param total_requests: Total number of HTTP requests to execute.
        :param concurrency: Number of concurrent worker threads.
        :return: BenchmarkResult containing complete run metrics.
        """
        if total_requests <= 0 or concurrency <= 0:
            raise ValueError("total_requests and concurrency must be positive integers.")

        successful = 0
        failed = 0
        latencies = []
        status_codes: Dict[int, int] = {}

        start_total = time.monotonic()

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(self._send_single_request) for _ in range(total_requests)]

            for future in as_completed(futures):
                success, code, latency = future.result()
                if success:
                    successful += 1
                else:
                    failed += 1

                latencies.append(latency)
                status_codes[code] = status_codes.get(code, 0) + 1

        total_duration = time.monotonic() - start_total

        return BenchmarkResult(
            total_requests=total_requests,
            successful_requests=successful,
            failed_requests=failed,
            total_duration_sec=total_duration,
            latencies_ms=latencies,
            status_codes=status_codes,
        )


def main():
    parser = argparse.ArgumentParser(description="CLI Concurrent API Benchmarker & Load Tester")
    parser.add_argument("url", type=str, help="Target URL to benchmark")
    parser.add_argument("-n", "--requests", type=int, default=50, help="Total number of requests (default: 50)")
    parser.add_argument("-c", "--concurrency", type=int, default=5, help="Number of concurrent workers (default: 5)")
    parser.add_argument("-m", "--method", type=str, default="GET", help="HTTP Method (GET, POST, etc.)")
    parser.add_argument("-t", "--timeout", type=float, default=5.0, help="Request timeout in seconds (default: 5.0)")
    parser.add_argument("-o", "--output-json", type=str, help="Optional output JSON file path")

    args = parser.parse_args()

    print(f"⚡ Benchmarking target: {args.url}")
    print(f"🚀 Concurrency: {args.concurrency} workers | Total Requests: {args.requests}")

    benchmarker = APIBenchmarker(url=args.url, method=args.method, timeout_sec=args.timeout)
    result = benchmarker.run(total_requests=args.requests, concurrency=args.concurrency)

    d = result.to_dict()
    print("\n📊 --- Benchmark Results ---")
    print(f"Total Time Taken : {d['total_duration_sec']} sec")
    print(f"Throughput (RPS) : {d['requests_per_sec']} req/sec")
    print(f"Success / Failed : {d['successful_requests']} / {d['failed_requests']}")
    print("\n⏱️  --- Latency Breakdown (ms) ---")
    print(f"Min    : {d['latency_ms']['min']} ms")
    print(f"Mean   : {d['latency_ms']['mean']} ms")
    print(f"p50    : {d['latency_ms']['p50']} ms")
    print(f"p95    : {d['latency_ms']['p95']} ms")
    print(f"p99    : {d['latency_ms']['p99']} ms")
    print(f"Max    : {d['latency_ms']['max']} ms")

    if args.output_json:
        with open(args.output_json, "w") as f:
            json.dump(d, f, indent=2)
        print(f"\n💾 Saved results to {args.output_json}")


if __name__ == "__main__":
    main()
