import tkinter as tk
from tkinter import ttk
import os
import sys
from PIL import Image, ImageTk

# Color scheme
COLORS = {
    "primary": "#3f51b5",      # Indigo
    "primary_dark": "#303f9f", # Dark Indigo
    "accent": "#ff4081",       # Pink
    "white": "#ffffff",
    "light_gray": "#f5f5f5",
    "gray": "#9e9e9e",
    "text": "#212121",
    "text_secondary": "#757575",
    "success": "#4caf50",
    "warning": "#ff9800",
    "error": "#f44336",
    "surface": "#ffffff",
    "background": "#f5f5f5",
}

# Font configurations
FONTS = {
    "title": ("Segoe UI", 18, "bold"),
    "subtitle": ("Segoe UI", 16, "bold"),
    "heading": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 10),
    "body_bold": ("Segoe UI", 10, "bold"),
    "small": ("Segoe UI", 8),
    "button": ("Segoe UI", 10),
    "label": ("Segoe UI", 10),
}

# Button styles
BUTTON_STYLES = {
    "default": {
        "bg": COLORS["primary"],
        "fg": COLORS["white"],
        "activebackground": COLORS["primary_dark"],
        "activeforeground": COLORS["white"],
        "relief": tk.FLAT,
        "borderwidth": 0,
        "padx": 15,
        "pady": 8,
        "font": FONTS["button"]
    },
    "accent": {
        "bg": COLORS["accent"],
        "fg": COLORS["white"],
        "activebackground": "#e91e63",
        "activeforeground": COLORS["white"],
        "relief": tk.FLAT,
        "borderwidth": 0,
        "padx": 15,
        "pady": 8,
        "font": FONTS["button"]
    },
    "success": {
        "bg": COLORS["success"],
        "fg": COLORS["white"],
        "activebackground": "#388e3c",
        "activeforeground": COLORS["white"],
        "relief": tk.FLAT,
        "borderwidth": 0,
        "padx": 15,
        "pady": 8,
        "font": FONTS["button"]
    },
    "primary": {
        "bg": COLORS["primary"],
        "fg": COLORS["white"],
        "activebackground": COLORS["primary_dark"],
        "activeforeground": COLORS["white"],
        "relief": tk.FLAT,
        "borderwidth": 0,
        "padx": 15,
        "pady": 8,
        "font": FONTS["button"]
    },
    "danger": {
        "bg": COLORS["error"],
        "fg": COLORS["white"],
        "activebackground": "#d32f2f",
        "activeforeground": COLORS["white"],
        "relief": tk.FLAT,
        "borderwidth": 0,
        "padx": 15,
        "pady": 8,
        "font": FONTS["button"]
    }
}

def setup_theme(root):
    """Apply the theme to the root window and configure ttk styles"""
    style = ttk.Style(root)
    
    # Configure ttk styles
    style.configure("TFrame", background=COLORS["background"])
    style.configure("TLabel", background=COLORS["background"], foreground=COLORS["text"], font=FONTS["body"])
    style.configure("TButton", 
                   background=COLORS["primary"], 
                   foreground=COLORS["white"], 
                   padding=(10, 5),
                   font=FONTS["button"])
    
    # Notebook styles (tabs)
    style.configure("TNotebook", background=COLORS["background"], tabmargins=(0, 5, 0, 0))
    style.configure("TNotebook.Tab", 
                   background=COLORS["light_gray"], 
                   foreground=COLORS["text_secondary"],
                   padding=(10, 5),
                   font=FONTS["button"])
    style.map("TNotebook.Tab", 
             background=[("selected", COLORS["primary"])],
             foreground=[("selected", COLORS["white"])])
    
    # Treeview styles (for tables)
    style.configure("Treeview",
                   background=COLORS["surface"],
                   foreground=COLORS["text"],
                   rowheight=25,
                   font=FONTS["body"])
    style.map("Treeview", 
             background=[("selected", COLORS["primary"])],
             foreground=[("selected", COLORS["white"])])
    style.configure("Treeview.Heading", 
                   background=COLORS["primary"], 
                   foreground=COLORS["white"],
                   font=FONTS["body_bold"],
                   relief="flat")
    
    # Entry styles
    style.configure("TEntry", padding=(5, 5))
    
    # Scale styles
    style.configure("TScale", background=COLORS["background"])
    
    # Progressbar styles
    style.configure("TProgressbar", 
                   background=COLORS["primary"],
                   troughcolor=COLORS["light_gray"],
                   thickness=8)
    
    return style

def apply_button_style(button, style_name="default"):
    """Apply a predefined button style to a tk.Button"""
    style = BUTTON_STYLES.get(style_name, BUTTON_STYLES["default"])
    for key, value in style.items():
        button[key] = value

def create_round_button(parent, text, command=None, style_name="default", width=120, height=40):
    """Create a rounded button with the specified style"""
    style = BUTTON_STYLES.get(style_name, BUTTON_STYLES["default"])
    
    frame = tk.Frame(parent, width=width, height=height, bg=style["bg"])
    frame.pack_propagate(False)
    
    button = tk.Button(frame, text=text, **style, command=command)
    button.pack(fill=tk.BOTH, expand=True)
    
    return frame, button

def load_and_resize_image(image_path, width, height):
    """Load an image and resize it to the specified dimensions"""
    try:
        img = Image.open(image_path)
        img = img.resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None

# Create application icon folder if it doesn't exist
def setup_icons():
    icons_dir = "icons"
    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir)
    
    # Return dictionary of icon paths
    return {
        "app": os.path.join(icons_dir, "app_icon.png"),
        "user": os.path.join(icons_dir, "user.png"),
        "attendance": os.path.join(icons_dir, "attendance.png"),
        "face": os.path.join(icons_dir, "face.png"),
        "settings": os.path.join(icons_dir, "settings.png"),
        "export": os.path.join(icons_dir, "export.png"),
    } 