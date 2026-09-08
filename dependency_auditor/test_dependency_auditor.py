import json
from pathlib import Path
from dependency_auditor.dependency_auditor import DependencyAuditor


def test_clean_requirements():
    content = """requests==2.31.0
flask==3.0.0
pytest==8.0.0
"""
    auditor = DependencyAuditor()
    issues = auditor.audit_requirements_txt(content, "requirements.txt")
    assert len(issues) == 0


def test_unpinned_and_insecure_requirements():
    content = """requests>=2.0.0
custom-pkg @ http://insecure.internal/pkg.whl
request==0.0.1
"""
    auditor = DependencyAuditor()
    issues = auditor.audit_requirements_txt(content, "requirements.txt")

    rule_ids = {i.rule_id for i in issues}
    assert "DEP001" in rule_ids  # Insecure HTTP
    assert "DEP002" in rule_ids  # Unpinned
    assert "DEP003" in rule_ids  # Deprecated package 'request'


def test_package_json_audit():
    pkg_json = {
        "name": "my-app",
        "license": "AGPL-3.0",
        "dependencies": {
            "express": "^4.18.2",
            "lodash": "latest",
        },
    }
    auditor = DependencyAuditor()
    issues = auditor.audit_package_json(json.dumps(pkg_json), "package.json")

    rule_ids = {i.rule_id for i in issues}
    assert "LIC001" in rule_ids  # Restrictive AGPL license
    assert "DEP002" in rule_ids  # Loose npm versions
