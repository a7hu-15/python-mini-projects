"""
🔗 URL Shortener (CLI)

A local CLI-based URL shortener that uses hash-based short codes.
Stores mappings in a JSON file for persistence.

Features:
    - Generate short codes from URLs using SHA-256 hashing
    - Configurable short code length (default: 6 characters)
    - Persistent storage in a local JSON file
    - Lookup / resolve short codes back to original URLs
    - List all stored URL mappings
    - Collision detection and handling
    - Click tracking (counts how many times a URL is resolved)

Usage:
    python url_shortener.py shorten https://example.com/very/long/url
    python url_shortener.py resolve abc123
    python url_shortener.py list
    python url_shortener.py stats

>>> shortener = URLShortener(storage_file=None)
>>> code = shortener.shorten("https://example.com")
>>> len(code)
6
>>> shortener.resolve(code)
'https://example.com'
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone


class URLShortener:
    """
    A hash-based URL shortener with persistent JSON storage.

    >>> s = URLShortener(storage_file=None)
    >>> code1 = s.shorten("https://google.com")
    >>> code2 = s.shorten("https://google.com")
    >>> code1 == code2
    True

    >>> s.resolve(code1)
    'https://google.com'

    >>> s.resolve("nonexistent") is None
    True

    >>> len(s.list_all()) == 1
    True
    """

    DEFAULT_CODE_LENGTH = 6
    DEFAULT_STORAGE_FILE = "url_store.json"

    def __init__(
        self,
        code_length: int = DEFAULT_CODE_LENGTH,
        storage_file: str | None = DEFAULT_STORAGE_FILE,
    ) -> None:
        """
        Initialize the URL shortener.

        Args:
            code_length: Length of generated short codes (4-12).
            storage_file: Path to JSON storage file. None for in-memory only.
        """
        self.code_length = max(4, min(12, code_length))
        self.storage_file = storage_file
        self._store: dict[str, dict] = {}

        if storage_file and os.path.exists(storage_file):
            self._load()

    def shorten(self, url: str) -> str:
        """
        Generate a short code for a URL.

        If the URL was already shortened, returns the existing code.

        Args:
            url: The URL to shorten.

        Returns:
            A short alphanumeric code.

        >>> s = URLShortener(storage_file=None)
        >>> code = s.shorten("https://python.org")
        >>> isinstance(code, str) and len(code) == 6
        True
        """
        url = url.strip()

        # Check if URL already exists
        for code, entry in self._store.items():
            if entry["url"] == url:
                return code

        # Generate hash-based short code
        code = self._generate_code(url)

        # Handle collisions (extremely rare with SHA-256)
        attempt = 0
        original_code = code
        while code in self._store:
            attempt += 1
            code = self._generate_code(url + str(attempt))

        # Store the mapping
        self._store[code] = {
            "url": url,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "clicks": 0,
        }

        self._save()
        return code

    def resolve(self, code: str) -> str | None:
        """
        Resolve a short code back to its original URL.

        Also increments the click counter.

        Args:
            code: The short code to look up.

        Returns:
            The original URL, or None if not found.

        >>> s = URLShortener(storage_file=None)
        >>> code = s.shorten("https://github.com")
        >>> s.resolve(code)
        'https://github.com'
        """
        code = code.strip()

        if code not in self._store:
            return None

        self._store[code]["clicks"] += 1
        self._save()
        return self._store[code]["url"]

    def delete(self, code: str) -> bool:
        """
        Delete a URL mapping.

        Args:
            code: The short code to delete.

        Returns:
            True if deleted, False if not found.

        >>> s = URLShortener(storage_file=None)
        >>> code = s.shorten("https://example.com")
        >>> s.delete(code)
        True
        >>> s.delete("nonexistent")
        False
        """
        if code in self._store:
            del self._store[code]
            self._save()
            return True
        return False

    def list_all(self) -> dict[str, dict]:
        """
        Return all stored URL mappings.

        Returns:
            Dictionary of {code: {url, created_at, clicks}}.
        """
        return dict(self._store)

    def get_stats(self) -> dict:
        """
        Get statistics about stored URLs.

        Returns:
            Dictionary with total_urls, total_clicks, most_clicked, etc.

        >>> s = URLShortener(storage_file=None)
        >>> _ = s.shorten("https://a.com")
        >>> stats = s.get_stats()
        >>> stats["total_urls"]
        1
        """
        total_clicks = sum(entry["clicks"] for entry in self._store.values())
        most_clicked = None

        if self._store:
            most_clicked_code = max(
                self._store, key=lambda k: self._store[k]["clicks"]
            )
            most_clicked = {
                "code": most_clicked_code,
                "url": self._store[most_clicked_code]["url"],
                "clicks": self._store[most_clicked_code]["clicks"],
            }

        return {
            "total_urls": len(self._store),
            "total_clicks": total_clicks,
            "most_clicked": most_clicked,
        }

    def _generate_code(self, text: str) -> str:
        """Generate a short code using SHA-256 hash."""
        hash_hex = hashlib.sha256(text.encode("utf-8")).hexdigest()
        # Use a mix of characters for the short code
        return hash_hex[: self.code_length]

    def _save(self) -> None:
        """Save the store to disk (if storage_file is set)."""
        if self.storage_file:
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(self._store, f, indent=2)

    def _load(self) -> None:
        """Load the store from disk."""
        if self.storage_file and os.path.exists(self.storage_file):
            with open(self.storage_file, "r", encoding="utf-8") as f:
                self._store = json.load(f)


def print_table(shortener: URLShortener) -> None:
    """Display all stored URLs in a formatted table."""
    urls = shortener.list_all()

    if not urls:
        print("  No URLs stored yet.")
        return

    print(f"  {'Code':<10} {'Clicks':<8} {'URL'}")
    print(f"  {'─' * 10} {'─' * 8} {'─' * 40}")

    for code, entry in urls.items():
        url = entry["url"]
        if len(url) > 50:
            url = url[:47] + "..."
        print(f"  {code:<10} {entry['clicks']:<8} {url}")


def main() -> None:
    """CLI entry point."""
    shortener = URLShortener()

    if len(sys.argv) < 2:
        # Interactive mode
        print("\n🔗 URL Shortener")
        print("─" * 30)
        print("Commands: shorten <url> | resolve <code> | list | stats | quit\n")

        while True:
            try:
                user_input = input("url> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

            if not user_input:
                continue

            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()

            if command in ("q", "quit", "exit"):
                print("Goodbye! 👋")
                break
            elif command == "shorten" and len(parts) > 1:
                code = shortener.shorten(parts[1])
                print(f"  ✅ Short code: {code}")
            elif command == "resolve" and len(parts) > 1:
                url = shortener.resolve(parts[1])
                if url:
                    print(f"  🔗 {url}")
                else:
                    print(f"  ❌ Code '{parts[1]}' not found")
            elif command == "list":
                print_table(shortener)
            elif command == "stats":
                stats = shortener.get_stats()
                print(f"  📊 Total URLs: {stats['total_urls']}")
                print(f"  📊 Total clicks: {stats['total_clicks']}")
                if stats["most_clicked"]:
                    mc = stats["most_clicked"]
                    print(f"  🏆 Most clicked: {mc['code']} ({mc['clicks']} clicks)")
            else:
                print("  Unknown command. Use: shorten <url> | resolve <code> | list | stats | quit")
        return

    # Command-line mode
    command = sys.argv[1].lower()

    if command == "shorten" and len(sys.argv) > 2:
        url = sys.argv[2]
        code = shortener.shorten(url)
        print(f"✅ {url} → {code}")

    elif command == "resolve" and len(sys.argv) > 2:
        code = sys.argv[2]
        url = shortener.resolve(code)
        if url:
            print(f"🔗 {code} → {url}")
        else:
            print(f"❌ Code '{code}' not found")

    elif command == "list":
        print_table(shortener)

    elif command == "stats":
        stats = shortener.get_stats()
        print(f"📊 Total URLs: {stats['total_urls']}")
        print(f"📊 Total clicks: {stats['total_clicks']}")

    else:
        print("Usage: python url_shortener.py [shorten <url> | resolve <code> | list | stats]")


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.ELLIPSIS)
    main()
