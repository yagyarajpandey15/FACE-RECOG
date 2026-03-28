import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Toplevel
import os
import sys
import pandas as pd
from datetime import datetime
import threading
import cv2
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import custom modules
from src.enhanced_face_recognition import EnhancedFaceRecognition
from src.theme import COLORS, FONTS, apply_button_style, setup_theme

class ImprovedAdminDashboard:
    def __init__(self, root, username="Admin"):
        self.root = root
        self.username = username
        
        # Configure window
        self.root.title(f"Face Recognition Admin Dashboard - {username}")
        self.root.state('zoomed')  # Maximize window
        self.root.minsize(1000, 700)
        
        # Setup theme
        self.style = setup_theme(self.root)
        
        # Initialize status_label early to avoid errors
        # Create a temporary frame for the status label
        self.temp_status_frame = ttk.Frame(self.root)
        self.temp_status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = ttk.Label(self.temp_status_frame, text="Initializing...")
        self.status_label.pack(side=tk.LEFT)
        
        # Now initialize face recognition
        self.recognition = EnhancedFaceRecognition(status_callback=self.update_status)
        
        # Create UI components
        self.create_ui()
        
        # Remove temporary status frame
        self.temp_status_frame.destroy()
        
    def create_ui(self):
        """Create the UI components"""
        # Main container
        self.main_container = ttk.Frame(self.root, padding=20)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header frame
        self.create_header()
        
        # Content frame
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create sidebar and main content area
        self.create_sidebar()
        self.create_main_content()
        
        # Status bar
        self.create_status_bar()
        
        # Show default panel
        self.show_panel("dashboard")
        
    def create_header(self):
        """Create header with title and user info"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(
            header_frame, 
            text="Face Recognition Attendance System",
            font=FONTS["title"],
            foreground=COLORS["primary"]
        )
        title_label.pack(side=tk.LEFT)
        
        # User info
        user_frame = ttk.Frame(header_frame)
        user_frame.pack(side=tk.RIGHT)
        
        user_label = ttk.Label(
            user_frame,
            text=f"Welcome, {self.username}",
            font=FONTS["body_bold"]
        )
        user_label.pack(side=tk.LEFT, padx=10)
        
        # Logout button with blue color
        logout_btn = tk.Button(
            user_frame,
            text="Logout",
            font=FONTS["button"],
            command=self.logout,
            bg=COLORS["primary"],
            fg="white",
            padx=10,
            pady=2,
            cursor="hand2"
        )
        logout_btn.pack(side=tk.LEFT)
        
    def create_sidebar(self):
        """Create sidebar with navigation options"""
        self.sidebar = ttk.Frame(self.content_frame, width=200, style="Sidebar.TFrame")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Make sure sidebar maintains its width
        self.sidebar.pack_propagate(False)
        
        # Custom style for sidebar
        self.style.configure("Sidebar.TFrame", background=COLORS["primary"])
        
        # Navigation buttons
        nav_buttons = [
            {"text": "📊 Dashboard", "command": lambda: self.show_panel("dashboard")},
            {"text": "👥 Employee Management", "command": lambda: self.show_panel("employees")},
            {"text": "📝 Attendance", "command": lambda: self.show_panel("attendance")},
            {"text": "🔍 Take Attendance", "command": lambda: self.show_panel("recognition")},
            {"text": "⚙️ Settings", "command": lambda: self.show_panel("settings")}
        ]
        
        for i, btn_info in enumerate(nav_buttons):
            nav_btn = tk.Button(
                self.sidebar,
                text=btn_info["text"],
                command=btn_info["command"],
                font=FONTS["body_bold"],
                bg=COLORS["primary"],
                fg=COLORS["white"],
                activebackground=COLORS["primary_dark"],
                activeforeground=COLORS["white"],
                relief=tk.FLAT,
                bd=0,
                padx=10,
                pady=15,
                anchor="w",
                width=25,
                cursor="hand2"
            )
            nav_btn.pack(fill=tk.X, pady=1)
        
    def create_main_content(self):
        """Create the main content area with panels"""
        self.main_panel = ttk.Frame(self.content_frame)
        self.main_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create panels dictionary
        self.panels = {}
        
        # Dashboard panel
        self.panels["dashboard"] = self.create_dashboard_panel()
        
        # Employees panel
        self.panels["employees"] = self.create_employees_panel()
        
        # Attendance panel
        self.panels["attendance"] = self.create_attendance_panel()
        
        # Recognition panel
        self.panels["recognition"] = self.create_recognition_panel()
        
        # Settings panel
        self.panels["settings"] = self.create_settings_panel()
        
    def create_dashboard_panel(self):
        """Create dashboard panel with summary information"""
        panel = ttk.Frame(self.main_panel)
        
        # Title
        title = ttk.Label(
            panel,
            text="Dashboard",
            font=FONTS["subtitle"]
        )
        title.pack(pady=10, anchor="w")
        
        # Cards container
        cards_frame = ttk.Frame(panel)
        cards_frame.pack(fill=tk.X, pady=10)
        
        # Statistics cards
        stats = [
            {"title": "Total Employees", "value": "0", "color": "#3498db"},
            {"title": "Today's Attendance", "value": "0", "color": "#2ecc71"},
            {"title": "Overall Attendance", "value": "0", "color": "#e74c3c"}
        ]
        
        for stat in stats:
            # Card frame
            card = tk.Frame(cards_frame, bg="white", padx=15, pady=15, relief=tk.RAISED, bd=1)
            card.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)
            
            # Title
            tk.Label(
                card,
                text=stat["title"],
                font=FONTS["body"],
                bg="white",
                fg=COLORS["text_secondary"]
            ).pack(anchor="w")
            
            # Value
            tk.Label(
                card,
                text=stat["value"],
                font=("Arial", 24, "bold"),
                bg="white",
                fg=stat["color"]
            ).pack(anchor="w", pady=10)
        
        # Quick actions frame
        quick_actions = ttk.LabelFrame(panel, text="Quick Actions")
        quick_actions.pack(fill=tk.X, pady=20)
        
        # Quick action buttons
        actions = [
            {"text": "Add Employee", "command": self.add_employee},
            {"text": "Take Attendance", "command": self.take_attendance},
            {"text": "View Reports", "command": self.view_attendance}
        ]
        
        buttons_frame = ttk.Frame(quick_actions)
        buttons_frame.pack(pady=10)
        
        for action in actions:
            btn = tk.Button(
                buttons_frame,
                text=action["text"],
                command=action["command"],
                width=15,
                height=2
            )
            apply_button_style(btn, "default")
            btn.pack(side=tk.LEFT, padx=10)
        
        # Recent activity (placeholder)
        recent = ttk.LabelFrame(panel, text="Recent Activity")
        recent.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Simple activity list
        activity_list = tk.Listbox(recent, height=10)
        activity_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add some placeholder items
        activity_list.insert(tk.END, "System initialized")
        
        # Function to update dashboard
        def update_dashboard():
            try:
                # Update employee count
                if os.path.exists("data/employees.csv"):
                    df_emp = pd.read_csv("data/employees.csv")
                    emp_count = len(df_emp)
                    cards_frame.winfo_children()[0].winfo_children()[1].config(text=str(emp_count))
                
                # Update today's attendance
                if os.path.exists("data/attendance.csv"):
                    df_att = pd.read_csv("data/attendance.csv")
                    today = datetime.now().strftime('%Y-%m-%d')
                    today_count = len(df_att[df_att['Date'] == today])
                    cards_frame.winfo_children()[1].winfo_children()[1].config(text=str(today_count))
                    
                    # Overall attendance
                    cards_frame.winfo_children()[2].winfo_children()[1].config(text=str(len(df_att)))
            except Exception as e:
                self.update_status(f"Error updating dashboard: {str(e)}")
        
        # Schedule dashboard updates
        self.root.after(1000, update_dashboard)
        
        return panel
    
    def create_employees_panel(self):
        """Create employees management panel"""
        panel = ttk.Frame(self.main_panel)
        
        # Title
        title = ttk.Label(
            panel,
            text="Employee Management",
            font=FONTS["subtitle"]
        )
        title.pack(pady=10, anchor="w")
        
        # Actions frame
        actions_frame = ttk.Frame(panel)
        actions_frame.pack(fill=tk.X, pady=10)
        
        # Add employee button
        add_btn = tk.Button(
            actions_frame,
            text="➕ Add New Employee",
            command=self.add_employee
        )
        apply_button_style(add_btn)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # Remove employee button
        remove_btn = tk.Button(
            actions_frame,
            text="❌ Remove Employee",
            command=self.remove_employee
        )
        apply_button_style(remove_btn, "accent")
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        # Refresh button
        refresh_btn = tk.Button(
            actions_frame,
            text="🔄 Refresh List",
            command=lambda: self.load_employee_data()
        )
        apply_button_style(refresh_btn)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # Search frame
        search_frame = ttk.Frame(panel)
        search_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        
        self.employee_search = ttk.Entry(search_frame, width=30)
        self.employee_search.pack(side=tk.LEFT, padx=5)
        
        # Employee list frame
        list_frame = ttk.Frame(panel)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(list_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview for employee list
        columns = ("ID", "Name")
        self.employee_tree = ttk.Treeview(list_frame, columns=columns, show="headings", yscrollcommand=y_scrollbar.set)
        
        # Configure columns
        self.employee_tree.heading("ID", text="ID")
        self.employee_tree.heading("Name", text="Name")
        self.employee_tree.column("ID", width=100)
        self.employee_tree.column("Name", width=300)
        
        # Configure scrollbar
        y_scrollbar.config(command=self.employee_tree.yview)
        
        # Pack treeview
        self.employee_tree.pack(fill=tk.BOTH, expand=True)
        
        # Function to load employee data
        def load_employee_data():
            # Clear current data
            for i in self.employee_tree.get_children():
                self.employee_tree.delete(i)
            
            try:
                # Load data from CSV
                if os.path.exists("data/employees.csv"):
                    df = pd.read_csv("data/employees.csv")
                    # Ensure ID column is integer type
                    df['ID'] = df['ID'].astype(int)
                    for _, row in df.iterrows():
                        self.employee_tree.insert("", tk.END, values=(row["ID"], row["Name"]))
                    
                    self.update_status(f"Loaded {len(df)} employees")
            except Exception as e:
                self.update_status(f"Error loading employee data: {str(e)}")
        
        # Store function reference
        self.load_employee_data = load_employee_data
        
        # Load initial data
        load_employee_data()
        
        # Add search functionality
        def search_employees(*args):
            query = self.employee_search.get().lower()
            
            # Clear current data
            for i in self.employee_tree.get_children():
                self.employee_tree.delete(i)
            
            try:
                # Load and filter data
                if os.path.exists("data/employees.csv"):
                    df = pd.read_csv("data/employees.csv")
                    # Ensure ID column is integer type
                    df['ID'] = df['ID'].astype(int)
                    
                    if query:
                        # Filter by ID or name
                        df = df[df['Name'].str.lower().str.contains(query) | 
                               df['ID'].astype(str).str.contains(query)]
                    
                    # Display filtered data
                    for _, row in df.iterrows():
                        self.employee_tree.insert("", tk.END, values=(row["ID"], row["Name"]))
            except Exception as e:
                self.update_status(f"Error searching employees: {str(e)}")
        
        # Bind search entry to search function
        self.employee_search.bind("<KeyRelease>", search_employees)
        
        return panel
    
    def create_attendance_panel(self):
        """Create attendance management panel"""
        panel = ttk.Frame(self.main_panel)
        
        # Title
        title = ttk.Label(
            panel,
            text="Attendance Records",
            font=FONTS["subtitle"]
        )
        title.pack(pady=10, anchor="w")
        
        # Controls frame
        controls_frame = ttk.Frame(panel)
        controls_frame.pack(fill=tk.X, pady=10)
        
        # Date filter
        ttk.Label(controls_frame, text="Date:").pack(side=tk.LEFT, padx=5)
        
        self.date_filter = ttk.Entry(controls_frame, width=15)
        self.date_filter.pack(side=tk.LEFT, padx=5)
        self.date_filter.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        # Filter button
        filter_btn = ttk.Button(
            controls_frame,
            text="Filter",
            command=lambda: self.load_attendance_data(self.date_filter.get())
        )
        filter_btn.pack(side=tk.LEFT, padx=5)
        
        # Reset button
        reset_btn = ttk.Button(
            controls_frame,
            text="Reset",
            command=lambda: self.load_attendance_data(None)
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Export button
        export_btn = tk.Button(
            controls_frame,
            text="📊 Export CSV"
        )
        apply_button_style(export_btn)
        export_btn.pack(side=tk.RIGHT, padx=5)
        export_btn.config(command=lambda: self.recognition.export_attendance(self.root))
        
        # Attendance list frame
        list_frame = ttk.Frame(panel)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(list_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview for attendance list
        columns = ("ID", "Name", "Date", "Time")
        self.attendance_tree = ttk.Treeview(list_frame, columns=columns, show="headings", yscrollcommand=y_scrollbar.set)
        
        # Configure columns
        for col in columns:
            self.attendance_tree.heading(col, text=col)
            self.attendance_tree.column(col, width=100)
        
        # Configure scrollbar
        y_scrollbar.config(command=self.attendance_tree.yview)
        
        # Pack treeview
        self.attendance_tree.pack(fill=tk.BOTH, expand=True)
        
        # Function to load attendance data
        def load_attendance_data(date_filter=None):
            # Clear current data
            for i in self.attendance_tree.get_children():
                self.attendance_tree.delete(i)
            
            try:
                # Load data from CSV
                if os.path.exists("data/attendance.csv"):
                    df = pd.read_csv("data/attendance.csv")
                    
                    # Apply date filter if specified
                    if date_filter:
                        df = df[df['Date'] == date_filter]
                    
                    # Sort by date and time
                    df = df.sort_values(by=['Date', 'Time'], ascending=[False, False])
                    
                    # Display data
                    for _, row in df.iterrows():
                        self.attendance_tree.insert("", tk.END, values=(
                            row["ID"], row["Name"], row["Date"], row["Time"]
                        ))
                    
                    self.update_status(f"Loaded {len(df)} attendance records")
            except Exception as e:
                self.update_status(f"Error loading attendance data: {str(e)}")
        
        # Store function reference
        self.load_attendance_data = load_attendance_data
        
        # Load initial data
        load_attendance_data()
        
        return panel
    
    def create_recognition_panel(self):
        """Create face recognition panel"""
        panel = ttk.Frame(self.main_panel)
        
        # Title
        title = ttk.Label(
            panel,
            text="Face Recognition",
            font=FONTS["subtitle"]
        )
        title.pack(pady=10, anchor="w")
        
        # Instructions
        instructions = ttk.Label(
            panel,
            text="Start face recognition to automatically mark attendance for recognized employees.",
            wraplength=600
        )
        instructions.pack(pady=10, anchor="w")
        
        # Buttons frame
        buttons_frame = ttk.Frame(panel)
        buttons_frame.pack(pady=20)
        
        # Start recognition button
        start_btn = tk.Button(
            buttons_frame,
            text="📷 Start Face Recognition",
            width=25,
            height=2,
            command=self.take_attendance
        )
        apply_button_style(start_btn, "success")
        start_btn.pack(side=tk.LEFT, padx=10)
        
        # Start auto-detection button
        self.auto_detect_active = False
        self.auto_detect_btn = tk.Button(
            buttons_frame,
            text="🔄 Start Auto Detection",
            width=25,
            height=2,
            command=self.toggle_auto_detection
        )
        apply_button_style(self.auto_detect_btn, "primary")
        self.auto_detect_btn.pack(side=tk.LEFT, padx=10)
        
        # Manual attendance button
        manual_btn = tk.Button(
            buttons_frame,
            text="📝 Mark Manual Attendance",
            width=25,
            height=2,
            command=self.mark_manual_attendance
        )
        apply_button_style(manual_btn)
        manual_btn.pack(side=tk.LEFT, padx=10)
        
        # Status frame
        status_frame = ttk.LabelFrame(panel, text="Recognition Status")
        status_frame.pack(fill=tk.X, pady=20, padx=10)
        
        self.recognition_status = ttk.Label(
            status_frame,
            text="Ready to start recognition",
            wraplength=600,
            padding=10
        )
        self.recognition_status.pack(fill=tk.X)
        
        return panel
    
    def create_settings_panel(self):
        """Create settings panel"""
        panel = ttk.Frame(self.main_panel)
        
        # Title
        title = ttk.Label(
            panel,
            text="Settings",
            font=FONTS["subtitle"]
        )
        title.pack(pady=10, anchor="w")
        
        # Settings frame
        settings_frame = ttk.LabelFrame(panel, text="System Settings")
        settings_frame.pack(fill=tk.X, pady=20, padx=10)
        
        # Some settings options
        options = [
            {"text": "Retrain Recognition Model", "command": self.retrain_model},
            {"text": "Backup Data", "command": self.backup_data},
            {"text": "Restore Default Settings", "command": self.restore_defaults}
        ]
        
        for option in options:
            option_frame = ttk.Frame(settings_frame)
            option_frame.pack(fill=tk.X, pady=10, padx=10)
            
            ttk.Label(option_frame, text=option["text"]).pack(side=tk.LEFT)
            
            ttk.Button(
                option_frame,
                text="Execute",
                command=option["command"]
            ).pack(side=tk.RIGHT)
        
        # About section
        about_frame = ttk.LabelFrame(panel, text="About")
        about_frame.pack(fill=tk.X, pady=20, padx=10)
        
        about_text = ttk.Label(
            about_frame,
            text="Face Recognition Attendance System\nVersion 2.0\n\nDeveloped using OpenCV and LBPH Face Recognition",
            padding=10
        )
        about_text.pack()
        
        return panel
    
    def create_status_bar(self):
        """Create status bar at the bottom"""
        self.status_bar = ttk.Frame(self.main_container)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        
        self.status_label = ttk.Label(
            self.status_bar,
            text="Ready",
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Current time
        self.time_label = ttk.Label(
            self.status_bar,
            text=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            anchor=tk.E
        )
        self.time_label.pack(side=tk.RIGHT)
        
        # Update time every second
        def update_time():
            self.time_label.config(text=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            self.root.after(1000, update_time)
        
        # Start time updates
        update_time()
    
    def show_panel(self, panel_name):
        """Show the specified panel and hide others"""
        for name, panel in self.panels.items():
            if name == panel_name:
                panel.pack(fill=tk.BOTH, expand=True)
            else:
                panel.pack_forget()
    
    def update_status(self, message):
        """Update status bar message"""
        try:
            # Make sure status_label exists and is valid
            if hasattr(self, "status_label") and self.status_label.winfo_exists():
                self.status_label.config(text=message)
            
            # Also update recognition panel status if it exists
            if hasattr(self, "recognition_status") and self.recognition_status.winfo_exists():
                self.recognition_status.config(text=message)
        except Exception as e:
            print(f"Error updating status: {str(e)}")
    
    # Actions
    def add_employee(self):
        """Add a new employee"""
        # Ask for employee name
        name = simpledialog.askstring("Add Employee", "Enter employee name:", parent=self.root)
        if name:
            # Show progress in status bar
            self.update_status(f"Adding new employee: {name}. Please wait...")
            self.recognition.add_employee(name, self.root)
            # Refresh employee list
            if hasattr(self, "load_employee_data"):
                self.load_employee_data()
            self.update_status(f"Employee {name} added successfully!")
    
    def remove_employee(self):
        """Remove an employee"""
        self.recognition.remove_employee(self.root)
        # Refresh employee list
        if hasattr(self, "load_employee_data"):
            self.load_employee_data()
    
    def take_attendance(self):
        """Start face recognition for attendance"""
        self.update_status("Starting face recognition...")
        self.recognition.recognize_faces(self.root)
        # Refresh attendance data
        if hasattr(self, "load_attendance_data"):
            self.load_attendance_data()
    
    def view_attendance(self):
        """View attendance records"""
        self.recognition.view_attendance(self.root)
    
    def mark_manual_attendance(self):
        """Mark attendance manually"""
        # Ask for employee ID or name
        id_or_name = simpledialog.askstring("Manual Attendance", "Enter employee ID or name:", parent=self.root)
        if not id_or_name:
            return
        
        try:
            # Find employee
            if os.path.exists("data/employees.csv"):
                df = pd.read_csv("data/employees.csv")
                # Convert ID to string for comparison
                df['ID'] = df['ID'].astype(str)
                
                # Try matching ID first
                match = df[df['ID'] == id_or_name]
                
                # If no match by ID, try matching by name
                if match.empty:
                    match = df[df['Name'].str.lower() == id_or_name.lower()]
                
                if match.empty:
                    messagebox.showinfo("Not Found", f"No employee found with ID or Name: {id_or_name}")
                    return
                
                emp_id = match.iloc[0]['ID']
                emp_name = match.iloc[0]['Name']
                
                # Log attendance
                success = self.recognition.log_attendance(emp_id, emp_name)
                
                if success:
                    messagebox.showinfo("Success", f"Attendance marked for {emp_name}")
                    # Refresh attendance data
                    if hasattr(self, "load_attendance_data"):
                        self.load_attendance_data()
                
        except Exception as e:
            self.update_status(f"Error marking manual attendance: {str(e)}")
            messagebox.showerror("Error", f"Failed to mark attendance: {str(e)}")
    
    def retrain_model(self):
        """Retrain the face recognition model"""
        result = messagebox.askyesno("Confirm", "This will retrain the face recognition model. Continue?")
        if result:
            # Show progress indicator
            progress_window = Toplevel(self.root)
            progress_window.title("Training Model")
            progress_window.geometry("300x100")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            # Center window
            progress_window.update_idletasks()
            width = progress_window.winfo_width()
            height = progress_window.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            progress_window.geometry(f"{width}x{height}+{x}+{y}")
            
            # Add progress components
            label = ttk.Label(progress_window, text="Training model. Please wait...")
            label.pack(pady=10)
            
            progress = ttk.Progressbar(progress_window, mode="indeterminate", length=200)
            progress.pack(pady=10)
            progress.start()
            
            # Function to run training in thread
            def train_thread():
                success = self.recognition.train_recognizer()
                progress_window.destroy()
                
                if success:
                    messagebox.showinfo("Success", "Model trained successfully")
                else:
                    messagebox.showerror("Error", "Failed to train model. Check if you have added employees")
            
            # Start training in a separate thread
            threading.Thread(target=train_thread).start()
    
    def backup_data(self):
        """Backup system data"""
        from tkinter import filedialog
        import shutil
        
        backup_dir = filedialog.askdirectory(title="Select Backup Directory")
        if not backup_dir:
            return
            
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_folder = os.path.join(backup_dir, f"attendance_backup_{timestamp}")
            os.makedirs(backup_folder, exist_ok=True)
            
            # Backup CSVs
            if os.path.exists("data/employees.csv"):
                shutil.copy2("data/employees.csv", os.path.join(backup_folder, "employees.csv"))
                
            if os.path.exists("data/attendance.csv"):
                shutil.copy2("data/attendance.csv", os.path.join(backup_folder, "attendance.csv"))
                
            # Backup face data
            if os.path.exists("face_data"):
                shutil.copytree("face_data", os.path.join(backup_folder, "face_data"))
                
            # Backup model
            if os.path.exists("data/face_model.yml"):
                shutil.copy2("data/face_model.yml", os.path.join(backup_folder, "face_model.yml"))
                
            messagebox.showinfo("Success", f"Data backed up to {backup_folder}")
            
        except Exception as e:
            self.update_status(f"Backup error: {str(e)}")
            messagebox.showerror("Error", f"Failed to backup data: {str(e)}")
    
    def restore_defaults(self):
        """Restore default settings"""
        result = messagebox.askyesno("Confirm", "This will reset all settings to default. Continue?")
        if result:
            # Reset settings here (placeholder)
            messagebox.showinfo("Success", "Settings restored to defaults")
    
    def logout(self):
        """Log out and return to login screen"""
        result = messagebox.askyesno("Confirm Logout", "Are you sure you want to log out?")
        if result:
            self.root.destroy()
            # Start login screen
            import subprocess
            import sys
            subprocess.Popen([sys.executable, "main.py"])

    def toggle_auto_detection(self):
        """Toggle auto detection mode"""
        if self.auto_detect_active:
            # Stop auto detection
            self.auto_detect_active = False
            self.auto_detect_btn.config(text="🔄 Start Auto Detection")
            apply_button_style(self.auto_detect_btn, "primary")
            self.update_status("Auto detection stopped")
            
            # Stop the camera if it's running
            if hasattr(self, "auto_detect_thread") and self.auto_detect_thread.is_alive():
                self.stop_auto_detection = True
        else:
            # Start auto detection
            self.auto_detect_active = True
            self.auto_detect_btn.config(text="⏹️ Stop Auto Detection")
            apply_button_style(self.auto_detect_btn, "danger")
            self.update_status("Auto detection started")
            
            # Start the auto detection thread
            self.stop_auto_detection = False
            self.auto_detect_thread = threading.Thread(target=self.run_auto_detection)
            self.auto_detect_thread.daemon = True
            self.auto_detect_thread.start()

    def run_auto_detection(self):
        """Run auto detection in a separate thread"""
        self.update_status("Initializing camera for auto detection...")
        
        # Initialize camera
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            self.update_status("Error: Cannot access webcam")
            self.toggle_auto_detection()  # Turn off auto detection
            return
        
        # Set lower resolution for better performance
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Load employee data
        try:
            if os.path.exists("data/employees.csv"):
                df = pd.read_csv("data/employees.csv")
                # Ensure ID column is integer type
                df['ID'] = df['ID'].astype(int)
            else:
                self.update_status("No employee data found")
                self.toggle_auto_detection()
                return
        except Exception as e:
            self.update_status(f"Error loading employee data: {str(e)}")
            self.toggle_auto_detection()
            return
        
        # Set for tracking recognized IDs to avoid duplicate attendance in quick succession
        recognized_ids = set()
        last_recognition_time = {}  # Track time of last recognition for each ID
        last_status_update = datetime.now()  # Track time of last status update
        last_status_message = ""  # Track last status message to avoid duplicates
        
        # Frame counter for skipping frames
        frame_count = 0
        
        # Main loop
        self.update_status("Auto detection is running. Face detection active...")
        while not self.stop_auto_detection:
            ret, frame = cam.read()
            if not ret:
                self.update_status("Error reading from camera")
                break
            
            # Skip frames to improve performance
            frame_count += 1
            if frame_count % 5 != 0:  # Process every 5th frame for even better performance
                continue
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.recognition.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            current_time = datetime.now()
            
            # Process each face
            for (x, y, w, h) in faces:
                # Extract face region
                face_img = gray[y:y+h, x:x+w]
                face_img = cv2.resize(face_img, (200, 200))
                
                try:
                    # Predict label
                    label, confidence = self.recognition.recognizer.predict(face_img)
                    
                    # Check confidence threshold (lower is better with LBPH)
                    if confidence < 70:
                        # Ensure consistent ID type handling
                        label_int = int(label)
                        name_row = df[df['ID'] == label_int]
                        if not name_row.empty:
                            name = name_row.iloc[0]['Name']
                            
                            # Ensure we don't log the same person too frequently
                            if label_int in last_recognition_time:
                                time_diff = (current_time - last_recognition_time[label_int]).total_seconds()
                                if time_diff < 300:  # Only log once per 5 minutes per person
                                    continue
                        
                            # Log attendance
                            success = self.recognition.log_attendance(label_int, name)
                            if success:
                                last_recognition_time[label_int] = current_time
                                
                                # Update status message
                                status_message = f"Attendance marked for {name}"
                                
                                # Only update status if it's a new message or 5 seconds have passed
                                time_since_last_update = (current_time - last_status_update).total_seconds()
                                if status_message != last_status_message or time_since_last_update > 5:
                                    # Update status on the main thread
                                    self.root.after(0, lambda n=name: self.update_status(f"Attendance marked for {n}"))
                                    last_status_update = current_time
                                    last_status_message = status_message
                                
                                # Refresh attendance list if we're on the attendance panel
                                if hasattr(self, "load_attendance_data"):
                                    self.root.after(1000, self.load_attendance_data)
                except Exception as e:
                    error_msg = f"Recognition error: {str(e)}"
                    # Only update error message if it's new
                    if error_msg != last_status_message:
                        self.update_status(error_msg)
                        last_status_message = error_msg
                    continue
            
            # Add a small delay to reduce CPU usage
            time.sleep(0.05)
        
        # Clean up
        cam.release()
        self.update_status("Auto detection stopped")

if __name__ == "__main__":
    # If run directly, start as standalone app
    root = tk.Tk()
    app = ImprovedAdminDashboard(root)
    root.mainloop() 