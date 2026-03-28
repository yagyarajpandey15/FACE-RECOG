"""
Run Face Recognition with Dialog Interface
"""
import sys
import os

if __name__ == "__main__":
    # Add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Create directories if they don't exist
    if not os.path.exists("faces"):
        os.makedirs("faces")
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Import and run admin dashboard with dialog-based face recognition
    import tkinter as tk
    from tkinter import messagebox
    
    try:
        # Import dialog-based face recognition module
        from src.face_recognition_module_dialog import FaceRecognitionSystem
        
        class AdminDashboardDialog:
            def __init__(self, root):
                self.root = root
                self.root.title("Face Recognition Attendance System")
                self.root.geometry("300x200")
                self.root.configure(bg="#f0f0f0")
                
                # Center window on screen
                screen_width = root.winfo_screenwidth()
                screen_height = root.winfo_screenheight()
                x = (screen_width / 2) - (300 / 2)
                y = (screen_height / 2) - (200 / 2)
                self.root.geometry(f"300x200+{int(x)}+{int(y)}")
                
                # Create face recognition system
                self.face_recognition = FaceRecognitionSystem()
                
                # Create UI
                self.create_ui()
            
            def create_ui(self):
                """Create the user interface"""
                # Header
                header = tk.Label(
                    self.root, 
                    text="Face Recognition\nAttendance System", 
                    font=("Arial", 14, "bold"),
                    bg="#f0f0f0"
                )
                header.pack(pady=20)
                
                # Face recognition button
                recognition_btn = tk.Button(
                    self.root, 
                    text="Start Face Recognition",
                    command=self.start_recognition,
                    bg="#4CAF50", 
                    fg="white",
                    font=("Arial", 12),
                    width=20
                )
                recognition_btn.pack(pady=10)
                
                # View attendance button
                attendance_btn = tk.Button(
                    self.root, 
                    text="View Attendance Data",
                    command=self.view_attendance,
                    font=("Arial", 12),
                    width=20
                )
                attendance_btn.pack(pady=5)
            
            def start_recognition(self):
                """Start face recognition in a new thread"""
                # Hide main window during recognition
                self.root.withdraw()
                
                # Start recognition (this will block until closed)
                self.face_recognition.start_recognition()
                
                # Show main window again
                self.root.deiconify()
            
            def view_attendance(self):
                """Display attendance data in a new window"""
                # Get attendance data
                df = self.face_recognition.get_attendance_data()
                
                if df.empty:
                    messagebox.showinfo("No Data", "No attendance data available")
                    return
                
                # Create new window
                attendance_window = tk.Toplevel(self.root)
                attendance_window.title("Attendance Data")
                attendance_window.geometry("500x400")
                
                # Create a table-like display
                cols = list(df.columns)
                
                # Create listbox with columns
                listbox = tk.Listbox(attendance_window, width=70, height=20, font=("Courier New", 10))
                listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                # Add column headers
                header = f"{cols[0]:<20} {cols[1]:<12} {cols[2]:<10}"
                listbox.insert(tk.END, header)
                listbox.insert(tk.END, "-" * 50)
                
                # Add data rows
                for _, row in df.iterrows():
                    item = f"{row[cols[0]]:<20} {row[cols[1]]:<12} {row[cols[2]]:<10}"
                    listbox.insert(tk.END, item)
        
        # Start the application
        root = tk.Tk()
        app = AdminDashboardDialog(root)
        root.mainloop()
    
    except Exception as e:
        print(f"Error: {str(e)}")
        messagebox.showerror("Error", f"An error occurred: {str(e)}") 