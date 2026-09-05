import pytest
from dockerfile_linter.dockerfile_linter import DockerfileLinter


def test_clean_dockerfile():
    content = """
FROM python:3.11-slim
HEALTHCHECK --interval=30s CMD curl -f http://localhost:8080/ || exit 1
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY . /app
WORKDIR /app
USER appuser
CMD ["python", "app.py"]
"""
    linter = DockerfileLinter()
    violations = linter.lint_content(content)
    # Should have no ERROR or WARNING violations
    critical_issues = [v for v in violations if v.severity in ("ERROR", "WARNING")]
    assert len(critical_issues) == 0


def test_unpinned_base_image_warning():
    content = """
FROM ubuntu:latest
USER appuser
HEALTHCHECK CMD exit 0
"""
    linter = DockerfileLinter()
    violations = linter.lint_content(content)
    rule_ids = [v.rule_id for v in violations]
    assert "DL002" in rule_ids


def test_missing_user_error():
    content = """
FROM python:3.10
HEALTHCHECK CMD exit 0
"""
    linter = DockerfileLinter()
    violations = linter.lint_content(content)
    rule_ids = [v.rule_id for v in violations]
    assert "DL001" in rule_ids


def test_add_instead_of_copy():
    content = """
FROM python:3.11-slim
ADD localfile.txt /app/
USER appuser
HEALTHCHECK CMD exit 0
"""
    linter = DockerfileLinter()
    violations = linter.lint_content(content)
    rule_ids = [v.rule_id for v in violations]
    assert "DL004" in rule_ids


def test_hardcoded_secret_detection():
    content = """
FROM alpine:3.18
ENV AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
USER appuser
HEALTHCHECK CMD exit 0
"""
    linter = DockerfileLinter()
    violations = linter.lint_content(content)
    rule_ids = [v.rule_id for v in violations]
    assert "DL007" in rule_ids
