# 🧩 CLI Python Code Smell & Maintainability Detector

A CLI utility and Python module that uses Python's built-in `ast` parser to analyze Python source code for maintainability smells, anti-patterns, and structural complexity.

## 🚀 Features

- 📦 **Wildcard Import Guard**: Detects `from module import *` statements.
- 🚨 **Exception Anti-Pattern Detection**: Flags bare `except:` and broad `except Exception:` clauses.
- 📏 **Function Length & Parameter Count**: Flags functions with > 30 lines or > 5 parameters.
- 🌀 **Deep Loop Nesting**: Detects nested loop structures exceeding 3 levels of depth.
- 🏗️ **Large Class Smell**: Flags classes exceeding 8 methods.

## 🛠️ Usage

### CLI

```bash
python3 code_smell_detector/code_smell_detector.py my_script.py --json
```

### Python API

```python
from code_smell_detector import analyze_code_smells

report = analyze_code_smells("my_script.py")
print(f"Smells found: {report['smell_count']}")
for smell in report['smells']:
    print(smell['message'])
```
