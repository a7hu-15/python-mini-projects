"""
🔐 Password Strength Checker

A comprehensive password strength analyzer that evaluates passwords based on
multiple security criteria and provides actionable feedback.

Scoring criteria:
    - Length (8+ chars minimum, 12+ recommended, 16+ excellent)
    - Uppercase letters
    - Lowercase letters
    - Digits
    - Special characters
    - No common patterns (123, abc, password, qwerty, etc.)
    - No character repetition (aaa, 111)

Strength levels:
    - 💀 Very Weak  (0-2 points)
    - 🔴 Weak       (3-4 points)
    - 🟡 Fair       (5-6 points)
    - 🟢 Strong     (7-8 points)
    - 🛡️  Very Strong (9+ points)

Usage:
    python password_checker.py                    # Interactive mode
    python password_checker.py "MyP@ssw0rd!"      # Check specific password

>>> result = check_password_strength("abc")
>>> result["strength"]
'Very Weak'

>>> result = check_password_strength("MyStr0ng!P@ss#2024")
>>> result["strength"]
'Very Strong'

>>> result = check_password_strength("Password123")
>>> result["strength"] in ('Very Weak', 'Weak', 'Fair')
True
"""

from __future__ import annotations

import re
import string
import sys


# Common password patterns to penalize
COMMON_PATTERNS = [
    "password", "123456", "qwerty", "abc123", "letmein",
    "admin", "welcome", "monkey", "dragon", "master",
    "login", "princess", "football", "shadow", "sunshine",
    "trustno1", "iloveyou", "batman", "access", "hello",
]

SEQUENTIAL_PATTERNS = [
    "0123456789",
    "abcdefghijklmnopqrstuvwxyz",
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
]


