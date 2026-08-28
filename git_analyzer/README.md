# 📊 Git Commit History & Contributor Analyzer

A Python CLI tool that parses Git repository logs to compute contributor statistics, commit volume, line additions/deletions (code churn), file modification hotspots, and activity trends.

## 🚀 Features

- **Contributor Aggregation**: Calculates commits, total lines added, total lines deleted, and net code contributions per developer.
- **File Hotspots**: Identifies frequently changed files (code churn hotspots).
- **Multiple Export Formats**:
  - `text`: Plain text ASCII summary.
  - `json`: Structured JSON for programmatic ingestion.
  - `markdown`: Styled Markdown table report ready for documentation or PR summaries.

## 💻 Usage

Analyze current repository with default text output:

```bash
python git_analyzer.py --repo .
```

Export Markdown analytics report:

```bash
python git_analyzer.py --repo . --format markdown
```

Export JSON analytics:

```bash
python git_analyzer.py --repo . --format json
```

## 🧪 Running Unit Tests

```bash
python -m unittest test_git_analyzer.py
```
