import tempfile
from pathlib import Path
from shell_linter.shell_linter import ShellLinter


def test_clean_script():
    clean_script = """#!/usr/bin/env bash
set -eo pipefail

echo "Starting deploy..."
TARGET_DIR="/opt/app"
if [[ -d "$TARGET_DIR" ]]; then
    echo "Directory exists"
fi
"""
    linter = ShellLinter()
    issues = linter.lint_content(clean_script)
    high_medium_issues = [i for i in issues if i.severity in ("HIGH", "MEDIUM")]
    assert len(high_medium_issues) == 0


def test_missing_shebang_and_safety_flags():
    bad_script = """echo "No shebang"
cd $UNQUOTED_VAR
eval "echo test"
"""
    linter = ShellLinter()
    issues = linter.lint_content(bad_script)

    rule_ids = {i.rule_id for i in issues}
    assert "SH002" in rule_ids  # missing shebang
    assert "SH003" in rule_ids  # missing set -e
    assert "SH006" in rule_ids  # eval usage
    assert "SH007" in rule_ids  # unquoted cd


def test_dangerous_rm_rf_and_secrets():
    bad_script = """#!/bin/bash
set -e
SECRET_KEY="sk_live_123456789"
rm -rf $DIR_PATH/
"""
    linter = ShellLinter()
    issues = linter.lint_content(bad_script)

    rule_ids = {i.rule_id for i in issues}
    assert "SH005" in rule_ids  # rm -rf $VAR
    assert "SH008" in rule_ids  # hardcoded secret


def test_lint_file(tmp_path):
    script_file = tmp_path / "test.sh"
    script_file.write_text("echo 'hello world'\n", encoding="utf-8")

    linter = ShellLinter()
    issues = linter.lint_file(script_file)
    assert len(issues) > 0
    assert issues[0].rule_id == "SH002"  # Missing shebang
