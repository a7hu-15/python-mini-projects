"""
Unit tests for Cron Expression Parser & Schedule Calculator
"""

from datetime import datetime
import unittest

from cron_parser.cron_parser import CronField, CronParser


class TestCronField(unittest.TestCase):
    def test_wildcard(self) -> None:
        vals = CronField.parse("*", 0, 5)
        self.assertEqual(vals, {0, 1, 2, 3, 4, 5})

    def test_range(self) -> None:
        vals = CronField.parse("1-4", 0, 10)
        self.assertEqual(vals, {1, 2, 3, 4})

    def test_step(self) -> None:
        vals = CronField.parse("*/15", 0, 59)
        self.assertEqual(vals, {0, 15, 30, 45})

    def test_comma_list(self) -> None:
        vals = CronField.parse("1,15,30", 0, 59)
        self.assertEqual(vals, {1, 15, 30})

    def test_invalid_range(self) -> None:
        with self.assertRaises(ValueError):
            CronField.parse("5-2", 0, 10)

    def test_out_of_bounds(self) -> None:
        with self.assertRaises(ValueError):
            CronField.parse("65", 0, 59)


class TestCronParser(unittest.TestCase):
    def test_parse_valid_expression(self) -> None:
        parser = CronParser("0 12 * * *")
        self.assertEqual(parser.minutes, {0})
        self.assertEqual(parser.hours, {12})

    def test_invalid_field_count(self) -> None:
        with self.assertRaises(ValueError):
            CronParser("0 12 * *")

    def test_matches_and_next_executions(self) -> None:
        parser = CronParser("15 10 * * *")
        start = datetime(2026, 1, 1, 10, 0, 0)
        next_runs = parser.get_next_executions(start, count=2)
        self.assertEqual(len(next_runs), 2)
        self.assertEqual(next_runs[0], datetime(2026, 1, 1, 10, 15, 0))
        self.assertEqual(next_runs[1], datetime(2026, 1, 2, 10, 15, 0))


if __name__ == "__main__":
    unittest.main()
