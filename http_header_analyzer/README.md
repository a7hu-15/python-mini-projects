# 🛡️ HTTP Security Header Analyzer

A lightweight Python CLI tool and library for auditing HTTP response headers against OWASP security guidelines and browser defense standards.

## 🚀 Features

- **Header Checks**: HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, X-XSS-Protection.
- **Server Leakage Detection**: Warns if headers like `Server` or `X-Powered-By` expose framework/version details.
- **Scoring & Grading**: Calculates a security score (0–100) and letter grade (A+ through F).
- **Multiple Output Formats**: Text audit summary or machine-readable JSON.

## 🛠️ Usage

### Run Default Audit
```bash
python3 http_header_analyzer.py
```

### Analyze Custom Headers via JSON
```bash
python3 http_header_analyzer.py --json '{"Strict-Transport-Security": "max-age=31536000", "X-Frame-Options": "DENY"}' --format text
```

### Run Unit Tests
```bash
python3 -m unittest test_http_header_analyzer.py
```
