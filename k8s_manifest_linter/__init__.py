"""Kubernetes Manifest Linter & Security Auditor Package."""
from .k8s_manifest_linter import audit_k8s_manifest

__all__ = ["audit_k8s_manifest"]
