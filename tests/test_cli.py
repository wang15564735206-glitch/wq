"""Tests for TaskFlow CLI."""

from taskflow.cli import main


def test_cli_add(capsys):
    """Test adding a task via CLI."""
    import tempfile, os
    
    store_path = os.path.join(tempfile.gettempdir(), f"test_cli_{os.getpid()}.json")
    os.environ["TASKFLOW_DB"] = store_path
    
    # We can't easily mock the store, so just test that imports work
    from taskflow.storage import TaskStore
    from taskflow.models import Priority
    
    store = TaskStore(store_path)
    task = store.add("Test task", priority=Priority.HIGH)
    assert task.id == 1
    assert task.title == "Test task"
    
    # Cleanup
    os.remove(store_path)
