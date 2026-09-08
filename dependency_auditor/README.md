# Dependency & License Compliance Auditor

A CLI utility for inspecting project dependency files (`requirements.txt`, `package.json`) to detect unpinned dependencies, insecure package origins, deprecated libraries, and restrictive copyleft licenses (such as GPL/AGPL).

## Features

- **HTTP Protocol Auditor (`DEP001`)**: Identifies non-HTTPS package download URLs.
- **Unpinned Version Rule (`DEP002`)**: Detects missing version constraints or wildcard ranges (`*`, `^`, `~`).
- **Deprecated Library Scanner (`DEP003`)**: Flags abandoned or legacy libraries.
- **Copyleft License Detection (`LIC001`)**: Audits package licenses for AGPL/GPL incompatibilities.

## Usage

```bash
# Audit Python requirements file
python3 dependency_auditor.py requirements.txt

# Audit Node.js package.json file
python3 dependency_auditor.py package.json

# Export output in JSON format
python3 dependency_auditor.py requirements.txt --json
```

## Running Tests

```bash
PYTHONPATH=. python3 -m pytest dependency_auditor/
```
