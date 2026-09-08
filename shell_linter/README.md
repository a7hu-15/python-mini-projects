# Shell Script Linter & Security Auditor

A lightweight CLI tool to audit Bash and Shell scripts for security vulnerabilities, dangerous command patterns, unquoted variable expansions, hardcoded secrets, and missing safety flags.

## Features

- **Shebang Validation (`SH002`)**: Ensures scripts have explicit interpreter directives.
- **Safety Flags Check (`SH003`, `SH004`)**: Warns if exit-on-error (`set -e`) or `pipefail` flags are omitted.
- **Hazardous Operations (`SH005`)**: Flags `rm -rf` operations using unvalidated variable expansions.
- **Arbitrary Code Execution (`SH006`)**: Identifies unsafe `eval` usage.
- **Path Expansion Risks (`SH007`)**: Detects unquoted path variables in `cd` commands.
- **Hardcoded Secret Detection (`SH008`)**: Scans for embedded API keys, tokens, and credentials.
- **Modern Syntax Rules (`SH009`, `SH010`)**: Encourages `$()` over legacy backticks and `[[ ... ]]` over `[ ... ]` in Bash.

## Usage

```bash
# Run audit on shell script
python3 shell_linter.py deploy.sh

# Output issues in JSON format
python3 shell_linter.py deploy.sh --json

# Filter by minimum severity (HIGH, MEDIUM, LOW, INFO)
python3 shell_linter.py deploy.sh --min-severity HIGH
```

## Running Tests

```bash
PYTHONPATH=. python3 -m pytest shell_linter/
```
