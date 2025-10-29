"""Game mechanics implementation for XP, levels, and achievements."""
import datetime
from typing import Optional

from gamelife.core.config import TaskPriority, TaskStatus, config
from gamelife.data.database import Database, Task, User

class Achievement:
    """Base class for achievements."""
    name: str
    description: str
    xp_reward: int = 50
    
    @classmethod
    def check(cls, user: User, db: Database) -> bool:
        """Check if achievement is completed."""
        raise NotImplementedError

class FirstTaskCompleted(Achievement):
    """Achievement for completing first task."""
    name = "First Steps"
    description = "Complete your first task"
    xp_reward = 25
    
    @classmethod
    def check(cls, user: User, db: Database) -> bool:
        """Check if user has completed at least one task."""
        tasks = db.get_tasks(user.id, TaskStatus.COMPLETED)
        return bool(tasks)

class SevenDayStreak(Achievement):
    """Achievement for maintaining a 7-day streak."""
    name = "Week Warrior"
    description = "Maintain a 7-day completion streak"
    xp_reward = 100
    
    @classmethod
    def check(cls, user: User, db: Database) -> bool:
        """Check if user has a 7+ day streak."""
        return user.streak >= 7

class HundredTasksCompleted(Achievement):
    """Achievement for completing 100 tasks."""
    name = "Century Club"
    description = "Complete 100 tasks"
    xp_reward = 500
    
    @classmethod
    def check(cls, user: User, db: Database) -> bool:
        """Check if user has completed 100 tasks."""
        tasks = db.get_tasks(user.id, TaskStatus.COMPLETED)
        return len(tasks) >= 100

class GameEngine:
    """Core game mechanics implementation."""
    
    def __init__(self, db: Database):
        """Initialize game engine with database connection."""
        self.db = db
        self.achievements = [
            FirstTaskCompleted,
            SevenDayStreak,
            HundredTasksCompleted
        ]
    
    def calculate_task_xp(
        self,
        task: Task,
        completion_time: Optional[datetime.datetime] = None
    ) -> int:
        """Calculate XP for task completion or penalty for failure."""
        if task.status not in (TaskStatus.COMPLETED, TaskStatus.FAILED):
            return 0
        
        # Get base XP values
        if task.status == TaskStatus.COMPLETED:
            base_xp = config.xp_config.base_rewards[task.priority]
            if completion_time:
                # Calculate early completion bonus
                time_early = task.due_at - completion_time
                for threshold in config.xp_config.early_bonus_thresholds:
                    if "days_early" in threshold:
                        if time_early >= datetime.timedelta(days=threshold["days_early"]):
                            bonus = base_xp * (threshold["bonus_pct"] / 100)
                            base_xp += bonus
                            break
                    elif "hours_early" in threshold:
                        if time_early >= datetime.timedelta(hours=threshold["hours_early"]):
                            bonus = base_xp * (threshold["bonus_pct"] / 100)
                            base_xp += bonus
                            break
        else:  # FAILED
            base_xp = -config.xp_config.base_penalties[task.priority]
        
        return max(base_xp, config.xp_config.xp_floor)
    
    def update_user_level(self, user: User) -> None:
        """Update user level based on XP."""
        old_level = user.level
        new_level = (user.xp // config.xp_per_level) + 1
        
        if new_level != old_level:
            user.level = new_level
            self.db.update_user_xp(user.id, user.xp, user.level)
    
    def get_user_rank(self, user: User) -> str:
        """Get user's current rank based on XP."""
        current_rank = config.ranks[0].name
        for rank in config.ranks:
            if user.xp >= rank.xp_min:
                current_rank = rank.name
            else:
                break
        return current_rank
    
    def update_streak(self, user: User) -> None:
        """Update user's completion streak."""
        today = datetime.date.today()
        
        if user.last_completion_date is None:
            user.streak = 1
        elif user.last_completion_date == today:
            return  # Already updated today
        elif user.last_completion_date == today - datetime.timedelta(days=1):
            user.streak += 1
        else:
            user.streak = 1
        
        user.longest_streak = max(user.streak, user.longest_streak)
        user.last_completion_date = today
        
        self.db.update_user_streak(
            user.id,
            user.streak,
            user.longest_streak,
            user.last_completion_date
        )
    
    def check_achievements(self, user: User) -> list[Achievement]:
        """Check and return any newly completed achievements."""
        completed = []
        for achievement_class in self.achievements:
            if achievement_class.check(user, self.db):
                completed.append(achievement_class)
        return completed
    
    def complete_task(self, task: Task, completion_time: datetime.datetime) -> int:
        """Handle task completion and return XP earned."""
        if task.status != TaskStatus.COMPLETED:
            task.status = TaskStatus.COMPLETED
            task.completed_at = completion_time
            self.db.update_task_status(task.id, task.status, task.completed_at)
            
            xp_earned = self.calculate_task_xp(task, completion_time)
            user = self.db.get_user_by_id(task.user_id)
            user.xp += xp_earned
            
            self.update_user_level(user)
            self.update_streak(user)
            
            # Check for new achievements
            new_achievements = self.check_achievements(user)
            achievement_xp = sum(a.xp_reward for a in new_achievements)
            user.xp += achievement_xp
            
            self.db.update_user_xp(user.id, user.xp, user.level)
            return xp_earned + achievement_xp
        
        return 0
    
    def fail_task(self, task: Task) -> int:
        """Handle task failure and return XP penalty."""
        if task.status != TaskStatus.FAILED:
            task.status = TaskStatus.FAILED
            self.db.update_task_status(task.id, task.status)
            
            xp_penalty = self.calculate_task_xp(task)
            user = self.db.get_user_by_id(task.user_id)
            user.xp = max(0, user.xp + xp_penalty)  # Don't go below 0
            
            self.update_user_level(user)
            self.db.update_user_xp(user.id, user.xp, user.level)
            return xp_penalty
        
        return 0