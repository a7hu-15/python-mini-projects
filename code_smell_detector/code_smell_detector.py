#!/usr/bin/env python3
"""
CLI Code Smell & Maintainability Detector.

Uses Python's built-in AST module to analyze Python source code for maintainability smells:
- Long functions (> 30 lines)
- Excessive parameters (> 5 parameters)
- Wildcard imports (from module import *)
- Broad exception handling (except Exception or bare except)
- Deep loop nesting (depth >= 3)
- Large classes (> 8 methods)
"""

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Union


class CodeSmellVisitor(ast.NodeVisitor):
    def __init__(self, max_func_lines=30, max_params=5, max_class_methods=8):
        self.max_func_lines = max_func_lines
        self.max_params = max_params
        self.max_class_methods = max_class_methods

        self.smells: List[Dict[str, Any]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._check_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._check_function(node)
        self.generic_visit(node)

    def _check_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]):
        # 1. Parameter count check
        num_args = len(node.args.args) + len(node.args.kwonlyargs)
        if node.args.vararg:
            num_args += 1
        if node.args.kwarg:
            num_args += 1

        # Ignore 'self' or 'cls' count if method
        first_arg = node.args.args[0].arg if node.args.args else None
        if first_arg in ("self", "cls"):
            num_args -= 1

        if num_args > self.max_params:
            self.smells.append({
                "type": "too_many_parameters",
                "line": node.lineno,
                "name": node.name,
                "severity": "warning",
                "message": f"Function `{node.name}` has {num_args} parameters (threshold: {self.max_params})."
            })

        # 2. Function line count check
        if hasattr(node, "end_lineno") and node.end_lineno:
            line_count = node.end_lineno - node.lineno + 1
            if line_count > self.max_func_lines:
                self.smells.append({
                    "type": "long_function",
                    "line": node.lineno,
                    "name": node.name,
                    "severity": "warning",
                    "message": f"Function `{node.name}` is too long ({line_count} lines, threshold: {self.max_func_lines})."
                })

    def visit_ClassDef(self, node: ast.ClassDef):
        methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        if len(methods) > self.max_class_methods:
            self.smells.append({
                "type": "large_class",
                "line": node.lineno,
                "name": node.name,
                "severity": "warning",
                "message": f"Class `{node.name}` has {len(methods)} methods (threshold: {self.max_class_methods})."
            })
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        for alias in node.names:
            if alias.name == "*":
                self.smells.append({
                    "type": "wildcard_import",
                    "line": node.lineno,
                    "name": node.module or "*",
                    "severity": "error",
                    "message": f"Wildcard import `from {node.module or '*'} import *` detected. Use explicit imports."
                })
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        if node.type is None:
            self.smells.append({
                "type": "bare_except",
                "line": node.lineno,
                "name": "except",
                "severity": "error",
                "message": "Bare `except:` clause detected. Specify concrete exception types."
            })
        elif isinstance(node.type, ast.Name) and node.type.id in ("Exception", "BaseException"):
            self.smells.append({
                "type": "broad_except",
                "line": node.lineno,
                "name": node.type.id,
                "severity": "warning",
                "message": f"Broad `except {node.type.id}:` clause caught. Catch specific exception classes."
            })
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        self._check_loop_nesting(node, current_depth=1)
        self.generic_visit(node)

    def visit_While(self, node: ast.While):
        self._check_loop_nesting(node, current_depth=1)
        self.generic_visit(node)

    def _check_loop_nesting(self, node: Union[ast.For, ast.While], current_depth: int):
        if current_depth >= 3:
            self.smells.append({
                "type": "deeply_nested_loop",
                "line": node.lineno,
                "name": "loop",
                "severity": "warning",
                "message": f"Loop nested at depth {current_depth} (threshold: 3). Refactor to reduce complexity."
            })
            return

        for child in node.body:
            if isinstance(child, (ast.For, ast.While)):
                self._check_loop_nesting(child, current_depth + 1)


def analyze_code_smells(source_input: Union[str, Path]) -> Dict[str, Any]:
    """
    Parses Python source code or file and returns list of code smells.
    """
    if isinstance(source_input, Path) or (isinstance(source_input, str) and "\n" not in source_input and Path(source_input).is_file()):
        file_path = Path(source_input)
        try:
            code = file_path.read_text(encoding="utf-8")
        except Exception as e:
            return {
                "valid": False,
                "file": str(file_path),
                "errors": [f"Failed to read file: {e}"],
                "smells": []
            }
        file_name = str(file_path)
    else:
        code = str(source_input)
        file_name = "<inline_code>"

    try:
        tree = ast.parse(code, filename=file_name)
    except SyntaxError as se:
        return {
            "valid": False,
            "file": file_name,
            "errors": [f"SyntaxError at line {se.lineno}: {se.msg}"],
            "smells": []
        }

    visitor = CodeSmellVisitor()
    visitor.visit(tree)

    has_errors = any(s["severity"] == "error" for s in visitor.smells)
    valid = not has_errors

    return {
        "valid": valid,
        "file": file_name,
        "smell_count": len(visitor.smells),
        "smells": visitor.smells,
        "errors": []
    }


def main():
    parser = argparse.ArgumentParser(description="CLI Code Smell & Maintainability Detector")
    parser.add_argument("file_path", type=str, help="Path to Python file (.py)")
    parser.add_argument("--json", action="store_true", help="Output audit report in JSON format")

    args = parser.parse_args()

    report = analyze_code_smells(Path(args.file_path))

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"\n🧩 Code Smell Analysis: {report['file']}")
        print("=" * 60)
        print(f"Total Smells Detected: {report['smell_count']}\n")

        if report["smells"]:
            for smell in report["smells"]:
                icon = "🚨" if smell["severity"] == "error" else "⚠️"
                print(f"  {icon} [Line {smell['line']}] {smell['message']}")
            print()
        else:
            print("✨ No maintainability smells detected!\n")

    if not report["valid"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
