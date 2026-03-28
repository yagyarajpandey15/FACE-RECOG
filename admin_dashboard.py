"""
Admin Dashboard for Face Recognition Attendance System
"""
import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import webbrowser
import subprocess

# Import the enhanced face recognition module
from src.face_recognition_module_complete import FaceRecognitionSystem

class AdminDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Dashboard - Face Recognition Attendance System")
        self.root.state('zoomed')  # Maximize window
        self.root.minsize(1000, 600)
        
        # Create face recognition system
        self.face_recognition = FaceRecognitionSystem()
        
        # Setup UI
        self.setup_ui()
        
        # Load initial data
        self.load_attendance_data()
    
    def setup_ui(self):
        """Setup the UI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(
            title_frame, 
            text="Face Recognition Attendance System - Admin Dashboard", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Attendance Records
        self.create_attendance_tab()
        
        # Tab 2: Statistics
        self.create_statistics_tab()
        
        # Tab 3: Management
        self.create_management_tab()
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(
            status_frame, 
            text=f"Ready. {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Version information
        version_label = ttk.Label(
            status_frame, 
            text="v1.0", 
            anchor=tk.E
        )
        version_label.pack(side=tk.RIGHT)
    
    def create_attendance_tab(self):
        """Create the attendance records tab"""
        attendance_tab = ttk.Frame(self.notebook)
        self.notebook.add(attendance_tab, text="Attendance Records")
        
        # Controls frame
        controls_frame = ttk.Frame(attendance_tab)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Date filter
        ttk.Label(controls_frame, text="Date:").grid(row=0, column=0, padx=5, pady=5)
        
        self.date_var = tk.StringVar()
        self.date_entry = DateEntry(
            controls_frame, 
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            textvariable=self.date_var
        )
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Filter button
        filter_btn = ttk.Button(
            controls_frame, 
            text="Filter", 
            command=self.filter_attendance
        )
        filter_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Reset button
        reset_btn = ttk.Button(
            controls_frame, 
            text="Reset", 
            command=self.load_attendance_data
        )
        reset_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Export buttons
        ttk.Button(
            controls_frame, 
            text="Export CSV", 
            command=self.export_csv
        ).grid(row=0, column=4, padx=5, pady=5)
        
        ttk.Button(
            controls_frame, 
            text="Export CSV with Images", 
            command=self.export_csv_with_images
        ).grid(row=0, column=5, padx=5, pady=5)
        
        # Search frame
        search_frame = ttk.Frame(controls_frame)
        search_frame.grid(row=0, column=6, padx=20, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.search_attendance())
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=15)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Table frame
        table_frame = ttk.Frame(attendance_tab)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create the treeview
        self.attendance_tree = ttk.Treeview(
            table_frame,
            columns=("name", "date", "time", "selfie"),
            show="headings"
        )
        
        # Add scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.attendance_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.attendance_tree.xview)
        self.attendance_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid scrollbars
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.attendance_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Set column headings
        self.attendance_tree.heading("name", text="Name")
        self.attendance_tree.heading("date", text="Date")
        self.attendance_tree.heading("time", text="Time")
        self.attendance_tree.heading("selfie", text="Selfie")
        
        # Set column widths
        self.attendance_tree.column("name", width=150)
        self.attendance_tree.column("date", width=100)
        self.attendance_tree.column("time", width=100)
        self.attendance_tree.column("selfie", width=200)
        
        # Bind double click to view selfie
        self.attendance_tree.bind("<Double-1>", self.view_selfie)
    
    def create_statistics_tab(self):
        """Create the statistics tab"""
        stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(stats_tab, text="Statistics")
        
        # Controls frame
        controls_frame = ttk.Frame(stats_tab)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Chart type selector
        ttk.Label(controls_frame, text="Chart Type:").grid(row=0, column=0, padx=5, pady=5)
        
        self.chart_type = tk.StringVar(value="daily")
        chart_combo = ttk.Combobox(
            controls_frame, 
            textvariable=self.chart_type,
            values=["daily", "weekly", "monthly", "by_name"],
            width=15,
            state="readonly"
        )
        chart_combo.grid(row=0, column=1, padx=5, pady=5)
        chart_combo.bind("<<ComboboxSelected>>", lambda e: self.update_statistics())
        
        # Date range
        ttk.Label(controls_frame, text="From:").grid(row=0, column=2, padx=5, pady=5)
        
        self.start_date_var = tk.StringVar()
        start_date_entry = DateEntry(
            controls_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            textvariable=self.start_date_var
        )
        start_date_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(controls_frame, text="To:").grid(row=0, column=4, padx=5, pady=5)
        
        self.end_date_var = tk.StringVar()
        end_date_entry = DateEntry(
            controls_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            textvariable=self.end_date_var
        )
        end_date_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Update button
        update_btn = ttk.Button(
            controls_frame, 
            text="Update Chart", 
            command=self.update_statistics
        )
        update_btn.grid(row=0, column=6, padx=5, pady=5)
        
        # Chart frame
        self.chart_frame = ttk.Frame(stats_tab)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_management_tab(self):
        """Create the management tab"""
        management_tab = ttk.Frame(self.notebook)
        self.notebook.add(management_tab, text="Management")
        
        # Left panel (registered faces)
        left_panel = ttk.Frame(management_tab)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(left_panel, text="Registered Faces", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # Frame for registered faces list
        faces_frame = ttk.Frame(left_panel)
        faces_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create listbox with scrollbar
        self.faces_listbox = tk.Listbox(faces_frame, font=("Arial", 10))
        faces_scrollbar = ttk.Scrollbar(faces_frame, orient=tk.VERTICAL, command=self.faces_listbox.yview)
        self.faces_listbox.configure(yscrollcommand=faces_scrollbar.set)
        
        faces_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.faces_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind double click to view registered face
        self.faces_listbox.bind("<Double-1>", self.view_registered_face)
        
        # Controls for registered faces
        faces_controls = ttk.Frame(left_panel)
        faces_controls.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            faces_controls,
            text="Register New Face",
            command=self.register_face
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            faces_controls,
            text="Delete Selected Face",
            command=self.delete_face
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            faces_controls,
            text="Refresh List",
            command=self.load_registered_faces
        ).pack(side=tk.RIGHT)
        
        # Right panel (actions)
        right_panel = ttk.Frame(management_tab)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(right_panel, text="Actions", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Buttons for different actions
        action_frame = ttk.Frame(right_panel)
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            action_frame,
            text="Start Face Recognition",
            command=self.start_recognition
        ).pack(fill=tk.X, pady=5)
        
        ttk.Button(
            action_frame,
            text="Backup Attendance Data",
            command=self.backup_attendance
        ).pack(fill=tk.X, pady=5)
        
        ttk.Button(
            action_frame,
            text="Teacher Mode",
            command=self.launch_teacher_mode
        ).pack(fill=tk.X, pady=5)
        
        # Load registered faces
        self.load_registered_faces()
    
    def load_attendance_data(self):
        """Load attendance data from CSV file"""
        try:
            # Get attendance data
            df = self.face_recognition.get_attendance_data()
            
            # Clear existing data
            self.attendance_tree.delete(*self.attendance_tree.get_children())
            
            # Add data to treeview
            for index, row in df.iterrows():
                selfie_path = row["SelfieImage"] if "SelfieImage" in df.columns else "No selfie"
                self.attendance_tree.insert(
                    "", 
                    tk.END, 
                    values=(row["Name"], row["Date"], row["Time"], selfie_path)
                )
            
            # Update status
            self.status_label.config(text=f"Loaded {len(df)} attendance records. {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Update statistics
            self.update_statistics()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load attendance data: {str(e)}")
    
    def filter_attendance(self):
        """Filter attendance by date"""
        try:
            date = self.date_var.get()
            
            if not date:
                self.load_attendance_data()
                return
            
            # Filter data
            df = self.face_recognition.get_attendance_data(date=date)
            
            # Clear existing data
            self.attendance_tree.delete(*self.attendance_tree.get_children())
            
            # Add filtered data to treeview
            for index, row in df.iterrows():
                selfie_path = row["SelfieImage"] if "SelfieImage" in df.columns else "No selfie"
                self.attendance_tree.insert(
                    "", 
                    tk.END, 
                    values=(row["Name"], row["Date"], row["Time"], selfie_path)
                )
            
            # Update status
            self.status_label.config(text=f"Filtered {len(df)} attendance records for {date}. {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to filter attendance data: {str(e)}")
    
    def search_attendance(self):
        """Search attendance by name"""
        try:
            search_term = self.search_var.get().lower()
            
            if not search_term:
                self.load_attendance_data()
                return
            
            # Get current items
            items = self.attendance_tree.get_children()
            
            # Check each item
            for item in items:
                values = self.attendance_tree.item(item, 'values')
                name = values[0].lower()
                
                # If found, keep item visible, otherwise hide
                if search_term in name:
                    self.attendance_tree.item(item, tags=())
                else:
                    self.attendance_tree.detach(item)
            
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")
    
    def export_csv(self):
        """Export attendance data to CSV"""
        try:
            # Ask for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension='.csv',
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Attendance Data"
            )
            
            if not file_path:
                return
            
            # Export data
            result_path = self.face_recognition.export_attendance(output_path=file_path, include_images=False)
            
            if result_path:
                messagebox.showinfo("Export Successful", f"Attendance data exported to {result_path}")
                # Open the directory containing the file
                directory = os.path.dirname(result_path)
                subprocess.Popen(f'explorer "{directory}"')
            else:
                messagebox.showerror("Export Failed", "Failed to export attendance data.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export attendance data: {str(e)}")
    
    def export_csv_with_images(self):
        """Export attendance data with images as a ZIP file"""
        try:
            # Ask for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension='.csv',
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Attendance Data with Images"
            )
            
            if not file_path:
                return
            
            # Export data with images
            result_path = self.face_recognition.export_attendance(output_path=file_path, include_images=True)
            
            if result_path:
                messagebox.showinfo("Export Successful", f"Attendance data with images exported to {result_path}")
                # Open the directory containing the file
                directory = os.path.dirname(result_path)
                subprocess.Popen(f'explorer "{directory}"')
            else:
                messagebox.showerror("Export Failed", "Failed to export attendance data with images.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export attendance data: {str(e)}")
    
    def update_statistics(self):
        """Update the statistics chart"""
        try:
            # Clear previous chart
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            
            # Get attendance data
            df = self.face_recognition.get_attendance_data()
            
            if df.empty:
                ttk.Label(self.chart_frame, text="No attendance data available for statistics").pack(pady=20)
                return
            
            # Filter by date range if provided
            start_date = self.start_date_var.get()
            end_date = self.end_date_var.get()
            
            if start_date:
                df = df[df["Date"] >= start_date]
            
            if end_date:
                df = df[df["Date"] <= end_date]
            
            # Get chart type
            chart_type = self.chart_type.get()
            
            # Create figure for plotting
            fig = plt.Figure(figsize=(8, 6), dpi=100)
            ax = fig.add_subplot(111)
            
            if chart_type == "daily":
                # Count attendance by date
                attendance_by_date = df.groupby('Date').size()
                title = "Daily Attendance"
                xlabel = "Date"
                ylabel = "Number of Attendees"
                attendance_by_date.plot(kind='bar', ax=ax)
                
            elif chart_type == "weekly":
                # Convert date to week number
                df['Week'] = pd.to_datetime(df['Date']).dt.strftime('%Y-W%U')
                attendance_by_week = df.groupby('Week').size()
                title = "Weekly Attendance"
                xlabel = "Week"
                ylabel = "Number of Attendees"
                attendance_by_week.plot(kind='bar', ax=ax)
                
            elif chart_type == "monthly":
                # Convert date to month
                df['Month'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m')
                attendance_by_month = df.groupby('Month').size()
                title = "Monthly Attendance"
                xlabel = "Month"
                ylabel = "Number of Attendees"
                attendance_by_month.plot(kind='bar', ax=ax)
                
            elif chart_type == "by_name":
                # Count attendance by name
                attendance_by_name = df.groupby('Name').size()
                title = "Attendance by Person"
                xlabel = "Name"
                ylabel = "Number of Days Present"
                attendance_by_name.plot(kind='bar', ax=ax)
            
            ax.set_title(title)
            ax.set_ylabel(ylabel)
            ax.set_xlabel(xlabel)
            
            # Rotate x-axis labels for readability
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # Adjust layout
            fig.tight_layout()
            
            # Display the chart
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update statistics: {str(e)}")
    
    def load_registered_faces(self):
        """Load list of registered faces"""
        # Clear listbox
        self.faces_listbox.delete(0, tk.END)
        
        # Get list of registered faces
        if os.path.exists(self.face_recognition.faces_dir):
            face_files = []
            
            for filename in os.listdir(self.face_recognition.faces_dir):
                if filename.endswith(('.jpg', '.jpeg', '.png')):
                    name = os.path.splitext(filename)[0]
                    face_files.append(name)
            
            # Add to listbox
            for name in sorted(face_files):
                self.faces_listbox.insert(tk.END, name)
    
    def view_selfie(self, event):
        """View the selfie associated with an attendance record"""
        # Get selected item
        selection = self.attendance_tree.selection()
        if not selection:
            return
        
        # Get selfie path
        item = self.attendance_tree.item(selection[0])
        values = item['values']
        
        if len(values) < 4:
            messagebox.showinfo("Info", "No selfie available for this record")
            return
        
        selfie_path = values[3]
        
        if selfie_path == "No_Selfie" or not selfie_path:
            messagebox.showinfo("Info", "No selfie available for this record")
            return
        
        # Construct full path
        full_path = os.path.join(self.face_recognition.data_dir, selfie_path)
        
        # Check if file exists
        if not os.path.exists(full_path):
            messagebox.showinfo("Info", f"Selfie file not found: {selfie_path}")
            return
        
        # Display the selfie using default image viewer
        try:
            if sys.platform == 'win32':
                os.startfile(full_path)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', full_path])
            else:
                subprocess.Popen(['xdg-open', full_path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open selfie: {str(e)}")
    
    def view_registered_face(self, event):
        """View a registered face"""
        # Get selected item
        selection = self.faces_listbox.curselection()
        if not selection:
            return
        
        name = self.faces_listbox.get(selection[0])
        
        # Construct full path
        face_path = os.path.join(self.face_recognition.faces_dir, f"{name}.jpg")
        
        # Check if file exists
        if not os.path.exists(face_path):
            messagebox.showinfo("Info", f"Face image not found: {name}")
            return
        
        # Display the face using default image viewer
        try:
            if sys.platform == 'win32':
                os.startfile(face_path)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', face_path])
            else:
                subprocess.Popen(['xdg-open', face_path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open face image: {str(e)}")
    
    def register_face(self):
        """Register a new face"""
        # Hide main window during registration
        self.root.withdraw()
        
        # Create temporary Tkinter root for dialog
        temp_root = tk.Tk()
        temp_root.withdraw()
        
        # Show dialog to get name
        name = simpledialog.askstring("Register New Face", "Enter name:", parent=temp_root)
        
        # Clean up temporary root
        temp_root.destroy()
        
        if name:
            success = self.face_recognition.register_new_face(name)
            if success:
                # Reload registered faces
                self.load_registered_faces()
        
        # Show main window again
        self.root.deiconify()
    
    def delete_face(self):
        """Delete a registered face"""
        # Get selected item
        selection = self.faces_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select a face to delete")
            return
        
        name = self.faces_listbox.get(selection[0])
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {name}?"):
            return
        
        # Delete face image
        face_path = os.path.join(self.face_recognition.faces_dir, f"{name}.jpg")
        
        try:
            if os.path.exists(face_path):
                os.remove(face_path)
                messagebox.showinfo("Success", f"Deleted {name}")
                
                # Reload registered faces
                self.load_registered_faces()
            else:
                messagebox.showinfo("Info", f"Face image not found: {name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete face: {str(e)}")
    
    def start_recognition(self):
        """Start face recognition"""
        # Hide main window
        self.root.withdraw()
        
        # Start recognition
        self.face_recognition.start_recognition()
        
        # Show main window again
        self.root.deiconify()
        
        # Reload attendance data
        self.load_attendance_data()
    
    def backup_attendance(self):
        """Backup attendance data"""
        try:
            # Ask for save location
            backup_dir = filedialog.askdirectory(title="Select Backup Location")
            
            if not backup_dir:
                return
            
            # Create timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create backup filenames
            attendance_backup = os.path.join(backup_dir, f"attendance_backup_{timestamp}.csv")
            
            # Copy attendance file
            shutil.copy2(self.face_recognition.attendance_file, attendance_backup)
            
            # Create a zip file of selfies
            import zipfile
            
            # Create a zip file
            selfies_zip = os.path.join(backup_dir, f"selfies_backup_{timestamp}.zip")
            
            with zipfile.ZipFile(selfies_zip, 'w') as zipf:
                # Add all selfie images
                if os.path.exists(self.face_recognition.selfies_dir):
                    for filename in os.listdir(self.face_recognition.selfies_dir):
                        filepath = os.path.join(self.face_recognition.selfies_dir, filename)
                        zipf.write(filepath, filename)
            
            messagebox.showinfo("Backup Successful", f"Attendance data and selfies backed up to {backup_dir}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {str(e)}")
    
    def launch_teacher_mode(self):
        """Launch teacher mode"""
        try:
            # Launch teacher dashboard in a new process
            subprocess.Popen([sys.executable, "teacher_dashboard.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch teacher mode: {str(e)}")

if __name__ == "__main__":
    try:
        # Import tkcalendar - show error if not installed
        from tkcalendar import DateEntry
    except ImportError:
        print("tkcalendar package is missing. Please install it with:")
        print("pip install tkcalendar")
        sys.exit(1)
    
    root = tk.Tk()
    app = AdminDashboard(root)
    root.mainloop() 