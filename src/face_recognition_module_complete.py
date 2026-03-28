import cv2
import os
import csv
import shutil
from datetime import datetime
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import simpledialog, messagebox

class FaceRecognitionSystem:
    def __init__(self, faces_dir="faces", data_dir="data"):
        self.faces_dir = faces_dir
        self.data_dir = data_dir
        self.attendance_file = os.path.join(data_dir, "attendance.csv")
        self.selfies_dir = os.path.join(data_dir, "selfies")
        
        # Load face cascade classifier
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Create necessary directories
        self.create_directories()
        
        # Create attendance file if it doesn't exist
        if not os.path.exists(self.attendance_file):
            with open(self.attendance_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Name", "Date", "Time", "SelfieImage"])
    
    def create_directories(self):
        """Create necessary directories if they don't exist"""
        for directory in [self.data_dir, self.faces_dir, self.selfies_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
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
                print(f"Attendance already marked for {name} today")
                return False, None
        except Exception:
            # If there's an error reading the file, just continue and try to write
            pass
        
        # Save selfie if frame is provided
        if frame is not None:
            # Create a filename with name and timestamp
            selfie_filename = f"{name}_{timestamp}.jpg"
            selfie_path = os.path.join(self.selfies_dir, selfie_filename)
            
            # Save the selfie
            cv2.imwrite(selfie_path, frame)
            # Use relative path in CSV
            selfie_path = os.path.join("selfies", selfie_filename)
        
        # Write attendance to CSV
        with open(self.attendance_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([name, date_str, time_str, selfie_path])
            print(f"Attendance marked for {name} at {time_str}")
        
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
            print(f"Error reading attendance data: {str(e)}")
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
            
            # If include_images is True, create a zip file with the CSV and images
            if include_images:
                import zipfile
                
                # Create a zip file
                zip_path = os.path.splitext(output_path)[0] + ".zip"
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    # Add the CSV file
                    zipf.write(output_path, os.path.basename(output_path))
                    
                    # Add all selfie images
                    for _, row in df.iterrows():
                        if row["SelfieImage"] != "No_Selfie":
                            image_path = os.path.join(self.data_dir, row["SelfieImage"])
                            if os.path.exists(image_path):
                                zipf.write(image_path, row["SelfieImage"])
                
                return zip_path
            
            return output_path
        
        except Exception as e:
            print(f"Error exporting attendance data: {str(e)}")
            return None
    
    def start_recognition(self, frame_callback=None):
        """Start basic face detection using webcam with dialog-based input"""
        # Create a root window for dialogs but keep it hidden
        root = tk.Tk()
        root.withdraw()
        
        # Open webcam
        video_capture = cv2.VideoCapture(0)
        
        if not video_capture.isOpened():
            print("Error: Could not open webcam")
            return
        
        print("Starting face detection...")
        
        marked_names = set()  # Track names already marked in this session
        
        while True:
            # Read frame from webcam
            ret, frame = video_capture.read()
            
            if not ret:
                print("Error: Failed to grab frame")
                break
            
            # Create a copy for display
            display_frame = frame.copy()
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Draw rectangle around faces
            for (x, y, w, h) in faces:
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(display_frame, "Face Detected", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Display instructions
            cv2.putText(display_frame, "Press 'm' to mark attendance", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(display_frame, "Press 'r' to register a face", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(display_frame, "Press 'q' to quit", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Display the frame
            cv2.imshow('Face Detection', display_frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
                
            elif key == ord('m'):
                # Pause video and show dialog for manual attendance
                cv2.putText(display_frame, "PAUSED - Enter name in dialog", (10, 80), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow('Face Detection', display_frame)
                
                # Get name using a dialog
                name = simpledialog.askstring("Mark Attendance", "Enter name:")
                if name:
                    success, _ = self.mark_attendance(name, frame)
                    if success:
                        marked_names.add(name)
            
            elif key == ord('r'):
                # Pause video and show dialog for face registration
                cv2.putText(display_frame, "PAUSED - Registering new face", (10, 80), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow('Face Detection', display_frame)
                
                # Get name using a dialog
                name = simpledialog.askstring("Register New Face", "Enter name:")
                if name:
                    self.register_new_face(name)
        
        # Release resources
        video_capture.release()
        cv2.destroyAllWindows()
        root.destroy()
    
    def register_new_face(self, name):
        """Register a new face"""
        if not name or name.strip() == "":
            print("Error: Name cannot be empty")
            return False
        
        # Make sure name doesn't contain invalid characters for filenames
        name = name.replace(" ", "_")
        
        # Check if face already exists
        face_path = os.path.join(self.faces_dir, f"{name}.jpg")
        if os.path.exists(face_path):
            print(f"Error: {name} is already registered")
            messagebox.showerror("Registration Error", f"{name} is already registered")
            return False
        
        # Open camera
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return False
        
        print(f"Registering new face for {name}")
        print("Press SPACE to capture, or ESC to cancel")
        
        # Counter for detected faces in current frame
        face_detected = False
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("Error: Failed to grab frame")
                cap.release()
                return False
            
            # Create a copy for display
            display_frame = frame.copy()
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Draw rectangle around faces and update detection status
            face_detected = len(faces) > 0
            for (x, y, w, h) in faces:
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Display instructions
            cv2.putText(display_frame, "Press SPACE to capture", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display_frame, "Press ESC to cancel", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Display face detection status
            if face_detected:
                cv2.putText(display_frame, "Face Detected", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(display_frame, "No Face Detected", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Display the frame
            cv2.imshow('Register New Face', display_frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESC key
                print("Registration cancelled")
                cap.release()
                cv2.destroyAllWindows()
                return False
                
            elif key == 32:  # SPACE key
                if face_detected:
                    # Save the face image
                    cv2.imwrite(face_path, frame)
                    print(f"Face registered: {name}")
                    
                    # Show success message
                    messagebox.showinfo("Registration Successful", f"{name} has been registered successfully!")
                    
                    cap.release()
                    cv2.destroyAllWindows()
                    return True
                else:
                    print("No face detected. Please try again.")
        
        return False 