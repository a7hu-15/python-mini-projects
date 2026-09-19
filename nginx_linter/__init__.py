"""CLI Nginx & Web Server Security Linter package."""
from .nginx_linter import audit_nginx_config

__all__ = ["audit_nginx_config"]
