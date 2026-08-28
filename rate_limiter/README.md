# ⏱️ Rate Limiter & Token Bucket Utility

A thread-safe Python utility providing **Token Bucket** and **Leaky Bucket** rate limiting algorithms, function decorators, and CLI simulation capabilities.

## 🚀 Features

- **Token Bucket Algorithm**: Handles bursty traffic up to bucket capacity and refills tokens continuously.
- **Leaky Bucket Algorithm**: Smooths out traffic spikes by outputting requests at a constant leak rate.
- **`@rate_limit` Decorator**: Easily protect python functions or API endpoints from excessive execution.
- **Thread-Safety**: Uses `threading.Lock()` for safe multi-threaded concurrency.
- **CLI Simulation Engine**: Interactively test and evaluate rate limiting under various load conditions.

## 💻 CLI Usage

Simulate 10 requests with a bucket capacity of 5 and refill rate of 2 tokens/sec:

```bash
python rate_limiter.py --capacity 5 --refill-rate 2.0 --requests 10 --delay 0.2
```

### Options:
- `--capacity`: Maximum bucket capacity (default: 5).
- `--refill-rate`: Tokens refilled per second (default: 2.0).
- `--requests`: Total number of simulated requests (default: 10).
- `--delay`: Delay interval between requests in seconds (default: 0.2).

## 🐍 Python Library Usage

```python
from rate_limiter import TokenBucketRateLimiter, rate_limit, RateLimitExceeded

limiter = TokenBucketRateLimiter(capacity=10, refill_rate=5.0)

# Direct token acquisition
if limiter.acquire(1):
    print("Request processed!")

# Function Decorator
@rate_limit(limiter, raise_on_exceeded=True)
def send_email():
    return "Email sent successfully"
```

## 🧪 Running Unit Tests

```bash
python -m unittest test_rate_limiter.py
```
