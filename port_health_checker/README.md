# 📡 CLI Network Service Port & Health Monitor

A CLI utility and Python module to audit network endpoints, test TCP port availability, measure connection latency, and check HTTP service health status.

## 🚀 Features

- 🔌 **TCP Port Testing**: Verifies port availability and measures socket connection latency (ms).
- 🌐 **HTTP/HTTPS Endpoint Auditing**: Checks response status codes (2xx/3xx) and latency.
- ⏱️ **Configurable Timeout**: Supports customizable socket & HTTP timeouts for fast CI checks.
- 📊 **JSON Export**: Provides machine-readable structured JSON reports for CI/CD pipelines.

## 🛠️ Usage

### CLI

```bash
# Test TCP Port
python3 port_health_checker/port_health_checker.py --host 127.0.0.1 --port 8080

# Test HTTP Endpoint with JSON output
python3 port_health_checker/port_health_checker.py --url https://httpbin.org/get --json
```

### Python API

```python
from port_health_checker import audit_port_health

targets = [
    {"host": "127.0.0.1", "port": 8080},
    {"url": "https://httpbin.org/get"}
]

report = audit_port_health(targets)
print(f"Healthy: {report['summary']['healthy']}/{report['summary']['total_targets']}")
```
