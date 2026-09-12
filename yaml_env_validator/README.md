# ⚙️ CLI YAML & Environment Configuration Validator

A lightweight CLI tool and Python module to audit `.env` and configuration files for syntax errors, secret leaks, missing mandatory fields, and formatting violations.

## 🚀 Features

- 🔒 **Hardcoded Secret Detection**: Identifies exposed AWS credentials, JWT tokens, private keys, and API keys.
- ❌ **Syntax Validation**: Flags missing `=` operators or malformed lines.
- ⚠️ **Empty Value Warnings**: Flags empty environment variables intended for production runtime.
- 🔤 **Naming Conventions**: Warns on non-`SCREAMING_SNAKE_CASE` keys.

## 🛠️ Usage

### CLI

```bash
python3 yaml_env_validator/yaml_env_validator.py .env
```

### Python API

```python
from yaml_env_validator import audit_config_file

report = audit_config_file(".env")
print(f"Valid: {report['valid']}")
print(f"Errors: {report['errors']}")
```
