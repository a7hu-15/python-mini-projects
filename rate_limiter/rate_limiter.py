"""
CLI Rate Limiter & Token Bucket Utility in Python.

Provides thread-safe Token Bucket and Leaky Bucket rate limiting algorithms,
a `@rate_limit` function decorator, and a CLI test suite runner.

Algorithms:
- Token Bucket: Allows bursts up to bucket capacity and refills tokens at a constant rate.
- Leaky Bucket: Enforces smooth outflow of requests at a fixed leak rate.

Features:
- Thread-safe token acquisition.
- Function decorator `@rate_limit` for easy API / function wrapping.
- Custom exception handling (`RateLimitExceeded`).
- CLI interface to simulate high concurrency request bursts.
"""

import argparse
import functools
import sys
import threading
import time
from typing import Callable, Optional, TypeVar, Any

T = TypeVar("T")


class RateLimitExceeded(Exception):
    """Raised when a request exceeds the configured rate limit."""
    pass


class TokenBucketRateLimiter:
    """
    Token Bucket Rate Limiter implementation.
    
    Tokens are added to the bucket at a rate of `refill_rate` tokens per second,
    up to a maximum `capacity`.
    """

    def __init__(self, capacity: int, refill_rate: float):
        """
        :param capacity: Maximum number of tokens bucket can hold.
        :param refill_rate: Number of tokens refilled per second.
        """
        if capacity <= 0 or refill_rate <= 0:
            raise ValueError("Capacity and refill rate must be positive values.")
        self.capacity: float = float(capacity)
        self.refill_rate: float = float(refill_rate)
        self.tokens: float = float(capacity)
        self.last_refill: float = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.last_refill = now
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)

    def acquire(self, tokens: int = 1, blocking: bool = False, timeout: Optional[float] = None) -> bool:
        """
        Attempt to consume `tokens` from the bucket.

        :param tokens: Number of tokens required.
        :param blocking: If True, sleep until tokens become available or timeout expires.
        :param timeout: Maximum time to wait in seconds if blocking.
        :return: True if tokens were acquired, False otherwise.
        """
        start_time = time.monotonic()

        while True:
            with self._lock:
                self._refill()
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True

            if not blocking:
                return False

            if timeout is not None and (time.monotonic() - start_time) >= timeout:
                return False

            time.sleep(0.01)


class LeakyBucketRateLimiter:
    """
    Leaky Bucket Rate Limiter implementation.

    Requests fill a bucket of max `capacity` which leaks at a constant `leak_rate` per second.
    """

    def __init__(self, capacity: int, leak_rate: float):
        """
        :param capacity: Maximum bucket depth (queue length).
        :param leak_rate: Number of requests processed (leaked) per second.
        """
        if capacity <= 0 or leak_rate <= 0:
            raise ValueError("Capacity and leak rate must be positive values.")
        self.capacity: float = float(capacity)
        self.leak_rate: float = float(leak_rate)
        self.water: float = 0.0
        self.last_leak: float = time.monotonic()
        self._lock = threading.Lock()

    def _leak(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_leak
        self.last_leak = now
        self.water = max(0.0, self.water - elapsed * self.leak_rate)

    def allow_request(self) -> bool:
        """
        Check if request can be accepted without overflowing bucket.

        :return: True if accepted, False if rate limit exceeded.
        """
        with self._lock:
            self._leak()
            if self.water + 1.0 <= self.capacity:
                self.water += 1.0
                return True
            return False


def rate_limit(limiter: TokenBucketRateLimiter, raise_on_exceeded: bool = True):
    """
    Function decorator to rate-limit calls to any target function.

    :param limiter: TokenBucketRateLimiter instance.
    :param raise_on_exceeded: If True, raises RateLimitExceeded; if False, returns None.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not limiter.acquire(1, blocking=False):
                if raise_on_exceeded:
                    raise RateLimitExceeded(f"Rate limit exceeded for function '{func.__name__}'.")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator


def main():
    parser = argparse.ArgumentParser(description="CLI Rate Limiter Simulation Utility")
    parser.add_argument("--capacity", type=int, default=5, help="Bucket capacity (default: 5)")
    parser.add_argument("--refill-rate", type=float, default=2.0, help="Tokens refilled per sec (default: 2.0)")
    parser.add_argument("--requests", type=int, default=10, help="Number of simulated requests (default: 10)")
    parser.add_argument("--delay", type=float, default=0.2, help="Delay between requests in sec (default: 0.2)")

    args = parser.parse_args()

    print(f"=== Starting Rate Limiter Simulation ===")
    print(f"Capacity: {args.capacity} | Refill Rate: {args.refill_rate}/sec")
    limiter = TokenBucketRateLimiter(args.capacity, args.refill_rate)

    accepted = 0
    rejected = 0

    for i in range(1, args.requests + 1):
        success = limiter.acquire(1, blocking=False)
        status = "ALLOWED" if success else "REJECTED"
        if success:
            accepted += 1
        else:
            rejected += 1
        print(f"Request #{i:02d}: {status} (Remaining tokens: {limiter.tokens:.2f})")
        time.sleep(args.delay)

    print("\n=== Simulation Summary ===")
    print(f"Total Requests: {args.requests} | Allowed: {accepted} | Rejected: {rejected}")


if __name__ == "__main__":
    main()
