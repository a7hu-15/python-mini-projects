"""Terraform Security & Best Practices Auditor Package."""
from .terraform_linter import audit_tf_manifest

__all__ = ["audit_tf_manifest"]
