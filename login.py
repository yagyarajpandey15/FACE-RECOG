import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import datetime
from PIL import Image, ImageTk
import sys
import pickle
from src.theme import COLORS, FONTS, apply_button_style, setup_theme

# Credentials file
CREDENTIALS_FILE = "data/credentials.json"

# Create data directory and credentials file if they don't exist
if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists(CREDENTIALS_FILE):
    default_credentials = {
        "admin": {
            "password": "admin123",
            "role": "admin"
        },
        "teacher": {
            "password": "teacher123",
            "role": "teacher"
        }
    }
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(default_credentials, f, indent=4)

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition Attendance System")
        self.root.geometry("500x450")
        self.root.resizable(False, False)
        self.root.config(bg=COLORS["background"])
        
        # Center window on screen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width / 2) - (500 / 2)
        y = (screen_height / 2) - (450 / 2)
        self.root.geometry(f"500x450+{int(x)}+{int(y)}")
        
        # Create main frame
        main_frame = tk.Frame(root, bg=COLORS["surface"], padx=30, pady=30)
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=400, height=380)
        
        # Add shadow effect to main frame
        shadow_frame = tk.Frame(root, bg="#dddddd")
        shadow_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=404, height=384, x=2, y=2)
        main_frame.lift()
        
        # Top banner
        banner_frame = tk.Frame(main_frame, bg=COLORS["primary"], height=70)
        banner_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Try to load app logo
        try:
            # Create a default logo if it doesn't exist
            logo_path = "icons/app_icon.png"
            if not os.path.exists(logo_path):
                # Create a simple logo
                img = Image.new('RGB', (100, 100), color=COLORS["primary"])
                img.save(logo_path)
                
            # Load and resize logo
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((50, 50), Image.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img)
            
            # Logo label
            logo_label = tk.Label(banner_frame, image=logo_photo, bg=COLORS["primary"])
            logo_label.image = logo_photo  # Keep a reference
            logo_label.pack(side=tk.LEFT, padx=10, pady=10)
            
        except Exception:
            # If logo loading fails, just show text
            pass
        
        # Header label with modern font
        header = tk.Label(
            banner_frame,
            text="Login",
            font=FONTS["title"],
            bg=COLORS["primary"],
            fg=COLORS["white"]
        )
        header.pack(side=tk.LEFT, padx=10, pady=20)
        
        # Login frame
        login_frame = tk.Frame(main_frame, bg=COLORS["surface"])
        login_frame.pack(fill=tk.X, pady=20)
        
        # Username
        username_label = tk.Label(
            login_frame,
            text="Username:",
            font=FONTS["body_bold"],
            bg=COLORS["surface"],
            fg=COLORS["text"]
        )
        username_label.grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        self.username_entry = ttk.Entry(login_frame, font=FONTS["body"], width=25)
        self.username_entry.grid(row=0, column=1, pady=(0, 15), padx=(10, 0))
        
        # Password
        password_label = tk.Label(
            login_frame,
            text="Password:",
            font=FONTS["body_bold"],
            bg=COLORS["surface"],
            fg=COLORS["text"]
        )
        password_label.grid(row=1, column=0, sticky="w", pady=(0, 15))
        
        self.password_entry = ttk.Entry(login_frame, font=FONTS["body"], width=25, show="•")
        self.password_entry.grid(row=1, column=1, pady=(0, 15), padx=(10, 0))
        
        # Remember me checkbox
        self.remember_var = tk.BooleanVar(value=False)
        remember_check = ttk.Checkbutton(
            login_frame,
            text="Remember me",
            variable=self.remember_var,
            style="TCheckbutton"
        )
        remember_check.grid(row=2, column=1, sticky="w", padx=(10, 0))
        
        # Try to load saved credentials
        self.load_remembered_credentials()
        
        # Login button frame for centering
        button_frame = tk.Frame(main_frame, bg=COLORS["surface"])
        button_frame.pack(fill=tk.X, pady=20)
        
        # Login button
        self.login_btn = tk.Button(
            button_frame,
            text="Login",
            font=FONTS["button"],
            command=self.login,
            width=15,
            cursor="hand2"
        )
        apply_button_style(self.login_btn, "primary")  # Changed to primary for better look
        self.login_btn.pack(pady=10)
        
        # Status frame
        status_frame = tk.Frame(main_frame, bg=COLORS["surface"], height=30)
        status_frame.pack(fill=tk.X)
        
        # Status label
        self.status_label = tk.Label(
            status_frame,
            text="",
            font=FONTS["small"],
            bg=COLORS["surface"],
            fg=COLORS["error"]
        )
        self.status_label.pack()
        
        # Footer
        footer = tk.Label(
            main_frame,
            text="© " + str(datetime.datetime.now().year) + " Face Recognition Attendance System",
            font=FONTS["small"],
            bg=COLORS["surface"],
            fg=COLORS["text_secondary"]
        )
        footer.pack(side=tk.BOTTOM, pady=10)
        
        # Set focus to username entry
        self.username_entry.focus()
        
        # Bind Enter key to login
        self.root.bind("<Return>", lambda event: self.login())
        
    def load_remembered_credentials(self):
        """Load remembered credentials if they exist"""
        try:
            credential_file = os.path.join("data", "remembered_login.dat")
            if os.path.exists(credential_file):
                with open(credential_file, "rb") as f:
                    credentials = pickle.load(f)
                    self.username_entry.insert(0, credentials.get("username", ""))
                    self.password_entry.insert(0, credentials.get("password", ""))
                    self.remember_var.set(True)
        except Exception as e:
            print(f"Error loading credentials: {str(e)}")
    
    def save_credentials(self, username, password):
        """Save credentials if remember me is checked"""
        if self.remember_var.get():
            try:
                os.makedirs("data", exist_ok=True)
                credential_file = os.path.join("data", "remembered_login.dat")
                with open(credential_file, "wb") as f:
                    pickle.dump({"username": username, "password": password}, f)
            except Exception as e:
                print(f"Error saving credentials: {str(e)}")
    
    def show_status(self, message, is_error=True):
        """Show status message"""
        self.status_label.config(
            text=message,
            fg=COLORS["error"] if is_error else COLORS["success"]
        )
    
    def login(self):
        """Handle login"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            self.show_status("Please enter both username and password")
            return
        
        # Check credentials
        try:
            with open(CREDENTIALS_FILE, "r") as f:
                credentials = json.load(f)
            
            if username in credentials and credentials[username]["password"] == password:
                # Save credentials if remember me is checked
                self.save_credentials(username, password)
                
                role = credentials[username]["role"]
                self.show_status("Login successful! Launching dashboard...", False)
                self.root.after(500, lambda: self.launch_main_app(username, role))
            else:
                self.show_status("Invalid username or password")
                self.password_entry.delete(0, tk.END)
        except Exception as e:
            self.show_status(f"Error: {str(e)}")
    
    def launch_main_app(self, username, role):
        """Launch the main application based on user role"""
        import subprocess
        
        try:
            if role == "admin":
                # Use the improved admin dashboard
                self.root.destroy()
                self.start_improved_admin_dashboard(username)
            else:
                # Launch teacher dashboard
                subprocess.Popen([sys.executable, "src/teacher_dashboard.py", username])
                self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch application: {str(e)}")
            self.show_status(f"Error launching application")
            
    def start_improved_admin_dashboard(self, username):
        """Start the improved admin dashboard directly"""
        try:
            # Create a new root window
            from src.improved_admin_dashboard import ImprovedAdminDashboard
            root = tk.Tk()
            # Apply theme first
            setup_theme(root)
            # Create the dashboard app
            app = ImprovedAdminDashboard(root, username)
            root.mainloop()
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch improved dashboard: {str(e)}")
            print(f"Error launching dashboard: {str(e)}")  # Print for debugging

if __name__ == "__main__":
    root = tk.Tk()
    from src.theme import setup_theme
    style = setup_theme(root)
    app = LoginWindow(root)
    root.mainloop() 