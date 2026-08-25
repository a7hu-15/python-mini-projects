"""CLI Data Validator & Schema Inspector.

A command-line tool and Python library for validating JSON and CSV data files against custom or inferred schemas. It detects missing required fields, type mismatches, format errors (e.g. email, URL), out-of-range values, and outputs formatted error summaries and JSON reports.

>>> validator = DataValidator()
>>> schema = {"name": {"type": "str", "required": True}, "age": {"type": "int", "min": 0, "max": 120}}
>>> errors = validator.validate_record({"name": "Alice", "age": 25}, schema)
>>> errors
[]
>>> errors = validator.validate_record({"age": -5}, schema)
>>> len(errors)
2
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class DataValidator:
    EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
    URL_REGEX = re.compile(r"^https?://[\w\.-]+(?:\.[\w\.-]+)+[/#?]?.*$")

    def __init__(self, schema: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        self.schema = schema or {}

    def validate_record(self, record: Dict[str, Any], schema: Optional[Dict[str, Dict[str, Any]]] = None) -> List[str]:
        active_schema = schema or self.schema
        errors: List[str] = []

        for field_name, rules in active_schema.items():
            value = record.get(field_name)

            # 1. Required check
            if rules.get("required", False) and (value is None or value == ""):
                errors.append(f"Missing required field: '{field_name}'")
                continue

            if value is None or value == "":
                continue

            # 2. Type validation
            expected_type = rules.get("type")
            if expected_type:
                if not self._check_type(value, expected_type):
                    errors.append(f"Field '{field_name}' value '{value}' is not of expected type '{expected_type}'")
                    continue

            # Convert numeric for range checks if needed
            numeric_val = None
            if expected_type in ("int", "integer"):
                try:
                    numeric_val = int(value)
                except ValueError:
                    pass
            elif expected_type in ("float", "number"):
                try:
                    numeric_val = float(value)
                except ValueError:
                    pass
            elif isinstance(value, (int, float)):
                numeric_val = value

            # 3. Range checks
            if numeric_val is not None:
                if "min" in rules and numeric_val < rules["min"]:
                    errors.append(f"Field '{field_name}' value {numeric_val} is less than min {rules['min']}")
                if "max" in rules and numeric_val > rules["max"]:
                    errors.append(f"Field '{field_name}' value {numeric_val} is greater than max {rules['max']}")

            # 4. String length checks
            if isinstance(value, str):
                if "min_length" in rules and len(value) < rules["min_length"]:
                    errors.append(f"Field '{field_name}' length {len(value)} is shorter than min length {rules['min_length']}")
                if "max_length" in rules and len(value) > rules["max_length"]:
                    errors.append(f"Field '{field_name}' length {len(value)} exceeds max length {rules['max_length']}")

            # 5. Format validation (email, url)
            fmt = rules.get("format")
            if fmt == "email" and isinstance(value, str):
                if not self.EMAIL_REGEX.match(value):
                    errors.append(f"Field '{field_name}' value '{value}' is not a valid email address")
            elif fmt == "url" and isinstance(value, str):
                if not self.URL_REGEX.match(value):
                    errors.append(f"Field '{field_name}' value '{value}' is not a valid URL")

            # 6. Allowed choices
            choices = rules.get("choices")
            if choices and value not in choices:
                errors.append(f"Field '{field_name}' value '{value}' must be one of {choices}")

        return errors

    def _check_type(self, value: Any, expected_type: str) -> bool:
        if expected_type in ("str", "string"):
            return isinstance(value, str)
        elif expected_type in ("int", "integer"):
            if isinstance(value, int) and not isinstance(value, bool):
                return True
            if isinstance(value, str):
                try:
                    int(value)
                    return True
                except ValueError:
                    return False
            return False
        elif expected_type in ("float", "number"):
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return True
            if isinstance(value, str):
                try:
                    float(value)
                    return True
                except ValueError:
                    return False
            return False
        elif expected_type in ("bool", "boolean"):
            if isinstance(value, bool):
                return True
            if isinstance(value, str) and value.lower() in ("true", "false", "1", "0"):
                return True
            return False
        return True

    def validate_file(self, file_path: Path, schema: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        suffix = file_path.suffix.lower()
        records: List[Dict[str, Any]] = []

        if suffix == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    records = data
                elif isinstance(data, dict):
                    records = [data]
                else:
                    raise ValueError("JSON content must be an object or array of objects")
        elif suffix == ".csv":
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                records = list(reader)
        else:
            raise ValueError(f"Unsupported file extension '{suffix}'. Expected .json or .csv")

        total_records = len(records)
        passed_records = 0
        all_errors: Dict[int, List[str]] = {}

        for index, record in enumerate(records):
            errs = self.validate_record(record, schema)
            if errs:
                all_errors[index] = errs
            else:
                passed_records += 1

        return {
            "file": str(file_path),
            "total_records": total_records,
            "passed_records": passed_records,
            "failed_records": len(all_errors),
            "is_valid": len(all_errors) == 0,
            "errors_by_record": all_errors,
        }


def main():
    parser = argparse.ArgumentParser(description="CLI Data Validator & Schema Inspector")
    parser.add_argument("--data", help="Path to input JSON or CSV data file")
    parser.add_argument("--schema", help="Path to JSON schema file")
    parser.add_argument("--output", help="Optional path to save JSON validation report")
    parser.add_argument("--cli", action="store_true", help="Run interactive CLI test demo")

    args = parser.parse_args()

    if args.cli or not (args.data and args.schema):
        print("=== CLI Data Validator & Schema Inspector Demo ===")
        sample_schema = {
            "user_id": {"type": "int", "required": True, "min": 1},
            "email": {"type": "str", "required": True, "format": "email"},
            "role": {"type": "str", "choices": ["admin", "editor", "user"]},
            "score": {"type": "float", "min": 0.0, "max": 100.0}
        }
        sample_records = [
            {"user_id": 101, "email": "alice@example.com", "role": "admin", "score": 95.5},
            {"user_id": "invalid_id", "email": "not-an-email", "role": "superadmin", "score": 150.0},
        ]
        validator = DataValidator()
        print("Schema Rules:")
        print(json.dumps(sample_schema, indent=2))
        print("\nValidating Demo Records:")
        for idx, rec in enumerate(sample_records):
            errs = validator.validate_record(rec, sample_schema)
            status = "✅ PASS" if not errs else f"❌ FAIL ({len(errs)} errors)"
            print(f"\nRecord #{idx + 1}: {rec} -> {status}")
            for e in errs:
                print(f"  - {e}")
        return

    data_path = Path(args.data)
    schema_path = Path(args.schema)

    if not data_path.exists():
        print(f"Error: Data file '{data_path}' not found.", file=sys.stderr)
        sys.exit(1)

    if not schema_path.exists():
        print(f"Error: Schema file '{schema_path}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    validator = DataValidator()
    report = validator.validate_file(data_path, schema)

    print("\n================ VALIDATION REPORT ================")
    print(f"File: {report['file']}")
    print(f"Total Records: {report['total_records']}")
    print(f"Passed: {report['passed_records']}")
    print(f"Failed: {report['failed_records']}")
    print(f"Status: {'✅ VALID' if report['is_valid'] else '❌ INVALID'}")

    if report["errors_by_record"]:
        print("\nDetailed Errors:")
        for idx, errs in report["errors_by_record"].items():
            print(f" Record #{idx}:")
            for e in errs:
                print(f"   - {e}")

    if args.output:
        out_path = Path(args.output)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"\nSaved report to '{out_path}'")


if __name__ == "__main__":
    main()
