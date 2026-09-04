# 📝 CLI Git Commit Message Linter & Hook Validator

A standalone CLI utility and Git hook validator that enforces Conventional Commits standard (`type[(scope)][!]: <description>`).

## 🚀 Features

- 🎯 Enforces standard Conventional Commit types (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`, etc.)
- 📏 Validates header character length limits (default <= 72 characters)
- 🔤 Checks subject casing and trailing punctuation rules
- 💥 Detects breaking changes (`!` suffix or `BREAKING CHANGE:` body footer)
- 🪝 Integrates directly with Git `commit-msg` hooks
- 📊 Supports JSON output mode (`--json`)

## 💻 Usage

### Lint Direct String Message
```bash
python3 git_commit_linter/git_commit_linter.py -m "feat(auth): implement JWT refresh token flow"
```

### Lint Git Commit Edit File (`.git/COMMIT_EDITMSG`)
```bash
python3 git_commit_linter/git_commit_linter.py -f .git/COMMIT_EDITMSG
```

### Install as Git `commit-msg` Hook
Add the following line to `.git/hooks/commit-msg` (and make it executable `chmod +x`):
```bash
python3 /path/to/git_commit_linter/git_commit_linter.py -f "$1"
```

## 🧪 Unit Tests

Run test suite using `unittest`:
```bash
python3 -m unittest git_commit_linter/test_git_commit_linter.py
```
