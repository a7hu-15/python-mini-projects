"""
Unit tests for JWT Inspector & Claims Decoder
"""

import base64
from datetime import datetime, timedelta, timezone
import json
import unittest

from jwt_inspector.jwt_inspector import JWTInspector


def create_mock_jwt(header: dict, payload: dict) -> str:
    h_bytes = json.dumps(header).encode("utf-8")
    p_bytes = json.dumps(payload).encode("utf-8")
    h_b64 = base64.urlsafe_b64encode(h_bytes).decode("utf-8").rstrip("=")
    p_b64 = base64.urlsafe_b64encode(p_bytes).decode("utf-8").rstrip("=")
    sig_b64 = "mock_signature_hash"
    return f"{h_b64}.{p_b64}.{sig_b64}"


class TestJWTInspector(unittest.TestCase):
    def test_valid_jwt(self) -> None:
        now = datetime.now(timezone.utc)
        exp = int((now + timedelta(hours=1)).timestamp())
        token = create_mock_jwt({"alg": "HS256", "typ": "JWT"}, {"sub": "user_123", "exp": exp})

        inspector = JWTInspector(token)
        self.assertEqual(inspector.header["alg"], "HS256")
        self.assertEqual(inspector.payload["sub"], "user_123")

        analysis = inspector.inspect_claims(reference_time=now)
        self.assertEqual(analysis["status"], "VALID")
        self.assertGreater(analysis["claims"]["time_remaining_seconds"], 0)

    def test_expired_jwt(self) -> None:
        now = datetime.now(timezone.utc)
        past_exp = int((now - timedelta(hours=1)).timestamp())
        token = create_mock_jwt({"alg": "RS256"}, {"exp": past_exp})

        inspector = JWTInspector(token)
        analysis = inspector.inspect_claims(reference_time=now)
        self.assertEqual(analysis["status"], "EXPIRED")
        self.assertTrue(len(analysis["warnings"]) > 0)

    def test_invalid_structure(self) -> None:
        with self.assertRaises(ValueError):
            JWTInspector("invalid.token.structure.extra")


if __name__ == "__main__":
    unittest.main()
