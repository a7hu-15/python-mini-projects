"""CLI Log File Analyzer & Metrics Aggregator.

A command-line tool for parsing web server access logs (Nginx / Apache combined format), aggregating metrics such as HTTP status code breakdown, top IP addresses, most requested endpoints, total bandwidth served, and error rate tracking.

>>> analyzer = LogAnalyzer()
>>> sample_line = '192.168.1.1 - - [26/Aug/2026:10:00:00 +0000] "GET /api/v1/users HTTP/1.1" 200 1024 "-" "Mozilla/5.0"'
>>> record = analyzer.parse_line(sample_line)
>>> record['ip']
'192.168.1.1'
>>> record['status']
200
>>> record['path']
'/api/v1/users'
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional


class LogAnalyzer:
    # Standard Nginx / Apache combined log pattern
    LOG_PATTERN = re.compile(
        r'^(?P<ip>[\w\.:-]+)\s+\S+\s+\S+\s+\[(?P<time>[^\]]+)\]\s+"(?P<method>[A-Z]+)\s+(?P<path>\S+)\s+[^\"]+"\s+(?P<status>\d{3})\s+(?P<size>\d+|-)'
    )

    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        match = self.LOG_PATTERN.match(line.strip())
        if not match:
            return None

        data = match.groupdict()
        size_bytes = 0 if data["size"] == "-" else int(data["size"])

        return {
            "ip": data["ip"],
            "timestamp": data["time"],
            "method": data["method"],
            "path": data["path"],
            "status": int(data["status"]),
            "size": size_bytes,
        }

    def analyze_logs(self, log_lines: List[str]) -> Dict[str, Any]:
        total_requests = 0
        parsed_count = 0
        failed_count = 0
        total_bandwidth = 0

        ip_counter: Counter[str] = Counter()
        endpoint_counter: Counter[str] = Counter()
        status_counter: Counter[int] = Counter()
        method_counter: Counter[str] = Counter()
        error_count = 0

        for line in log_lines:
            if not line.strip() or line.startswith("#"):
                continue

            total_requests += 1
            record = self.parse_line(line)

            if not record:
                failed_count += 1
                continue

            parsed_count += 1
            ip_counter[record["ip"]] += 1
            endpoint_counter[record["path"]] += 1
            status_counter[record["status"]] += 1
            method_counter[record["method"]] += 1
            total_bandwidth += record["size"]

            if record["status"] >= 400:
                error_count += 1

        error_rate = (error_count / parsed_count * 100) if parsed_count > 0 else 0.0

        return {
            "total_lines_read": total_requests,
            "parsed_requests": parsed_count,
            "failed_lines": failed_count,
            "total_bandwidth_bytes": total_bandwidth,
            "total_bandwidth_mb": round(total_bandwidth / (1024 * 1024), 2),
            "error_rate_percentage": round(error_rate, 2),
            "top_ips": dict(ip_counter.most_common(5)),
            "top_endpoints": dict(endpoint_counter.most_common(5)),
            "status_codes": dict(status_counter),
            "http_methods": dict(method_counter),
        }


SAMPLE_LOGS = [
    '192.168.1.10 - - [26/Aug/2026:10:00:01 +0000] "GET /index.html HTTP/1.1" 200 2048 "-" "Mozilla/5.0"',
    '192.168.1.11 - - [26/Aug/2026:10:00:02 +0000] "GET /api/v1/data HTTP/1.1" 200 5120 "-" "Mozilla/5.0"',
    '192.168.1.10 - - [26/Aug/2026:10:00:03 +0000] "POST /api/v1/login HTTP/1.1" 200 1280 "-" "Mozilla/5.0"',
    '192.168.1.12 - - [26/Aug/2026:10:00:04 +0000] "GET /images/logo.png HTTP/1.1" 304 0 "-" "Mozilla/5.0"',
    '192.168.1.13 - - [26/Aug/2026:10:00:05 +0000] "GET /admin HTTP/1.1" 403 512 "-" "Mozilla/5.0"',
    '192.168.1.14 - - [26/Aug/2026:10:00:06 +0000] "GET /missing HTTP/1.1" 404 320 "-" "Mozilla/5.0"',
    '192.168.1.10 - - [26/Aug/2026:10:00:07 +0000] "GET /api/v1/data HTTP/1.1" 500 150 "-" "Mozilla/5.0"',
]


def main():
    parser = argparse.ArgumentParser(description="CLI Log File Analyzer & Metrics Aggregator")
    parser.add_argument("--log", help="Path to HTTP access log file")
    parser.add_argument("--output", help="Optional path to export JSON metrics report")
    parser.add_argument("--cli", action="store_true", help="Run interactive CLI demo")

    args = parser.parse_args()

    analyzer = LogAnalyzer()

    if args.cli or not args.log:
        print("=== CLI Log File Analyzer Demo ===")
        print(f"Parsing {len(SAMPLE_LOGS)} sample log lines...\n")
        report = analyzer.analyze_logs(SAMPLE_LOGS)
        print("Log Analysis Metrics:")
        print(json.dumps(report, indent=2))
        return

    log_file = Path(args.log)
    if not log_file.exists():
        print(f"Error: Log file '{log_file}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    report = analyzer.analyze_logs(lines)

    print("\n================ LOG ANALYSIS SUMMARY ================")
    print(f"Total Requests Analyzed: {report['parsed_requests']}")
    print(f"Total Bandwidth: {report['total_bandwidth_mb']} MB ({report['total_bandwidth_bytes']} bytes)")
    print(f"Error Rate: {report['error_rate_percentage']}%")

    print("\nTop IP Addresses:")
    for ip, count in report["top_ips"].items():
        print(f"  {ip:18} -> {count} requests")

    print("\nTop Endpoints:")
    for path, count in report["top_endpoints"].items():
        print(f"  {path:30} -> {count} requests")

    print("\nHTTP Status Codes:")
    for code, count in report["status_codes"].items():
        print(f"  {code} -> {count} responses")

    if args.output:
        out_path = Path(args.output)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"\nSaved analysis metrics to '{out_path}'")


if __name__ == "__main__":
    main()
