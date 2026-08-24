"""
CLI Task & Todo Manager with JSON Persistence, Priorities, & Search

A practical command-line tool for managing daily tasks and todo lists.
Supports task creation, completion, deletion, priority tagging (HIGH, MEDIUM, LOW),
due date tracking, search by keyword, and JSON storage persistence.

Features:
- Add task with title, description, priority, and optional due date
- Mark tasks as completed or pending
- Filter tasks by status (PENDING / COMPLETED) or priority
- Search tasks by keyword in title or description
- Summary dashboard of task statistics
- Automatic JSON file persistence

>>> manager = TaskManager(storage_path=":memory:")
>>> manager.add_task("Finish DSA report", "Complete graph traversal section", priority="HIGH")
True
>>> manager.add_task("Buy groceries", "Milk, eggs, bread", priority="LOW")
True
>>> len(manager.list_tasks())
2
>>> manager.complete_task(1)
True
>>> manager.get_summary()["completed"]
1
>>> len(manager.search_tasks("groceries"))
1
"""

from __future__ import annotations

from datetime import datetime
import json
import os
from typing import Any, Dict, List, Optional

VALID_PRIORITIES = {"HIGH", "MEDIUM", "LOW"}
VALID_STATUSES = {"PENDING", "COMPLETED"}