def check_password_strength(password: str) -> dict:
    """
    Analyze the strength of a password and return detailed results.

    Args:
        password: The password string to evaluate.

    Returns:
        A dictionary containing:
            - score: Integer score (0-10+)
            - strength: String label (Very Weak to Very Strong)
            - feedback: List of improvement suggestions
            - details: Dict of individual check results

    >>> result = check_password_strength("a")
    >>> result["score"] < 5
    True

    >>> result = check_password_strength("Xy9!mK2@pQ#rL5")
    >>> result["score"] >= 7
    True
    """
    score = 0
    feedback = []
    details = {}

    # --- Length checks ---
    length = len(password)
    if length >= 16:
        score += 3
        details["length"] = "Excellent (16+ chars)"
    elif length >= 12:
        score += 2
        details["length"] = "Good (12+ chars)"
    elif length >= 8:
        score += 1
        details["length"] = "Acceptable (8+ chars)"
    else:
        feedback.append("Use at least 8 characters (12+ recommended)")
        details["length"] = f"Too short ({length} chars)"

    # --- Character diversity ---
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?`~]", password))

    if has_upper:
        score += 1
        details["uppercase"] = "✓ Contains uppercase"
    else:
        feedback.append("Add uppercase letters (A-Z)")
        details["uppercase"] = "✗ No uppercase"

    if has_lower:
        score += 1
        details["lowercase"] = "✓ Contains lowercase"
    else:
        feedback.append("Add lowercase letters (a-z)")
        details["lowercase"] = "✗ No lowercase"

    if has_digit:
        score += 1
        details["digits"] = "✓ Contains digits"
    else:
        feedback.append("Add numbers (0-9)")
        details["digits"] = "✗ No digits"

    if has_special:
        score += 1
        details["special"] = "✓ Contains special characters"
    else:
        feedback.append("Add special characters (!@#$%^&*)")
        details["special"] = "✗ No special characters"

    # --- Unique character ratio ---
    unique_ratio = len(set(password)) / max(len(password), 1)
    if unique_ratio >= 0.7:
        score += 1
        details["uniqueness"] = f"✓ Good variety ({unique_ratio:.0%} unique)"
    else:
        feedback.append("Avoid repeating characters too much")
        details["uniqueness"] = f"✗ Low variety ({unique_ratio:.0%} unique)"

    # --- Common pattern detection ---
    password_lower = password.lower()

    has_common = any(pattern in password_lower for pattern in COMMON_PATTERNS)
    if has_common:
        score -= 2
        feedback.append("Avoid common words like 'password', 'admin', 'qwerty'")
        details["common_patterns"] = "✗ Contains common password pattern"
    else:
        details["common_patterns"] = "✓ No common patterns"

    # --- Sequential character detection ---
    has_sequential = False
    for seq in SEQUENTIAL_PATTERNS:
        for i in range(len(seq) - 2):
            if seq[i : i + 3] in password_lower:
                has_sequential = True
                break
        if has_sequential:
            break

    if has_sequential:
        score -= 1
        feedback.append("Avoid sequential characters (abc, 123, qwerty)")
        details["sequential"] = "✗ Contains sequential characters"
    else:
        score += 1
        details["sequential"] = "✓ No sequential patterns"

    # --- Repeated characters detection ---
    has_repeats = bool(re.search(r"(.)\1{2,}", password))
    if has_repeats:
        score -= 1
        feedback.append("Avoid repeating the same character 3+ times (aaa, 111)")
        details["repetition"] = "✗ Has repeated characters"
    else:
        details["repetition"] = "✓ No excessive repetition"

    # --- Determine strength level ---
    score = max(0, score)  # Floor at 0

    if score <= 2:
        strength = "Very Weak"
    elif score <= 4:
        strength = "Weak"
    elif score <= 6:
        strength = "Fair"
    elif score <= 8:
        strength = "Strong"
    else:
        strength = "Very Strong"

    if not feedback:
        feedback.append("Great password! Keep it safe.")

    return {
        "score": score,
        "strength": strength,
        "feedback": feedback,
        "details": details,
    }


def get_strength_bar(score: int, max_score: int = 10) -> str:
    """
    Generate a visual strength bar.

    >>> len(get_strength_bar(5)) > 0
    True
    """
    filled = min(score, max_score)
    bar = "█" * filled + "░" * (max_score - filled)
    return f"[{bar}] {score}/{max_score}"


def display_results(password: str, result: dict) -> None:
    """Display password analysis results in a formatted way."""
    strength_icons = {
        "Very Weak": "💀",
        "Weak": "🔴",
        "Fair": "🟡",
        "Strong": "🟢",
        "Very Strong": "🛡️",
    }

    icon = strength_icons.get(result["strength"], "❓")

    print("\n" + "=" * 50)
    print("  🔐 PASSWORD STRENGTH ANALYSIS")
    print("=" * 50)
    print(f"  Password:  {'*' * len(password)}")
    print(f"  Length:    {len(password)} characters")
    print(f"  Strength:  {icon} {result['strength']}")
    print(f"  Score:     {get_strength_bar(result['score'])}")

    print("\n  📋 Details:")
    for key, value in result["details"].items():
        print(f"    {value}")

    if result["feedback"]:
        print("\n  💡 Suggestions:")
        for tip in result["feedback"]:
            print(f"    → {tip}")

    print("=" * 50)


def generate_strong_password(length: int = 16) -> str:
    """
    Generate a cryptographically strong random password.

    Args:
        length: Desired password length (minimum 8).

    Returns:
        A randomly generated strong password.

    >>> pwd = generate_strong_password(16)
    >>> len(pwd)
    16
    >>> result = check_password_strength(pwd)
    >>> result["score"] >= 6
    True
    """
    import secrets

    length = max(length, 8)

    # Ensure at least one of each character type
    chars = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"),
    ]

    # Fill the rest with random characters from all categories
    all_chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    chars.extend(secrets.choice(all_chars) for _ in range(length - 4))

    # Shuffle to avoid predictable positions
    result = list(chars)
    secrets.SystemRandom().shuffle(result)

    return "".join(result)


if __name__ == "__main__":
    import doctest

    doctest.testmod()

    if len(sys.argv) > 1:
        # Command-line mode
        password = sys.argv[1]
        result = check_password_strength(password)
        display_results(password, result)
    else:
        # Interactive mode
        print("\n🔐 Password Strength Checker")
        print("-" * 30)

        while True:
            password = input("\nEnter a password to check (or 'q' to quit, 'g' to generate): ")

            if password.lower() == "q":
                print("Goodbye! Stay secure! 🔒")
                break
            elif password.lower() == "g":
                generated = generate_strong_password()
                print(f"\n  🎲 Generated password: {generated}")
                result = check_password_strength(generated)
                display_results(generated, result)
            else:
                result = check_password_strength(password)
                display_results(password, result)
