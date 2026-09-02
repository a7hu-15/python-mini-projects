# 🐍 Python Mini Projects

A collection of small but practical Python projects — perfect for learning and portfolio building.

Each project is self-contained, well-documented, and can be run independently.

## 📂 Projects

| # | Project | Description |
|---|---------|-------------|
| 1 | [Password Strength Checker](password_checker/) | Analyze password strength with detailed feedback |
| 2 | [Markdown to HTML Converter](md_to_html/) | Convert Markdown text to clean HTML |
| 3 | [URL Shortener](url_shortener/) | CLI-based URL shortener using hashing |
| 4 | [CLI Expense Tracker](expense_tracker/) | Track expenses with category summaries and JSON storage |
| 5 | [CLI Task Manager](task_manager/) | Track tasks with priorities, due dates, and JSON storage |
| 6 | [File Organizer & Renamer](file_organizer/) | Auto-sort directory files into subfolders and regex batch rename |
| 7 | [Markdown Live Previewer](markdown_previewer/) | Parse and render Markdown documents to ANSI terminal text or HTML |
| 8 | [CLI System Health Monitor](system_monitor/) | Fetch system hardware info, CPU architecture, and disk metrics |
| 9 | [CLI Data Validator](data_validator/) | Validate JSON/CSV records against type rules and custom schemas |
| 10 | [CLI Log File Analyzer](log_analyzer/) | Parse web access logs, calculate bandwidth metrics, and track error rates |
| 11 | [CLI Markdown Table Generator](markdown_table_generator/) | Convert CSV/JSON data to formatted Markdown tables with sorting and filtering |
| 12 | [CLI Code Metrics & LOC Counter](code_metrics_counter/) | Analyze lines of code, comments, and blank lines across project directories |
| 13 | [CLI Config Merger & Diff Tool](config_merger/) | Recursive JSON config merger with env var substitution & structural diffing |
| 14 | [CLI JSON/XML Converter & Formatter](json_converter/) | Multi-format data structure converter for JSON and XML |
| 15 | [CLI File Hash Generator & Duplicate Finder](file_hash_dedupe/) | Compute MD5/SHA256 checksums and scan directory trees for duplicates |
| 16 | [CLI Environment Variables (.env) Linter](env_linter/) | Validate .env syntax, missing variables, and hardcoded secret leaks |
| 17 | [CLI Rate Limiter & Token Bucket Utility](rate_limiter/) | Thread-safe Token Bucket & Leaky Bucket rate limiter with function decorators |
| 18 | [CLI Git History & Contributor Analyzer](git_analyzer/) | Compute commit volume, code churn, author statistics, and Markdown reports |
| 19 | [CLI Concurrent API Benchmarker](api_benchmarker/) | Multithreaded HTTP API load tester with latency percentiles (p50, p95, p99) and RPS |
| 20 | [CLI SQL Schema & Query Static Linter](sql_linter/) | Static analysis for SQL queries detecting SELECT *, missing WHERE, and index anti-patterns |
| 21 | [CLI Cron Expression Parser](cron_parser/) | Parse 5-part cron syntax, validate fields, and calculate upcoming execution schedules |
| 22 | [CLI JWT Inspector & Claims Decoder](jwt_inspector/) | Zero-dependency JSON Web Token decoder with claim validity inspection and warnings |
| 23 | [CLI Markdown Link & Anchor Checker](markdown_link_checker/) | Validate relative file paths, media links, and heading anchors (#anchor) in Markdown docs |
| 24 | [CLI Secret & Sensitive Data Scanner](secret_scanner/) | Scan codebases and configs for leaked API keys, credentials, tokens, and private keys |

## 🚀 How to Run

Each project has its own directory. Navigate to any project and run:

```bash
python password_checker/password_checker.py
python md_to_html/md_to_html.py
python url_shortener/url_shortener.py
python expense_tracker/expense_tracker.py --cli
python task_manager/task_manager.py --cli
python file_organizer/file_organizer.py --cli
```

## 🤝 Contributing

Want to add a mini project? Go for it! Just:
1. Create a new directory with a descriptive name
2. Include a `README.md` in the project directory
3. Make the main script runnable standalone

## 📄 License

MIT License
