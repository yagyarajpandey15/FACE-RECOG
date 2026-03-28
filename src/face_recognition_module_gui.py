import cv2
import os
import csv
import shutil
from datetime import datetime
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import simpledialog, messagebox
import threading

class FaceRecognitionSystem:
    def __init__(self, faces_dir="faces", data_dir="data", status_callback=None):
        self.faces_dir = faces_dir
        self.data_dir = data_dir
        self.attendance_file = os.path.join(data_dir, "attendance.csv")
        self.selfies_dir = os.path.join(data_dir, "selfies")
        self.status_callback = status_callback  # Callback for status updates
        self.log_queue = []  # Store recent log messages
        
        # Load face cascade classifier
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Create necessary directories
        self.create_directories()
        
        # Create attendance file if it doesn't exist
        if not os.path.exists(self.attendance_file):
            with open(self.attendance_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Name", "Date", "Time", "SelfieImage"])
    
    def set_status_callback(self, callback):
        """Set the status callback function"""
        self.status_callback = callback
    
    def log(self, message):
        """Log a message and call the status callback if available"""
        self.log_queue.append(message)
        # Keep only last 10 messages
        if len(self.log_queue) > 10:
            self.log_queue.pop(0)
            
        # Call the status callback if available
        if self.status_callback:
            self.status_callback(message)
        
    def create_directories(self):
        """Create necessary directories if they don't exist"""
        for directory in [self.data_dir, self.faces_dir, self.selfies_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                self.log(f"Created directory: {directory}")
    
    def mark_attendance(self, name, frame=None):
        """Mark attendance for a person and save selfie"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        
        # Default selfie path
        selfie_path = "No_Selfie"
        
        # Check if already marked for today
        try:
            df = pd.read_csv(self.attendance_file)
            today_records = df[df["Date"] == date_str]
            if name in today_records["Name"].values:
                self.log(f"Attendance already marked for {name} today")
                return False, None
        except Exception as e:
            self.log(f"Warning: {str(e)}")
        
        # Save selfie if frame is provided
        if frame is not None:
            # Create a filename with name and timestamp
            selfie_filename = f"{name}_{timestamp}.jpg"
            selfie_path = os.path.join(self.selfies_dir, selfie_filename)
            
            # Save the selfie
            cv2.imwrite(selfie_path, frame)
            self.log(f"Saved selfie: {selfie_filename}")
            # Use relative path in CSV
            selfie_path = os.path.join("selfies", selfie_filename)
        
        # Write attendance to CSV
        with open(self.attendance_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([name, date_str, time_str, selfie_path])
            self.log(f"Attendance marked for {name} at {time_str}")
        
        return True, selfie_path
    
    def get_attendance_data(self, date=None, name=None):
        """Get attendance data, optionally filtered by date or name"""
        try:
            df = pd.read_csv(self.attendance_file)
            
            # Apply filters if specified
            if date:
                df = df[df["Date"] == date]
            
            if name:
                df = df[df["Name"] == name]
                
            return df
        except Exception as e:
            self.log(f"Error reading attendance data: {str(e)}")
            return pd.DataFrame(columns=["Name", "Date", "Time", "SelfieImage"])
    
    def export_attendance(self, output_path=None, include_images=False):
        """Export attendance data to CSV and optionally include images"""
        try:
            # Default export filename with timestamp
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"attendance_export_{timestamp}.csv"
            
            # Read attendance data
            df = pd.read_csv(self.attendance_file)
            
            # Export to CSV
            df.to_csv(output_path, index=False)
            self.log(f"Attendance data exported to: {output_path}")
            
            # If include_images is True, create a zip file with the CSV and images
            if include_images:
                import zipfile
                
                # Create a zip file
                zip_path = os.path.splitext(output_path)[0] + ".zip"
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    # Add the CSV file
                    zipf.write(output_path, os.path.basename(output_path))
                    
                    # Add all selfie images
                    img_count = 0
                    for _, row in df.iterrows():
                        if row["SelfieImage"] != "No_Selfie":
                            image_path = os.path.join(self.data_dir, row["SelfieImage"])
                            if os.path.exists(image_path):
                                zipf.write(image_path, row["SelfieImage"])
                                img_count += 1
                    
                    self.log(f"Added {img_count} selfie images to the export")
                
                self.log(f"Attendance data with images exported to: {zip_path}")
                return zip_path
            
            return output_path
        
        except Exception as e:
            self.log(f"Error exporting attendance data: {str(e)}")
            return None
    
    def start_recognition(self, status_frame=None, parent_window=None):
        """Start face detection with GUI status updates"""
        recognition_window = tk.Toplevel() if parent_window else tk.Tk()
        recognition_window.title("Face Recognition")
        recognition_window.geometry("800x600")
        
        # Main frame
        main_frame = tk.Frame(recognition_window)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Video frame
        video_frame = tk.Label(main_frame)
        video_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Controls frame
        controls_frame = tk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Status frame
        status_frame_local = tk.Frame(main_frame)
        status_frame_local.pack(fill=tk.X, padx=10, pady=5)
        
        # Status label
        status_label = tk.Label(status_frame_local, text="Starting face detection...", anchor="w")
        status_label.pack(fill=tk.X)
        
        # Buttons
        mark_btn = tk.Button(
            controls_frame, 
            text="Mark Attendance (M)", 
            command=lambda: self.manual_attendance_dialog(recognition_window, video_capture, status_label)
        )
        mark_btn.pack(side=tk.LEFT, padx=5)
        
        register_btn = tk.Button(
            controls_frame, 
            text="Register Face (R)", 
            command=lambda: self.register_face_dialog(recognition_window, video_capture, status_label)
        )
        register_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(
            controls_frame, 
            text="Close (Q)", 
            command=lambda: self.stop_recognition(recognition_window, video_capture)
        )
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        # Start webcam in a separate thread
        video_capture = cv2.VideoCapture(0)
        if not video_capture.isOpened():
            status_label.config(text="Error: Could not open webcam")
            messagebox.showerror("Error", "Could not open webcam")
            recognition_window.destroy()
            return
        
        # Set callbacks
        def update_status(message):
            status_label.config(text=message)
            # Update the parent status frame if provided
            if status_frame and hasattr(status_frame, "status_label"):
                status_frame.status_label.config(text=message)
        
        self.set_status_callback(update_status)
        self.log("Starting face detection...")
        
        # Store recognized faces
        marked_names = set()
        
        # Function to update video frame
        def update_frame():
            ret, frame = video_capture.read()
            if ret:
                # Process frame
                display_frame = frame.copy()
                
                # Convert to grayscale for face detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = self.face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                )
                
                # Draw rectangle around faces
                for (x, y, w, h) in faces:
                    cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(display_frame, "Face Detected", (x, y-10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Convert to RGB for tkinter
                rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                img = cv2.resize(rgb_frame, (750, 500))
                
                # Convert to PhotoImage
                from PIL import Image, ImageTk
                img = Image.fromarray(img)
                imgtk = ImageTk.PhotoImage(image=img)
                
                # Update the label
                video_frame.imgtk = imgtk
                video_frame.configure(image=imgtk)
                
                # Schedule the next update
                if video_frame.winfo_exists():
                    video_frame.after(10, update_frame)
            else:
                self.log("Error: Failed to grab frame")
        
        # Key bindings
        recognition_window.bind('m', lambda e: self.manual_attendance_dialog(recognition_window, video_capture, status_label))
        recognition_window.bind('r', lambda e: self.register_face_dialog(recognition_window, video_capture, status_label))
        recognition_window.bind('q', lambda e: self.stop_recognition(recognition_window, video_capture))
        
        # Start updating the frame
        update_frame()
        
        # Run the window
        recognition_window.mainloop()
    
    def manual_attendance_dialog(self, parent, video_capture, status_label):
        """Show dialog for manual attendance"""
        # Pause the video temporarily
        ret, frame = video_capture.read()
        
        if ret:
            # Get name using a dialog
            name = simpledialog.askstring("Mark Attendance", "Enter name:", parent=parent)
            if name:
                status_label.config(text="Processing attendance...")
                success, _ = self.mark_attendance(name, frame)
                if success:
                    status_label.config(text=f"Attendance marked for {name}")
                else:
                    status_label.config(text=f"Attendance already marked for {name}")
        else:
            self.log("Error: Failed to grab frame for attendance")
    
    def register_face_dialog(self, parent, video_capture, status_label):
        """Show dialog for face registration"""
        # Ask for name
        name = simpledialog.askstring("Register New Face", "Enter name:", parent=parent)
        
        if not name:
            return
        
        # Show registration window
        register_window = tk.Toplevel(parent)
        register_window.title(f"Register Face: {name}")
        register_window.geometry("600x500")
        
        # Video frame
        video_frame = tk.Label(register_window)
        video_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status label
        reg_status = tk.Label(register_window, text="Position your face in the frame and press Capture")
        reg_status.pack(pady=5)
        
        # Button frame
        button_frame = tk.Frame(register_window)
        button_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Face detected flag
        face_detected = [False]
        
        # Update frame function
        def update_register_frame():
            nonlocal face_detected
            ret, frame = video_capture.read()
            if ret and video_frame.winfo_exists():
                # Process frame
                display_frame = frame.copy()
                
                # Convert to grayscale for face detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = self.face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                )
                
                # Update face detected flag
                face_detected[0] = len(faces) > 0
                
                # Draw rectangle around faces
                for (x, y, w, h) in faces:
                    cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Show detection status
                if face_detected[0]:
                    reg_status.config(text="Face detected! Click Capture to register.")
                else:
                    reg_status.config(text="No face detected. Please position your face in frame.")
                
                # Convert to RGB for tkinter
                rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                img = cv2.resize(rgb_frame, (550, 400))
                
                # Convert to PhotoImage
                from PIL import Image, ImageTk
                img = Image.fromarray(img)
                imgtk = ImageTk.PhotoImage(image=img)
                
                # Update the label
                video_frame.imgtk = imgtk
                video_frame.configure(image=imgtk)
                
                # Schedule next update
                if video_frame.winfo_exists():
                    video_frame.after(10, update_register_frame)
        
        # Capture function
        def capture_face():
            if not face_detected[0]:
                messagebox.showwarning("Warning", "No face detected. Please position your face correctly.")
                return
            
            ret, frame = video_capture.read()
            if ret:
                # Make sure name doesn't contain invalid characters for filenames
                safe_name = name.replace(" ", "_")
                
                # Create faces directory if it doesn't exist
                if not os.path.exists(self.faces_dir):
                    os.makedirs(self.faces_dir)
                
                # Check if face already exists
                face_path = os.path.join(self.faces_dir, f"{safe_name}.jpg")
                if os.path.exists(face_path):
                    if not messagebox.askyesno("Overwrite", f"{name} already exists. Overwrite?"):
                        register_window.destroy()
                        return
                
                # Save the face image
                cv2.imwrite(face_path, frame)
                self.log(f"Face registered: {name}")
                
                # Show success message
                messagebox.showinfo("Success", f"{name} has been registered successfully!")
                
                # Close the registration window
                register_window.destroy()
            
        # Button to capture
        capture_btn = tk.Button(
            button_frame, 
            text="Capture", 
            command=capture_face
        )
        capture_btn.pack(side=tk.LEFT, padx=5)
        
        # Button to cancel
        cancel_btn = tk.Button(
            button_frame, 
            text="Cancel", 
            command=register_window.destroy
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Start updating frame
        update_register_frame()
    
    def stop_recognition(self, window, video_capture):
        """Stop the recognition and release resources"""
        if video_capture and video_capture.isOpened():
            video_capture.release()
        window.destroy()
    
    def get_face_list(self):
        """Get list of registered faces"""
        if not os.path.exists(self.faces_dir):
            return []
            
        face_files = []
        for filename in os.listdir(self.faces_dir):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                name = os.path.splitext(filename)[0]
                face_files.append(name)
                
        return sorted(face_files)
        
    def delete_face(self, name):
        """Delete a registered face"""
        if not name:
            return False
            
        face_path = os.path.join(self.faces_dir, f"{name}.jpg")
        if os.path.exists(face_path):
            os.remove(face_path)
            self.log(f"Deleted face: {name}")
            return True
        else:
            self.log(f"Face not found: {name}")
            return False 