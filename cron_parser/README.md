# ⏰ Cron Expression Parser & Schedule Calculator

A lightweight Python CLI tool and library for parsing standard 5-part cron syntax and calculating upcoming execution schedules.

## 🌟 Features

- **Standard Cron Syntax Support**: Handles wildcards (`*`), steps (`*/15`), ranges (`1-5`), and lists (`1,15,30`).
- **Validation**: Strict boundary validation for minute (0-59), hour (0-23), day of month (1-31), month (1-12), and day of week (0-6).
- **Next N Executions**: Calculates exact future execution timestamps starting from any target datetime.
- **Tabular Formatting**: Pretty-printed output of expanded field values and upcoming run schedules.

## 🚀 Usage

### Command Line Interface

```bash
python cron_parser.py "*/15 9-17 * * 1-5" -n 5
```

### Python API

```python
from datetime import datetime
from cron_parser import CronParser

parser = CronParser("0 12 * * *")
next_runs = parser.get_next_executions(datetime.now(), count=3)

for dt in next_runs:
    print(dt)
```

## 🧪 Testing

Run pytest or unittest:

```bash
pytest test_cron_parser.py
```
