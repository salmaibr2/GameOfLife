"""Main application GUI."""
import tkinter as tk
from tkinter import ttk
from typing import Optional

try:
    import ttkbootstrap as ttk
    USING_BOOTSTRAP = True
except ImportError:
    USING_BOOTSTRAP = False

from gamelife.core.game import GameEngine
from gamelife.data.database import Database
from gamelife.gui.views import (
    AchievementsView,
    DashboardView,
    ProfileSelectView,
    ReportsView,
    TaskEditorView,
    TaskListView
)

class GameLifeApp:
    """Main application window."""
    
    def __init__(self):
        """Initialize the application."""
        if USING_BOOTSTRAP:
            self.root = ttk.Window(
                title="Game of Life - Task Manager",
                themename="superhero"
            )
        else:
            self.root = tk.Tk()
            self.root.title("Game of Life - Task Manager")
        
        self.db = Database()
        self.game = GameEngine(self.db)
        self.current_user = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the main UI components."""
        self.root.geometry("1024x768")
        
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create navigation frame
        self.nav_frame = ttk.Frame(self.main_container)
        self.nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Create content frame
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.setup_navigation()
        self.show_profile_select()
    
    def setup_navigation(self):
        """Set up navigation buttons."""
        nav_style = "primary.TButton" if USING_BOOTSTRAP else "TButton"
        
        ttk.Button(
            self.nav_frame,
            text="Dashboard",
            command=self.show_dashboard,
            style=nav_style,
            width=20
        ).pack(pady=2)
        
        ttk.Button(
            self.nav_frame,
            text="Tasks",
            command=self.show_task_list,
            style=nav_style,
            width=20
        ).pack(pady=2)
        
        ttk.Button(
            self.nav_frame,
            text="Achievements",
            command=self.show_achievements,
            style=nav_style,
            width=20
        ).pack(pady=2)
        
        ttk.Button(
            self.nav_frame,
            text="Reports",
            command=self.show_reports,
            style=nav_style,
            width=20
        ).pack(pady=2)
        
        ttk.Button(
            self.nav_frame,
            text="Switch Profile",
            command=self.show_profile_select,
            style=nav_style,
            width=20
        ).pack(pady=2)
    
    def clear_content(self):
        """Clear the content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_profile_select(self):
        """Show the profile selection view."""
        self.clear_content()
        ProfileSelectView(
            self.content_frame,
            self.db,
            self.on_profile_selected
        ).pack(fill=tk.BOTH, expand=True)
    
    def show_dashboard(self):
        """Show the dashboard view."""
        if not self.current_user:
            self.show_profile_select()
            return
        
        self.clear_content()
        DashboardView(
            self.content_frame,
            self.current_user,
            self.game
        ).pack(fill=tk.BOTH, expand=True)
    
    def show_task_list(self):
        """Show the task list view."""
        if not self.current_user:
            self.show_profile_select()
            return
        
        self.clear_content()
        TaskListView(
            self.content_frame,
            self.current_user,
            self.game,
            self.show_task_editor
        ).pack(fill=tk.BOTH, expand=True)
    
    def show_task_editor(self, task_id: Optional[int] = None):
        """Show the task editor view."""
        if not self.current_user:
            self.show_profile_select()
            return
        
        self.clear_content()
        TaskEditorView(
            self.content_frame,
            self.current_user,
            self.game,
            task_id,
            self.show_task_list
        ).pack(fill=tk.BOTH, expand=True)
    
    def show_achievements(self):
        """Show the achievements view."""
        if not self.current_user:
            self.show_profile_select()
            return
        
        self.clear_content()
        AchievementsView(
            self.content_frame,
            self.current_user,
            self.game
        ).pack(fill=tk.BOTH, expand=True)
    
    def show_reports(self):
        """Show the reports view."""
        if not self.current_user:
            self.show_profile_select()
            return
        
        self.clear_content()
        ReportsView(
            self.content_frame,
            self.current_user,
            self.game
        ).pack(fill=tk.BOTH, expand=True)
    
    def on_profile_selected(self, user):
        """Handle profile selection."""
        self.current_user = user
        self.show_dashboard()
    
    def run(self):
        """Start the application main loop."""
        self.root.mainloop()