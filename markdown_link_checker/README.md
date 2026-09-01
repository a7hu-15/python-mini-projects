# 🔗 Markdown Link & Anchor Checker CLI

A fast, lightweight CLI utility for validating local file paths, media references, and Markdown heading anchors (`#heading-slug`) across project documentation.

## ✨ Features

- 🔍 **Relative File Path Validation**: Ensures linked relative paths and image files exist on disk.
- ⚓ **Heading Anchor Inspection**: Automatically slugifies headers (`#header-name`) and verifies anchor target existence.
- 📂 **Recursive Repository Scanning**: Scans single files or entire nested markdown directory trees.
- ⚡ **Zero External Dependencies**: Built entirely with Python standard library.

## 🚀 Usage

### Check a Single Markdown File

```bash
python markdown_link_checker.py README.md
```

### Check an Entire Directory Recursively

```bash
python markdown_link_checker.py ./docs
```

## 🧪 Running Tests

Run the test suite using `unittest`:

```bash
python -m unittest test_markdown_link_checker.py
```
