"""Database models and repository for Game of Life."""
import datetime
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from gamelife.core.config import TaskPriority, TaskStatus, config

@dataclass
class User:
    """User profile data model."""
    id: Optional[int]
    username: str
    xp: int = 0
    level: int = 1
    streak: int = 0
    longest_streak: int = 0
    last_completion_date: Optional[datetime.date] = None
    created_at: datetime.datetime = datetime.datetime.now(datetime.UTC)

@dataclass
class Task:
    """Task data model."""
    id: Optional[int]
    user_id: int
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus
    due_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None
    category: Optional[str] = None
    created_at: datetime.datetime = datetime.datetime.now(datetime.UTC)
    updated_at: datetime.datetime = datetime.datetime.now(datetime.UTC)

class Database:
    """Database connection and repository implementation."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database connection."""
        self.db_path = db_path or config.db_path
        self._init_db()
    
    def _init_db(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    xp INTEGER NOT NULL DEFAULT 0,
                    level INTEGER NOT NULL DEFAULT 1,
                    streak INTEGER NOT NULL DEFAULT 0,
                    longest_streak INTEGER NOT NULL DEFAULT 0,
                    last_completion_date DATE,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT NOT NULL,
                    status TEXT NOT NULL,
                    category TEXT,
                    due_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
                CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
                CREATE INDEX IF NOT EXISTS idx_tasks_due_at ON tasks(due_at);
            """)
    
    def create_user(self, username: str) -> User:
        """Create a new user profile."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO users (username) VALUES (?)",
                (username,)
            )
            user_id = cursor.lastrowid
            return User(id=user_id, username=username)
    
    def get_user(self, username: str) -> Optional[User]:
        """Get user by username."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            if row:
                return User(**dict(row))
            return None
    
    def create_task(self, task: Task) -> Task:
        """Create a new task."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO tasks (
                    user_id, title, description, priority, status,
                    category, due_at, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.user_id, task.title, task.description,
                    task.priority.name, task.status.name,
                    task.category, task.due_at.isoformat(),
                    task.completed_at.isoformat() if task.completed_at else None
                )
            )
            task.id = cursor.lastrowid
            return task
    
    def get_tasks(self, user_id: int, status: Optional[TaskStatus] = None) -> List[Task]:
        """Get tasks for a user, optionally filtered by status."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM tasks WHERE user_id = ?"
            params = [user_id]
            
            if status:
                query += " AND status = ?"
                params.append(status.name)
            
            cursor = conn.execute(query, params)
            return [
                Task(
                    **{
                        **dict(row),
                        'priority': TaskPriority[row['priority']],
                        'status': TaskStatus[row['status']],
                        'due_at': datetime.datetime.fromisoformat(row['due_at']),
                        'completed_at': (
                            datetime.datetime.fromisoformat(row['completed_at'])
                            if row['completed_at']
                            else None
                        )
                    }
                )
                for row in cursor.fetchall()
            ]
    
    def update_task_status(
        self,
        task_id: int,
        status: TaskStatus,
        completed_at: Optional[datetime.datetime] = None
    ) -> None:
        """Update task status and completion time."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE tasks 
                SET status = ?, completed_at = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    status.name,
                    completed_at.isoformat() if completed_at else None,
                    task_id
                )
            )
    
    def update_user_xp(self, user_id: int, xp: int, level: int) -> None:
        """Update user XP and level."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE users SET xp = ?, level = ? WHERE id = ?",
                (xp, level, user_id)
            )
    
    def update_user_streak(
        self,
        user_id: int,
        streak: int,
        longest_streak: int,
        last_completion_date: datetime.date
    ) -> None:
        """Update user streak information."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE users 
                SET streak = ?, longest_streak = ?, last_completion_date = ?
                WHERE id = ?
                """,
                (streak, longest_streak, last_completion_date.isoformat(), user_id)
            )