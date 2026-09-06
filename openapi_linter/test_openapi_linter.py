"""
Unit tests for OpenAPI Schema Linter.
"""

import json
import pytest
from openapi_linter.openapi_linter import OpenAPILinter, LintViolation


def test_valid_openapi_spec():
    """Test that a compliant OpenAPI 3.0 spec produces no errors/warnings."""
    valid_spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "Sample API",
            "version": "1.0.0",
            "description": "A clean test API"
        },
        "paths": {
            "/users/{user_id}": {
                "get": {
                    "summary": "Get user by ID",
                    "operationId": "getUserById",
                    "parameters": [
                        {
                            "name": "user_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {"description": "User details"},
                        "404": {"description": "User not found"}
                    }
                }
            }
        }
    }

    linter = OpenAPILinter()
    violations = linter.lint_spec(valid_spec)
    errors = [v for v in violations if v.severity == "ERROR"]
    assert len(errors) == 0


def test_missing_version_and_info():
    """Test detection of missing openapi version and info title/version."""
    invalid_spec = {
        "paths": {}
    }

    linter = OpenAPILinter()
    violations = linter.lint_spec(invalid_spec)

    rule_ids = {v.rule_id for v in violations}
    assert "OPENAPI-01" in rule_ids  # Missing openapi version
    assert "OPENAPI-02" in rule_ids  # Missing info object
    assert "OPENAPI-04" in rule_ids  # Empty paths


def test_undeclared_path_parameter():
    """Test detection of path parameter in URL not declared in parameters list."""
    spec_with_missing_param = {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {
            "/items/{item_id}/comments/{comment_id}": {
                "get": {
                    "summary": "Get comment",
                    "operationId": "getComment",
                    "parameters": [
                        {"name": "item_id", "in": "path", "required": True}
                        # comment_id is missing!
                    ],
                    "responses": {"200": {"description": "OK"}, "404": {"description": "Not Found"}}
                }
            }
        }
    }

    linter = OpenAPILinter()
    violations = linter.lint_spec(spec_with_missing_param)

    undeclared_violations = [v for v in violations if v.rule_id == "OPENAPI-05"]
    assert len(undeclared_violations) == 1
    assert "comment_id" in undeclared_violations[0].message


def test_missing_operation_metadata_and_responses():
    """Test warnings for missing operationId, summary, and error responses."""
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {
            "/orders": {
                "post": {
                    "responses": {
                        "201": {"description": "Created"}
                    }
                }
            }
        }
    }

    linter = OpenAPILinter()
    violations = linter.lint_spec(spec)

    rule_ids = [v.rule_id for v in violations]
    assert "OPENAPI-06" in rule_ids  # Missing summary/operationId
    assert "OPENAPI-07" in rule_ids  # Missing error response (4xx/5xx/default)


def test_invalid_json_file_linting(tmp_path):
    """Test linting an unparseable JSON file."""
    bad_json_file = tmp_path / "bad.json"
    bad_json_file.write_text("{ invalid json structure ", encoding="utf-8")

    linter = OpenAPILinter()
    violations = linter.lint_file(str(bad_json_file))

    assert len(violations) == 1
    assert violations[0].rule_id == "OPENAPI-00"
    assert violations[0].severity == "ERROR"
