"""
CLI OpenAPI / Swagger Schema Linter & Security Auditor.

Parses OpenAPI 3.0 / 3.1 schema definitions (JSON format) and checks against
API design standards, path parameter consistency, operation metadata, and security best practices.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional


@dataclass
class LintViolation:
    rule_id: str
    severity: str  # 'ERROR', 'WARNING', 'INFO'
    path_context: str
    message: str


class OpenAPILinter:
    """Linter engine for analyzing OpenAPI spec objects."""

    HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
    PARAM_REGEX = re.compile(r"\{([a-zA-Z0-9_]+)\}")

    def __init__(self):
        self.violations: List[LintViolation] = []

    def lint_spec(self, spec: Dict[str, Any]) -> List[LintViolation]:
        """Lints an parsed OpenAPI specification dictionary."""
        self.violations = []

        # Rule 1: OpenAPI Version Presence
        openapi_version = spec.get("openapi") or spec.get("swagger")
        if not openapi_version:
            self.violations.append(
                LintViolation(
                    rule_id="OPENAPI-01",
                    severity="ERROR",
                    path_context="root",
                    message="Missing top-level 'openapi' or 'swagger' version definition",
                )
            )

        # Rule 2: Info Object Metadata
        info = spec.get("info")
        if not isinstance(info, dict):
            self.violations.append(
                LintViolation(
                    rule_id="OPENAPI-02",
                    severity="ERROR",
                    path_context="root.info",
                    message="Missing required top-level 'info' object",
                )
            )
        else:
            if not info.get("title"):
                self.violations.append(
                    LintViolation(
                        rule_id="OPENAPI-02",
                        severity="ERROR",
                        path_context="root.info.title",
                        message="Missing required 'info.title' string",
                    )
                )
            if not info.get("version"):
                self.violations.append(
                    LintViolation(
                        rule_id="OPENAPI-02",
                        severity="ERROR",
                        path_context="root.info.version",
                        message="Missing required 'info.version' string",
                    )
                )
            if not info.get("description"):
                self.violations.append(
                    LintViolation(
                        rule_id="OPENAPI-03",
                        severity="WARNING",
                        path_context="root.info.description",
                        message="Missing recommended 'info.description' for documentation clarity",
                    )
                )

        # Rule 3: Paths Object Presence
        paths = spec.get("paths")
        if not isinstance(paths, dict) or not paths:
            self.violations.append(
                LintViolation(
                    rule_id="OPENAPI-04",
                    severity="ERROR",
                    path_context="root.paths",
                    message="Specification must contain non-empty 'paths' object",
                )
            )
            return self.violations

        # Rule 4: Path & Operation Level Auditing
        components = spec.get("components", {})
        security_schemes = components.get("securitySchemes", {}) if isinstance(components, dict) else {}

        for path_key, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue

            # Path naming convention check (REST hyphens vs underscores/camelCase)
            segments = [s for s in path_key.split("/") if s and not s.startswith("{")]
            for seg in segments:
                if "_" in seg or any(c.isupper() for c in seg):
                    self.violations.append(
                        LintViolation(
                            rule_id="OPENAPI-08",
                            severity="INFO",
                            path_context=f"paths[{path_key}]",
                            message=f"Path segment '{seg}' should use kebab-case instead of snake_case or camelCase",
                        )
                    )

            # Path parameter extraction
            path_params_in_url = set(self.PARAM_REGEX.findall(path_key))

            # Path-level parameter definitions
            path_level_params = path_item.get("parameters", [])
            path_param_names = set()
            if isinstance(path_level_params, list):
                for p in path_level_params:
                    if isinstance(p, dict) and p.get("in") == "path":
                        path_param_names.add(p.get("name"))

            # Audit operations
            for method, op_data in path_item.items():
                if method.lower() not in self.HTTP_METHODS:
                    continue
                if not isinstance(op_data, dict):
                    continue

                op_context = f"paths[{path_key}].{method.upper()}"

                # Operation Metadata
                if not op_data.get("summary") and not op_data.get("description"):
                    self.violations.append(
                        LintViolation(
                            rule_id="OPENAPI-06",
                            severity="WARNING",
                            path_context=op_context,
                            message="Operation is missing 'summary' or 'description'",
                        )
                    )

                if not op_data.get("operationId"):
                    self.violations.append(
                        LintViolation(
                            rule_id="OPENAPI-06",
                            severity="WARNING",
                            path_context=op_context,
                            message="Operation is missing 'operationId'",
                        )
                    )

                # Path parameter declared check
                op_params = op_data.get("parameters", [])
                op_param_names = set()
                if isinstance(op_params, list):
                    for p in op_params:
                        if isinstance(p, dict) and p.get("in") == "path":
                            op_param_names.add(p.get("name"))

                all_declared_path_params = path_param_names.union(op_param_names)
                for param_in_url in path_params_in_url:
                    if param_in_url not in all_declared_path_params:
                        self.violations.append(
                            LintViolation(
                                rule_id="OPENAPI-05",
                                severity="ERROR",
                                path_context=op_context,
                                message=f"Path parameter '{{{param_in_url}}}' in URL is not declared in operation or path parameters",
                            )
                        )

                # Response status codes check
                responses = op_data.get("responses")
                if not isinstance(responses, dict) or not responses:
                    self.violations.append(
                        LintViolation(
                            rule_id="OPENAPI-07",
                            severity="ERROR",
                            path_context=f"{op_context}.responses",
                            message="Operation must specify at least one response definition",
                        )
                    )
                else:
                    has_error_resp = any(code in responses for code in ["400", "401", "403", "404", "500", "default"])
                    if not has_error_resp:
                        self.violations.append(
                            LintViolation(
                                rule_id="OPENAPI-07",
                                severity="WARNING",
                                path_context=f"{op_context}.responses",
                                message="Operation missing standard error response (4xx/5xx or default)",
                            )
                        )

                # Security check
                op_security = op_data.get("security", spec.get("security", []))
                if op_security:
                    for sec_req in op_security:
                        if isinstance(sec_req, dict):
                            for sec_name in sec_req.keys():
                                if sec_name not in security_schemes:
                                    self.violations.append(
                                        LintViolation(
                                            rule_id="OPENAPI-09",
                                            severity="WARNING",
                                            path_context=f"{op_context}.security",
                                            message=f"Security scheme '{sec_name}' referenced but not defined in components.securitySchemes",
                                        )
                                    )

        return self.violations

    def lint_file(self, filepath: str) -> List[LintViolation]:
        """Loads JSON file from disk and returns lint violations."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                spec = json.load(f)
        except json.JSONDecodeError as err:
            return [
                LintViolation(
                    rule_id="OPENAPI-00",
                    severity="ERROR",
                    path_context=filepath,
                    message=f"Invalid JSON syntax: {err.msg} at line {err.lineno} col {err.colno}",
                )
            ]
        except Exception as err:
            return [
                LintViolation(
                    rule_id="OPENAPI-00",
                    severity="ERROR",
                    path_context=filepath,
                    message=f"Failed to read file: {err}",
                )
            ]

        return self.lint_spec(spec)


