"""CLI interface for TaskFlow."""

import argparse
import sys
from datetime import datetime

from .models import Priority
from .storage import TaskStore


def cmd_add(args, store: TaskStore) -> None:
    """Add a new task."""
    try:
        priority_map = {"low": Priority.LOW, "medium": Priority.MEDIUM, "high": Priority.HIGH}
        priority = priority_map.get(args.priority, Priority.MEDIUM)
        
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
        
        task = store.add(
            title=args.title,
            description=args.description or "",
            priority=priority,
            due_date=args.due,
            tags=tags,
        )
        print(f"Added task #{task.id}: {task.title}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list(args, store: TaskStore) -> None:
    """List tasks."""
    tasks = store.list_tasks(
        completed=args.show_all,
        priority=get_priority(args.priority),
        tag=args.tag,
    )
    
    if not tasks:
        print("No tasks found.")
        return
    
    print(f"\n{'─' * 50}")
    for task in tasks:
        line = str(task)
        if task.due_date:
            line += f"  📅 {task.due_date.strftime('%Y-%m-%d')}"
        if task.tags:
            line += f"  {' '.join(f'#{t}' for t in task.tags)}"
        print(line)
    print(f"{'─' * 50}")
    print(f"Showing {len(tasks)} task(s)")


def cmd_complete(args, store: TaskStore) -> None:
    """Mark a task as complete."""
    task = store.complete(args.id)
    if task:
        print(f"Completed task #{task.id}: {task.title}")
    else:
        print(f"Task #{args.id} not found.", file=sys.stderr)
        sys.exit(1)


def cmd_delete(args, store: TaskStore) -> None:
    """Delete a task."""
    if store.delete(args.id):
        print(f"Deleted task #{args.id}.")
    else:
        print(f"Task #{args.id} not found.", file=sys.stderr)
        sys.exit(1)


def cmd_stats(args, store: TaskStore) -> None:
    """Show task statistics."""
    stats = store.stats()
    
    print(f"\n{'─' * 40}")
    print(f"  Total tasks:     {stats['total']}")
    print(f"  Completed:       {stats['completed']}")
    print(f"  Pending:         {stats['pending']}")
    print(f"  Completion rate: {stats['completion_rate']}%")
    print(f"")
    print(f"  🔴 High priority:    {stats['high_priority']}")
    print(f"  🟡 Medium priority:  {stats['medium_priority']}")
    print(f"  🟢 Low priority:     {stats['low_priority']}")
    print(f"{'─' * 40}\n")


def get_priority(value: str) -> Priority | None:
    """Convert string to Priority enum."""
    if not value:
        return None
    mapping = {"low": Priority.LOW, "medium": Priority.MEDIUM, "high": Priority.HIGH}
    return mapping.get(value.lower())


def main(argv=None):
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="taskflow",
        description="TaskFlow - A modern command-line task manager",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    
    store = TaskStore()
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title")
    add_parser.add_argument("-d", "--description", help="Task description")
    add_parser.add_argument("-p", "--priority", choices=["low", "medium", "high"], default="medium",
                           help="Task priority (default: medium)")
    add_parser.add_argument("--due", help="Due date (YYYY-MM-DD)")
    add_parser.add_argument("-t", "--tags", help="Comma-separated tags")
    add_parser.set_defaults(func=cmd_add)
    
    # List command
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--priority", choices=["low", "medium", "high"], help="Filter by priority")
    list_parser.add_argument("--tag", help="Filter by tag")
    list_parser.add_argument("--show-all", action="store_true", help="Show completed tasks too")
    list_parser.set_defaults(func=cmd_list)
    
    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Mark a task as complete")
    complete_parser.add_argument("id", type=int, help="Task ID")
    complete_parser.set_defaults(func=cmd_complete)
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("id", type=int, help="Task ID")
    delete_parser.set_defaults(func=cmd_delete)
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show statistics")
    stats_parser.set_defaults(func=cmd_stats)
    
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    args.func(args, store)


if __name__ == "__main__":
    main()
