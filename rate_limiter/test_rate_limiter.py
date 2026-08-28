"""
Unit tests for CLI Rate Limiter Utility.
"""

import time
import unittest
from rate_limiter import (
    TokenBucketRateLimiter,
    LeakyBucketRateLimiter,
    rate_limit,
    RateLimitExceeded,
)


class TestTokenBucketRateLimiter(unittest.TestCase):
    def test_burst_capacity(self):
        limiter = TokenBucketRateLimiter(capacity=3, refill_rate=1.0)
        self.assertTrue(limiter.acquire(1))
        self.assertTrue(limiter.acquire(1))
        self.assertTrue(limiter.acquire(1))
        self.assertFalse(limiter.acquire(1))

    def test_refill_tokens(self):
        limiter = TokenBucketRateLimiter(capacity=2, refill_rate=10.0)
        self.assertTrue(limiter.acquire(2))
        self.assertFalse(limiter.acquire(1))
        time.sleep(0.15)  # Should refill ~1.5 tokens
        self.assertTrue(limiter.acquire(1))

    def test_decorator_usage(self):
        limiter = TokenBucketRateLimiter(capacity=1, refill_rate=1.0)

        @rate_limit(limiter, raise_on_exceeded=True)
        def dummy_api():
            return "SUCCESS"

        self.assertEqual(dummy_api(), "SUCCESS")
        with self.assertRaises(RateLimitExceeded):
            dummy_api()


class TestLeakyBucketRateLimiter(unittest.TestCase):
    def test_capacity_and_leak(self):
        limiter = LeakyBucketRateLimiter(capacity=2, leak_rate=10.0)
        self.assertTrue(limiter.allow_request())
        self.assertTrue(limiter.allow_request())
        self.assertFalse(limiter.allow_request())  # Bucket full
        time.sleep(0.15)  # Leaks water
        self.assertTrue(limiter.allow_request())


if __name__ == "__main__":
    unittest.main()
