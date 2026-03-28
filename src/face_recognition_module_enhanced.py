import cv2
import os
import csv
from datetime import datetime
import pandas as pd
import numpy as np
import threading
import tkinter as tk
from tkinter import simpledialog
import pickle

class FaceRecognitionSystem:
    def __init__(self, faces_dir="faces", data_dir="data"):
        self.faces_dir = faces_dir
        self.data_dir = data_dir
        self.attendance_file = os.path.join(data_dir, "attendance.csv")
        self.model_path = os.path.join(data_dir, "face_recognizer.pkl")
        self.labels_path = os.path.join(data_dir, "face_labels.pkl")
        
        # Create face recognizer
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Load face cascade classifier
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Store face labels and IDs
        self.face_labels = {}
        self.label_ids = {}
        self.next_id = 0
        
        # Create attendance file if it doesn't exist
        if not os.path.exists(self.attendance_file):
            with open(self.attendance_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Name", "Date", "Time"])
        
        # Load existing model if available
        self.load_recognizer()
    
    def load_recognizer(self):
        """Load saved face recognizer model if it exists, otherwise train a new one"""
        # Check if model and labels files exist
        if os.path.exists(self.model_path) and os.path.exists(self.labels_path):
            try:
                # Load the recognizer
                self.recognizer.read(self.model_path)
                
                # Load the labels
                with open(self.labels_path, 'rb') as f:
                    data = pickle.load(f)
                    self.face_labels = data['face_labels']
                    self.label_ids = data['label_ids']
                    self.next_id = data['next_id']
                
                print("Face recognition model loaded successfully")
                return True
            except Exception as e:
                print(f"Error loading face recognition model: {str(e)}")
        
        # If we couldn't load the model, train a new one if faces exist
        if os.path.exists(self.faces_dir) and len(os.listdir(self.faces_dir)) > 0:
            print("No model found or error loading model. Training new model...")
            self.train_recognizer()
            return True
        
        print("No faces found to train model")
        return False
    
    def save_recognizer(self):
        """Save the face recognizer model and labels"""
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Save the model
        self.recognizer.write(self.model_path)
        
        # Save the labels
        data = {
            'face_labels': self.face_labels,
            'label_ids': self.label_ids,
            'next_id': self.next_id
        }
        with open(self.labels_path, 'wb') as f:
            pickle.dump(data, f)
        
        print("Face recognition model saved successfully")
    
    def train_recognizer(self):
        """Train the face recognizer using images from the faces directory"""
        if not os.path.exists(self.faces_dir):
            print("Faces directory does not exist")
            return False
        
        face_files = [f for f in os.listdir(self.faces_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
        if not face_files:
            print("No face images found for training")
            return False
        
        # Reset recognition data
        self.face_labels = {}
        self.label_ids = {}
        self.next_id = 0
        
        # Training data
        faces = []
        labels = []
        
        # Process each image in the faces directory
        for filename in face_files:
            # Get name from filename (without extension)
            name = os.path.splitext(filename)[0]
            
            # Get or assign an ID for this name
            if name not in self.face_labels:
                self.face_labels[self.next_id] = name
                self.label_ids[name] = self.next_id
                self.next_id += 1
            
            # Load and process image
            image_path = os.path.join(self.faces_dir, filename)
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            
            if img is None:
                print(f"Could not read image: {filename}")
                continue
            
            # Detect face in the image
            faces_rect = self.face_cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=4)
            
            if len(faces_rect) == 0:
                print(f"No face detected in {filename}")
                continue
            
            # Use the largest face if multiple detected
            if len(faces_rect) > 1:
                # Find the largest face
                largest_area = 0
                largest_idx = 0
                for i, (x, y, w, h) in enumerate(faces_rect):
                    area = w * h
                    if area > largest_area:
                        largest_area = area
                        largest_idx = i
                face_rect = faces_rect[largest_idx]
            else:
                face_rect = faces_rect[0]
            
            # Extract face region
            x, y, w, h = face_rect
            face_img = img[y:y+h, x:x+w]
            
            # Add to training data
            faces.append(face_img)
            labels.append(self.label_ids[name])
        
        if not faces:
            print("No valid faces found for training")
            return False
        
        # Train the recognizer
        print("Training face recognizer...")
        self.recognizer.train(faces, np.array(labels))
        
        # Save the model
        self.save_recognizer()
        
        print(f"Face recognizer trained with {len(faces)} images of {len(set(labels))} people")
        return True
    
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
        """Start face recognition using webcam"""
        # Create a root window for dialogs but keep it hidden
        root = tk.Tk()
        root.withdraw()
        
        # Open webcam
        video_capture = cv2.VideoCapture(0)
        
        if not video_capture.isOpened():
            print("Error: Could not open webcam")
            return
        
        print("Starting face recognition...")
        
        marked_names = set()  # Track names already marked in this session
        
        while True:
            # Read frame from webcam
            ret, frame = video_capture.read()
            
            if not ret:
                print("Error: Failed to grab frame")
                break
            
            # Make a copy for display
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
            
            # Process each detected face
            for (x, y, w, h) in faces:
                # Extract face region
                face_roi = gray[y:y+h, x:x+w]
                
                # Try to recognize the face
                name = "Unknown"
                attendance_marked = False
                
                # Only attempt recognition if the model has been trained
                if os.path.exists(self.model_path):
                    try:
                        label_id, confidence = self.recognizer.predict(face_roi)
                        
                        # Lower confidence means better match (with LBPH)
                        if confidence < 80:  # Threshold for positive identification
                            if label_id in self.face_labels:
                                name = self.face_labels[label_id]
                                
                                # Mark attendance if not already marked
                                if name not in marked_names:
                                    attendance_marked = self.mark_attendance(name)
                                    if attendance_marked:
                                        marked_names.add(name)
                    except Exception as e:
                        print(f"Error during face recognition: {str(e)}")
                
                # Draw rectangle and name on face
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.rectangle(display_frame, (x, y+h-25), (x+w, y+h), (0, 255, 0), cv2.FILLED)
                cv2.putText(display_frame, name, (x+6, y+h-6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
                
                # If attendance was marked, show indication
                if attendance_marked:
                    cv2.putText(display_frame, "Attendance Marked!", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Add instructions to the display
            cv2.putText(display_frame, "Press 'm' to mark attendance manually", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(display_frame, "Press 'r' to register a new face", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(display_frame, "Press 'q' to quit", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Display the frame
            cv2.imshow('Face Recognition', display_frame)
            
            # If callback provided, call it with the processed frame
            if frame_callback:
                frame_callback(display_frame, marked_names)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
                
            elif key == ord('m'):
                # Manual attendance marking with dialog
                cv2.putText(display_frame, "PAUSED - Enter name in dialog", (10, 80), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow('Face Recognition', display_frame)
                
                # Get name using a dialog
                name = simpledialog.askstring("Mark Attendance", "Enter name:", parent=root)
                if name:
                    self.mark_attendance(name)
                    marked_names.add(name)
            
            elif key == ord('r'):
                # Register new face with dialog
                cv2.putText(display_frame, "PAUSED - Registering new face", (10, 80), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow('Face Recognition', display_frame)
                
                # Get name using a dialog
                name = simpledialog.askstring("Register New Face", "Enter name:", parent=root)
                if name:
                    self.register_new_face(name)
                    # Retrain the recognizer
                    self.train_recognizer()
        
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
            cv2.putText(display_frame, "Press SPACE to capture", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display_frame, "Press ESC to cancel", (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Display face detection status
            if face_detected:
                cv2.putText(display_frame, "Face Detected", (10, 90), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(display_frame, "No Face Detected", (10, 90), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
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
                    
                    cap.release()
                    cv2.destroyAllWindows()
                    return True
                else:
                    print("No face detected. Please try again.")
        
        return False 