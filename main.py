import os
import sys
import tkinter as tk
from tkinter import ttk
from login import LoginWindow
from src.theme import setup_theme, COLORS, FONTS

# Make sure all required directories exist
def create_required_directories():
    """Create all required directories for the application"""
    directories = [
        "data",
        "faces",
        "data/selfies",
        "icons",
        "face_data"  # Added for the new LBPH face recognition approach
    ]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

if __name__ == "__main__":
    # Create required directories
    create_required_directories()
    
    # Start the login window
    root = tk.Tk()
    # Apply theme
    style = setup_theme(root)
    # Create the login window
    app = LoginWindow(root)
    root.mainloop() 