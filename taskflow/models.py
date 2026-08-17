"""Data models for TaskFlow."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Task:
    """A single task in the system."""
    
    id: int
    title: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    tags: list = field(default_factory=list)
    
    def __str__(self) -> str:
        status = "✓" if self.completed else "○"
        priority_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}[self.priority.value]
        return f"{status} [{priority_icon}] #{self.id} {self.title}"
