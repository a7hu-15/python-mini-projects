# 🏗️ CLI Terraform Security & Best Practices Auditor

A CLI utility and Python module to audit Terraform (`.tf`) files for security vulnerabilities, open ingress rules, unencrypted S3 buckets, hardcoded cloud credentials, and missing tags.

## 🚀 Features

- 🛡️ **Open Ingress Rules**: Flags security groups opening `0.0.0.0/0` access.
- 🔐 **Hardcoded Secret Detection**: Identifies exposed AWS access keys, secret keys, and database passwords.
- 🪣 **S3 Bucket Encryption**: Flags S3 bucket resources lacking server-side encryption.
- 🏷️ **Resource Tags**: Recommends adding standard resource tags.

## 🛠️ Usage

### CLI

```bash
python3 terraform_linter/terraform_linter.py main.tf
```

### Python API

```python
from terraform_linter import audit_tf_manifest

report = audit_tf_manifest("main.tf")
print(f"Passed: {report['valid']}")
print(f"Errors: {report['errors']}")
```
