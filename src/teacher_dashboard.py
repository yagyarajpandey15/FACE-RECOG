import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import pandas as pd
from datetime import datetime
import threading

# Add parent directory to path so we can import the face recognition module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Use the simplified face recognition module instead
from src.face_recognition_module_simple import FaceRecognitionSystem

class TeacherDashboard:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.face_recognition = FaceRecognitionSystem()
        self.recognition_running = False
        self.recognition_thread = None
        
        # Configure root window
        self.root.title(f"Teacher Dashboard - {username}")
        self.root.geometry("900x500")
        self.root.minsize(700, 400)
        self.root.configure(bg="#f5f5f5")
        
        # Create menu
        self.create_menu()
        
        # Create main frame
        self.main_frame = tk.Frame(root, bg="#f5f5f5")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create header
        self.header_label = tk.Label(
            self.main_frame, 
            text=f"Welcome, {username}!", 
            font=("Arial", 18, "bold"),
            bg="#f5f5f5"
        )
        self.header_label.pack(pady=10, anchor="w")
        
        # Create dashboard content
        self.create_dashboard_content()
        
        # Load initial data
        self.load_attendance_data()
    
    def create_menu(self):
        """Create the menu bar"""
        menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Refresh Data", command=self.load_attendance_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Recognition menu
        recognition_menu = tk.Menu(menu_bar, tearoff=0)
        recognition_menu.add_command(label="Start Face Recognition", command=self.start_recognition)
        menu_bar.add_cascade(label="Recognition", menu=recognition_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def create_dashboard_content(self):
        """Create the dashboard content"""
        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Tab 1: Attendance Records
        self.attendance_tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.attendance_tab, text="Attendance Records")
        
        # Controls frame
        controls_frame = tk.Frame(self.attendance_tab, bg="white")
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Date filter
        tk.Label(controls_frame, text="Filter by date:", bg="white").pack(side=tk.LEFT, padx=(0, 10))
        
        # Date entry
        self.date_entry = tk.Entry(controls_frame, width=12)
        self.date_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Filter button
        filter_btn = tk.Button(controls_frame, text="Filter", command=self.filter_attendance)
        filter_btn.pack(side=tk.LEFT, padx=5)
        
        # Reset button
        reset_btn = tk.Button(controls_frame, text="Reset", command=self.load_attendance_data)
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Export button
        export_btn = tk.Button(controls_frame, text="Export CSV", command=self.export_attendance)
        export_btn.pack(side=tk.RIGHT)
        
        # Treeview for attendance data
        self.tree_frame = tk.Frame(self.attendance_tab)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(self.tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview
        self.attendance_tree = ttk.Treeview(
            self.tree_frame, 
            columns=("name", "date", "time"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        
        # Configure scrollbar
        scrollbar.config(command=self.attendance_tree.yview)
        
        # Set column headings
        self.attendance_tree.heading("name", text="Name")
        self.attendance_tree.heading("date", text="Date")
        self.attendance_tree.heading("time", text="Time")
        
        # Set column widths
        self.attendance_tree.column("name", width=150)
        self.attendance_tree.column("date", width=100)
        self.attendance_tree.column("time", width=100)
        
        self.attendance_tree.pack(fill=tk.BOTH, expand=True)
        
        # Tab 2: Take Attendance
        self.take_attendance_tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.take_attendance_tab, text="Take Attendance")
        
        # Take attendance content
        take_attendance_frame = tk.Frame(self.take_attendance_tab, bg="white")
        take_attendance_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Instruction label
        instruction_label = tk.Label(
            take_attendance_frame, 
            text="Click the button below to start face recognition and take attendance.",
            font=("Arial", 12),
            bg="white",
            wraplength=500
        )
        instruction_label.pack(pady=20)
        
        # Start recognition button
        start_btn = tk.Button(
            take_attendance_frame, 
            text="Start Face Recognition", 
            command=self.start_recognition,
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            padx=10,
            pady=5
        )
        start_btn.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(
            take_attendance_frame, 
            text="", 
            font=("Arial", 10),
            bg="white",
            fg="#666666"
        )
        self.status_label.pack(pady=10)
    
    def load_attendance_data(self):
        """Load attendance data from CSV file"""
        try:
            df = self.face_recognition.get_attendance_data()
            
            # Clear existing data
            self.attendance_tree.delete(*self.attendance_tree.get_children())
            
            # Add data to treeview
            for index, row in df.iterrows():
                self.attendance_tree.insert("", tk.END, values=(row["Name"], row["Date"], row["Time"]))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load attendance data: {str(e)}")
    
    def filter_attendance(self):
        """Filter attendance data by date"""
        date = self.date_entry.get()
        if not date:
            messagebox.showerror("Error", "Please enter a date in YYYY-MM-DD format")
            return
        
        try:
            df = self.face_recognition.get_attendance_data(date)
            
            # Clear existing data
            self.attendance_tree.delete(*self.attendance_tree.get_children())
            
            # Add filtered data to treeview
            for index, row in df.iterrows():
                self.attendance_tree.insert("", tk.END, values=(row["Name"], row["Date"], row["Time"]))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to filter attendance data: {str(e)}")
    
    def export_attendance(self):
        """Export attendance data to CSV file"""
        try:
            filename = f"attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df = self.face_recognition.get_attendance_data()
            df.to_csv(filename, index=False)
            messagebox.showinfo("Export Successful", f"Attendance data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
    
    def start_recognition(self):
        """Start face recognition process"""
        if self.recognition_running:
            messagebox.showinfo("Info", "Face recognition is already running")
            return
        
        self.recognition_running = True
        self.status_label.config(text="Face recognition is running. Press 'q' in the video window to stop.")
        self.recognition_thread = threading.Thread(target=self.run_recognition, daemon=True)
        self.recognition_thread.start()
    
    def run_recognition(self):
        """Run face recognition in a separate thread"""
        try:
            self.face_recognition.start_recognition()
        finally:
            self.recognition_running = False
            # Update status label using the event loop
            self.root.after(0, lambda: self.status_label.config(text="Face recognition stopped"))
    
    def show_about(self):
        """Show about information"""
        messagebox.showinfo(
            "About Face Recognition Attendance System",
            "Face Recognition Attendance System\n\n"
            "This system uses facial recognition technology to automate attendance tracking.\n\n"
            "Features:\n"
            "- Automated attendance marking\n"
            "- View attendance records\n\n"
            "Version: 1.0"
        )

if __name__ == "__main__":
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = "Teacher"
    
    root = tk.Tk()
    app = TeacherDashboard(root, username)
    root.mainloop() 