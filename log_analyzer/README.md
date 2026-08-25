# 📊 CLI Log File Analyzer & Metrics Aggregator

A command-line HTTP log parser and analytics tool for Nginx and Apache combined access logs.

## 🌟 Features

- **Regex Log Parsing**: Extracts IP, timestamp, HTTP method, URI path, status code, and response payload size.
- **Key Metrics Aggregation**:
  - Top IP clients
  - Top requested URI endpoints
  - HTTP Status Code distribution (200s, 300s, 400s, 500s)
  - HTTP method breakdown (GET, POST, etc.)
  - Total bandwidth consumption (Bytes & MB)
  - Error rate tracking percentage
- **JSON Export**: Export metrics summary for monitoring dashboards.

## 🚀 Usage

### Run Built-in Demo
```bash
python log_analyzer/log_analyzer.py --cli
```

### Analyze Log File
```bash
python log_analyzer/log_analyzer.py --log /var/log/nginx/access.log --output metrics.json
```
