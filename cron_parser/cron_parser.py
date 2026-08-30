"""
Cron Expression Parser & Next Schedule Calculator

A CLI tool and library for parsing standard 5-part cron expressions:
    <minute> <hour> <day-of-month> <month> <day-of-week>

Features:
    - Supports wildcards (*), step values (*/15), ranges (1-5), and comma lists (1,15,30).
    - Validates field constraints (e.g. minute 0-59, hour 0-23, month 1-12).
    - Calculates next N upcoming execution timestamps starting from a given datetime.
    - CLI interface with formatted tabular output.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
import sys
from typing import Dict, List, Set


class CronField:
    """Parses a single cron field and expands it into a set of allowed integer values."""

    @staticmethod
    def parse(expression: str, min_val: int, max_val: int) -> Set[int]:
        allowed: Set[int] = set()

        for part in expression.split(","):
            part = part.strip()
            if not part:
                continue

            if "/" in part:
                subparts = part.split("/")
                if len(subparts) != 2:
                    raise ValueError(f"Invalid step expression: '{part}'")

                range_part, step_str = subparts[0], subparts[1]
                if not step_str.isdigit():
                    raise ValueError(f"Step must be an integer: '{step_str}'")
                step = int(step_str)
                if step <= 0:
                    raise ValueError(f"Step must be positive: {step}")

                if range_part == "*":
                    start, end = min_val, max_val
                elif "-" in range_part:
                    s_str, e_str = range_part.split("-")
                    start, end = int(s_str), int(e_str)
                else:
                    start, end = int(range_part), max_val

                for val in range(start, end + 1, step):
                    if min_val <= val <= max_val:
                        allowed.add(val)

            elif "-" in part:
                s_str, e_str = part.split("-")
                start, end = int(s_str), int(e_str)
                if start > end:
                    raise ValueError(f"Invalid range start > end: '{part}'")
                for val in range(start, end + 1):
                    if min_val <= val <= max_val:
                        allowed.add(val)

            elif part == "*":
                allowed.update(range(min_val, max_val + 1))

            else:
                if not part.isdigit():
                    raise ValueError(f"Invalid integer field: '{part}'")
                val = int(part)
                if not (min_val <= val <= max_val):
                    raise ValueError(f"Value {val} out of bounds ({min_val}-{max_val})")
                allowed.add(val)

        return allowed


class CronParser:
    """Parses standard 5-field cron strings and calculates future execution schedules."""

    FIELD_SPECS = [
        ("minute", 0, 59),
        ("hour", 0, 23),
        ("day_of_month", 1, 31),
        ("month", 1, 12),
        ("day_of_week", 0, 6),  # 0 = Sunday, 6 = Saturday
    ]

    def __init__(self, cron_expression: str) -> None:
        self.raw_expression = cron_expression.strip()
        parts = self.raw_expression.split()
        if len(parts) != 5:
            raise ValueError(
                f"Cron expression must have exactly 5 fields, got {len(parts)}: '{cron_expression}'"
            )

        self.minutes = CronField.parse(parts[0], 0, 59)
        self.hours = CronField.parse(parts[1], 0, 23)
        self.days_of_month = CronField.parse(parts[2], 1, 31)
        self.months = CronField.parse(parts[3], 1, 12)
        self.days_of_week = CronField.parse(parts[4], 0, 6)

    def matches(self, dt: datetime) -> bool:
        """Check if a given datetime matches the cron schedule."""
        dow = (dt.weekday() + 1) % 7  # Convert Monday=0..Sunday=6 to Sunday=0..Saturday=6
        return (
            dt.minute in self.minutes
            and dt.hour in self.hours
            and dt.day in self.days_of_month
            and dt.month in self.months
            and dow in self.days_of_week
        )

    def get_next_executions(self, start_dt: datetime, count: int = 5) -> List[datetime]:
        """Find the next N execution datetimes starting from start_dt (truncated to minutes)."""
        executions: List[datetime] = []
        curr = start_dt.replace(second=0, microsecond=0) + timedelta(minutes=1)

        # Search up to 5 years into the future to avoid infinite loop
        max_search = curr + timedelta(days=365 * 5)
        while curr < max_search and len(executions) < count:
            if self.matches(curr):
                executions.append(curr)
            curr += timedelta(minutes=1)

        return executions

    def to_dict(self) -> Dict[str, List[int]]:
        """Return expanded dictionary representation of allowed values."""
        return {
            "minute": sorted(list(self.minutes)),
            "hour": sorted(list(self.hours)),
            "day_of_month": sorted(list(self.days_of_month)),
            "month": sorted(list(self.months)),
            "day_of_week": sorted(list(self.days_of_week)),
        }


def format_summary(parser: CronParser, executions: List[datetime]) -> str:
    lines = [f"Cron Expression: {parser.raw_expression}", "=" * 50, "Expanded Fields:"]
    field_dict = parser.to_dict()
    for name, vals in field_dict.items():
        val_str = " ".join(map(str, vals))
        lines.append(f"  {name:<15}: {val_str}")

    lines.append("\nUpcoming Executions:")
    for i, dt in enumerate(executions, 1):
        lines.append(f"  {i}. {dt.strftime('%Y-%m-%d %H:%M:%S (%A)')}")

    return "\n".join(lines)


def main() -> None:
    arg_parser = argparse.ArgumentParser(description="Parse cron expressions and calculate upcoming executions.")
    arg_parser.add_argument("expression", type=str, help="5-part cron expression (e.g. '*/15 9-17 * * 1-5')")
    arg_parser.add_argument("-n", "--count", type=int, default=5, help="Number of upcoming executions to show")

    args = arg_parser.parse_args()

    try:
        parser = CronParser(args.expression)
        now = datetime.now()
        next_runs = parser.get_next_executions(now, count=args.count)
        print(format_summary(parser, next_runs))
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
