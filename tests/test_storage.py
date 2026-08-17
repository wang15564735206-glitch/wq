"""Tests for TaskFlow storage."""

import os
import tempfile
from datetime import datetime

import pytest

from taskflow.models import Priority
from taskflow.storage import TaskStore, StorageError


class TestTaskStore:
    """Tests for TaskStore class."""
    
    def test_add_task(self, tmp_path):
        """Test adding a new task."""
        store = TaskStore(str(tmp_path / "test.json"))
        task = store.add("Buy groceries", priority=Priority.HIGH)
        
        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.priority == Priority.HIGH
        assert not task.completed
    
    def test_list_tasks_empty(self, tmp_path):
        """Test listing tasks when empty."""
        store = TaskStore(str(tmp_path / "empty.json"))
        tasks = store.list_tasks()
        
        assert tasks == []
    
    def test_list_tasks_filtered(self, tmp_path):
        """Test filtering tasks."""
        store = TaskStore(str(tmp_path / "filter.json"))
        store.add("Low priority task", priority=Priority.LOW)
        store.add("High priority task", priority=Priority.HIGH)
        store.add("Another high task", priority=Priority.HIGH)
        
        high = store.list_tasks(priority=Priority.HIGH)
        assert len(high) == 2
        assert all(t.priority == Priority.HIGH for t in high)
    
    def test_complete_task(self, tmp_path):
        """Test completing a task."""
        store = TaskStore(str(tmp_path / "complete.json"))
        task = store.add("Complete me")
        
        result = store.complete(task.id)
        assert result is not None
        assert result.completed is True
        assert result.id == task.id
    
    def test_complete_nonexistent(self, tmp_path):
        """Test completing a non-existent task."""
        store = TaskStore(str(tmp_path / "nonexist.json"))
        result = store.complete(999)
        assert result is None
    
    def test_delete_task(self, tmp_path):
        """Test deleting a task."""
        store = TaskStore(str(tmp_path / "delete.json"))
        task = store.add("Delete me")
        
        assert store.delete(task.id) is True
        assert store.get(task.id) is None
    
    def test_delete_nonexistent(self, tmp_path):
        """Test deleting a non-existent task."""
        store = TaskStore(str(tmp_path / "delete_nonexist.json"))
        assert store.delete(999) is False
    
    def test_stats(self, tmp_path):
        """Test statistics calculation."""
        store = TaskStore(str(tmp_path / "stats.json"))
        store.add("Task 1", priority=Priority.HIGH)
        store.add("Task 2", priority=Priority.MEDIUM)
        store.add("Task 3", priority=Priority.LOW)
        task4 = store.add("Task 4", priority=Priority.HIGH)
        
        store.complete(task4.id)
        
        stats = store.stats()
        assert stats["total"] == 4
        assert stats["completed"] == 1
        assert stats["pending"] == 3
        assert stats["high_priority"] == 1
        assert stats["completion_rate"] == 25.0
    
    def test_persistence(self, tmp_path):
        """Test that tasks persist across instances."""
        path = str(tmp_path / "persist.json")
        
        store1 = TaskStore(path)
        store1.add("Persistent task")
        
        store2 = TaskStore(path)
        tasks = store2.list_tasks()
        
        assert len(tasks) == 1
        assert tasks[0].title == "Persistent task"
    
    def test_invalid_date(self, tmp_path):
        """Test invalid date format raises error."""
        store = TaskStore(str(tmp_path / "invalid.json"))
        with pytest.raises(StorageError, match="Invalid date"):
            store.add("Bad date", due_date="not-a-date")
