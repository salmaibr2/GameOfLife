"""Test configuration and fixtures."""
import datetime
import os
import tempfile
from pathlib import Path

import pytest

from gamelife.core.config import TaskPriority, TaskStatus
from gamelife.data.database import Database, Task, User

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp()
    os.close(fd)
    
    db = Database(Path(path))
    yield db
    
    os.unlink(path)

@pytest.fixture
def test_user(temp_db):
    """Create a test user."""
    user = temp_db.create_user("test_user")
    return user

@pytest.fixture
def test_task(temp_db, test_user):
    """Create a test task."""
    task = Task(
        id=None,
        user_id=test_user.id,
        title="Test Task",
        description="Test Description",
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.PENDING,
        due_at=datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)
    )
    return temp_db.create_task(task)