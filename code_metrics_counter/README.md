# CLI Code Metrics & LOC Counter

A Python command line tool that scans project source code, calculates total lines, code logic, comments, and blank lines categorized by file extension, and produces summary reports.

## Features
- **Multi-language Support**: Automatically recognizes comment syntax for Python, JavaScript, TypeScript, C/C++, Java, Go, Rust, HTML, CSS, YAML, and Shell.
- **Recursive Directory Scan**: Traverses project structures while ignoring common directories (`.git`, `node_modules`, `venv`).
- **Flexible Reports**: Formats output as an ASCII console table or structured JSON.

## Usage

### Scan Current Directory
```bash
python code_metrics.py
```

### Scan Specific Path with Exclusions
```bash
python code_metrics.py /path/to/project --exclude build dist --json
```

### Run Unit Tests
```bash
python -m unittest test_code_metrics.py
```
