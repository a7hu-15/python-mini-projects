# ☸️ CLI Kubernetes Manifest Linter & Security Auditor

A CLI utility and Python module to audit Kubernetes YAML/JSON manifests for security risks, missing resource limits, root execution, and unpinned container image tags.

## 🚀 Features

- 🛡️ **Security Context Checking**: Flags `privileged: true` and `allowPrivilegeEscalation: true`.
- 🏷️ **Unpinned Image Tags**: Warns on `:latest` container image tags.
- ⚡ **Resource Limits**: Checks for missing CPU/memory limits and requests.
- 🩺 **Health Probes**: Flags missing `livenessProbe` and `readinessProbe` definitions.

## 🛠️ Usage

### CLI

```bash
python3 k8s_manifest_linter/k8s_manifest_linter.py deployment.yaml
```

### Python API

```python
from k8s_manifest_linter import audit_k8s_manifest

report = audit_k8s_manifest("deployment.yaml")
print(f"Passed: {report['valid']}")
print(f"Errors: {report['errors']}")
```
