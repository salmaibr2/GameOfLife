# GameOfLife
Gamifying task management! Project for CS122

Game of Life is a gamified task management application that transforms boring chores into exciting quests. Complete tasks to earn XP, level up, unlock achievements, and earn screen time rewards. Miss deadlines? Face XP penalties. It's time to make productivity fun!
🌟 Features
Core Gameplay

XP System: Earn experience points for completing tasks, lose XP for missing deadlines
Level Progression: Gain levels as you accumulate XP (100 XP per level)
Rank Titles: Progress from "Procrastinator" to "Legend" based on total XP
Screen Time Rewards: Earn guilt-free screen time minutes for leveling up (30 min per level)

Task Management

Priority Levels: Low, Medium, High, Critical (higher priority = more XP + bigger penalties)
Due Dates: Set deadlines and earn bonus XP for early completion
Auto-Fail: Overdue tasks automatically fail and apply XP penalties
Task Tracking: View active tasks, completed tasks, and task history

Progression System

Achievements: Unlock special achievements for milestones (First task, 7-day streak, 100 tasks, etc.)
Streaks: Build daily completion streaks for motivation
Statistics: Track completion rate, longest streak, and total tasks completed

🎯 XP Rewards & Penalties
PriorityXP RewardXP PenaltyUse CaseLow+10 XP-15 XPQuick tasks, remindersMedium+25 XP-38 XPStandard daily tasksHigh+50 XP-75 XPImportant assignmentsCritical+100 XP-150 XPMajor deadlines, exams
Bonus XP: Complete tasks early to earn up to 50% bonus XP!
📊 Rank System
RankXP RequiredBenefitsProcrastinator0 XPStarting rankDabbler100 XP+30 min screen timeDoer300 XP+90 min screen timeAchiever600 XP+180 min screen timeChampion1,000 XP+300 min screen timeMaster1,500 XP+450 min screen timeLegend2,500 XP+750 min screen time
🏗️ Class Structure
Core Classes

Task: Represents individual tasks with XP values, due dates, and priority levels
Player: Manages user profile, XP, level, rank, screen time, and statistics
Achievement: Defines unlockable achievements with requirements and bonuses
TaskManager: Main controller that handles all game logic, task operations, and player progression

Enums

Priority: Task priority levels (LOW, MEDIUM, HIGH, CRITICAL)
TaskStatus: Task states (PENDING, IN_PROGRESS, COMPLETED, OVERDUE, FAILED)
Rank: Player rank progression system

