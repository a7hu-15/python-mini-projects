# 🔒 CLI Secret & Sensitive Data Scanner

A zero-dependency Python CLI tool and library for scanning repositories, codebases, and configuration files to detect leaked API keys, tokens, credentials, and private keys.

## 🌟 Features

- **Zero External Dependencies**: Built with Python 3 standard libraries (`re`, `pathlib`, `json`, `argparse`).
- **Comprehensive Detection Rules**:
  - AWS Access Keys (`AKIA...`) & Secret Access Keys
  - GitHub Personal Access Tokens (`ghp_...`, `github_pat_...`)
  - Stripe Secret Keys (`sk_live_...`)
  - OpenAI API Keys (`sk-...`)
  - Slack Bot Tokens & Webhooks (`xoxb-...`, `https://hooks.slack.com/...`)
  - RSA / DSA / EC Private Key Headers (`-----BEGIN PRIVATE KEY-----`)
  - JSON Web Tokens (JWT) & Generic Bearer Tokens
- **Smart Directory Traversal**: Automatically skips binary files and common directories (`.git`, `node_modules`, `.venv`, `.pytest_cache`, `dist`).
- **Redaction / Masking**: Redacts discovered secrets (`sk_test_...` -> `sk_******************def`) in safe console logs.
- **Export Options**: Formatted CLI terminal tables or JSON output for CI/CD integration.

## 🚀 Quick Start

### Command Line Interface

Scan the current directory:

```bash
python secret_scanner/secret_scanner.py
```

Scan a specific file or directory with JSON output:

```bash
python secret_scanner/secret_scanner.py ./my_project --json
```

Display unmasked secrets:

```bash
python secret_scanner/secret_scanner.py ./my_project --unmask
```

Filter by minimum severity:

```bash
python secret_scanner/secret_scanner.py . --severity HIGH
```

### Python Library Usage

```python
from secret_scanner import SecretScanner

scanner = SecretScanner()
findings = scanner.scan_directory("./src")

for finding in findings:
    print(f"[{finding.severity}] {finding.rule_name} at {finding.file_path}:{finding.line_number}")
```

## 🧪 Testing

Run unit tests with Python's built-in test runner:

```bash
python3 -m unittest secret_scanner/test_secret_scanner.py
```
