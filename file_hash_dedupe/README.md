# 🔍 CLI File Hash Generator & Duplicate Finder

A high-performance CLI file integrity checksum generator (MD5, SHA256) and directory deduplication scanner.

## Features
- Fast chunked file hash computation
- Recursive directory scanning for exact content duplicates
- Dry-run reporting and automated duplicate cleanup mode

## Usage

```bash
# Compute SHA256 hash of a file
python file_hash_dedupe.py sample.pdf --algo sha256

# Scan directory for duplicate files
python file_hash_dedupe.py /path/to/folder --dedupe

# Delete duplicate copies (keeps first copy)
python file_hash_dedupe.py /path/to/folder --dedupe --delete
```

## Running Tests

```bash
python3 -m unittest test_file_hash_dedupe.py
```
