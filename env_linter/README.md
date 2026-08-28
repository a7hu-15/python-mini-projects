# 🛡️ CLI Environment Variables (.env) Linter & Secret Inspector

A developer utility for syntax validation, formatting check, missing variable detection, and credential leak scanning across `.env` files.

## Features
- Syntax and key naming convention check (UPPERCASE_WITH_UNDERSCORES)
- Secret detection (AWS keys, GitHub tokens, RSA private keys, Stripe live keys)
- Automatic key comparison between `.env` and `.env.example` template files

## Usage

```bash
# Lint current .env file
python env_linter.py .env

# Compare against .env.example template
python env_linter.py .env --example .env.example
```

## Running Tests

```bash
python3 -m unittest test_env_linter.py
```
