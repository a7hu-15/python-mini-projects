"""CLI SSL/TLS Certificate Inspector & Expiration Checker.

Inspects domain SSL/TLS certificates, verifies validity windows, computes days remaining
until expiration, lists Subject Alternative Names (SANs), and alerts on impending expiry.
"""

import argparse
from datetime import datetime, timezone
import json
import socket
import ssl
import sys
from typing import Any, Dict, List, Optional, Tuple


def parse_cert_date(date_str: str) -> datetime:
    """Parses SSL certificate date string (e.g. 'May 20 23:59:59 2026 GMT') into a UTC datetime object."""
    # Format standard for OpenSSL certificate timestamps
    return datetime.strptime(date_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)


def parse_certificate(cert: Dict[str, Any], hostname: str) -> Dict[str, Any]:
    """Parses Python ssl socket raw cert dictionary into structured output format.

    Args:
        cert: Dictionary returned by SSLSocket.getpeercert()
        hostname: Domain name inspected

    Returns:
        Structured dictionary containing parsed metadata and expiration status.
    """
    # Extract Common Name (CN) from subject
    subject_dict = {}
    for rdn in cert.get("subject", ()):
        for key, value in rdn:
            subject_dict[key] = value

    # Extract Issuer details
    issuer_dict = {}
    for rdn in cert.get("issuer", ()):
        for key, value in rdn:
            issuer_dict[key] = value

    # Extract Subject Alternative Names (SANs)
    sans: List[str] = []
    for san_type, san_value in cert.get("subjectAltName", ()):
        if san_type.lower() in ("dns", "ip address"):
            sans.append(san_value)

    not_before_raw = cert.get("notBefore", "")
    not_after_raw = cert.get("notAfter", "")

    not_before_dt = parse_cert_date(not_before_raw) if not_before_raw else None
    not_after_dt = parse_cert_date(not_after_raw) if not_after_raw else None

    now = datetime.now(timezone.utc)
    days_remaining = None
    status = "UNKNOWN"

    if not_after_dt:
        time_diff = not_after_dt - now
        days_remaining = time_diff.days
        if days_remaining < 0:
            status = "EXPIRED"
        elif days_remaining <= 30:
            status = "WARNING"
        else:
            status = "HEALTHY"

    return {
        "hostname": hostname,
        "subject_cn": subject_dict.get("commonName", "N/A"),
        "issuer_cn": issuer_dict.get("commonName", "N/A"),
        "issuer_org": issuer_dict.get("organizationName", "N/A"),
        "valid_from": not_before_dt.isoformat() if not_before_dt else "N/A",
        "valid_until": not_after_dt.isoformat() if not_after_dt else "N/A",
        "days_remaining": days_remaining,
        "status": status,
        "subject_alt_names": sans,
        "serial_number": cert.get("serialNumber", "N/A"),
        "version": cert.get("version", "N/A"),
    }


def fetch_cert_info(hostname: str, port: int = 443, timeout: int = 5) -> Dict[str, Any]:
    """Fetches and inspects SSL certificate over socket connection.

    Args:
        hostname: Domain or host IP
        port: TLS port (default 443)
        timeout: Socket connection timeout in seconds

    Returns:
        Parsed certificate details dictionary.
    """
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port), timeout=timeout) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            if not cert:
                raise ValueError("No SSL certificate presented by host")
            return parse_certificate(cert, hostname)


def format_report(info: Dict[str, Any], warn_days: int = 30) -> str:
    """Formats certificate info dict into human-readable ASCII summary report."""
    status_icon = "✅" if info["status"] == "HEALTHY" else ("⚠️" if info["status"] == "WARNING" else "❌")
    
    lines = [
        f"==================================================",
        f" SSL/TLS Certificate Report: {info['hostname']}",
        f"==================================================",
        f" Status           : {status_icon} {info['status']}",
        f" Common Name (CN) : {info['subject_cn']}",
        f" Issuer           : {info['issuer_cn']} ({info['issuer_org']})",
        f" Valid From       : {info['valid_from']}",
        f" Valid Until      : {info['valid_until']}",
        f" Days Remaining   : {info['days_remaining']} days",
        f" Serial Number    : {info['serial_number']}",
        f" SANs ({len(info['subject_alt_names'])})      : {', '.join(info['subject_alt_names'][:5])}"
        + ("..." if len(info['subject_alt_names']) > 5 else ""),
        f"==================================================",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="CLI SSL/TLS Certificate Inspector & Expiration Checker")
    parser.add_argument("--host", required=True, help="Target hostname or domain (e.g. github.com)")
    parser.add_argument("--port", type=int, default=443, help="Port number (default: 443)")
    parser.add_argument("--timeout", type=int, default=5, help="Socket timeout in seconds (default: 5)")
    parser.add_argument("--warn-days", type=int, default=30, help="Days remaining threshold for warning (default: 30)")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()

    try:
        info = fetch_cert_info(args.host, args.port, args.timeout)
        # Update status according to user-defined warn-days
        if info["days_remaining"] is not None:
            if info["days_remaining"] < 0:
                info["status"] = "EXPIRED"
            elif info["days_remaining"] <= args.warn_days:
                info["status"] = "WARNING"
            else:
                info["status"] = "HEALTHY"

        if args.json:
            print(json.dumps(info, indent=2))
        else:
            print(format_report(info, warn_days=args.warn_days))

        if info["status"] in ("EXPIRED", "WARNING"):
            sys.exit(1)

    except Exception as e:
        print(f"Error inspecting certificate for {args.host}: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
