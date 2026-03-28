import cv2
import face_recognition
import numpy as np
import os
import csv
from datetime import datetime
import pandas as pd

class FaceRecognitionSystem:
    def __init__(self, faces_dir="faces", data_dir="data"):
        self.faces_dir = faces_dir
        self.data_dir = data_dir
        self.attendance_file = os.path.join(data_dir, "attendance.csv")
        self.known_face_encodings = []
        self.known_face_names = []
        
        # Create attendance file if it doesn't exist
        if not os.path.exists(self.attendance_file):
            with open(self.attendance_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Name", "Date", "Time"])
        
        # Load known faces
        self.load_known_faces()
    
    def load_known_faces(self):
        """Load known faces from the faces directory"""
        print("Loading known faces...")
        self.known_face_encodings = []
        self.known_face_names = []
        
        # Check if faces directory exists
        if not os.path.exists(self.faces_dir):
            print(f"Creating faces directory: {self.faces_dir}")
            os.makedirs(self.faces_dir)
            return
        
        for filename in os.listdir(self.faces_dir):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                print(f"Loading face: {filename}")
                try:
                    # Load image file
                    face_image = face_recognition.load_image_file(os.path.join(self.faces_dir, filename))
                    
                    # Get face encodings (features)
                    face_encodings = face_recognition.face_encodings(face_image)
                    
                    # If at least one face is found, use the first one
                    if len(face_encodings) > 0:
                        face_encoding = face_encodings[0]
                        
                        # Get name from filename (remove extension)
                        name = os.path.splitext(filename)[0]
                        
                        self.known_face_encodings.append(face_encoding)
                        self.known_face_names.append(name)
                        print(f"Successfully loaded face: {name}")
                    else:
                        print(f"No face found in {filename}")
                except Exception as e:
                    print(f"Error loading {filename}: {str(e)}")
        
        print(f"Loaded {len(self.known_face_names)} known faces")
    
    def mark_attendance(self, name):
        """Mark attendance for a recognized person"""
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
        """Start the face recognition process using webcam"""
        video_capture = cv2.VideoCapture(0)
        marked_names = set()  # Track names already marked in this session
        
        if not video_capture.isOpened():
            print("Error: Could not open webcam")
            return
        
        print("Starting face recognition...")
        
        while True:
            # Read frame from webcam
            ret, frame = video_capture.read()
            
            if not ret:
                print("Error: Failed to grab frame")
                break
            
            # Convert BGR to RGB (face_recognition uses RGB)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Find faces in current frame
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            # Loop through each face found in the frame
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                name = "Unknown"
                attendance_marked = False
                
                # Compare with known faces
                if self.known_face_encodings:
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
                    
                    # Calculate face distance (lower = more similar)
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    
                    if len(face_distances) > 0:
                        # Get best match
                        best_match_index = np.argmin(face_distances)
                        
                        if matches[best_match_index]:
                            name = self.known_face_names[best_match_index]
                            
                            # Mark attendance if not already marked
                            if name not in marked_names:
                                attendance_marked = self.mark_attendance(name)
                                if attendance_marked:
                                    marked_names.add(name)
                
                # Draw a rectangle and name
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                
                # Draw a label with name
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
                
                # If attendance was marked, show text
                if attendance_marked:
                    cv2.putText(frame, "Marked!", (left + 6, top - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 0), 1)
            
            # Display the frame
            cv2.imshow('Face Recognition', frame)
            
            # If callback provided, call it with the processed frame
            if frame_callback:
                frame_callback(frame, marked_names)
            
            # Break loop on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Release resources
        video_capture.release()
        cv2.destroyAllWindows()
    
    def register_new_face(self, name):
        """Register a new face using webcam"""
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
            
            # Find faces in current frame
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            
            # Draw rectangle around each face
            for top, right, bottom, left in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            
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
                # Check if face found
                if not face_locations:
                    print("No face detected. Please try again.")
                    continue
                
                # Save the face image
                cv2.imwrite(face_path, frame)
                print(f"Face registered: {name}")
                
                # Update known faces
                self.load_known_faces()
                
                cap.release()
                cv2.destroyAllWindows()
                return True
        
        return False 