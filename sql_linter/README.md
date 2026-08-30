# 🔍 SQL Schema & Query Static Linter

A fast, standalone Python CLI tool to lint SQL queries and database migration scripts for performance anti-patterns, dangerous operations, and syntax style violations.

## 📋 Lint Rules

| Rule Code | Severity | Description |
|-----------|----------|-------------|
| `ERR001`  | `ERROR`   | Detects `SELECT *` anti-pattern. |
| `ERR002`  | `ERROR`   | Critical: Missing `WHERE` clause on `UPDATE` or `DELETE` statement. |
| `WARN001` | `WARNING` | Keywords not capitalized (e.g. `select` vs `SELECT`). |
| `WARN002` | `WARNING` | Leading wildcard in `LIKE '%...'` condition (prevents B-tree index usage). |
| `WARN003` | `WARNING` | `JOIN` statement missing explicit `ON` or `USING` condition. |
| `INFO001` | `INFO`    | `ORDER BY` without a `LIMIT` clause on potentially large datasets. |

## 🚀 Usage

Lint a raw query directly:

```bash
python sql_linter.py -q "SELECT * FROM users WHERE email LIKE '%@gmail.com';"
```

Lint a SQL file:

```bash
python sql_linter.py schema.sql
```

Ignore style capitalization warnings:

```bash
python sql_linter.py schema.sql --ignore-style
```

## 🧪 Testing

Run unit tests:

```bash
python3 -m unittest test_sql_linter.py
```
