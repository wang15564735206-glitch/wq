"""Storage layer for TaskFlow - uses JSON file persistence."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .models import Task, Priority


class StorageError(Exception):
    """Base exception for storage operations."""
    pass


class TaskStore:
    """Manages task persistence using a JSON file."""
    
    def __init__(self, filepath: Optional[str] = None):
        if filepath is None:
            filepath = os.path.join(os.path.expanduser("~"), ".taskflow.json")
        self.filepath = Path(filepath)
        self.tasks: List[Task] = []
        self._load()
    
    def _load(self) -> None:
        """Load tasks from JSON file."""
        if not self.filepath.exists():
            self.tasks = []
            return
        
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.tasks = []
            for item in data.get("tasks", []):
                task = Task(
                    id=item["id"],
                    title=item["title"],
                    description=item.get("description", ""),
                    priority=Priority(item["priority"]),
                    completed=item.get("completed", False),
                    created_at=datetime.fromisoformat(item["created_at"]),
                    due_date=datetime.fromisoformat(item["due_date"]) if item.get("due_date") else None,
                    tags=item.get("tags", []),
                )
                self.tasks.append(task)
        except (json.JSONDecodeError, KeyError) as e:
            raise StorageError(f"Failed to load tasks: {e}")
    
    def _save(self) -> None:
        """Save tasks to JSON file."""
        try:
            data = {
                "version": "1.0",
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "description": t.description,
                        "priority": t.priority.value,
                        "completed": t.completed,
                        "created_at": t.created_at.isoformat(),
                        "due_date": t.due_date.isoformat() if t.due_date else None,
                        "tags": t.tags,
                    }
                    for t in self.tasks
                ]
            }
            
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError as e:
            raise StorageError(f"Failed to save tasks: {e}")
    
    def add(self, title: str, description: str = "", priority: Priority = Priority.MEDIUM, 
            due_date: Optional[str] = None, tags: Optional[List[str]] = None) -> Task:
        """Add a new task and return it."""
        new_id = max((t.id for t in self.tasks), default=0) + 1
        
        parsed_due = None
        if due_date:
            try:
                parsed_due = datetime.fromisoformat(due_date)
            except ValueError:
                raise StorageError(f"Invalid date format: {due_date}. Use YYYY-MM-DD or ISO format.")
        
        task = Task(
            id=new_id,
            title=title,
            description=description,
            priority=priority,
            due_date=parsed_due,
            tags=tags or [],
        )
        
        self.tasks.append(task)
        self._save()
        return task
    
    def list_tasks(self, completed: Optional[bool] = None, priority: Optional[Priority] = None,
                   tag: Optional[str] = None) -> List[Task]:
        """List tasks with optional filters."""
        result = self.tasks
        
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        
        if priority is not None:
            result = [t for t in result if t.priority == priority]
        
        if tag is not None:
            result = [t for t in result if tag.lower() in [tg.lower() for tg in t.tags]]
        
        return sorted(result, key=lambda t: (t.completed, -self._priority_value(t.priority), t.id))
    
    def _priority_value(self, priority: Priority) -> int:
        """Convert priority to sort value (higher = more urgent)."""
        return {"low": 0, "medium": 1, "high": 2}[priority.value]
    
    def complete(self, task_id: int) -> Optional[Task]:
        """Mark a task as completed."""
        for task in self.tasks:
            if task.id == task_id:
                task.completed = True
                self._save()
                return task
        return None
    
    def delete(self, task_id: int) -> bool:
        """Delete a task by ID."""
        initial_len = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.id != task_id]
        if len(self.tasks) < initial_len:
            self._save()
            return True
        return False
    
    def get(self, task_id: int) -> Optional[Task]:
        """Get a task by ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def stats(self) -> dict:
        """Get statistics about tasks."""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.completed)
        high = sum(1 for t in self.tasks if t.priority == Priority.HIGH and not t.completed)
        medium = sum(1 for t in self.tasks if t.priority == Priority.MEDIUM and not t.completed)
        low = sum(1 for t in self.tasks if t.priority == Priority.LOW and not t.completed)
        
        return {
            "total": total,
            "completed": completed,
            "pending": total - completed,
            "high_priority": high,
            "medium_priority": medium,
            "low_priority": low,
            "completion_rate": round(completed / total * 100, 1) if total > 0 else 0,
        }
