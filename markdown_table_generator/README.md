# CLI Markdown Table Generator & CSV Converter

A lightweight Python CLI tool for parsing CSV and JSON dataset files and rendering clean GFM Markdown tables with sorting, filtering, and custom column alignment options.

## Features
- **CSV & JSON Parser**: Auto-detects input file formats or takes raw input strings.
- **Sorting & Filtering**: Filter dataset rows by column values and sort numerically or alphabetically.
- **Alignment Support**: Supports Left, Right, and Center alignment formatting for individual columns.
- **Zero External Dependencies**: Standard library Python 3.

## Usage

### Interactive Demo
Run without arguments to preview sample output:
```bash
python markdown_table.py
```

### CLI Command Options
```bash
python markdown_table.py input.csv --sort Price --numeric --reverse -o table.md
```

### Running Unit Tests
```bash
python -m unittest test_markdown_table.py
```
