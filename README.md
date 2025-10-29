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



** DETAILED BREAKDOWN **
Game of Life — Gamified Task Manager (Design Spec, no code)
Target environment

Python: 3.12 (Apple Silicon primary; partner must run on standard 3.10–3.12 on macOS/Windows).

Virtual env: built-in venv.

GUI toolkit: Tkinter (tkinter + ttk), optional theming via ttkbootstrap if allowed.

Database: SQLite (file-based), via sqlite3 in stdlib.

Packaging/distribution: zip or editable install from repo; run as python -m gamelife from venv.

Core features mapped to rubric

Multiple profiles: local list of users stored in DB. No external auth.

CRUD tasks: add, edit (due date only), delete (soft archive), with deadlines, single category, description, priority, status.

Categorization: single category per task from a maintained list.

Visual report: Tasks-by-priority chart (matplotlib) view + save image.

To-do view: sortable/filterable list with text search.

Data storage: SQLite DB file persisted next to app data directory.

GUI: Tkinter-based, event-driven, responsive enough for class demos.

OOP: classes for Task, Player, Achievement hierarchy, TaskManager (controller), repositories; Strategy pattern for rewards/penalties; polymorphic achievements; encapsulation of XP updates.

File I/O: DB read/write; export reports as PNG; optional CSV export.

Error handling + logging: user-friendly dialogs; rotating file logs at INFO.

Game rules and constraints (final decisions)

Priorities and base XP:

Low: +10 / −15

Medium: +25 / −38

High: +50 / −75

Critical: +100 / −150

Early completion bonus (Option B, hard-coded thresholds; non-stacking, pick highest applicable):

≥ 7 days early: +50% of base reward

≥ 3 days early: +25%

≥ 24 hours early: +10%

Otherwise: 0%

Evaluated against the task’s current due date at time of completion. Changing due date does not change base reward/penalty amounts because those are strictly priority-based.

Status transitions:

PENDING → IN_PROGRESS (user action)

PENDING/IN_PROGRESS → OVERDUE at due timestamp

OVERDUE → FAILED exactly 24 hours after due timestamp if not completed; apply penalty once at transition to FAILED.

Completion and penalties:

Completing a task awards base XP by priority plus early bonus.

Failing a task applies penalty once.

XP floor: 0. No negative XP.

Streaks:

A “day” is calendar day on the user’s system timezone. A single completed task on a day counts for that day’s streak.

Current streak, longest streak, total completion days tracked.

Rank/levels:

Levels: 100 XP per level, unlimited.

Ranks by total XP: Procrastinator (0), Dabbler (100), Doer (300), Achiever (600), Champion (1000), Master (1500), Legend (2500).

Screen time rewards: omitted entirely for this version.

Edit constraints:

Priority is immutable after creation.

Due date/time can be edited; base XP rewards/penalties do not change due to due-date edits.

Delete behavior:

“Delete” is soft-archive: tasks move to Archive and are excluded from active lists by default but remain in history. Archived tasks don’t affect streaks moving forward; historic stats remain intact.

Data model (conceptual)

users

id (PK), display_name (unique), created_at

xp_total (int, ≥0), level (derived or cached), rank (derived or cached)

Streaks: streak_current, streak_longest, last_completion_date (date)

categories

id (PK), name (unique), color_hex (optional)

tasks

id (PK), user_id (FK), title, description, priority (enum: LOW/MEDIUM/HIGH/CRITICAL)

category_id (FK, nullable for “Uncategorized” default)

status (enum: PENDING/IN_PROGRESS/COMPLETED/OVERDUE/FAILED/ARCHIVED)

due_at (UTC), created_at (UTC), started_at (UTC, nullable), completed_at (UTC, nullable), failed_at (UTC, nullable), archived_at (UTC, nullable)

reward_base (int) frozen at creation from priority table

penalty_base (int) frozen at creation from priority table

reward_awarded (int, nullable) final XP granted

penalty_applied (int, nullable) final XP penalized

achievements

Catalog: id (PK), code (unique), name, description, is_active

user_achievements

user_id, achievement_id, unlocked_at

completions_by_day

user_id, date (YYYY-MM-DD), count (for streak logic and charts)

meta

schema_version for migrations

Notes:

All timestamps stored as UTC; GUI shows local time.

Enums enforced at application layer; DB stores canonical strings.

OOP design

Priority enum; TaskStatus enum; Rank enum.

Task entity: encapsulates allowed transitions and guards:

Can’t change priority after creation.

Status transition methods raise validation errors if invalid.

