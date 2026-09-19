#!/usr/bin/env python3
"""
CLI Network Service Port & Health Monitor.

Audits network endpoints for TCP connection connectivity, latency response times,
SSL/TLS handshake validity, and HTTP response status codes.
"""

import argparse
import json
import socket
import ssl
import sys
import time
import urllib.request
from typing import Dict, List, Any, Optional, Tuple


def check_tcp_port(host: str, port: int, timeout: float = 3.0) -> Tuple[bool, float, Optional[str]]:
    """
    Attempts a TCP connection to host:port and measures connection latency in milliseconds.
    """
    start = time.perf_counter()
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return True, latency_ms, None
    except Exception as e:
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return False, latency_ms, str(e)


def check_http_health(url: str, timeout: float = 3.0) -> Tuple[bool, int, float, Optional[str]]:
    """
    Checks HTTP/HTTPS endpoint availability, status code, and latency.
    """
    start = time.perf_counter()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PortHealthChecker/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status_code = resp.getcode()
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            is_ok = 200 <= status_code < 400
            return is_ok, status_code, latency_ms, None
    except urllib.error.HTTPError as he:
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return False, he.code, latency_ms, f"HTTP Error {he.code}"
    except Exception as e:
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return False, 0, latency_ms, str(e)


def audit_port_health(targets: List[Dict[str, Any]], timeout: float = 3.0) -> Dict[str, Any]:
    """
    Audits a list of target dictionaries:
    Each target can be {"host": "localhost", "port": 8080} or {"url": "http://localhost:8080/health"}
    """
    results: List[Dict[str, Any]] = []

    for target in targets:
        if "url" in target:
            url = target["url"]
            is_ok, status_code, latency_ms, err = check_http_health(url, timeout=timeout)
            results.append({
                "target": url,
                "type": "http",
                "healthy": is_ok,
                "status_code": status_code,
                "latency_ms": latency_ms,
                "error": err
            })
        elif "host" in target and "port" in target:
            host = target["host"]
            port = int(target["port"])
            is_ok, latency_ms, err = check_tcp_port(host, port, timeout=timeout)
            results.append({
                "target": f"{host}:{port}",
                "type": "tcp",
                "healthy": is_ok,
                "latency_ms": latency_ms,
                "error": err
            })

    total = len(results)
    healthy_count = sum(1 for r in results if r["healthy"])
    all_healthy = total > 0 and healthy_count == total

    return {
        "valid": all_healthy,
        "summary": {
            "total_targets": total,
            "healthy": healthy_count,
            "unhealthy": total - healthy_count
        },
        "results": results
    }


def main():
    parser = argparse.ArgumentParser(description="CLI Network Service Port & Health Monitor")
    parser.add_argument("--host", type=str, help="Host name or IP address (e.g. 127.0.0.1 or google.com)")
    parser.add_argument("--port", type=int, help="Port number (e.g. 80, 443, 8080)")
    parser.add_argument("--url", type=str, help="HTTP/HTTPS endpoint URL to test (e.g. https://httpbin.org/get)")
    parser.add_argument("--timeout", type=float, default=3.0, help="Connection timeout in seconds (default: 3.0)")
    parser.add_argument("--json", action="store_true", help="Output audit report in JSON format")

    args = parser.parse_args()

    targets = []
    if args.url:
        targets.append({"url": args.url})
    if args.host and args.port:
        targets.append({"host": args.host, "port": args.port})

    if not targets:
        print("Error: Please specify either --url or both --host and --port.", file=sys.stderr)
        sys.exit(2)

    report = audit_port_health(targets, timeout=args.timeout)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("\n📡 Service Port & Health Monitor Report")
        print("=" * 60)
        summary = report["summary"]
        print(f"Status: {'✅ ALL HEALTHY' if report['valid'] else '⚠️ SERVICE ISSUES DETECTED'}")
        print(f"Targets Tested: {summary['total_targets']} | Healthy: {summary['healthy']} | Unhealthy: {summary['unhealthy']}\n")

        for res in report["results"]:
            icon = "✅" if res["healthy"] else "❌"
            if res["type"] == "http":
                print(f"  {icon} [HTTP] {res['target']} - Code: {res['status_code']} - {res['latency_ms']} ms")
            else:
                print(f"  {icon} [TCP]  {res['target']} - {res['latency_ms']} ms")
            if res["error"]:
                print(f"      Reason: {res['error']}")
        print()

    if not report["valid"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
