# 🔒 Log Anonymizer & PII Masker

A CLI tool and Python utility for redacting Personally Identifiable Information (PII) and secret tokens from application logs, stream output, and files.

## 🚀 Features

- **Supported PII Types**: Email addresses, IPv4/IPv6 addresses, Credit Card numbers, SSNs, Phone numbers, JWT Tokens, and API keys.
- **Multiple Masking Strategies**:
  - `placeholder`: Replaces PII with tags like `[EMAIL]`, `[IPV4]`, `[SSN]`.
  - `hash`: Replaces PII with deterministic SHA256 hashes like `[EMAIL:a1b2c3d4]`.
  - `redact`: Replaces PII with redacted blocks (`████████`).
- **Stream Processing**: Pipe log output directly via stdin.

## 🛠️ Usage

### Mask Log Stream via Stdin
```bash
echo "User alice@example.com logged in from 192.168.1.1" | python3 log_anonymizer.py
```

### Anonymize File with Hash Strategy
```bash
python3 log_anonymizer.py input.log --strategy hash --output clean.log
```

### Run Unit Tests
```bash
python3 test_log_anonymizer.py
```
