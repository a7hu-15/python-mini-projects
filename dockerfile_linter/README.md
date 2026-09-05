# CLI Dockerfile Linter & Security Auditor

A lightweight CLI tool to audit Dockerfiles for security vulnerabilities, bad practices, unpinned base images, hardcoded secrets, and layer optimization issues.

## 🚀 Features

- **DL001**: Missing non-root `USER` instruction detection.
- **DL002**: Unpinned or `:latest` base image tags.
- **DL003**: `apt-get update` missing package list cleanup (`rm -rf /var/lib/apt/lists/*`).
- **DL004**: Prefer `COPY` over `ADD` for local filesystem resources.
- **DL005**: Missing `HEALTHCHECK` directive.
- **DL007**: Hardcoded credentials / API secret detection in `ENV` / `ARG`.
- **DL008**: Avoid `sudo` usage in `RUN` layers.

## 🛠️ Usage

```bash
python dockerfile_linter.py path/to/Dockerfile
```

## 🧪 Testing

```bash
python -m pytest test_dockerfile_linter.py
```
