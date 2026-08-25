# 🔍 CLI Data Validator & Schema Inspector

A lightweight Python tool for validating JSON and CSV files against custom type and schema constraints.

## 🌟 Features

- **Multi-Format Support**: Validates `.json` and `.csv` datasets.
- **Rule Engine**:
  - Required vs Optional fields
  - Type checking (`str`, `int`, `float`, `bool`)
  - Range validation (`min`, `max` values)
  - String length constraints (`min_length`, `max_length`)
  - Format checking (regex patterns for `email` and `url`)
  - Enum allowed values (`choices`)
- **JSON Report Export**: Detailed error breakdown per row/record.

## 🚀 Usage

### Run Built-in Interactive Demo
```bash
python data_validator/data_validator.py --cli
```

### Validate File Against Schema
```bash
python data_validator/data_validator.py --data users.csv --schema schema.json --output report.json
```

### Sample Schema (`schema.json`)
```json
{
  "user_id": {"type": "int", "required": true, "min": 1},
  "email": {"type": "str", "required": true, "format": "email"},
  "role": {"type": "str", "choices": ["admin", "editor", "user"]},
  "score": {"type": "float", "min": 0.0, "max": 100.0}
}
```
