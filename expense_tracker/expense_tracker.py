"""
CLI Expense Tracker with Categorization & JSON Persistence

A lightweight command-line interface application for tracking personal expenses.
Supports adding expenses, viewing summaries by category, filtering by date ranges,
and persisting data in local JSON storage.

Features:
- Add expense with amount, category, date, and description
- View full expense history
- Generate summary reports (total spending, per-category breakdown)
- Filter expenses by category
- Save & Load expense history automatically to JSON storage

>>> tracker = ExpenseTracker(storage_path=":memory:")
>>> tracker.add_expense(25.50, "Food", "Lunch with colleagues", "2026-08-20")
True
>>> tracker.add_expense(15.00, "Transport", "Bus pass", "2026-08-21")
True
>>> tracker.get_total_spent()
40.5
>>> tracker.get_category_summary()["Food"]
25.5
>>> len(tracker.list_expenses())
2
"""

from __future__ import annotations

from datetime import datetime
import json
import os
from typing import Any


class ExpenseTracker:
    """
    Expense tracker manager to manage, analyze, and persist expenses.
    """

    def __init__(self, storage_path: str = "expenses.json") -> None:
        """
        Initialize ExpenseTracker.

        Args:
            storage_path: Path to JSON file for persistence, or ':memory:' for transient storage.
        """
        self.storage_path = storage_path
        self.expenses: list[dict[str, Any]] = []
        if self.storage_path != ":memory:":
            self._load_expenses()

    def add_expense(
        self, amount: float, category: str, description: str, date_str: str | None = None
    ) -> bool:
        """
        Add a new expense item.

        Args:
            amount: Positive numeric monetary amount.
            category: Category name (e.g., Food, Transport, Utilities, Entertainment).
            description: Brief note or details.
            date_str: Optional YYYY-MM-DD date string. Defaults to today.

        Returns:
            True if expense was successfully added.

        Raises:
            ValueError: If amount <= 0 or invalid date format.
        """
        if amount <= 0:
            raise ValueError("Expense amount must be positive.")

        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        else:
            # Validate YYYY-MM-DD format
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError as err:
                raise ValueError("Date format must be YYYY-MM-DD") from err

        expense = {
            "id": len(self.expenses) + 1,
            "amount": round(float(amount), 2),
            "category": category.strip().capitalize(),
            "description": description.strip(),
            "date": date_str,
        }

        self.expenses.append(expense)
        if self.storage_path != ":memory:":
            self._save_expenses()
        return True

    def list_expenses(self, category_filter: str | None = None) -> list[dict[str, Any]]:
        """
        Retrieve list of expenses, optionally filtered by category.
        """
        if not category_filter:
            return list(self.expenses)

        cat = category_filter.strip().capitalize()
        return [exp for exp in self.expenses if exp["category"] == cat]

    def get_total_spent(self) -> float:
        """Calculate cumulative total expenses."""
        return round(sum(exp["amount"] for exp in self.expenses), 2)

    def get_category_summary(self) -> dict[str, float]:
        """
        Calculate total expenses grouped by category.
        """
        summary: dict[str, float] = {}
        for exp in self.expenses:
            cat = exp["category"]
            summary[cat] = round(summary.get(cat, 0.0) + exp["amount"], 2)
        return summary

    def clear(self) -> None:
        """Clear all recorded expenses."""
        self.expenses.clear()
        if self.storage_path != ":memory:" and os.path.exists(self.storage_path):
            os.remove(self.storage_path)

    def _save_expenses(self) -> None:
        """Persist expenses to JSON storage file."""
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, indent=2)

    def _load_expenses(self) -> None:
        """Load expenses from JSON storage file if present."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self.expenses = json.load(f)
            except Exception:
                self.expenses = []


def run_cli() -> None:
    """Interactive Command-Line Interface for Expense Tracker."""
    tracker = ExpenseTracker("expenses.json")
    print("========================================")
    print("   📊 Python CLI Expense Tracker 📊")
    print("========================================")

    while True:
        print("\nMenu:")
        print("1. Add Expense")
        print("2. List All Expenses")
        print("3. View Category Summary")
        print("4. View Total Spent")
        print("5. Exit")

        choice = input("\nEnter option (1-5): ").strip()

        if choice == "1":
            try:
                amt = float(input("Amount ($): "))
                cat = input("Category (e.g. Food, Rent, Travel): ")
                desc = input("Description: ")
                date_in = input("Date (YYYY-MM-DD, press Enter for Today): ").strip()
                tracker.add_expense(amt, cat, desc, date_in if date_in else None)
                print("✅ Expense added successfully!")
            except ValueError as e:
                print(f"❌ Error: {e}")

        elif choice == "2":
            exps = tracker.list_expenses()
            if not exps:
                print("No expenses recorded yet.")
            else:
                print("\nRecorded Expenses:")
                print(f"{'ID':<4} | {'Date':<10} | {'Category':<12} | {'Amount':<8} | Description")
                print("-" * 60)
                for exp in exps:
                    print(
                        f"{exp['id']:<4} | {exp['date']:<10} | {exp['category']:<12} | ${exp['amount']:<7.2f} | {exp['description']}"
                    )

        elif choice == "3":
            summary = tracker.get_category_summary()
            if not summary:
                print("No expenses recorded yet.")
            else:
                print("\nCategory Breakdown:")
                for cat, total in summary.items():
                    print(f"  • {cat:<15}: ${total:.2f}")

        elif choice == "4":
            print(f"\nTotal Spending: ${tracker.get_total_spent():.2f}")

        elif choice == "5":
            print("Goodbye! Happy saving! 💰")
            break
        else:
            print("Invalid option. Please choose 1-5.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        run_cli()
    else:
        import doctest

        print("Running Expense Tracker doctests...")
        results = doctest.testmod()
        if results.failed == 0:
            print(f"✅ All {results.attempted} tests passed!")
        else:
            print(f"❌ {results.failed} tests failed out of {results.attempted}")
