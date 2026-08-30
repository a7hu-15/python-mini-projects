# ⚡ Concurrent API Benchmarker & Load Tester

A lightweight, zero-dependency Python CLI tool for concurrent HTTP API benchmarking and load testing.

## 🚀 Features

- **Concurrent Execution**: Multithreaded requests via `ThreadPoolExecutor`.
- **Latency Percentiles**: Calculates `p50`, `p90`, `p95`, `p99`, min, max, and mean response times.
- **RPS Calculation**: Measures throughput in Requests Per Second.
- **Status Breakdown**: Tracks 2xx, 4xx, 5xx HTTP response codes.
- **JSON Export**: Export results to JSON format for CI/CD integration.

## 🛠️ Usage

Run directly via python CLI:

```bash
python api_benchmarker.py https://httpbin.org/get -n 50 -c 10
```

### Options

| Flag | Long Flag | Description | Default |
|------|-----------|-------------|---------|
| `-n` | `--requests` | Total requests to execute | `50` |
| `-c` | `--concurrency` | Number of worker threads | `5` |
| `-m` | `--method` | HTTP method (GET, POST) | `GET` |
| `-t` | `--timeout` | Request timeout (sec) | `5.0` |
| `-o` | `--output-json` | Output JSON file path | `None` |

## 🧪 Testing

Run unit tests:

```bash
python3 -m unittest test_api_benchmarker.py
```
