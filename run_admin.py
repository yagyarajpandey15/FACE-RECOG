"""
Run Admin Dashboard Directly
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
    
    # Import and run admin dashboard
    from src.admin_dashboard import AdminDashboard
    import tkinter as tk
    
    root = tk.Tk()
    app = AdminDashboard(root, "Admin")
    root.mainloop() 