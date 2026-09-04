# 🔒 SSL/TLS Certificate Inspector & Expiration Checker

A lightweight CLI tool to inspect domain SSL/TLS certificates, verify validity periods, extract Subject Alternative Names (SANs), and warn when certificates are nearing expiration.

## 🚀 Features

- 📅 Calculates exact days remaining until certificate expiration
- 🚨 Customizable warning threshold (`--warn-days`)
- 🌐 Extracts Common Name (CN), Issuer details, SANs, serial number, and TLS version
- 📊 Supports human-readable ASCII report and structured `--json` output
- ⚙️ Standard library implementation with zero external runtime dependencies

## 💻 Usage

### Basic Domain Inspection
```bash
python3 ssl_cert_inspector/ssl_cert_inspector.py --host github.com
```

### Specify Port, Timeout & Custom Warning Threshold
```bash
python3 ssl_cert_inspector/ssl_cert_inspector.py --host example.com --port 443 --warn-days 14
```

### Output JSON Format for Automation / CI/CD
```bash
python3 ssl_cert_inspector/ssl_cert_inspector.py --host google.com --json
```

## 🧪 Unit Tests

Run the test suite using `unittest`:
```bash
python3 -m unittest ssl_cert_inspector/test_ssl_cert_inspector.py
```
