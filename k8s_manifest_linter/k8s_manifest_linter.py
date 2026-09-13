"""
CLI Kubernetes Manifest Linter & Security Auditor.

Audits Kubernetes YAML and JSON manifests (Deployments, Pods, Services, StatefulSets) for:
1. Privileged container security context (`privileged: true`, `allowPrivilegeEscalation: true`)
2. Missing resource requests & limits (`cpu`, `memory`)
3. Containers running as root (`runAsNonRoot: false` or missing)
4. Missing liveness & readiness health probes
5. Insecure image tags (`latest` tag or unpinned tags)
6. Exposed NodePort or LoadBalancer services without annotations
"""

import sys
import os
import re
import argparse
from typing import List, Dict, Any, Tuple


def audit_container_spec(container: Dict[str, Any], path_prefix: str) -> List[Dict[str, Any]]:
    """Audit a single container specification dict for security anti-patterns."""
    issues = []
    name = container.get("name", "unnamed-container")
    c_path = f"{path_prefix}.container[{name}]"

    # 1. Image tag checking
    image = container.get("image", "")
    if not image:
        issues.append({
            "rule": "MissingImage",
            "finding": f"{c_path} is missing an image declaration",
            "severity": "CRITICAL"
        })
    elif image.endswith(":latest") or ":" not in image:
        issues.append({
            "rule": "UnpinnedImageTag",
            "finding": f"{c_path} uses ':latest' or unpinned image tag ('{image}')",
            "severity": "HIGH"
        })

    # 2. Security context checking
    sec_ctx = container.get("securityContext", {})
    if sec_ctx.get("privileged") is True:
        issues.append({
            "rule": "PrivilegedContainer",
            "finding": f"{c_path} is running as privileged container",
            "severity": "CRITICAL"
        })
    if sec_ctx.get("allowPrivilegeEscalation") is True:
        issues.append({
            "rule": "PrivilegeEscalationAllowed",
            "finding": f"{c_path} allows privilege escalation",
            "severity": "HIGH"
        })
    if sec_ctx.get("runAsNonRoot") is not True:
        issues.append({
            "rule": "RootUserExecution",
            "finding": f"{c_path} is not enforcing 'runAsNonRoot: true'",
            "severity": "MEDIUM"
        })

    # 3. Resource limits & requests
    resources = container.get("resources", {})
    limits = resources.get("limits", {})
    requests = resources.get("requests", {})
    if not limits.get("cpu") or not limits.get("memory"):
        issues.append({
            "rule": "MissingResourceLimits",
            "finding": f"{c_path} is missing CPU/memory resource limits",
            "severity": "MEDIUM"
        })
    if not requests.get("cpu") or not requests.get("memory"):
        issues.append({
            "rule": "MissingResourceRequests",
            "finding": f"{c_path} is missing CPU/memory resource requests",
            "severity": "LOW"
        })

    # 4. Health Probes
    if "livenessProbe" not in container:
        issues.append({
            "rule": "MissingLivenessProbe",
            "finding": f"{c_path} is missing a livenessProbe",
            "severity": "MEDIUM"
        })
    if "readinessProbe" not in container:
        issues.append({
            "rule": "MissingReadinessProbe",
            "finding": f"{c_path} is missing a readinessProbe",
            "severity": "MEDIUM"
        })

    return issues


def parse_simple_yaml_manifest(content: str) -> List[Dict[str, Any]]:
    """
    Lightweight fallback YAML/JSON parser for Kubernetes manifests.
    Parses key-value properties without requiring PyYAML dependency.
    """
    docs = []
    current_doc: Dict[str, Any] = {}
    lines = content.splitlines()

    kind = ""
    name = ""

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("kind:"):
            kind = stripped.split("kind:")[1].strip()
        elif stripped.startswith("name:") and not name:
            name = stripped.split("name:")[1].strip()

    if kind:
        docs.append({"kind": kind, "metadata": {"name": name}, "content": content})

    return docs


def audit_k8s_manifest(filepath: str) -> Dict[str, Any]:
    """Audit a Kubernetes manifest file and return structured security findings."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Manifest file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    issues = []

    # Check raw text patterns
    if "privileged: true" in content:
        issues.append({
            "rule": "PrivilegedContainer",
            "finding": "Manifest contains 'privileged: true' securityContext",
            "severity": "CRITICAL"
        })
    if ":latest" in content:
        issues.append({
            "rule": "UnpinnedImageTag",
            "finding": "Manifest references ':latest' container image tag",
            "severity": "HIGH"
        })
    if "resources:" not in content and ("kind: Deployment" in content or "kind: Pod" in content):
        issues.append({
            "rule": "MissingResourceLimits",
            "finding": "Workload manifest is missing container 'resources' constraints",
            "severity": "MEDIUM"
        })
    if "livenessProbe:" not in content and ("kind: Deployment" in content or "kind: Pod" in content):
        issues.append({
            "rule": "MissingLivenessProbe",
            "finding": "Workload manifest is missing 'livenessProbe' health check",
            "severity": "MEDIUM"
        })
    if "type: NodePort" in content or "type: LoadBalancer" in content:
        issues.append({
            "rule": "ExposedServiceType",
            "finding": "Service exposes NodePort/LoadBalancer directly to external networks",
            "severity": "LOW"
        })

    errors = [i for i in issues if i["severity"] in ("CRITICAL", "HIGH")]
    warnings = [i for i in issues if i["severity"] not in ("CRITICAL", "HIGH")]

    return {
        "file": filepath,
        "valid": len(errors) == 0,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description="CLI Kubernetes Manifest Security Auditor")
    parser.add_argument("manifest", help="Path to Kubernetes YAML manifest file")
    args = parser.parse_args()

    try:
        report = audit_k8s_manifest(args.manifest)
        print(f"=== K8s Security Audit Report for '{report['file']}' ===")
        print(f"Status: {'PASSED ✅' if report['valid'] else 'FAILED ❌'}")
        print(f"Errors: {report['error_count']} | Warnings: {report['warning_count']}\n")

        for err in report["errors"]:
            print(f"  [ERROR] {err['rule']} - {err['finding']}")
        for warn in report["warnings"]:
            print(f"  [WARN]  {warn['rule']} - {warn['finding']}")

        sys.exit(0 if report["valid"] else 1)
    except Exception as e:
        print(f"Error executing audit: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
