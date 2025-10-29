"""GUI views for the Game of Life application."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from gamelife.core.config import TaskPriority, TaskStatus
from gamelife.core.game import GameEngine
from gamelife.data.database import Database, Task, User

class ProfileSelectView(ttk.Frame):
    """Profile selection and creation view."""
    
    def __init__(
        self,
        parent: ttk.Frame,
        db: Database,
        on_select: Callable[[User], None]
    ):
        """Initialize profile selection view."""
        super().__init__(parent)
        self.db = db
        self.on_select = on_select
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Profile creation
        create_frame = ttk.LabelFrame(self, text="Create New Profile")
        create_frame.pack(padx=10, pady=5, fill=tk.X)
        
        ttk.Label(create_frame, text="Username:").pack(side=tk.LEFT, padx=5)
        self.username_entry = ttk.Entry(create_frame)
        self.username_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            create_frame,
            text="Create Profile",
            command=self.create_profile
        ).pack(side=tk.LEFT, padx=5)
        
        # Profile selection
        select_frame = ttk.LabelFrame(self, text="Select Profile")
        select_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Profile listbox
        self.profiles_listbox = tk.Listbox(select_frame)
        self.profiles_listbox.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        ttk.Button(
            select_frame,
            text="Select Profile",
            command=self.select_profile
        ).pack(padx=5, pady=5)
        
        self.load_profiles()
    
    def load_profiles(self):
        """Load existing profiles into the listbox."""
        # TODO: Implement get_all_users in Database class
        pass
    
    def create_profile(self):
        """Create a new user profile."""
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Username cannot be empty")
            return
        
        try:
            user = self.db.create_user(username)
            self.on_select(user)
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
    
    def select_profile(self):
        """Select an existing profile."""
        selection = self.profiles_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a profile")
            return
        
        username = self.profiles_listbox.get(selection[0])
        user = self.db.get_user(username)
        if user:
            self.on_select(user)

class DashboardView(ttk.Frame):
    """Main dashboard view."""
    
    def __init__(self, parent: ttk.Frame, user: User, game: GameEngine):
        """Initialize dashboard view."""
        super().__init__(parent)
        self.user = user
        self.game = game
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI components."""
        # User stats
        stats_frame = ttk.LabelFrame(self, text="Your Stats")
        stats_frame.pack(padx=10, pady=5, fill=tk.X)
        
        rank = self.game.get_user_rank(self.user)
        
        ttk.Label(
            stats_frame,
            text=f"Level {self.user.level} {rank}"
        ).pack()
        
        ttk.Label(
            stats_frame,
            text=f"XP: {self.user.xp}"
        ).pack()
        
        ttk.Label(
            stats_frame,
            text=f"Current Streak: {self.user.streak} days"
        ).pack()
        
        ttk.Label(
            stats_frame,
            text=f"Longest Streak: {self.user.longest_streak} days"
        ).pack()
        
        # Task summary
        summary_frame = ttk.LabelFrame(self, text="Task Summary")
        summary_frame.pack(padx=10, pady=5, fill=tk.X)
        
        tasks = self.game.db.get_tasks(self.user.id)
        pending = len([t for t in tasks if t.status == TaskStatus.PENDING])
        in_progress = len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS])
        completed = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
        failed = len([t for t in tasks if t.status == TaskStatus.FAILED])
        
        ttk.Label(
            summary_frame,
            text=f"Pending: {pending}"
        ).pack()
        
        ttk.Label(
            summary_frame,
            text=f"In Progress: {in_progress}"
        ).pack()
        
        ttk.Label(
            summary_frame,
            text=f"Completed: {completed}"
        ).pack()
        
        ttk.Label(
            summary_frame,
            text=f"Failed: {failed}"
        ).pack()

