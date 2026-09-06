# 🔍 OpenAPI / Swagger Schema Linter & Auditor

A CLI utility built in Python to parse and lint OpenAPI 3.0 / 3.1 schema definitions. It audits API endpoints for design best practices, path parameter consistency, operation metadata, and security rules.

## ✨ Features

- 🎯 **Path Parameter Validation**: Ensures all `{param}` variables in URL templates are explicitly declared in parameters.
- 📋 **Metadata Auditing**: Checks for missing `operationId`, `summary`, `description`, and `info` fields.
- 🛡️ **Security Checks**: Audits references to global `securitySchemes` in `components`.
- 🚨 **Response Standard Verification**: Warns on endpoints missing 4xx/5xx error responses.
- 💻 **CLI Integration**: Formatted human-readable output or machine-parsable JSON report with exit status flags.

## 🚀 Usage

Lint an OpenAPI JSON spec file:

```bash
python -m openapi_linter.openapi_linter path/to/openapi.json
```

Generate JSON output report:

```bash
python -m openapi_linter.openapi_linter path/to/openapi.json --format json
```

Fail build on warnings:

```bash
python -m openapi_linter.openapi_linter path/to/openapi.json --fail-on-warning
```

## 🧪 Running Tests

```bash
python3 -m pytest openapi_linter/
```
