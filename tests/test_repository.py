"""Integration tests for repository operations."""
import datetime

import pytest

from gamelife.core.config import TaskPriority, TaskStatus
from gamelife.data.database import Task, User

def test_user_crud(temp_db):
    """Test user creation, retrieval, and update operations."""
    # Create user
    user = temp_db.create_user("test_user")
    assert user.id is not None
    assert user.username == "test_user"
    
    # Retrieve user
    retrieved = temp_db.get_user("test_user")
    assert retrieved is not None
    assert retrieved.id == user.id
    assert retrieved.username == user.username
    
    # Update XP and level
    temp_db.update_user_xp(user.id, 100, 2)
    updated = temp_db.get_user("test_user")
    assert updated.xp == 100
    assert updated.level == 2
    
    # Update streak
    today = datetime.date.today()
    temp_db.update_user_streak(user.id, 5, 5, today)
    updated = temp_db.get_user("test_user")
    assert updated.streak == 5
    assert updated.longest_streak == 5
    assert updated.last_completion_date == today

def test_task_crud(temp_db, test_user):
    """Test task creation, retrieval, and update operations."""
    # Create task
    task = Task(
        id=None,
        user_id=test_user.id,
        title="Test Task",
        description="Test Description",
        priority=TaskPriority.HIGH,
        status=TaskStatus.PENDING,
        due_at=datetime.datetime.now(datetime.UTC)
    )
    
    created = temp_db.create_task(task)
    assert created.id is not None
    
    # Get tasks
    tasks = temp_db.get_tasks(test_user.id)
    assert len(tasks) == 1
    assert tasks[0].id == created.id
    assert tasks[0].title == task.title
    
    # Update status
    now = datetime.datetime.now(datetime.UTC)
    temp_db.update_task_status(created.id, TaskStatus.COMPLETED, now)
    
    tasks = temp_db.get_tasks(test_user.id, TaskStatus.COMPLETED)
    assert len(tasks) == 1
    assert tasks[0].status == TaskStatus.COMPLETED
    assert tasks[0].completed_at == now

def test_task_filtering(temp_db, test_user):
    """Test task filtering by status."""
    # Create tasks with different statuses
    now = datetime.datetime.now(datetime.UTC)
    
    tasks = [
        Task(
            id=None,
            user_id=test_user.id,
            title=f"Task {i}",
            description=f"Description {i}",
            priority=TaskPriority.MEDIUM,
            status=status,
            due_at=now
        )
        for i, status in enumerate([
            TaskStatus.PENDING,
            TaskStatus.IN_PROGRESS,
            TaskStatus.COMPLETED,
            TaskStatus.FAILED
        ])
    ]
    
    for task in tasks:
        temp_db.create_task(task)
    
    # Test filtering
    pending = temp_db.get_tasks(test_user.id, TaskStatus.PENDING)
    assert len(pending) == 1
    assert pending[0].status == TaskStatus.PENDING
    
    completed = temp_db.get_tasks(test_user.id, TaskStatus.COMPLETED)
    assert len(completed) == 1
    assert completed[0].status == TaskStatus.COMPLETED
    
    # Test getting all tasks
    all_tasks = temp_db.get_tasks(test_user.id)
    assert len(all_tasks) == 4