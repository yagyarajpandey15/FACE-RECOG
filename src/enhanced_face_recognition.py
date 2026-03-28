import cv2
import os
import numpy as np
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Toplevel
import shutil
from PIL import Image, ImageTk
import threading
import time

class EnhancedFaceRecognition:
    def __init__(self, status_callback=None):
        # Define file paths
        self.face_data_dir = 'face_data'
        self.employee_csv = 'data/employees.csv'
        self.attendance_csv = 'data/attendance.csv'
        
        # Create necessary directories
        self.setup_directories()
        
        # Initialize face cascade classifier
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Initialize face recognizer
        try:
            self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        except AttributeError:
            from cv2 import face
            self.recognizer = face.LBPHFaceRecognizer_create()
            
        # Status callback for UI updates
        self.status_callback = status_callback
        
        # Load trained model if exists
        self.model_file = os.path.join('data', 'face_model.yml')
        if os.path.exists(self.model_file):
            try:
                self.recognizer.read(self.model_file)
                self.log("Face recognition model loaded")
            except Exception as e:
                self.log(f"Error loading model: {str(e)}")
                
    def setup_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs('data', exist_ok=True)
        os.makedirs(self.face_data_dir, exist_ok=True)
        
        # Initialize employee CSV if it doesn't exist
        if not os.path.exists(self.employee_csv):
            pd.DataFrame(columns=['ID', 'Name']).to_csv(self.employee_csv, index=False)
            
        # Initialize attendance CSV if it doesn't exist
        if not os.path.exists(self.attendance_csv):
            pd.DataFrame(columns=['ID', 'Name', 'Date', 'Time']).to_csv(self.attendance_csv, index=False)
    
    def log(self, message):
        """Log a message and call the status callback if available"""
        print(message)  # Also print for debugging
        if self.status_callback:
            self.status_callback(message)
    
    def add_employee(self, name, parent_window=None):
        """Add a new employee with face images"""
        if not name or name.strip() == "":
            messagebox.showerror("Error", "Please enter a name")
            return False
            
        # Create capture window
        capture_window = Toplevel(parent_window) if parent_window else tk.Tk()
        capture_window.title("Capture Employee Face")
        capture_window.geometry("800x600")
        
        # Main frame
        main_frame = tk.Frame(capture_window)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Video frame
        video_frame = tk.Label(main_frame)
        video_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status frame
        status_frame = tk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        # Status label
        status_label = tk.Label(status_frame, text="Capturing face images... Look at the camera")
        status_label.pack(fill=tk.X)
        
        # Counter label
        counter_label = tk.Label(status_frame, text="Images: 0/20")
        counter_label.pack(fill=tk.X)
        
        # Add auto-capture toggle
        auto_capture_var = tk.BooleanVar(value=True)
        auto_capture_cb = tk.Checkbutton(
            status_frame, 
            text="Auto-Capture (Turn this off if you want to manually capture)",
            variable=auto_capture_var
        )
        auto_capture_cb.pack(pady=5)
        
        # Manual capture button (initially hidden)
        manual_capture_btn = tk.Button(status_frame, text="Capture Image", state="disabled")
        manual_capture_btn.pack(pady=5)
        
        # Generate employee ID
        emp_id = self.get_next_employee_id()
        
        # Create employee folder
        emp_folder = os.path.join(self.face_data_dir, str(emp_id))
        os.makedirs(emp_folder, exist_ok=True)
        
        # Image counter
        img_counter = [0]
        max_images = 20
        
        # Start camera
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            messagebox.showerror("Camera Error", "Cannot access webcam")
            capture_window.destroy()
            return False
        
        # Set lower resolution for better performance
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Auto/manual capture toggle function
        def toggle_auto_capture():
            if auto_capture_var.get():
                manual_capture_btn.config(state="disabled")
            else:
                manual_capture_btn.config(state="normal")
        
        # Bind checkbox to toggle function
        auto_capture_cb.config(command=toggle_auto_capture)
        
        # Manual capture function
        def manual_capture():
            nonlocal frame, gray
            if img_counter[0] < max_images:
                # Find faces in the current frame
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                if len(faces) > 0:
                    # Take the largest face detected
                    faces = sorted(faces, key=lambda x: x[2]*x[3], reverse=True)
                    x, y, w, h = faces[0]
                    
                    # Save face
                    face_img = gray[y:y+h, x:x+w]
                    face_img = cv2.resize(face_img, (200, 200))
                    file_path = os.path.join(emp_folder, f'{img_counter[0]}.jpg')
                    cv2.imwrite(file_path, face_img)
                    img_counter[0] += 1
                    counter_label.config(text=f"Images: {img_counter[0]}/{max_images}")
                    
                    # Flash effect - avoid using opacity parameter
                    flash_effect()
        
        # Flash effect function (without opacity parameter)
        def flash_effect():
            # Create a white overlay frame
            flash_frame = tk.Frame(capture_window, bg="white")
            flash_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            # Use transparency by configuring after a short delay
            capture_window.after(50, lambda: flash_frame.place_forget())
            
        # Configure manual capture button
        manual_capture_btn.config(command=manual_capture)
            
        # Variables to track face presence and time
        face_present = [False]
        last_capture_time = [0]
        min_interval = 0.5  # Minimum seconds between captures
        frame_skip = [0]  # For processing only every few frames
        
        # Frame and gray frame references for manual capture
        frame = None
        gray = None
        
        # Function to update the video frame
        def update_frame():
            nonlocal frame, gray
            ret, frame = cam.read()
            if ret:
                # Skip some frames for better performance
                frame_skip[0] += 1
                process_this_frame = (frame_skip[0] % 2 == 0)  # Process every other frame
                
                if process_this_frame:
                    # Convert to grayscale for face detection
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Detect faces
                    faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                    
                    # Auto-capture when appropriate
                    current_time = time.time()
                    
                    # Process each face detected
                    for (x, y, w, h) in faces:
                        # Draw rectangle around face
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        
                        # Auto-capture logic
                        if auto_capture_var.get() and img_counter[0] < max_images:
                            # Only capture if enough time has passed since last capture
                            if current_time - last_capture_time[0] > min_interval:
                                face_img = gray[y:y+h, x:x+w]
                                face_img = cv2.resize(face_img, (200, 200))
                                file_path = os.path.join(emp_folder, f'{img_counter[0]}.jpg')
                                cv2.imwrite(file_path, face_img)
                                img_counter[0] += 1
                                counter_label.config(text=f"Images: {img_counter[0]}/{max_images}")
                                last_capture_time[0] = current_time
                                
                                # Flash effect for auto-capture (once every 4 captures)
                                if img_counter[0] % 4 == 0:
                                    flash_effect()
                        
                        # Mark that a face was found
                        face_present[0] = True
                        break
                
                # Convert to RGB for tkinter (every frame for smooth display)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = cv2.resize(rgb_frame, (750, 500))
                
                # Convert to PhotoImage
                imgtk = ImageTk.PhotoImage(image=Image.fromarray(img))
                
                # Update the label
                video_frame.imgtk = imgtk
                video_frame.configure(image=imgtk)
                
                # Schedule next update if not at max images
                if img_counter[0] < max_images and video_frame.winfo_exists():
                    video_frame.after(20, update_frame)  # 20ms = ~50 FPS for smoother display
                elif img_counter[0] >= max_images:
                    # Finished capturing
                    status_label.config(text="Capture complete! Saving employee data...")
                    # Save to CSV and train model
                    self.save_employee_data(emp_id, name)
                    # Close window after a delay
                    capture_window.after(1000, lambda: finish_capture())
            else:
                status_label.config(text="Error: Cannot read from camera")
        
        # Function to close resources
        def finish_capture():
            cam.release()
            messagebox.showinfo("Success", f"Employee {name} added successfully!")
            capture_window.destroy()
        
        # Start update loop
        update_frame()
        
        # Wait for window to be destroyed
        capture_window.protocol("WM_DELETE_WINDOW", lambda: (cam.release(), capture_window.destroy()))
        capture_window.mainloop()
        
        return True
    
    def get_next_employee_id(self):
        """Get the next available employee ID"""
        if os.path.exists(self.employee_csv):
            df = pd.read_csv(self.employee_csv)
            if not df.empty:
                return int(df['ID'].max()) + 1
        return 1
    
    def save_employee_data(self, emp_id, name):
        """Save employee data to CSV and train model"""
        try:
            # Save to CSV
            if os.path.exists(self.employee_csv):
                df = pd.read_csv(self.employee_csv)
            else:
                df = pd.DataFrame(columns=['ID', 'Name'])
            
            new_employee = pd.DataFrame([{'ID': emp_id, 'Name': name}])
            df = pd.concat([df, new_employee], ignore_index=True)
            df.to_csv(self.employee_csv, index=False)
            
            # Train the model with all faces
            self.train_recognizer()
            
            self.log(f"Employee {name} (ID: {emp_id}) saved successfully")
            return True
        except Exception as e:
            self.log(f"Error saving employee data: {str(e)}")
            return False
    
    def train_recognizer(self):
        """Train the face recognizer with all faces"""
        faces, labels = [], []
        
        # Iterate through each employee folder
        for emp_folder in os.listdir(self.face_data_dir):
            emp_id = int(emp_folder)
            folder_path = os.path.join(self.face_data_dir, emp_folder)
            
            if not os.path.isdir(folder_path):
                continue
            
            # Load face images
            for img_name in os.listdir(folder_path):
                img_path = os.path.join(folder_path, img_name)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue
                faces.append(img)
                labels.append(emp_id)
        
        if len(faces) == 0:
            self.log("No face data available for training")
            return False
        
        # Train the recognizer
        self.recognizer.train(faces, np.array(labels))
        
        # Save the model
        self.recognizer.write(self.model_file)
        
        self.log(f"Face recognition model trained with {len(faces)} images of {len(set(labels))} people")
        return True
    
    def recognize_faces(self, parent_window=None):
        """Start face recognition process for attendance"""
        if not os.path.exists(self.employee_csv):
            messagebox.showerror("Error", "No employees found.")
            return
            
        # Load employee data
        df = pd.read_csv(self.employee_csv)
        # Ensure ID column is integer type
        df['ID'] = df['ID'].astype(int)
        
        if df.empty:
            messagebox.showerror("Error", "No employees found.")
            return
            
        # Check if model exists
        if not os.path.exists(self.model_file):
            messagebox.showerror("Error", "Face recognition model not found. Add employees first.")
            return
            
        # Create recognition window
        recog_window = Toplevel(parent_window) if parent_window else tk.Tk()
        recog_window.title("Face Recognition")
        recog_window.geometry("800x600")
        
        # Main frame
        main_frame = tk.Frame(recog_window)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Video frame
        video_frame = tk.Label(main_frame)
        video_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status frame
        status_frame = tk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        # Status label
        status_label = tk.Label(status_frame, text="Recognizing faces... Press Q to quit")
        status_label.pack(fill=tk.X)
        
        # Control frame
        control_frame = tk.Frame(status_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        # Rectangle color options
        color_var = tk.StringVar(value="green")
        color_label = tk.Label(control_frame, text="Rectangle Color:")
        color_label.pack(side=tk.LEFT, padx=5)
        
        color_options = {"Green": "green", "Red": "red", "Blue": "blue", "Yellow": "yellow"}
        color_menu = tk.OptionMenu(control_frame, color_var, *color_options.keys())
        color_menu.pack(side=tk.LEFT, padx=5)
        
        # Start camera
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            messagebox.showerror("Camera Error", "Cannot access webcam")
            recog_window.destroy()
            return
            
        # Set lower resolution for better performance
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Store recognized IDs to avoid duplicate attendance
        recognized_ids = set()
        
        # Color mapping
        color_mapping = {
            "green": (0, 255, 0),
            "red": (0, 0, 255),
            "blue": (255, 0, 0),
            "yellow": (0, 255, 255)
        }
        
        # Frame counter for skipping frames to improve performance
        frame_count = 0
        
        # Function to update video frame
        def update_frame():
            nonlocal frame_count
            ret, frame = cam.read()
            if ret:
                frame_count += 1
                process_this_frame = (frame_count % 2 == 0)  # Process every other frame
                
                if process_this_frame:
                    # Convert to grayscale for face detection
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Detect faces
                    faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                    
                    # Get current selected color
                    rect_color = color_mapping[color_var.get().lower()]
                    
                    # Process each face
                    for (x, y, w, h) in faces:
                        # Extract face region
                        face_img = gray[y:y+h, x:x+w]
                        face_img = cv2.resize(face_img, (200, 200))
                        
                        try:
                            # Predict label
                            label, confidence = self.recognizer.predict(face_img)
                            
                            # Check confidence threshold
                            if confidence < 70:  # Lower confidence means better match
                                # Convert label to same type as in dataframe
                                name_row = df[df['ID'] == int(label)]
                                if not name_row.empty:
                                    name = name_row.iloc[0]['Name']
                                    cv2.putText(frame, f"{name} ({round(confidence, 2)})", (x, y-10),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, rect_color, 2)
                                    
                                    # Draw rectangle around face with selected color
                                    cv2.rectangle(frame, (x, y), (x+w, y+h), rect_color, 2)
                                    
                                    # Log attendance if not already logged
                                    if label not in recognized_ids:
                                        self.log_attendance(int(label), name)
                                        recognized_ids.add(label)
                                        status_label.config(text=f"Attendance marked for {name}")
                            else:
                                cv2.putText(frame, f"Unknown ({round(confidence, 2)})", (x, y-10),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                                # Draw red rectangle for unknown faces
                                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                        except Exception as e:
                            self.log(f"Recognition error: {str(e)}")
                            # Draw yellow rectangle for error cases
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
                
                # Convert to RGB for tkinter
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = cv2.resize(rgb_frame, (750, 500))
                
                # Convert to PhotoImage
                imgtk = ImageTk.PhotoImage(image=Image.fromarray(img))
                
                # Update the label
                video_frame.imgtk = imgtk
                video_frame.configure(image=imgtk)
                
                # Schedule next update
                if video_frame.winfo_exists():
                    video_frame.after(20, update_frame)  # 20ms = ~50 FPS for smoother display
            else:
                status_label.config(text="Error: Cannot read from camera")
        
        # Function to close resources
        def close_window():
            cam.release()
            recog_window.destroy()
        
        # Start update loop
        update_frame()
        
        # Close button
        close_btn = tk.Button(status_frame, text="Close (Q)", command=close_window)
        close_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Key binding
        recog_window.bind('q', lambda e: close_window())
        
        # Handle window close
        recog_window.protocol("WM_DELETE_WINDOW", close_window)
        recog_window.mainloop()
    
    def log_attendance(self, emp_id, name):
        """Log attendance for an employee"""
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        
        try:
            # Create default DataFrame with correct structure
            default_df = pd.DataFrame(columns=['ID', 'Name', 'Date', 'Time'])
            
            # Load existing attendance file if it exists
            if os.path.exists(self.attendance_csv):
                try:
                    df = pd.read_csv(self.attendance_csv)
                    
                    # Verify if the loaded CSV has all required columns
                    required_columns = ['ID', 'Name', 'Date', 'Time']
                    has_all_columns = all(col in df.columns for col in required_columns)
                    
                    if not has_all_columns:
                        self.log("Attendance CSV missing required columns, creating new file with correct structure")
                        # If structure is incorrect, use the default structure
                        df = default_df
                except Exception as e:
                    self.log(f"Error reading attendance CSV: {str(e)}, creating new file")
                    df = default_df
            else:
                df = default_df
            
            # Convert emp_id to string to ensure consistent type
            emp_id_str = str(emp_id)
            
            # Convert df ID column to string for comparison
            if not df.empty and 'ID' in df.columns:
                df['ID'] = df['ID'].astype(str)
            
            # Check if already marked for today
            if 'ID' in df.columns and 'Date' in df.columns:
                already_marked = ((df['ID'] == emp_id_str) & (df['Date'] == date_str)).any()
            else:
                already_marked = False
            
            if not already_marked:
                # Add new attendance record
                new_record = pd.DataFrame([{
                    'ID': emp_id_str, 
                    'Name': name, 
                    'Date': date_str, 
                    'Time': time_str
                }])
                
                df = pd.concat([df, new_record], ignore_index=True)
                df.to_csv(self.attendance_csv, index=False)
                self.log(f"Attendance marked for {name} (ID: {emp_id_str}) on {date_str} at {time_str}")
                return True
            else:
                self.log(f"Attendance already marked for {name} today")
                return False
        except Exception as e:
            self.log(f"Error logging attendance: {str(e)}")
            # Print stack trace for debugging
            import traceback
            print(traceback.format_exc())
            return False
    
    def view_attendance(self, parent_window=None):
        """View attendance records"""
        view_window = Toplevel(parent_window) if parent_window else tk.Tk()
        view_window.title("Attendance Records")
        view_window.geometry("800x600")
        
        # Main frame
        main_frame = tk.Frame(view_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load attendance data
        try:
            if os.path.exists(self.attendance_csv):
                df = pd.read_csv(self.attendance_csv)
            else:
                df = pd.DataFrame(columns=['ID', 'Name', 'Date', 'Time'])
            
            # Create treeview
            tree = ttk.Treeview(main_frame, columns=("ID", "Name", "Date", "Time"), show="headings")
            for col in ("ID", "Name", "Date", "Time"):
                tree.heading(col, text=col)
                tree.column(col, anchor=tk.CENTER)
            
            # Add scrollbars
            vsb = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
            hsb = ttk.Scrollbar(main_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            
            # Pack scrollbars
            vsb.pack(side=tk.RIGHT, fill=tk.Y)
            hsb.pack(side=tk.BOTTOM, fill=tk.X)
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Insert data
            for index, row in df.iterrows():
                tree.insert("", "end", values=(row['ID'], row['Name'], row['Date'], row['Time']))
            
            # Control frame
            control_frame = tk.Frame(view_window)
            control_frame.pack(fill=tk.X, padx=10, pady=10)
            
            # Export button
            export_btn = tk.Button(control_frame, text="Export CSV", 
                                  command=lambda: self.export_attendance(view_window))
            export_btn.pack(side=tk.LEFT, padx=5)
            
            # Close button
            close_btn = tk.Button(control_frame, text="Close", command=view_window.destroy)
            close_btn.pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            self.log(f"Error viewing attendance: {str(e)}")
            messagebox.showerror("Error", f"Failed to load attendance data: {str(e)}")
        
        view_window.mainloop()
    
    def export_attendance(self, parent_window=None):
        """Export attendance data to CSV"""
        from tkinter import filedialog
        
        try:
            # Ask for filename
            filename = filedialog.asksaveasfilename(
                parent=parent_window,
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Attendance"
            )
            
            if not filename:
                return
            
            # Copy attendance file
            shutil.copy2(self.attendance_csv, filename)
            
            messagebox.showinfo("Success", f"Attendance data exported to {filename}")
            
        except Exception as e:
            self.log(f"Error exporting attendance: {str(e)}")
            messagebox.showerror("Error", f"Failed to export attendance: {str(e)}")
    
    def remove_employee(self, parent_window=None):
        """Remove an employee"""
        remove_window = Toplevel(parent_window) if parent_window else tk.Tk()
        remove_window.title("Remove Employee")
        remove_window.geometry("400x300")
        
        # Main frame
        main_frame = tk.Frame(remove_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header = tk.Label(main_frame, text="Remove Employee", font=("Arial", 16, "bold"))
        header.pack(pady=10)
        
        # Input frame
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        # Label
        tk.Label(input_frame, text="Enter Employee ID or Name:").pack(side=tk.LEFT, padx=5)
        
        # Entry
        entry = tk.Entry(input_frame, width=20)
        entry.pack(side=tk.LEFT, padx=5)
        
        # Function to remove employee
        def do_remove():
            val = entry.get().strip()
            if not val:
                messagebox.showerror("Input Error", "Please enter Employee ID or Name.")
                return
            
            try:
                if not os.path.exists(self.employee_csv):
                    messagebox.showerror("Error", "No employee data found.")
                    return
                
                df = pd.read_csv(self.employee_csv)
                # Convert ID to string for comparison
                df['ID'] = df['ID'].astype(str)
                
                # Try matching ID first
                match = df[df['ID'] == val]
                
                # If no match by ID, try matching by name
                if match.empty:
                    match = df[df['Name'].str.lower() == val.lower()]
                
                if match.empty:
                    messagebox.showinfo("Not Found", f"No employee found with ID or Name: {val}")
                    return
                
                emp_id = match.iloc[0]['ID']
                emp_name = match.iloc[0]['Name']
                
                # Confirm deletion
                if not messagebox.askyesno("Confirm", f"Are you sure you want to remove {emp_name} (ID: {emp_id})?"):
                    return
                
                # Remove from CSV
                df = df[df['ID'] != emp_id]
                df.to_csv(self.employee_csv, index=False)
                
                # Remove face data folder
                folder_path = os.path.join(self.face_data_dir, str(emp_id))
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)
                
                # Retrain model
                self.train_recognizer()
                
                messagebox.showinfo("Success", f"Employee '{emp_name}' removed successfully!")
                remove_window.destroy()
                
            except Exception as e:
                self.log(f"Error removing employee: {str(e)}")
                messagebox.showerror("Error", f"Failed to remove employee: {str(e)}")
        
        # Buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        # Remove button
        remove_btn = tk.Button(button_frame, text="Remove", bg="red", fg="white", command=do_remove)
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        cancel_btn = tk.Button(button_frame, text="Cancel", command=remove_window.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        remove_window.mainloop() 