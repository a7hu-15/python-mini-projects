# 🔗 CLI URL Shortener

A lightweight, hash-based local URL shortener utility written in Python with JSON storage and click analytics.

## Features
- Hash-based short code generation (SHA-256)
- Click counter and analytics tracking
- Persistent JSON file storage
- Interactive CLI and command-line argument modes

## Quick Start

```bash
# Shorten a URL
python url_shortener.py shorten https://example.com/very/long/path

# Resolve a short code
python url_shortener.py resolve <short_code>

# List all mappings
python url_shortener.py list

# View analytics
python url_shortener.py stats
```

## Running Tests

```bash
python3 -m unittest test_url_shortener.py
```
