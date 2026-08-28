# 🔐 CLI Password Strength Checker & Generator

A security utility to evaluate password complexity, compute entropy scores, detect common patterns, and generate cryptographically strong passwords.

## Features
- Detailed security evaluation (length, character diversity, uniqueness, common patterns)
- Actionable feedback and improvement suggestions
- Visual strength bar display
- Cryptographically secure password generator using Python's `secrets` module

## Usage

```bash
# Evaluate a password
python password_checker.py "MyP@ssw0rd!2026"

# Generate a strong password interactively
python password_checker.py
```

## Running Tests

```bash
python3 -m unittest test_password_checker.py
```