Player entity:

Holds XP, level, rank, streak logic.

Methods: add_xp(amount), apply_penalty(amount), register_completion(date).

Enforces XP floor at 0.

RewardStrategy (interface) and concrete strategies:

PriorityBaseReward: returns base reward for a given priority (already frozen per task on creation).

EarlyBonusStrategy: computes 0/10/25/50% bonus based on time delta before due_at.

PenaltyStrategy: returns base penalty for priority (frozen per task on creation).

Achievement abstract base with evaluate(event, state)->Optional[Unlock]:

Examples:

FirstTaskCompleted

SevenDayStreak

HundredTasksCompleted

Achievements subscribe to domain events (task completed, streak updated, total tasks changed).

TaskManager (application service/controller):

Orchestrates task lifecycle, XP updates, streak updates, achievements.

Performs status sweeps to flip OVERDUE/FAILED based on time.

Exposes query methods with sorting/filtering.

Repositories (encapsulation over SQLite):

UserRepository, TaskRepository, AchievementRepository.

No heavy ORM; simple parameterized SQL behind clean methods.

Composition:

TaskManager composes repositories and strategies.

Polymorphism:

Achievement subclasses; possibly pluggable strategy instances if we extend later.

Algorithms and rules
Early bonus calculation

Input: now, task.due_at, task.reward_base.

Compute delta = due_at - completed_at.

If delta >= 7 days: bonus = ceil(0.5 * reward_base)

Else if delta >= 3 days: bonus = ceil(0.25 * reward_base)

Else if delta >= 24 hours: bonus = ceil(0.10 * reward_base)

Else: 0

Total reward = reward_base + bonus. Record in reward_awarded.

Overdue to failed sweep

Triggered:

On app start.

Periodic timer via Tkinter after() every 60 seconds.

On task list refresh, run a lightweight check for visible tasks.

Logic:

If now >= due_at and status in {PENDING, IN_PROGRESS}: set status OVERDUE.

If status OVERDUE and now >= due_at + 24h: set status FAILED once, set failed_at, apply penalty penalty_base, record penalty_applied.

Streak updates

On completion:

Normalize to local date d.

If d == last_completion_date: don’t increment current streak twice.

Else if d == last_completion_date + 1 day: streak_current += 1.

Else: streak_current = 1.

Update streak_longest = max(...).

Upsert completions_by_day (user_id, d, +1).

Update last_completion_date = d.

GUI design (Tkinter)

Windows/views:

Profile Select: list of users; add/edit user.

Dashboard: KPIs (XP, level, rank, current/longest streak), quick actions.

Task List:

Treeview with columns: Title, Priority, Category, Due, Status.

Sorting by clicking headers (due date, priority, category, status).

Filters pane: text search, priority multi-select, category dropdown, status multi-select, date range, show/hide archived.

Toolbar: Add, Edit, Start, Complete, Archive, Restore, Refresh.

Task Editor:

Title, description, category dropdown, priority selector (disabled on edit), due date/time pickers.

Achievements tab:

Grid/list of achievements, locked vs unlocked, unlock date.

Reports tab:

“Tasks by Priority” bar chart rendered with matplotlib (embed canvas), Save as PNG.

UX niceties:

Status bar for feedback.

Dialogs for confirmations (archive, restore).

Non-blocking periodic sweep using after().

Optional ttkbootstrap theme if permitted.

Sorting/filtering definitions

Sort keys: due_at asc/desc, priority desc, category asc, status, title.

Filters:

Text search on title/description.

Priority in {L, M, H, C}.

Status in selectable set; default excludes ARCHIVED.

Category equals selected id.

Due date range [start, end].

Show Archived toggle.

Validation rules

Title required, 1–120 chars.

Description optional, ≤ 2000 chars.

Due date/time required, must be in future at creation.

Priority required; immutable after creation.

Category optional; default to “Uncategorized.”

Logging and errors

Rotating logs at INFO:

Handler: max 1 MB, backupCount 5.

Location via platformdirs.user_log_dir("GameOfLife").

Log key events: profile load, CRUD, status sweeps, XP changes, streak updates, achievement unlocks, DB errors.

Error surfaces to user via messageboxes with human text; details in logs.

Persistence and paths

DB file at platformdirs.user_data_dir("GameOfLife")/gamelife.db.

Reports saved under user_documents_dir/GameOfLife/Reports with timestamped filenames.

Schema versioning: meta(schema_version) so we can run migrations later.

Packaging and repo hygiene

Repository layout:
