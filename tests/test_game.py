"""Test cases for game mechanics."""
import datetime

import pytest

from gamelife.core.config import TaskPriority, TaskStatus
from gamelife.core.game import GameEngine

def test_task_completion_xp(temp_db, test_user, test_task):
    """Test XP calculation for task completion."""
    game = GameEngine(temp_db)
    completion_time = datetime.datetime.now(datetime.UTC)
    xp_earned = game.complete_task(test_task, completion_time)
    
    assert xp_earned > 0
    assert test_task.status == TaskStatus.COMPLETED
    assert test_task.completed_at == completion_time

def test_early_completion_bonus(temp_db, test_user):
    """Test early completion bonus calculation."""
    game = GameEngine(temp_db)
    due_date = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=10)
    
    task = test_task = temp_db.create_task(Task(
        id=None,
        user_id=test_user.id,
        title="Early Task",
        description="Test early completion",
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.PENDING,
        due_at=due_date
    ))
    
    # Complete 7 days early
    completion_time = due_date - datetime.timedelta(days=7)
    xp_earned = game.complete_task(task, completion_time)
    
    # Should get 50% bonus
    assert xp_earned == 37  # 25 base + 12 bonus (rounded down)

def test_task_failure_penalty(temp_db, test_user, test_task):
    """Test XP penalty for task failure."""
    game = GameEngine(temp_db)
    initial_xp = test_user.xp
    
    test_task.status = TaskStatus.FAILED
    penalty = game.fail_task(test_task)
    
    assert penalty < 0
    assert test_user.xp == max(0, initial_xp + penalty)

def test_streak_maintenance(temp_db, test_user):
    """Test streak counting and maintenance."""
    game = GameEngine(temp_db)
    
    # Create and complete a task
    task1 = temp_db.create_task(Task(
        id=None,
        user_id=test_user.id,
        title="Streak Task 1",
        description="Test streak",
        priority=TaskPriority.LOW,
        status=TaskStatus.PENDING,
        due_at=datetime.datetime.now(datetime.UTC)
    ))
    
    game.complete_task(task1, datetime.datetime.now(datetime.UTC))
    assert test_user.streak == 1
    
    # Complete another task the next day
    task2 = temp_db.create_task(Task(
        id=None,
        user_id=test_user.id,
        title="Streak Task 2",
        description="Test streak",
        priority=TaskPriority.LOW,
        status=TaskStatus.PENDING,
        due_at=datetime.datetime.now(datetime.UTC)
    ))
    
    next_day = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)
    game.complete_task(task2, next_day)
    assert test_user.streak == 2
    assert test_user.longest_streak == 2

def test_achievement_unlocking(temp_db, test_user):
    """Test achievement unlocking mechanics."""
    game = GameEngine(temp_db)
    
    # Complete first task to unlock FirstTaskCompleted
    task = temp_db.create_task(Task(
        id=None,
        user_id=test_user.id,
        title="Achievement Task",
        description="Test achievements",
        priority=TaskPriority.LOW,
        status=TaskStatus.PENDING,
        due_at=datetime.datetime.now(datetime.UTC)
    ))
    
    initial_xp = test_user.xp
    game.complete_task(task, datetime.datetime.now(datetime.UTC))
    
    # Should get task XP + achievement XP
    assert test_user.xp > initial_xp
    achievements = game.check_achievements(test_user)
    assert any(a.__name__ == "FirstTaskCompleted" for a in achievements)