def main():
    parser = argparse.ArgumentParser(description="CLI OpenAPI Schema Linter & Auditor")
    parser.add_argument("file", help="Path to OpenAPI JSON specification file")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--fail-on-warning", action="store_true", help="Exit with non-zero status code on warnings")

    args = parser.parse_args()

    linter = OpenAPILinter()
    violations = linter.lint_file(args.file)

    errors = [v for v in violations if v.severity == "ERROR"]
    warnings = [v for v in violations if v.severity == "WARNING"]

    if args.format == "json":
        output = {
            "summary": {
                "total_violations": len(violations),
                "errors": len(errors),
                "warnings": len(warnings),
                "info": len(violations) - len(errors) - len(warnings),
            },
            "violations": [asdict(v) for v in violations],
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\n🔍 OpenAPI Linter Report: {args.file}")
        print("=" * 60)

        if not violations:
            print("✅ No violations found! Your OpenAPI specification is clean.")
        else:
            for v in violations:
                symbol = "❌" if v.severity == "ERROR" else ("⚠️" if v.severity == "WARNING" else "ℹ️")
                print(f"{symbol} [{v.rule_id}] [{v.severity}] {v.path_context}")
                print(f"   {v.message}\n")

            print("=" * 60)
            print(f"Summary: {len(errors)} Errors | {len(warnings)} Warnings | {len(violations) - len(errors) - len(warnings)} Info")

    if errors or (args.fail-on-warning and warnings):
        sys.exit(1)


if __name__ == "__main__":
    main()
