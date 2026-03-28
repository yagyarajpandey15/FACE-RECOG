import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

# Add parent directory to path so we can import the face recognition module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Use the simplified face recognition module instead
from src.face_recognition_module_simple import FaceRecognitionSystem

class AdminDashboard:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.face_recognition = FaceRecognitionSystem()
        self.recognition_running = False
        self.recognition_thread = None
        
        # Configure root window
        self.root.title(f"Admin Dashboard - {username}")
        self.root.geometry("1000x600")
        self.root.minsize(800, 500)
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
            font=("Arial", 20, "bold"),
            bg="#f5f5f5"
        )
        self.header_label.pack(pady=10, anchor="w")
        
        # Create dashboard sections
        self.create_dashboard_sections()
        
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
        recognition_menu.add_command(label="Register New Face", command=self.register_new_face)
        menu_bar.add_cascade(label="Recognition", menu=recognition_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def create_dashboard_sections(self):
        """Create the dashboard sections"""
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
        
        # Tab 2: Statistics
        self.stats_tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.stats_tab, text="Statistics")
        
        # Frame for the chart
        self.chart_frame = tk.Frame(self.stats_tab, bg="white")
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 3: Registered Faces
        self.faces_tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.faces_tab, text="Registered Faces")
        
        # Controls for faces tab
        faces_controls = tk.Frame(self.faces_tab, bg="white")
        faces_controls.pack(fill=tk.X, padx=10, pady=10)
        
        # Button to register new face
        register_btn = tk.Button(faces_controls, text="Register New Face", command=self.register_new_face)
        register_btn.pack(side=tk.LEFT)
        
        # Button to refresh faces list
        refresh_faces_btn = tk.Button(faces_controls, text="Refresh List", command=self.load_faces)
        refresh_faces_btn.pack(side=tk.LEFT, padx=10)
        
        # List of registered faces
        self.faces_listbox = tk.Listbox(self.faces_tab, bg="white", height=15)
        self.faces_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load registered faces
        self.load_faces()
    
    def load_attendance_data(self):
        """Load attendance data from CSV file"""
        try:
            df = self.face_recognition.get_attendance_data()
            
            # Clear existing data
            self.attendance_tree.delete(*self.attendance_tree.get_children())
            
            # Add data to treeview
            for index, row in df.iterrows():
                self.attendance_tree.insert("", tk.END, values=(row["Name"], row["Date"], row["Time"]))
            
            # Update statistics
            self.update_statistics(df)
            
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
            
            # Update statistics for filtered data
            self.update_statistics(df)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to filter attendance data: {str(e)}")
    
    def update_statistics(self, df):
        """Update the statistics tab with charts"""
        # Clear previous chart if exists
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        if len(df) == 0:
            tk.Label(self.chart_frame, text="No attendance data available", bg="white").pack(pady=20)
            return
        
        # Create figure for plotting
        fig = plt.Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        # Count attendance by date
        attendance_by_date = df.groupby('Date').size()
        
        # Plot the data
        attendance_by_date.plot(kind='bar', ax=ax)
        
        ax.set_title('Attendance by Date')
        ax.set_ylabel('Number of Attendees')
        ax.set_xlabel('Date')
        
        # Create a canvas to display the chart
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def export_attendance(self):
        """Export attendance data to CSV file"""
        try:
            filename = f"attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df = self.face_recognition.get_attendance_data()
            df.to_csv(filename, index=False)
            messagebox.showinfo("Export Successful", f"Attendance data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
    
    def load_faces(self):
        """Load list of registered faces"""
        # Clear listbox
        self.faces_listbox.delete(0, tk.END)
        
        # Check if faces directory exists
        if not os.path.exists('faces'):
            os.makedirs('faces')
            return
        
        # List all files in faces directory
        for filename in os.listdir('faces'):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                name = os.path.splitext(filename)[0]
                self.faces_listbox.insert(tk.END, name)
    
    def register_new_face(self):
        """Open dialog to register a new face"""
        name = simpledialog.askstring("Register New Face", "Enter name:")
        if name:
            # Run face registration in a separate thread
            threading.Thread(target=self.run_face_registration, args=(name,), daemon=True).start()
    
    def run_face_registration(self, name):
        """Run face registration process"""
        self.face_recognition.register_new_face(name)
        # Reload faces list
        self.root.after(0, self.load_faces)
    
    def start_recognition(self):
        """Start face recognition process"""
        if self.recognition_running:
            messagebox.showinfo("Info", "Face recognition is already running")
            return
        
        self.recognition_running = True
        self.recognition_thread = threading.Thread(target=self.run_recognition, daemon=True)
        self.recognition_thread.start()
        messagebox.showinfo("Info", "Face recognition started. Press 'q' in the video window to stop.")
    
    def run_recognition(self):
        """Run face recognition in a separate thread"""
        try:
            self.face_recognition.start_recognition()
        finally:
            self.recognition_running = False
    
    def show_about(self):
        """Show about information"""
        messagebox.showinfo(
            "About Face Recognition Attendance System",
            "Face Recognition Attendance System\n\n"
            "This system uses facial recognition technology to automate attendance tracking.\n\n"
            "Features:\n"
            "- Automated attendance marking\n"
            "- Face registration\n"
            "- Attendance reports\n\n"
            "Version: 1.0"
        )

if __name__ == "__main__":
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = "Admin"
    
    root = tk.Tk()
    app = AdminDashboard(root, username)
    root.mainloop() 