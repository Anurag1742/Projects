"""
Duplicate File Remover - GUI Application with Advanced Features

Features included:
- Tkinter-based GUI with folder selection and drag-drop support
- Duplicate detection by SHA256 + file size + name filtering
- Image perceptual hashing using PIL + imagehash
- File type and size filters
- Embedded Matplotlib visualization of duplicate stats
- Scheduled scans using APScheduler
- Notifications via plyer
- Logging and recovery data stored in SQLite database
- File versioning metadata to allow undo restoration
- Password protection for critical actions
- Dark/Light theme switching
- Basic voice command support (scan command)

Requirements:
- Python 3.7+
- Packages: pillow, imagehash, matplotlib, apscheduler, plyer, speechrecognition, pyaudio, sqlite3 (builtin)
- On Windows, pyaudio must be installed separately (or use official wheels)

Usage:
- Run this script to launch the GUI.
"""

import os
import sys
import hashlib
import shutil
import datetime
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import sqlite3
from functools import partial

from PIL import Image, UnidentifiedImageError
import imagehash

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from apscheduler.schedulers.background import BackgroundScheduler

try:
    from plyer import notification
except ImportError:
    notification = None  # Notifications won't work

try:
    import speech_recognition as sr
except ImportError:
    sr = None

# Constants and folders
APP_NAME = "Duplicate File Remover GUI"
DB_FILE = "duplicate_remover.db"
DUPLICATE_FOLDER = "duplicates"
TRASH_FOLDER = "trash_bin"
RECOVERY_FOLDER = "recovery_data"

# Supported image extensions for perceptual hashing
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'}

# Password for securing deletion and recovery (in real app, do better handling)
SECURE_PASSWORD = "admin123"  # Change or store securely in production

# Default theme colors
THEMES = {
    "light": {
        "bg": "#f0f0f0",
        "fg": "#202020",
        "button_bg": "#e0e0e0",
        "button_fg": "#202020",
        "entry_bg": "#ffffff",
        "entry_fg": "#202020",
    },
    "dark": {
        "bg": "#191919",
        "fg": "#e0e0e0",
        "button_bg": "#333333",
        "button_fg": "#e0e0e0",
        "entry_bg": "#2b2b2b",
        "entry_fg": "#e0e0e0",
    }
}

class DuplicateFileRemoverApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("1000x720")
        self.minsize(900, 700)

        self.current_theme = "dark"
        self.style = ttk.Style(self)
        self.configure(bg=THEMES[self.current_theme]["bg"])
        self.set_theme(self.current_theme)

        # Initialize database
        self.init_database()

        # Scheduler for scans
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

        # Initialize variables
        self.selected_folder = tk.StringVar()
        self.file_types_filter = tk.StringVar(value="*")  # e.g. *.jpg;*.png
        self.min_file_size = tk.IntVar(value=0)  # in KB
        self.max_file_size = tk.IntVar(value=10240)  # default max 10MB
        self.scan_in_progress = threading.Event()
        self.duplicates = []  # List of tuples (dup_path, original_path)
        self.duplicate_stats = {}  # filetype: count
        self.versioning_enabled = True

        # Create GUI components
        self.create_widgets()

        # Setup voice command thread if available
        if sr:
            threading.Thread(target=self.voice_command_listener, daemon=True).start()

    def set_theme(self, theme_name):
        """Apply theme colors to widgets"""
        colors = THEMES.get(theme_name, THEMES["light"])
        self.style.configure('TLabel', background=colors["bg"], foreground=colors["fg"])
        self.style.configure('TButton', background=colors["button_bg"], foreground=colors["button_fg"])
        self.style.configure('TEntry', fieldbackground=colors["entry_bg"], foreground=colors["entry_fg"])
        self.configure(bg=colors["bg"])
        # Background for frames
        for frame in [self.main_frame, self.filter_frame, self.log_frame, self.control_frame]:
            frame.configure(bg=colors["bg"])

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.set_theme(self.current_theme)

    def create_widgets(self):
        """Create main GUI components"""

        # Frames for layout
        self.main_frame = tk.Frame(self, bg=THEMES[self.current_theme]["bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top Control Frame for folder selection and filters
        self.control_frame = tk.Frame(self.main_frame, bg=THEMES[self.current_theme]["bg"])
        self.control_frame.pack(fill=tk.X, pady=(0, 10))

        # Folder selection
        folder_label = ttk.Label(self.control_frame, text="Folder to Scan:")
        folder_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
        folder_entry = ttk.Entry(self.control_frame, textvariable=self.selected_folder, width=60)
        folder_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        browse_button = ttk.Button(self.control_frame, text="Browse", command=self.browse_folder)
        browse_button.grid(row=0, column=2, sticky="ew", padx=(0, 10))
        self.control_frame.columnconfigure(1, weight=1)

        # Filters
        self.filter_frame = tk.LabelFrame(self.main_frame, text="Filters", bg=THEMES[self.current_theme]["bg"], fg=THEMES[self.current_theme]["fg"])
        self.filter_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(self.filter_frame, text="File Types (semicolon-separated, e.g. *.jpg;*.png):").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        self.file_types_entry = ttk.Entry(self.filter_frame, textvariable=self.file_types_filter, width=40)
        self.file_types_entry.grid(row=0, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(self.filter_frame, text="Min Size (KB):").grid(row=0, column=2, sticky="w", padx=5, pady=3)
        self.min_size_entry = ttk.Entry(self.filter_frame, textvariable=self.min_file_size, width=10)
        self.min_size_entry.grid(row=0, column=3, sticky="w", padx=5, pady=3)

        ttk.Label(self.filter_frame, text="Max Size (KB):").grid(row=0, column=4, sticky="w", padx=5, pady=3)
        self.max_size_entry = ttk.Entry(self.filter_frame, textvariable=self.max_file_size, width=10)
        self.max_size_entry.grid(row=0, column=5, sticky="w", padx=5, pady=3)

        # Scan and Action buttons
        self.scan_button = ttk.Button(self.main_frame, text="Scan for Duplicates", command=self.start_scan)
        self.scan_button.pack(fill=tk.X, pady=(0, 10))

        self.action_frame = tk.Frame(self.main_frame, bg=THEMES[self.current_theme]["bg"])
        self.action_frame.pack(fill=tk.X, pady=(0, 10))

        self.move_button = ttk.Button(self.action_frame, text="Move Duplicates to Folder", command=self.move_duplicates, state=tk.DISABLED)
        self.move_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.delete_button = ttk.Button(self.action_frame, text="Safe Delete (Trash)", command=self.safe_delete_duplicates, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.perm_delete_button = ttk.Button(self.action_frame, text="Permanent Delete", command=self.permanent_delete_duplicates, state=tk.DISABLED)
        self.perm_delete_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.recover_button = ttk.Button(self.action_frame, text="Recover Deleted Files", command=self.recover_files)
        self.recover_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.theme_button = ttk.Button(self.main_frame, text="Toggle Dark/Light Theme", command=self.toggle_theme)
        self.theme_button.pack(fill=tk.X, pady=(0, 5))

        # Log frame with scrollable text
        self.log_frame = tk.LabelFrame(self.main_frame, text="Log & Duplicate Preview", bg=THEMES[self.current_theme]["bg"], fg=THEMES[self.current_theme]["fg"])
        self.log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = ScrolledText(self.log_frame, state='disabled', bg=THEMES[self.current_theme]["entry_bg"], fg=THEMES[self.current_theme]["entry_fg"])
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Visualization frame with matplotlib chart
        self.visual_frame = tk.LabelFrame(self.main_frame, text="Duplicates Visualization", bg=THEMES[self.current_theme]["bg"], fg=THEMES[self.current_theme]["fg"])
        self.visual_frame.pack(fill=tk.BOTH, expand=True, pady=(10,0))

        self.figure, self.ax = plt.subplots(figsize=(8,3))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.visual_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.selected_folder.set(folder_selected)

    def log(self, message, level='info'):
        """Thread-safe logging in GUI"""
        # Color coding by level
        colors = {
            'info': 'black',
            'error': 'red',
            'warn': 'orange',
            'success': 'green'
        }
        color = colors.get(level, 'black')
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, message + "\n", (color,))
        self.log_text.tag_config(color, foreground=color)
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')

    def start_scan(self):
        """Start duplicate scan in separate thread to avoid blocking GUI"""
        if self.scan_in_progress.is_set():
            messagebox.showwarning(APP_NAME, "A scan is already running. Please wait.")
            return

        folder = self.selected_folder.get()
        if not os.path.isdir(folder):
            messagebox.showerror(APP_NAME, "Please select a valid folder to scan.")
            return

        # Clear previous results
        self.duplicates.clear()
        self.duplicate_stats.clear()
        self.clear_visualization()
        self.clear_log()
        self.disable_action_buttons()

        self.log(f"Starting scan in folder: {folder}")

        # Start thread
        thread = threading.Thread(target=self.scan_for_duplicates, args=(folder,), daemon=True)
        self.scan_in_progress.set()
        thread.start()

    def scan_for_duplicates(self, folder):
        try:
            file_types = [t.strip().lower() for t in self.file_types_filter.get().split(';') if t.strip()]
            if not file_types:
                file_types = ["*"]

            min_size_b = self.min_file_size.get() * 1024
            max_size_b = self.max_file_size.get() * 1024

            hash_map = {}
            duplicates = []

            # SQLite cursor for recording scan
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()

            # Create table to store scanned files (for versioning and logs)
            c.execute('''
                CREATE TABLE IF NOT EXISTS scanned_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE,
                    file_hash TEXT,
                    file_size INTEGER,
                    mtime REAL,
                    is_duplicate INTEGER,
                    original_file TEXT,
                    scan_time TEXT
                )
            ''')
            conn.commit()

            scan_start_time = datetime.datetime.now().isoformat()

            for root, _, files in os.walk(folder):
                for file in files:
                    full_path = os.path.join(root, file)
                    ext = os.path.splitext(file)[1].lower()

                    # Filter by file type
                    if "*" not in file_types and ext not in file_types:
                        continue

                    try:
                        stat = os.stat(full_path)
                    except Exception as e:
                        self.log(f"[Error] Cannot access {full_path}: {str(e)}", 'error')
                        continue

                    # Filter by size
                    if stat.st_size < min_size_b or stat.st_size > max_size_b:
                        continue

                    # File hash calculation
                    file_hash = None

                    # For images, use perceptual hash (more tolerant)
                    if ext in IMAGE_EXTENSIONS:
                        try:
                            with Image.open(full_path) as img:
                                file_hash = str(imagehash.average_hash(img))
                        except (UnidentifiedImageError, OSError) as e:
                            # If image can't be opened, fallback to sha256
                            file_hash = self.get_file_hash(full_path)
                    else:
                        file_hash = self.get_file_hash(full_path)

                    if not file_hash:
                        continue

                    # Combine hash with file size for detection robustness
                    composite_key = f"{file_hash}_{stat.st_size}"

                    if composite_key in hash_map:
                        original_file = hash_map[composite_key]
                        duplicates.append((full_path, original_file))

                        # Log in db as duplicate
                        c.execute('''
                            INSERT OR REPLACE INTO scanned_files
                            (file_path, file_hash, file_size, mtime, is_duplicate, original_file, scan_time)
                            VALUES (?, ?, ?, ?, 1, ?, ?)
                        ''', (full_path, file_hash, stat.st_size, stat.st_mtime, original_file, scan_start_time))
                    else:
                        hash_map[composite_key] = full_path
                        c.execute('''
                            INSERT OR REPLACE INTO scanned_files
                            (file_path, file_hash, file_size, mtime, is_duplicate, original_file, scan_time) 
                            VALUES (?, ?, ?, ?, 0, NULL, ?)
                        ''', (full_path, file_hash, stat.st_size, stat.st_mtime, scan_start_time))

                    conn.commit()

            conn.close()

            self.duplicates = duplicates

            if not duplicates:
                self.log("✅ No duplicates found.", 'success')
            else:
                self.log(f"⚠️ Found {len(duplicates)} duplicates.", 'warn')
                self.enable_action_buttons()

            self.build_duplicate_stats()
            self.plot_duplicates()

        except Exception as e:
            self.log(f"[Error] Scan failed: {str(e)}", 'error')
        finally:
            self.scan_in_progress.clear()

    def get_file_hash(self, filepath):
        """Calculate sha256 hash of a file"""
        try:
            hasher = hashlib.sha256()
            with open(filepath, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            self.log(f"[Error] Cannot hash file {filepath}: {str(e)}", 'error')
            return None

    def build_duplicate_stats(self):
        """Build stats dictionary for visualization"""
        stats = {}
        for dup_path, orig_path in self.duplicates:
            ext = os.path.splitext(dup_path)[1].lower()
            stats[ext] = stats.get(ext, 0) + 1
        self.duplicate_stats = stats

    def plot_duplicates(self):
        self.ax.clear()
        if not self.duplicate_stats:
            self.ax.text(0.5, 0.5, 'No duplicates found to plot.', transform=self.ax.transAxes,
                         ha='center', va='center', fontsize=14, color='gray')
        else:
            items = sorted(self.duplicate_stats.items(), key=lambda x: x[1], reverse=True)
            labels, counts = zip(*items)
            labels = [l if l else '(no ext)' for l in labels]
            self.ax.bar(labels, counts, color='tomato')
            self.ax.set_title("Duplicate File Counts by Type")
            self.ax.set_ylabel("Count")
            self.ax.set_xlabel("File Extension")
            self.ax.grid(axis='y')
        self.canvas.draw()

    def clear_visualization(self):
        self.ax.clear()
        self.canvas.draw()

    def clear_log(self):
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.configure(state='disabled')

    def enable_action_buttons(self):
        self.move_button.configure(state=tk.NORMAL)
        self.delete_button.configure(state=tk.NORMAL)
        self.perm_delete_button.configure(state=tk.NORMAL)

    def disable_action_buttons(self):
        self.move_button.configure(state=tk.DISABLED)
        self.delete_button.configure(state=tk.DISABLED)
        self.perm_delete_button.configure(state=tk.DISABLED)

    def password_prompt(self, action_name="perform this action"):
        pwd = tk.simpledialog.askstring(APP_NAME, f"Enter password to {action_name}:", show='*')
        if pwd == SECURE_PASSWORD:
            return True
        else:
            messagebox.showerror(APP_NAME, "Incorrect password.")
            return False

    def move_duplicates(self):
        if not self.password_prompt("move duplicates"):
            return
        self.perform_action_on_duplicates(action="move")

    def safe_delete_duplicates(self):
        if not self.password_prompt("safe delete duplicates"):
            return
        self.perform_action_on_duplicates(action="safe_delete")

    def permanent_delete_duplicates(self):
        if not self.password_prompt("permanently delete duplicates"):
            return
        answer = messagebox.askyesno(APP_NAME, "Permanently deleting cannot be undone. Are you sure?")
        if answer:
            self.perform_action_on_duplicates(action="permanent_delete")

    def perform_action_on_duplicates(self, action):
        """Handle duplicates with specified action"""
        if not self.duplicates:
            messagebox.showinfo(APP_NAME, "No duplicates to process.")
            return

        # Ensure backup folders
        os.makedirs(DUPLICATE_FOLDER, exist_ok=True)
        os.makedirs(TRASH_FOLDER, exist_ok=True)
        os.makedirs(RECOVERY_FOLDER, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        recovery_data = {}

