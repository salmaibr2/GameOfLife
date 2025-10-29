"""Configuration management for Game of Life."""
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional

import platformdirs

class TaskPriority(Enum):
    """Task priority levels."""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()

class TaskStatus(Enum):
    """Task status states."""
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    OVERDUE = auto()
    FAILED = auto()

@dataclass
class XPConfig:
    """Experience points configuration."""
    base_rewards: Dict[TaskPriority, int] = None
    base_penalties: Dict[TaskPriority, int] = None
    early_bonus_thresholds: List[Dict[str, int]] = None
    xp_floor: int = 0

    def __post_init__(self):
        if self.base_rewards is None:
            self.base_rewards = {
                TaskPriority.LOW: 10,
                TaskPriority.MEDIUM: 25,
                TaskPriority.HIGH: 50,
                TaskPriority.CRITICAL: 100
            }
        if self.base_penalties is None:
            self.base_penalties = {
                TaskPriority.LOW: 15,
                TaskPriority.MEDIUM: 38,
                TaskPriority.HIGH: 75,
                TaskPriority.CRITICAL: 150
            }
        if self.early_bonus_thresholds is None:
            self.early_bonus_thresholds = [
                {"days_early": 7, "bonus_pct": 50},
                {"days_early": 3, "bonus_pct": 25},
                {"hours_early": 24, "bonus_pct": 10}
            ]

@dataclass
class RankConfig:
    """Rank configuration."""
    name: str
    xp_min: int

@dataclass
class Config:
    """Main application configuration."""
    xp_per_level: int = 100
    ranks: List[RankConfig] = None
    xp_config: XPConfig = None
    db_path: Optional[Path] = None

    def __post_init__(self):
        if self.ranks is None:
            self.ranks = [
                RankConfig("Procrastinator", 0),
                RankConfig("Dabbler", 100),
                RankConfig("Doer", 300),
                RankConfig("Achiever", 600),
                RankConfig("Champion", 1000),
                RankConfig("Master", 1500),
                RankConfig("Legend", 2500)
            ]
        if self.xp_config is None:
            self.xp_config = XPConfig()
        if self.db_path is None:
            data_dir = Path(platformdirs.user_data_dir("GameOfLife"))
            data_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = data_dir / "gamelife.db"

# Global configuration instance
config = Config()