import cv2
import os
import csv
from datetime import datetime
import pandas as pd
import numpy as np
import threading

class FaceRecognitionSystem:
    def __init__(self, faces_dir="faces", data_dir="data"):
        self.faces_dir = faces_dir
        self.data_dir = data_dir
        self.attendance_file = os.path.join(data_dir, "attendance.csv")
        
        # Load face cascade classifier
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Create attendance file if it doesn't exist
        if not os.path.exists(self.attendance_file):
            with open(self.attendance_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Name", "Date", "Time"])
    
    def mark_attendance(self, name):
        """Mark attendance for a person"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        # Check if already marked for today
        try:
            df = pd.read_csv(self.attendance_file)
            today_records = df[df["Date"] == date_str]
            if name in today_records["Name"].values:
                print(f"Attendance already marked for {name} today")
                return False
        except:
            # If there's an error reading the file, just continue and try to write
            pass
        
        # Write attendance to CSV
        with open(self.attendance_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([name, date_str, time_str])
            print(f"Attendance marked for {name} at {time_str}")
        
        return True
    
    def get_attendance_data(self, date=None):
        """Get attendance data, optionally filtered by date"""
        try:
            df = pd.read_csv(self.attendance_file)
            if date:
                return df[df["Date"] == date]
            return df
        except Exception as e:
            print(f"Error reading attendance data: {str(e)}")
            return pd.DataFrame(columns=["Name", "Date", "Time"])
    
    def start_recognition(self, frame_callback=None):
        """Start basic face detection (not recognition) using webcam"""
        # Open a sample video or webcam
        video_capture = cv2.VideoCapture(0)
        
        if not video_capture.isOpened():
            print("Error: Could not open webcam")
            return
        
        print("Starting face detection...")
        print("NOTE: This is a simplified version without actual face recognition.")
        print("To mark attendance manually, press 'm' and enter a name.")
        
        while True:
            # Read frame from webcam
            ret, frame = video_capture.read()
            
            if not ret:
                print("Error: Failed to grab frame")
                break
            
            # Convert to grayscale
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
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, "Face Detected", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Display instructions
            cv2.putText(frame, "Press 'm' to mark attendance manually", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(frame, "Press 'q' to quit", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            # Display the frame
            cv2.imshow('Face Detection', frame)
            
            # If callback provided, call it with the processed frame
            if frame_callback:
                frame_callback(frame, set())
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
                
            elif key == ord('m'):
                # Pause video
                cv2.putText(frame, "PAUSED - Enter name in console", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow('Face Detection', frame)
                
                # Get name from console input
                name = input("Enter name to mark attendance: ")
                if name:
                    self.mark_attendance(name)
        
        # Release resources
        video_capture.release()
        cv2.destroyAllWindows()
    
    def register_new_face(self, name):
        """Register a new face - in this simplified version, we just save an image with the name"""
        if not name or name.strip() == "":
            print("Error: Name cannot be empty")
            return False
        
        # Make sure name doesn't contain invalid characters for filenames
        name = name.replace(" ", "_")
        
        # Create faces directory if it doesn't exist
        if not os.path.exists(self.faces_dir):
            os.makedirs(self.faces_dir)
        
        # Check if face already exists
        face_path = os.path.join(self.faces_dir, f"{name}.jpg")
        if os.path.exists(face_path):
            print(f"Error: {name} is already registered")
            return False
        
        # Open camera
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return False
        
        print("Press SPACE to capture, or ESC to cancel")
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("Error: Failed to grab frame")
                cap.release()
                return False
            
            # Display instructions
            cv2.putText(frame, "Press SPACE to capture", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Press ESC to cancel", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Detect faces
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            # Draw rectangle around detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Display the frame
            cv2.imshow('Register New Face', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESC key
                print("Registration cancelled")
                cap.release()
                cv2.destroyAllWindows()
                return False
                
            elif key == 32:  # SPACE key
                # Save the face image
                cv2.imwrite(face_path, frame)
                print(f"Image saved as: {name}")
                
                cap.release()
                cv2.destroyAllWindows()
                return True
        
        return False 