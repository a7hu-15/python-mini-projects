# 📋 CLI Task & Todo Manager

A feature-rich command-line task manager for organizing personal and professional tasks with JSON storage persistence.

## 🚀 Features

- ➕ **Add Tasks**: Assign title, description, priority (`HIGH`, `MEDIUM`, `LOW`), and optional due date (`YYYY-MM-DD`).
- ✅ **Task Completion**: Mark tasks completed with automated timestamping.
- 🔍 **Search & Filter**: Search by keyword across title/description, or filter by pending/completed status.
- 📊 **Task Dashboard Summary**: View real-time completion progress and high-priority pending alerts.
- 💾 **JSON Persistence**: Automatically save state to `tasks.json`.

## 💻 Usage

Run doctests:
```bash
python task_manager/task_manager.py
```

Launch interactive CLI mode:
```bash
python task_manager/task_manager.py --cli
```