class TaskListView(ttk.Frame):
    """Task list view with filtering and sorting."""
    
    def __init__(
        self,
        parent: ttk.Frame,
        user: User,
        game: GameEngine,
        on_edit: Callable[[Optional[int]], None]
    ):
        """Initialize task list view."""
        super().__init__(parent)
        self.user = user
        self.game = game
        self.on_edit = on_edit
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Controls frame
        controls = ttk.Frame(self)
        controls.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(
            controls,
            text="New Task",
            command=lambda: self.on_edit(None)
        ).pack(side=tk.LEFT, padx=5)
        
        # Filter controls
        filter_frame = ttk.LabelFrame(controls, text="Filters")
        filter_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="Status:").pack(side=tk.LEFT, padx=5)
        self.status_var = tk.StringVar(value="ALL")
        status_cb = ttk.Combobox(
            filter_frame,
            textvariable=self.status_var,
            values=["ALL"] + [s.name for s in TaskStatus],
            state="readonly"
        )
        status_cb.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="Priority:").pack(side=tk.LEFT, padx=5)
        self.priority_var = tk.StringVar(value="ALL")
        priority_cb = ttk.Combobox(
            filter_frame,
            textvariable=self.priority_var,
            values=["ALL"] + [p.name for p in TaskPriority],
            state="readonly"
        )
        priority_cb.pack(side=tk.LEFT, padx=5)
        
        # Task list
        self.tree = ttk.Treeview(
            self,
            columns=("title", "priority", "status", "due_at"),
            show="headings"
        )
        
        self.tree.heading("title", text="Title")
        self.tree.heading("priority", text="Priority")
        self.tree.heading("status", text="Status")
        self.tree.heading("due_at", text="Due Date")
        
        self.tree.column("title", width=200)
        self.tree.column("priority", width=100)
        self.tree.column("status", width=100)
        self.tree.column("due_at", width=150)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Bind events
        self.tree.bind("<Double-1>", self.on_double_click)
        self.status_var.trace("w", lambda *args: self.refresh_tasks())
        self.priority_var.trace("w", lambda *args: self.refresh_tasks())
        
        self.refresh_tasks()
    
    def refresh_tasks(self):
        """Refresh the task list with current filters."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        tasks = self.game.db.get_tasks(self.user.id)
        
        # Apply filters
        if self.status_var.get() != "ALL":
            tasks = [t for t in tasks if t.status.name == self.status_var.get()]
        
        if self.priority_var.get() != "ALL":
            tasks = [t for t in tasks if t.priority.name == self.priority_var.get()]
        
        # Sort by due date
        tasks.sort(key=lambda t: t.due_at)
        
        for task in tasks:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    task.title,
                    task.priority.name,
                    task.status.name,
                    task.due_at.strftime("%Y-%m-%d %H:%M")
                ),
                tags=(str(task.id),)
            )
    
    def on_double_click(self, event):
        """Handle double click on task."""
        item = self.tree.selection()[0]
        task_id = int(self.tree.item(item, "tags")[0])
        self.on_edit(task_id)

class TaskEditorView(ttk.Frame):
    """Task editor view."""
    
    def __init__(
        self,
        parent: ttk.Frame,
        user: User,
        game: GameEngine,
        task_id: Optional[int],
        on_save: Callable[[], None]
    ):
        """Initialize task editor view."""
        super().__init__(parent)
        self.user = user
        self.game = game
        self.task_id = task_id
        self.on_save = on_save
        self.task = None
        
        if task_id:
            self.task = self.game.db.get_task(task_id)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Title
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(title_frame, text="Title:").pack(side=tk.LEFT)
        self.title_entry = ttk.Entry(title_frame, width=50)
        self.title_entry.pack(side=tk.LEFT, padx=5)
        
        if self.task:
            self.title_entry.insert(0, self.task.title)
        
        # Description
        desc_frame = ttk.LabelFrame(self, text="Description")
        desc_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.desc_text = tk.Text(desc_frame, wrap=tk.WORD, height=5)
        self.desc_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        if self.task:
            self.desc_text.insert("1.0", self.task.description)
        
        # Task details
        details_frame = ttk.Frame(self)
        details_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Priority
        ttk.Label(details_frame, text="Priority:").pack(side=tk.LEFT)
        self.priority_var = tk.StringVar(
            value=self.task.priority.name if self.task else TaskPriority.MEDIUM.name
        )
        priority_cb = ttk.Combobox(
            details_frame,
            textvariable=self.priority_var,
            values=[p.name for p in TaskPriority],
            state="readonly" if self.task else "normal"
        )
        priority_cb.pack(side=tk.LEFT, padx=5)
        
        # Due date/time
        ttk.Label(details_frame, text="Due:").pack(side=tk.LEFT, padx=5)
        self.due_entry = ttk.Entry(details_frame)
        self.due_entry.pack(side=tk.LEFT)
        
        if self.task:
            self.due_entry.insert(0, self.task.due_at.strftime("%Y-%m-%d %H:%M"))
        
        # Category
        ttk.Label(details_frame, text="Category:").pack(side=tk.LEFT, padx=5)
        self.category_entry = ttk.Entry(details_frame)
        self.category_entry.pack(side=tk.LEFT)
        
        if self.task and self.task.category:
            self.category_entry.insert(0, self.task.category)
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        
        ttk.Button(
            btn_frame,
            text="Save",
            command=self.save_task
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.on_save
        ).pack(side=tk.LEFT, padx=5)
    
    def save_task(self):
        """Save the task."""
        try:
            title = self.title_entry.get().strip()
            if not title:
                raise ValueError("Title is required")
            
            description = self.desc_text.get("1.0", tk.END).strip()
            priority = TaskPriority[self.priority_var.get()]
            category = self.category_entry.get().strip() or None
            
            # Parse due date
            due_str = self.due_entry.get().strip()
            if not due_str:
                raise ValueError("Due date is required")
            
            due_at = datetime.datetime.strptime(due_str, "%Y-%m-%d %H:%M")
            
            if self.task:
                # Update existing task
                self.task.title = title
                self.task.description = description
                self.task.category = category
                self.task.due_at = due_at
                self.game.db.update_task(self.task)
            else:
                # Create new task
                task = Task(
                    id=None,
                    user_id=self.user.id,
                    title=title,
                    description=description,
                    priority=priority,
                    status=TaskStatus.PENDING,
                    category=category,
                    due_at=due_at
                )
                self.game.db.create_task(task)
            
            self.on_save()
            
        except (ValueError, TypeError) as e:
            messagebox.showerror("Error", str(e))

class AchievementsView(ttk.Frame):
    """Achievements view."""
    
    def __init__(self, parent: ttk.Frame, user: User, game: GameEngine):
        """Initialize achievements view."""
        super().__init__(parent)
        self.user = user
        self.game = game
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Create achievements list
        self.tree = ttk.Treeview(
            self,
            columns=("name", "description", "status", "reward"),
            show="headings"
        )
        
        self.tree.heading("name", text="Achievement")
        self.tree.heading("description", text="Description")
        self.tree.heading("status", text="Status")
        self.tree.heading("reward", text="XP Reward")
        
        self.tree.column("name", width=150)
        self.tree.column("description", width=300)
        self.tree.column("status", width=100)
        self.tree.column("reward", width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.load_achievements()
    
    def load_achievements(self):
        """Load achievements into the tree view."""
        for achievement_class in self.game.achievements:
            completed = achievement_class.check(self.user, self.game.db)
            status = "Completed" if completed else "Locked"
            
            self.tree.insert(
                "",
                tk.END,
                values=(
                    achievement_class.name,
                    achievement_class.description,
                    status,
                    f"+{achievement_class.xp_reward} XP"
                )
            )

class ReportsView(ttk.Frame):
    """Reports and statistics view."""
    
    def __init__(self, parent: ttk.Frame, user: User, game: GameEngine):
        """Initialize reports view."""
        super().__init__(parent)
        self.user = user
        self.game = game
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Create figure
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.plot_tasks_by_priority()
    
    def plot_tasks_by_priority(self):
        """Plot tasks by priority chart."""
        tasks = self.game.db.get_tasks(self.user.id)
        priority_counts = {p.name: 0 for p in TaskPriority}
        
        for task in tasks:
            priority_counts[task.priority.name] += 1
        
        ax = self.figure.add_subplot(111)
        priorities = list(priority_counts.keys())
        counts = list(priority_counts.values())
        
        ax.bar(priorities, counts)
        ax.set_title("Tasks by Priority")
        ax.set_ylabel("Number of Tasks")
        
        self.figure.tight_layout()
        self.canvas.draw()