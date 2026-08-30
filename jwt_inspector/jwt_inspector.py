"""
JWT (JSON Web Token) Inspector & Claims Decoder

A zero-dependency Python CLI tool and library for decoding, inspecting, and analyzing
JSON Web Tokens (JWTs).

Features:
    - Decodes JWT header, payload, and signature components without third-party dependencies.
    - Inspects standard claims: exp (expiration), nbf (not before), iat (issued at), iss, sub, aud.
    - Formats timestamp claims into human-readable ISO-8601 datetimes.
    - Calculates remaining validity time or flags expired tokens.
    - Formatted CLI summary and JSON export.
"""

from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import json
import sys
from typing import Any, Dict, Optional, Tuple


class JWTInspector:
    """Class to parse and inspect JSON Web Tokens (JWT)."""

    def __init__(self, token: str) -> None:
        self.raw_token = token.strip()
        self.header, self.payload, self.signature_b64 = self._parse_token(self.raw_token)

    @staticmethod
    def _base64url_decode(input_str: str) -> bytes:
        """Decode base64url string with proper padding."""
        rem = len(input_str) % 4
        if rem > 0:
            input_str += "=" * (4 - rem)
        return base64.urlsafe_b64decode(input_str.encode("utf-8"))

    def _parse_token(self, token: str) -> Tuple[Dict[str, Any], Dict[str, Any], str]:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid JWT structure: expected 3 parts, got {len(parts)}")

        header_b64, payload_b64, signature_b64 = parts[0], parts[1], parts[2]

        try:
            header_json = self._base64url_decode(header_b64).decode("utf-8")
            header = json.loads(header_json)
        except Exception as err:
            raise ValueError(f"Failed to decode JWT header: {err}")

        try:
            payload_json = self._base64url_decode(payload_b64).decode("utf-8")
            payload = json.loads(payload_json)
        except Exception as err:
            raise ValueError(f"Failed to decode JWT payload: {err}")

        return header, payload, signature_b64

    def inspect_claims(self, reference_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Inspect standard JWT claims relative to reference_time (defaults to UTC now)."""
        ref_dt = reference_time or datetime.now(timezone.utc)
        ref_ts = ref_dt.timestamp()

        analysis: Dict[str, Any] = {
            "algorithm": self.header.get("alg", "UNKNOWN"),
            "token_type": self.header.get("typ", "JWT"),
            "claims": {},
            "status": "VALID",
            "warnings": [],
        }

        # Expiration (exp)
        if "exp" in self.payload:
            exp_ts = float(self.payload["exp"])
            exp_dt = datetime.fromtimestamp(exp_ts, tz=timezone.utc)
            analysis["claims"]["exp"] = exp_dt.isoformat()
            if ref_ts > exp_ts:
                analysis["status"] = "EXPIRED"
                analysis["warnings"].append(f"Token expired at {exp_dt.isoformat()}")
            else:
                remaining_sec = int(exp_ts - ref_ts)
                analysis["claims"]["time_remaining_seconds"] = remaining_sec

        # Not Before (nbf)
        if "nbf" in self.payload:
            nbf_ts = float(self.payload["nbf"])
            nbf_dt = datetime.fromtimestamp(nbf_ts, tz=timezone.utc)
            analysis["claims"]["nbf"] = nbf_dt.isoformat()
            if ref_ts < nbf_ts:
                analysis["status"] = "NOT_YET_VALID"
                analysis["warnings"].append(f"Token not valid before {nbf_dt.isoformat()}")

        # Issued At (iat)
        if "iat" in self.payload:
            iat_ts = float(self.payload["iat"])
            iat_dt = datetime.fromtimestamp(iat_ts, tz=timezone.utc)
            analysis["claims"]["iat"] = iat_dt.isoformat()

        # Other standard claims
        for claim in ["iss", "sub", "aud", "jti"]:
            if claim in self.payload:
                analysis["claims"][claim] = self.payload[claim]

        return analysis

    def summary(self) -> str:
        return format_jwt_report(self)


def format_jwt_report(inspector: JWTInspector) -> str:
    analysis = inspector.inspect_claims()
    lines = [
        "🔒 JWT Inspection Report",
        "=" * 50,
        f"Header:    {json.dumps(inspector.header)}",
        f"Algorithm: {analysis['algorithm']}",
        f"Status:    {analysis['status']}",
    ]

    if analysis["warnings"]:
        lines.append("Warnings:")
        for w in analysis["warnings"]:
            lines.append(f"  ⚠️  {w}")

    lines.append("\nDecoded Payload:")
    lines.append(json.dumps(inspector.payload, indent=2))

    return "\n".join(lines)


def main() -> None:
    arg_parser = argparse.ArgumentParser(description="Inspect and decode JSON Web Tokens (JWT)")
    arg_parser.add_argument("token", type=str, help="JWT token string (header.payload.signature)")
    arg_parser.add_argument("--json", action="store_true", help="Output result in raw JSON format")

    args = arg_parser.parse_args()

    try:
        inspector = JWTInspector(args.token)
        if args.json:
            result = {
                "header": inspector.header,
                "payload": inspector.payload,
                "analysis": inspector.inspect_claims(),
            }
            print(json.dumps(result, indent=2))
        else:
            print(format_jwt_report(inspector))
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
