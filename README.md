# TaskFlow - Modern CLI Task Manager

A sleek, zero-dependency task manager for your terminal.

## Features

- ✅ Add tasks with titles, descriptions, and priorities
- 🔴🟡🟢 Three priority levels (high, medium, low)
- 📅 Due date support
- 🏷️ Tag-based filtering
- 📊 Statistics dashboard
- 💾 Automatic persistence to JSON
- 🚫 Zero external dependencies

## Installation

```bash
pip install -e .
```

Or run directly:

```bash
python -m taskflow.cli
```

## Usage

### Add a task
```bash
taskflow add "Buy groceries" -p high -t shopping --due 2026-08-20
taskflow add "Write documentation" -d "Document the API" -p medium -t work
```

### List tasks
```bash
taskflow list                          # Show pending tasks
taskflow list --show-all               # Show all tasks
taskflow list --priority high          # Filter by priority
taskflow list --tag shopping           # Filter by tag
```

### Complete a task
```bash
taskflow complete 1
```

### Delete a task
```bash
taskflow delete 1
```

### View statistics
```bash
taskflow stats
```

## Project Structure

```
wq/
├── taskflow/
│   ├── __init__.py    # Package init
│   ├── models.py      # Data models (Task, Priority)
│   ├── storage.py     # JSON persistence layer
│   └── cli.py         # Command-line interface
├── tests/
│   └── test_storage.py
├── pyproject.toml     # Project configuration
└── README.md
```

## Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=taskflow

# Type check (requires mypy)
mypy taskflow
```

## License

MIT
