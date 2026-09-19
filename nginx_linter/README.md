# 🌐 CLI Nginx & Web Server Security Linter

A CLI utility and Python module to audit Nginx configuration (`.conf`) files for security vulnerabilities, weak SSL/TLS protocols, missing security headers, directory traversal risks, and information disclosure.

## 🚀 Features

- 🛡️ **Information Disclosure**: Detects exposed `server_tokens on;` directive.
- 📁 **Directory Listing**: Flags insecure `autoindex on;` directory browsing.
- 🔒 **TLS Protocol Audit**: Rejects outdated SSLv2, SSLv3, TLSv1, and TLSv1.1 protocols.
- 🧩 **Security Header Checks**: Validates presence of `X-Frame-Options`, `Content-Security-Policy`, `HSTS`, etc.
- ⚠️ **Path Traversal Guard**: Detects trailing slash mismatch in `location` / `alias` definitions.

## 🛠️ Usage

### CLI

```bash
python3 nginx_linter/nginx_linter.py nginx.conf --json
```

### Python API

```python
from nginx_linter import audit_nginx_config

report = audit_nginx_config("nginx.conf")
print(f"Passed: {report['valid']}")
print(f"Errors: {report['errors']}")
```
