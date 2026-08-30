# 🔑 JWT Inspector & Claims Decoder

A zero-dependency Python CLI tool and library for inspecting, decoding, and validating JSON Web Tokens (JWTs).

## 🌟 Features

- **Zero External Dependencies**: Pure Python implementation using `base64` and `json`.
- **Claims Analysis**: Inspects `exp`, `nbf`, `iat`, `iss`, `sub`, and `aud` claims.
- **Expiration Detection**: Automatically checks token expiration status and calculates remaining validity duration.
- **CLI & JSON Export**: Pretty-printed console output or structured JSON exports for automation scripts.

## 🚀 Usage

### Command Line Interface

```bash
python jwt_inspector.py "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
```

### Python API

```python
from jwt_inspector import JWTInspector

inspector = JWTInspector("<your_jwt_token>")
print(inspector.header)
print(inspector.payload)

analysis = inspector.inspect_claims()
print(analysis["status"])
```

## 🧪 Testing

Run pytest or unittest:

```bash
pytest test_jwt_inspector.py
```