class TaskManager:
    """
    Manages task list state, priority levels, search, filtering, and persistence.
    """

    def __init__(self, storage_path: str = "tasks.json") -> None:
        """
        Initialize TaskManager.

        Args:
            storage_path: Path to JSON storage file or ':memory:' for transient storage.
        """
        self.storage_path = storage_path
        self.tasks: List[Dict[str, Any]] = []
        self._next_id: int = 1
        if self.storage_path != ":memory:":
            self._load_tasks()

    def add_task(
        self,
        title: str,
        description: str = "",
        priority: str = "MEDIUM",
        due_date: Optional[str] = None,
    ) -> bool:
        """
        Add a new task.

        Args:
            title: Task summary title.
            description: Detailed notes or context.
            priority: Task priority ('HIGH', 'MEDIUM', 'LOW'). Defaults to 'MEDIUM'.
            due_date: Optional due date string in 'YYYY-MM-DD' format.

        Returns:
            True if task added successfully.

        Raises:
            ValueError: If title is empty or invalid priority/date format.
        """
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be empty.")

        priority = priority.strip().upper()
        if priority not in VALID_PRIORITIES:
            raise ValueError(f"Invalid priority '{priority}'. Must be one of {VALID_PRIORITIES}.")

        if due_date:
            try:
                datetime.strptime(due_date.strip(), "%Y-%m-%d")
                due_date = due_date.strip()
            except ValueError as err:
                raise ValueError("Due date must be in YYYY-MM-DD format.") from err

        task = {
            "id": self._next_id,
            "title": title,
            "description": description.strip(),
            "priority": priority,
            "status": "PENDING",
            "due_date": due_date,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "completed_at": None,
        }

        self.tasks.append(task)
        self._next_id += 1
        if self.storage_path != ":memory:":
            self._save_tasks()
        return True

    def complete_task(self, task_id: int) -> bool:
        """
        Mark task with task_id as COMPLETED.

        >>> m = TaskManager(storage_path=":memory:")
        >>> m.add_task("Review PR")
        True
        >>> m.complete_task(1)
        True
        >>> m.list_tasks()[0]["status"]
        'COMPLETED'
        """
        for task in self.tasks:
            if task["id"] == task_id:
                task["status"] = "COMPLETED"
                task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                if self.storage_path != ":memory:":
                    self._save_tasks()
                return True
        return False

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by ID.

        >>> m = TaskManager(storage_path=":memory:")
        >>> m.add_task("Temp task")
        True
        >>> m.delete_task(1)
        True
        >>> len(m.tasks)
        0
        """
        initial_len = len(self.tasks)
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        if len(self.tasks) < initial_len:
            if self.storage_path != ":memory:":
                self._save_tasks()
            return True
        return False

    def list_tasks(
        self,
        status_filter: Optional[str] = None,
        priority_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve list of tasks matching optional status or priority filters.
        """
        filtered = self.tasks
        if status_filter:
            sf = status_filter.strip().upper()
            filtered = [t for t in filtered if t["status"] == sf]

        if priority_filter:
            pf = priority_filter.strip().upper()
            filtered = [t for t in filtered if t["priority"] == pf]

        return filtered

    def search_tasks(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Search tasks matching keyword in title or description.

        >>> m = TaskManager(storage_path=":memory:")
        >>> m.add_task("Write unit tests", "Focus on boundary cases")
        True
        >>> len(m.search_tasks("boundary"))
        1
        """
        kw = keyword.lower().strip()
        return [
            t for t in self.tasks if kw in t["title"].lower() or kw in t["description"].lower()
        ]

    def get_summary(self) -> Dict[str, int]:
        """
        Return task statistics summary.
        """
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t["status"] == "COMPLETED")
        pending = total - completed
        high_priority = sum(1 for t in self.tasks if t["priority"] == "HIGH" and t["status"] == "PENDING")

        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "high_priority_pending": high_priority,
        }

    def _save_tasks(self) -> None:
        """Persist tasks to JSON file."""
        data = {"next_id": self._next_id, "tasks": self.tasks}
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _load_tasks(self) -> None:
        """Load tasks from JSON file if available."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.tasks = data.get("tasks", [])
                    self._next_id = data.get("next_id", len(self.tasks) + 1)
            except Exception:
                self.tasks = []
                self._next_id = 1


def run_cli() -> None:
    """Interactive CLI interface for Task Manager."""
    manager = TaskManager("tasks.json")
    print("========================================")
    print("      📋 Python CLI Task Manager 📋")
    print("========================================")

    while True:
        summary = manager.get_summary()
        print(f"\n[Tasks: {summary['total']} Total | {summary['pending']} Pending | {summary['completed']} Done | 🚨 {summary['high_priority_pending']} High Priority]")
        print("\nOptions:")
        print("1. Add Task")
        print("2. List Tasks")
        print("3. Mark Task Complete")
        print("4. Delete Task")
        print("5. Search Tasks")
        print("6. Exit")

        choice = input("\nChoose an option (1-6): ").strip()

        if choice == "1":
            try:
                title = input("Title: ")
                desc = input("Description (optional): ")
                priority = input("Priority (HIGH / MEDIUM / LOW, default MEDIUM): ").strip() or "MEDIUM"
                due = input("Due Date (YYYY-MM-DD, optional): ").strip() or None
                manager.add_task(title, desc, priority, due)
                print("✅ Task added successfully!")
            except ValueError as e:
                print(f"❌ Error: {e}")

        elif choice == "2":
            filter_choice = input("Filter by (1: All, 2: Pending, 3: Completed): ").strip()
            status_map = {"2": "PENDING", "3": "COMPLETED"}
            tasks = manager.list_tasks(status_filter=status_map.get(filter_choice))

            if not tasks:
                print("No tasks found.")
            else:
                print("\nTask List:")
                print(f"{'ID':<4} | {'Status':<10} | {'Priority':<8} | {'Due Date':<10} | Title")
                print("-" * 65)
                for t in tasks:
                    status_icon = "✅" if t["status"] == "COMPLETED" else "⏳"
                    due_str = t["due_date"] or "N/A"
                    print(f"{t['id']:<4} | {status_icon} {t['status']:<7} | {t['priority']:<8} | {due_str:<10} | {t['title']}")

        elif choice == "3":
            try:
                tid = int(input("Task ID to complete: "))
                if manager.complete_task(tid):
                    print("✅ Task marked as completed!")
                else:
                    print("❌ Task ID not found.")
            except ValueError:
                print("❌ Invalid Task ID.")

        elif choice == "4":
            try:
                tid = int(input("Task ID to delete: "))
                if manager.delete_task(tid):
                    print("🗑️ Task deleted!")
                else:
                    print("❌ Task ID not found.")
            except ValueError:
                print("❌ Invalid Task ID.")

        elif choice == "5":
            kw = input("Enter search keyword: ").strip()
            results = manager.search_tasks(kw)
            if not results:
                print(f"No tasks matching '{kw}'.")
            else:
                print(f"\nSearch Results for '{kw}':")
                for t in results:
                    print(f"  • [{t['id']}] ({t['priority']}) {t['title']} - {t['status']}")

        elif choice == "6":
            print("Goodbye! Stay productive! 🚀")
            break
        else:
            print("Invalid option. Choose 1-6.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        run_cli()
    else:
        import doctest

        print("Running Task Manager doctests...")
        results = doctest.testmod()
        if results.failed == 0:
            print(f"✅ All {results.attempted} tests passed!")
        else:
            print(f"❌ {results.failed} tests failed out of {results.attempted}")
