"""
Student Club Management System
A comprehensive GUI application for managing student clubs
Students can create and join clubs, admins have extended privileges
"""

# ==================== IMPORTS ====================
import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime
import hashlib


# ==================== CLASSES ====================

class User:
    """User class representing a system user"""
    def __init__(self, username, password, full_name, email, user_type="student"):
        self.username = username
        self.password = self._hash_password(password)
        self.full_name = full_name
        self.email = email
        self.user_type = user_type  # "student" or "admin"
        self.joined_clubs = []
        self.created_clubs = []  # Track clubs created by this user
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _hash_password(self, password):
        """Hash password for security"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password):
        """Verify password"""
        return self.password == hashlib.sha256(password.encode()).hexdigest()
    
    def can_create_clubs(self):
        """Check if user can create clubs (students AND admins can)"""
        return True  # All users can create clubs now
    
    def can_create_events(self):
        """Check if user can create events (only admins can)"""
        return self.user_type == "admin"
    
    def to_dict(self):
        """Convert user object to dictionary for storage"""
        return {
            "username": self.username,
            "password": self.password,
            "full_name": self.full_name,
            "email": self.email,
            "user_type": self.user_type,
            "joined_clubs": self.joined_clubs,
            "created_clubs": self.created_clubs,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create user object from dictionary"""
        user = cls(data["username"], "", data["full_name"], data["email"], data["user_type"])
        user.password = data["password"]
        user.joined_clubs = data.get("joined_clubs", [])
        user.created_clubs = data.get("created_clubs", [])
        user.created_at = data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return user


class Club:
    """Club class representing a student club"""
    def __init__(self, club_id, name, description, category, creator_username):
        self.club_id = club_id
        self.name = name
        self.description = description
        self.category = category
        self.creator_username = creator_username  # Who created the club
        self.members = [creator_username]  # Creator is automatically a member
        self.events = []
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def add_member(self, username):
        """Add a member to the club"""
        if username not in self.members:
            self.members.append(username)
            return True
        return False
    
    def remove_member(self, username):
        """Remove a member from the club"""
        if username in self.members:
            self.members.remove(username)
            return True
        return False
    
    def add_event(self, event):
        """Add an event to the club"""
        self.events.append(event)
    
    def is_creator(self, username):
        """Check if user is the creator of this club"""
        return self.creator_username == username
    
    def to_dict(self):
        """Convert club object to dictionary for storage"""
        events_dict = [event.to_dict() for event in self.events]
        return {
            "club_id": self.club_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "creator_username": self.creator_username,
            "members": self.members,
            "events": events_dict,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create club object from dictionary"""
        club = cls(data["club_id"], data["name"], data["description"], 
                   data["category"], data["creator_username"])
        club.members = data["members"]
        club.created_at = data["created_at"]
        club.events = [Event.from_dict(event_data) for event_data in data.get("events", [])]
        return club


class Event:
    """Event class representing club events"""
    def __init__(self, event_id, name, description, date, time, location, club_id):
        self.event_id = event_id
        self.name = name
        self.description = description
        self.date = date
        self.time = time
        self.location = location
        self.club_id = club_id
        self.attendees = []
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def add_attendee(self, username):
        """Add attendee to event"""
        if username not in self.attendees:
            self.attendees.append(username)
            return True
        return False
    
    def to_dict(self):
        """Convert event object to dictionary"""
        return {
            "event_id": self.event_id,
            "name": self.name,
            "description": self.description,
            "date": self.date,
            "time": self.time,
            "location": self.location,
            "club_id": self.club_id,
            "attendees": self.attendees,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create event object from dictionary"""
        event = cls(data["event_id"], data["name"], data["description"],
                    data["date"], data["time"], data["location"], data["club_id"])
        event.attendees = data.get("attendees", [])
        event.created_at = data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return event


class DataManager:
    """Manages data storage and retrieval"""
    
    DATA_DIR = "club_data"
    USERS_FILE = os.path.join(DATA_DIR, "users.json")
    CLUBS_FILE = os.path.join(DATA_DIR, "clubs.json")
    
    @classmethod
    def initialize(cls):
        """Initialize data directory and files"""
        if not os.path.exists(cls.DATA_DIR):
            os.makedirs(cls.DATA_DIR)
        
        # Create empty files if they don't exist
        if not os.path.exists(cls.USERS_FILE):
            with open(cls.USERS_FILE, 'w') as f:
                json.dump([], f)
        
        if not os.path.exists(cls.CLUBS_FILE):
            with open(cls.CLUBS_FILE, 'w') as f:
                json.dump([], f)
    
    @classmethod
    def save_users(cls, users):
        """Save users to file"""
        users_dict = [user.to_dict() for user in users]
        with open(cls.USERS_FILE, 'w') as f:
            json.dump(users_dict, f, indent=2)
    
    @classmethod
    def load_users(cls):
        """Load users from file"""
        try:
            with open(cls.USERS_FILE, 'r') as f:
                users_data = json.load(f)
                return [User.from_dict(data) for data in users_data]
        except:
            return []
    
    @classmethod
    def save_clubs(cls, clubs):
        """Save clubs to file"""
        clubs_dict = [club.to_dict() for club in clubs]
        with open(cls.CLUBS_FILE, 'w') as f:
            json.dump(clubs_dict, f, indent=2)
    
    @classmethod
    def load_clubs(cls):
        """Load clubs from file"""
        try:
            with open(cls.CLUBS_FILE, 'r') as f:
                clubs_data = json.load(f)
                return [Club.from_dict(data) for data in clubs_data]
        except:
            return []
    
    @classmethod
    def find_user_by_username(cls, username):
        """Find a user by username"""
        users = cls.load_users()
        for user in users:
            if user.username == username:
                return user
        return None
    
    @classmethod
    def find_club_by_id(cls, club_id):
        """Find a club by ID"""
        clubs = cls.load_clubs()
        for club in clubs:
            if club.club_id == club_id:
                return club
        return None
    
    @classmethod
    def find_clubs_by_creator(cls, username):
        """Find all clubs created by a specific user"""
        clubs = cls.load_clubs()
        return [club for club in clubs if club.creator_username == username]


# ==================== GUI CLASSES ====================

class LoginWindow:
    """Login window for the application"""
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Student Club Management System - Login")
        self.window.geometry("400x500")
        self.window.resizable(False, False)
        
        # Initialize data manager
        DataManager.initialize()
        
        # Create sample admin if no users exist
        self._create_sample_data()
        
        # Setup GUI
        self.setup_gui()
        
        # Center window
        self.center_window()
        
        self.window.mainloop()
    
    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_gui(self):
        """Setup the login GUI"""
        # Title
        title_label = tk.Label(self.window, text="Student Club Management", 
                               font=("Arial", 20, "bold"), fg="navy")
        title_label.pack(pady=30)
        
        subtitle_label = tk.Label(self.window, text="Login to Your Account",
                                  font=("Arial", 12))
        subtitle_label.pack(pady=10)
        
        # Login Frame
        login_frame = tk.Frame(self.window, bg="lightgray", relief=tk.RIDGE, bd=2)
        login_frame.pack(pady=20, padx=40, fill="both")
        
        # Username
        tk.Label(login_frame, text="Username:", bg="lightgray", 
                font=("Arial", 11)).grid(row=0, column=0, pady=10, padx=10, sticky="w")
        self.username_entry = tk.Entry(login_frame, font=("Arial", 11), width=25)
        self.username_entry.grid(row=0, column=1, pady=10, padx=10)
        
        # Password
        tk.Label(login_frame, text="Password:", bg="lightgray",
                font=("Arial", 11)).grid(row=1, column=0, pady=10, padx=10, sticky="w")
        self.password_entry = tk.Entry(login_frame, font=("Arial", 11), width=25, show="*")
        self.password_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # Login Button
        login_btn = tk.Button(login_frame, text="Login", bg="green", fg="white",
                              font=("Arial", 12, "bold"), width=15,
                              command=self.login)
        login_btn.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Signup link
        signup_label = tk.Label(self.window, text="Don't have an account?",
                                font=("Arial", 10))
        signup_label.pack()
        
        signup_btn = tk.Button(self.window, text="Sign Up Here", bg="blue", fg="white",
                               font=("Arial", 10, "bold"), command=self.open_signup)
        signup_btn.pack(pady=5)
    
    def _create_sample_data(self):
        """Create sample admin and clubs if no data exists"""
        users = DataManager.load_users()
        clubs = DataManager.load_clubs()
        
        # Create sample admin if no users exist
        if not users:
            admin = User("admin", "admin123", "System Administrator", "admin@college.edu", "admin")
            student = User("student1", "pass123", "John Student", "john@college.edu", "student")
            users.append(admin)
            users.append(student)
            DataManager.save_users(users)
        
        # Create sample clubs if none exist
        if not clubs:
            sample_clubs = [
                Club("CLUB001", "Programming Club", "Learn and practice programming skills. We work on projects, prepare for coding competitions, and explore new technologies.", "Technology", "admin"),
                Club("CLUB002", "Chess Club", "Play chess, learn strategies, and participate in tournaments. All skill levels welcome!", "Sports", "admin"),
                Club("CLUB003", "Photography Club", "Explore the art of photography. Learn techniques, go on photo walks, and showcase your work.", "Arts", "admin"),
                Club("CLUB004", "Debate Society", "Develop public speaking and critical thinking skills through debates and discussions.", "Academic", "admin"),
                Club("CLUB005", "Robotics Club", "Build and program robots. Participate in robotics competitions and workshops.", "Technology", "admin")
            ]
            DataManager.save_clubs(sample_clubs)
    
    def login(self):
        """Handle login attempt"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        users = DataManager.load_users()
        for user in users:
            if user.username == username and user.verify_password(password):
                self.window.destroy()
                DashboardWindow(user)
                return
        
        messagebox.showerror("Error", "Invalid username or password")
    
    def open_signup(self):
        """Open signup window"""
        self.window.withdraw()
        SignupWindow(self)


class SignupWindow:
    """Signup window for new users"""
    
    def __init__(self, login_window):
        self.login_window = login_window
        self.window = tk.Toplevel()
        self.window.title("Student Club Management System - Sign Up")
        self.window.geometry("450x550")
        self.window.resizable(False, False)
        
        self.setup_gui()
        self.center_window()
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_gui(self):
        """Setup the signup GUI"""
        # Title
        title_label = tk.Label(self.window, text="Create New Account",
                               font=("Arial", 18, "bold"), fg="navy")
        title_label.pack(pady=20)
        
        # Signup Frame
        signup_frame = tk.Frame(self.window, bg="lightgray", relief=tk.RIDGE, bd=2)
        signup_frame.pack(pady=20, padx=40, fill="both")
        
        # Full Name
        tk.Label(signup_frame, text="Full Name:", bg="lightgray",
                font=("Arial", 11)).grid(row=0, column=0, pady=10, padx=10, sticky="w")
        self.name_entry = tk.Entry(signup_frame, font=("Arial", 11), width=25)
        self.name_entry.grid(row=0, column=1, pady=10, padx=10)
        
        # Email
        tk.Label(signup_frame, text="Email:", bg="lightgray",
                font=("Arial", 11)).grid(row=1, column=0, pady=10, padx=10, sticky="w")
        self.email_entry = tk.Entry(signup_frame, font=("Arial", 11), width=25)
        self.email_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # Username
        tk.Label(signup_frame, text="Username:", bg="lightgray",
                font=("Arial", 11)).grid(row=2, column=0, pady=10, padx=10, sticky="w")
        self.username_entry = tk.Entry(signup_frame, font=("Arial", 11), width=25)
        self.username_entry.grid(row=2, column=1, pady=10, padx=10)
        
        # Password
        tk.Label(signup_frame, text="Password:", bg="lightgray",
                font=("Arial", 11)).grid(row=3, column=0, pady=10, padx=10, sticky="w")
        self.password_entry = tk.Entry(signup_frame, font=("Arial", 11), width=25, show="*")
        self.password_entry.grid(row=3, column=1, pady=10, padx=10)
        
        # Confirm Password
        tk.Label(signup_frame, text="Confirm Password:", bg="lightgray",
                font=("Arial", 11)).grid(row=4, column=0, pady=10, padx=10, sticky="w")
        self.confirm_entry = tk.Entry(signup_frame, font=("Arial", 11), width=25, show="*")
        self.confirm_entry.grid(row=4, column=1, pady=10, padx=10)
        
        # User Type
        tk.Label(signup_frame, text="Account Type:", bg="lightgray",
                font=("Arial", 11)).grid(row=5, column=0, pady=10, padx=10, sticky="w")
        self.user_type = tk.StringVar(value="student")
        student_rb = tk.Radiobutton(signup_frame, text="Student", variable=self.user_type,
                                    value="student", bg="lightgray")
        student_rb.grid(row=5, column=1, pady=5, padx=10, sticky="w")
        admin_rb = tk.Radiobutton(signup_frame, text="Admin", variable=self.user_type,
                                  value="admin", bg="lightgray")
        admin_rb.grid(row=6, column=1, pady=5, padx=10, sticky="w")
        
        # Signup Button
        signup_btn = tk.Button(signup_frame, text="Create Account", bg="green", fg="white",
                               font=("Arial", 12, "bold"), width=15,
                               command=self.signup)
        signup_btn.grid(row=7, column=0, columnspan=2, pady=20)
        
        # Back to login
        back_btn = tk.Button(self.window, text="Back to Login", bg="gray", fg="white",
                             font=("Arial", 10), command=self.go_back)
        back_btn.pack(pady=10)
    
    def signup(self):
        """Handle signup attempt"""
        full_name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm = self.confirm_entry.get().strip()
        user_type = self.user_type.get()
        
        # Validate
        if not all([full_name, email, username, password, confirm]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return
        
        # Check if username exists
        users = DataManager.load_users()
        for user in users:
            if user.username == username:
                messagebox.showerror("Error", "Username already exists")
                return
        
        # Create new user
        new_user = User(username, password, full_name, email, user_type)
        users.append(new_user)
        DataManager.save_users(users)
        
        messagebox.showinfo("Success", "Account created successfully! You can now login.")
        self.go_back()
    
    def go_back(self):
        """Go back to login window"""
        self.window.destroy()
        self.login_window.window.deiconify()
    
    def on_close(self):
        """Handle window close"""
        self.go_back()


class CreateClubDialog:
    """Dialog for creating a new club (available to all users)"""
    
    def __init__(self, parent, user, callback):
        self.parent = parent
        self.user = user
        self.callback = callback
        self.window = tk.Toplevel(parent.window)
        self.window.title("Create New Club")
        self.window.geometry("500x450")
        self.window.resizable(False, False)
        self.window.transient(parent.window)
        self.window.grab_set()
        
        self.setup_gui()
        self.center_window()
    
    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_gui(self):
        """Setup the create club dialog"""
        # Title
        title_label = tk.Label(self.window, text="Create New Club",
                               font=("Arial", 16, "bold"), fg="navy")
        title_label.pack(pady=20)
        
        # Form Frame
        form_frame = tk.Frame(self.window, bg="lightgray", relief=tk.RIDGE, bd=2)
        form_frame.pack(pady=20, padx=30, fill="both", expand=True)
        
        # Club Name
        tk.Label(form_frame, text="Club Name:", bg="lightgray",
                font=("Arial", 11)).grid(row=0, column=0, pady=10, padx=10, sticky="w")
        self.name_entry = tk.Entry(form_frame, font=("Arial", 11), width=30)
        self.name_entry.grid(row=0, column=1, pady=10, padx=10)
        
        # Category
        tk.Label(form_frame, text="Category:", bg="lightgray",
                font=("Arial", 11)).grid(row=1, column=0, pady=10, padx=10, sticky="w")
        self.category_combo = ttk.Combobox(form_frame, values=["Academic", "Sports", "Arts", "Technology", "Other"], width=27)
        self.category_combo.grid(row=1, column=1, pady=10, padx=10)
        self.category_combo.set("Academic")
        
        # Description
        tk.Label(form_frame, text="Description:", bg="lightgray",
                font=("Arial", 11)).grid(row=2, column=0, pady=10, padx=10, sticky="nw")
        self.desc_text = tk.Text(form_frame, height=8, width=30)
        self.desc_text.grid(row=2, column=1, pady=10, padx=10)
        
        # Buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Create Club", bg="green", fg="white",
                 font=("Arial", 11, "bold"), width=12,
                 command=self.create_club).pack(side="left", padx=10)
        
        tk.Button(button_frame, text="Cancel", bg="gray", fg="white",
                 font=("Arial", 11), width=12,
                 command=self.window.destroy).pack(side="left", padx=10)
    
    def create_club(self):
        """Create the club"""
        name = self.name_entry.get().strip()
        category = self.category_combo.get()
        description = self.desc_text.get("1.0", tk.END).strip()
        
        if not name or not description:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        # Load existing clubs
        clubs = DataManager.load_clubs()
        
        # Check if club name already exists
        for club in clubs:
            if club.name.lower() == name.lower():
                messagebox.showerror("Error", "A club with this name already exists!")
                return
        
        # Generate club ID
        club_id = f"CLUB{len(clubs) + 1:03d}"
        
        # Create club
        new_club = Club(club_id, name, description, category, self.user.username)
        clubs.append(new_club)
        DataManager.save_clubs(clubs)
        
        # Update user's created clubs list
        users = DataManager.load_users()
        for i, u in enumerate(users):
            if u.username == self.user.username:
                u.created_clubs.append(club_id)
                users[i] = u
                self.user = u
                break
        DataManager.save_users(users)
        
        messagebox.showinfo("Success", f"Club '{name}' created successfully!\n\nYou have been automatically added as a member.")
        
        self.window.destroy()
        if self.callback:
            self.callback()


class CreateEventDialog:
    """Dialog for creating a new event (admin only)"""
    
    def __init__(self, parent, clubs, callback):
        self.parent = parent
        self.clubs = clubs
        self.callback = callback
        self.window = tk.Toplevel(parent.window)
        self.window.title("Create New Event")
        self.window.geometry("550x500")
        self.window.resizable(False, False)
        self.window.transient(parent.window)
        self.window.grab_set()
        
        self.setup_gui()
        self.center_window()
    
    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_gui(self):
        """Setup the create event dialog"""
        # Title
        title_label = tk.Label(self.window, text="Create New Event",
                               font=("Arial", 16, "bold"), fg="navy")
        title_label.pack(pady=20)
        
        # Form Frame
        form_frame = tk.Frame(self.window, bg="lightgray", relief=tk.RIDGE, bd=2)
        form_frame.pack(pady=20, padx=30, fill="both", expand=True)
        
        # Select Club
        tk.Label(form_frame, text="Select Club:", bg="lightgray",
                font=("Arial", 11)).grid(row=0, column=0, pady=10, padx=10, sticky="w")
        self.club_combo = ttk.Combobox(form_frame, values=[c.name for c in self.clubs], width=27)
        self.club_combo.grid(row=0, column=1, pady=10, padx=10)
        
        # Event Name
        tk.Label(form_frame, text="Event Name:", bg="lightgray",
                font=("Arial", 11)).grid(row=1, column=0, pady=10, padx=10, sticky="w")
        self.name_entry = tk.Entry(form_frame, font=("Arial", 11), width=30)
        self.name_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # Date
        tk.Label(form_frame, text="Date (YYYY-MM-DD):", bg="lightgray",
                font=("Arial", 11)).grid(row=2, column=0, pady=10, padx=10, sticky="w")
        self.date_entry = tk.Entry(form_frame, font=("Arial", 11), width=30)
        self.date_entry.grid(row=2, column=1, pady=10, padx=10)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Time
        tk.Label(form_frame, text="Time (HH:MM):", bg="lightgray",
                font=("Arial", 11)).grid(row=3, column=0, pady=10, padx=10, sticky="w")
        self.time_entry = tk.Entry(form_frame, font=("Arial", 11), width=30)
        self.time_entry.grid(row=3, column=1, pady=10, padx=10)
        self.time_entry.insert(0, "14:00")
        
        # Location
        tk.Label(form_frame, text="Location:", bg="lightgray",
                font=("Arial", 11)).grid(row=4, column=0, pady=10, padx=10, sticky="w")
        self.location_entry = tk.Entry(form_frame, font=("Arial", 11), width=30)
        self.location_entry.grid(row=4, column=1, pady=10, padx=10)
        
        # Description
        tk.Label(form_frame, text="Description:", bg="lightgray",
                font=("Arial", 11)).grid(row=5, column=0, pady=10, padx=10, sticky="nw")
        self.desc_text = tk.Text(form_frame, height=5, width=30)
        self.desc_text.grid(row=5, column=1, pady=10, padx=10)
        
        # Buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Create Event", bg="green", fg="white",
                 font=("Arial", 11, "bold"), width=12,
                 command=self.confirm_create).pack(side="left", padx=10)
        
        tk.Button(button_frame, text="Cancel", bg="gray", fg="white",
                 font=("Arial", 11), width=12,
                 command=self.window.destroy).pack(side="left", padx=10)
    
    def confirm_create(self):
        """Show confirmation dialog before creating event"""
        # First, validate the form
        club_name = self.club_combo.get()
        event_name = self.name_entry.get().strip()
        event_date = self.date_entry.get().strip()
        event_time = self.time_entry.get().strip()
        event_location = self.location_entry.get().strip()
        event_desc = self.desc_text.get("1.0", tk.END).strip()
        
        if not all([club_name, event_name, event_date, event_time, event_location, event_desc]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        # Show confirmation dialog
        confirm_msg = f"Please confirm event details:\n\n"
        confirm_msg += f"Club: {club_name}\n"
        confirm_msg += f"Event: {event_name}\n"
        confirm_msg += f"Date: {event_date}\n"
        confirm_msg += f"Time: {event_time}\n"
        confirm_msg += f"Location: {event_location}\n\n"
        confirm_msg += "Do you want to create this event?"
        
        result = messagebox.askyesno("Confirm Event Creation", confirm_msg)
        
        if result:
            self.create_event()
    
    def create_event(self):
        """Create the event"""
        club_name = self.club_combo.get()
        event_name = self.name_entry.get().strip()
        event_date = self.date_entry.get().strip()
        event_time = self.time_entry.get().strip()
        event_location = self.location_entry.get().strip()
        event_desc = self.desc_text.get("1.0", tk.END).strip()
        
        # Find club
        club = None
        for c in self.clubs:
            if c.name == club_name:
                club = c
                break
        
        if not club:
            messagebox.showerror("Error", "Club not found")
            return
        
        # Generate event ID
        event_id = f"EVT{len(club.events) + 1:03d}"
        
        # Create event
        new_event = Event(event_id, event_name, event_desc, event_date, 
                         event_time, event_location, club.club_id)
        club.add_event(new_event)
        
        # Save
        DataManager.save_clubs(self.clubs)
        
        messagebox.showinfo("Success", f"Event '{event_name}' created successfully!")
        
        self.window.destroy()
        if self.callback:
            self.callback()


class DashboardWindow:
    """Main dashboard window"""
    
    def __init__(self, user):
        self.user = user
        self.window = tk.Tk()
        self.window.title(f"Student Club Management System - Dashboard ({user.full_name})")
        self.window.geometry("1000x650")
        
        # Load data
        self.refresh_data()
        
        # Setup GUI
        self.setup_gui()
        self.center_window()
        
        self.window.mainloop()
    
    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def refresh_data(self):
        """Refresh all data from files"""
        self.clubs = DataManager.load_clubs()
        # Refresh user data to get latest changes
        users = DataManager.load_users()
        for u in users:
            if u.username == self.user.username:
                self.user = u
                break
    
    def setup_gui(self):
        """Setup the dashboard GUI"""
        # Create menu bar
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Create Club", command=self.open_create_club_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Logout", command=self.logout)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.window.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Top frame with welcome message
        top_frame = tk.Frame(self.window, bg="navy", height=80)
        top_frame.pack(fill="x")
        
        welcome_label = tk.Label(top_frame, text=f"Welcome, {self.user.full_name}!",
                                  font=("Arial", 16, "bold"), fg="white", bg="navy")
        welcome_label.pack(side="left", padx=20, pady=20)
        
        user_type_label = tk.Label(top_frame, text=f"Role: {self.user.user_type.title()}",
                                    font=("Arial", 12), fg="lightgray", bg="navy")
        user_type_label.pack(side="right", padx=20, pady=20)
        
        # Create Club button in top bar
        create_club_btn = tk.Button(top_frame, text="+ Create New Club", bg="orange", fg="white",
                                     font=("Arial", 10, "bold"), command=self.open_create_club_dialog)
        create_club_btn.pack(side="right", padx=20, pady=15)
        
        # Main content area with notebook (tabs)
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_clubs_tab()
        self.create_my_clubs_tab()
        self.create_my_created_clubs_tab()
        self.create_events_tab()
        
        if self.user.user_type == "admin":
            self.create_admin_tab()
    
    def create_clubs_tab(self):
        """Create the clubs browsing tab"""
        clubs_frame = ttk.Frame(self.notebook)
        self.notebook.add(clubs_frame, text="All Clubs")
        
        # Search frame
        search_frame = tk.Frame(clubs_frame)
        search_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(search_frame, text="Search Clubs:", font=("Arial", 11)).pack(side="left", padx=5)
        self.search_entry = tk.Entry(search_frame, font=("Arial", 11), width=30)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_clubs)
        
        # Clubs display area with scrollbar
        canvas_frame = tk.Frame(clubs_frame)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.clubs_canvas = tk.Canvas(canvas_frame)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.clubs_canvas.yview)
        self.scrollable_frame = tk.Frame(self.clubs_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.clubs_canvas.configure(scrollregion=self.clubs_canvas.bbox("all"))
        )
        
        self.clubs_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.clubs_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.clubs_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.display_clubs()
    
    def display_clubs(self, search_term=""):
        """Display clubs in the scrollable frame"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        filtered_clubs = self.clubs
        if search_term:
            filtered_clubs = [c for c in self.clubs if search_term.lower() in c.name.lower() 
                             or search_term.lower() in c.description.lower()]
        
        if not filtered_clubs:
            tk.Label(self.scrollable_frame, text="No clubs found", 
                    font=("Arial", 12)).pack(pady=50)
            return
        
        # Display clubs in grid (2 columns)
        for i, club in enumerate(filtered_clubs):
            row = i // 2
            col = i % 2
            
            club_frame = tk.Frame(self.scrollable_frame, bg="lightgray", relief=tk.RIDGE, bd=2)
            club_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Creator label
            creator_info = f"Created by: {club.creator_username}"
            tk.Label(club_frame, text=creator_info, bg="lightgray", 
                    font=("Arial", 8), fg="gray").pack(anchor="e", padx=5, pady=2)
            
            # Club name
            tk.Label(club_frame, text=club.name, font=("Arial", 14, "bold"),
                    bg="lightgray", fg="navy").pack(pady=5)
            
            # Category
            tk.Label(club_frame, text=f"Category: {club.category}",
                    bg="lightgray", font=("Arial", 10)).pack()
            
            # Description
            desc = club.description[:100] + "..." if len(club.description) > 100 else club.description
            tk.Label(club_frame, text=desc, bg="lightgray", 
                    font=("Arial", 10), wraplength=250).pack(pady=5, padx=10)
            
            # Members count
            tk.Label(club_frame, text=f"Members: {len(club.members)}",
                    bg="lightgray", font=("Arial", 10)).pack()
            
            # Join/Leave button based on membership
            if club.club_id in self.user.joined_clubs:
                leave_btn = tk.Button(club_frame, text="Leave Club", bg="red", fg="white",
                                      command=lambda c=club: self.leave_club(c))
                leave_btn.pack(pady=5)
            else:
                join_btn = tk.Button(club_frame, text="Join Club", bg="green", fg="white",
                                     command=lambda c=club: self.join_club(c))
                join_btn.pack(pady=5)
    
    def search_clubs(self, event):
        """Handle club search"""
        self.display_clubs(self.search_entry.get())
    
    def join_club(self, club):
        """Join a club"""
        if club.add_member(self.user.username):
            self.user.joined_clubs.append(club.club_id)
            
            # Save updates
            users = DataManager.load_users()
            for i, u in enumerate(users):
                if u.username == self.user.username:
                    users[i] = self.user
                    break
            DataManager.save_users(users)
            
            clubs = DataManager.load_clubs()
            for i, c in enumerate(clubs):
                if c.club_id == club.club_id:
                    clubs[i] = club
                    break
            DataManager.save_clubs(clubs)
            
            messagebox.showinfo("Success", f"You have joined {club.name}!")
            self.refresh_data()
            self.display_clubs(self.search_entry.get() if hasattr(self, 'search_entry') else "")
            self.update_my_clubs()
            self.update_my_created_clubs()
        else:
            messagebox.showerror("Error", "Could not join club")
    
    def leave_club(self, club):
        """Leave a club"""
        if messagebox.askyesno("Confirm", f"Are you sure you want to leave {club.name}?"):
            if club.remove_member(self.user.username):
                if club.club_id in self.user.joined_clubs:
                    self.user.joined_clubs.remove(club.club_id)
                
                # Save updates
                users = DataManager.load_users()
                for i, u in enumerate(users):
                    if u.username == self.user.username:
                        users[i] = self.user
                        break
                DataManager.save_users(users)
                
                clubs = DataManager.load_clubs()
                for i, c in enumerate(clubs):
                    if c.club_id == club.club_id:
                        clubs[i] = club
                        break
                DataManager.save_clubs(clubs)
                
                messagebox.showinfo("Success", f"You have left {club.name}!")
                self.refresh_data()
                self.display_clubs(self.search_entry.get() if hasattr(self, 'search_entry') else "")
                self.update_my_clubs()
                self.update_my_created_clubs()
    
    def create_my_clubs_tab(self):
        """Create the 'My Clubs' tab"""
        self.my_clubs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.my_clubs_frame, text="My Joined Clubs")
        self.update_my_clubs()
    
    def update_my_clubs(self):
        """Update the My Clubs display"""
        for widget in self.my_clubs_frame.winfo_children():
            widget.destroy()
        
        user_clubs = [club for club in self.clubs if club.club_id in self.user.joined_clubs]
        
        if not user_clubs:
            tk.Label(self.my_clubs_frame, text="You haven't joined any clubs yet.\n\nClick 'All Clubs' tab to browse and join clubs!",
                    font=("Arial", 12), fg="gray").pack(pady=50)
            return
        
        tk.Label(self.my_clubs_frame, text=f"Clubs You've Joined ({len(user_clubs)})",
                font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=10)
        
        for club in user_clubs:
            club_frame = tk.Frame(self.my_clubs_frame, bg="lightblue", relief=tk.RIDGE, bd=2)
            club_frame.pack(fill="x", padx=20, pady=10)
            
            tk.Label(club_frame, text=club.name, font=("Arial", 14, "bold"),
                    bg="lightblue").pack(anchor="w", padx=10, pady=5)
            
            tk.Label(club_frame, text=club.description, bg="lightblue",
                    font=("Arial", 11), wraplength=700).pack(anchor="w", padx=10, pady=5)
            
            tk.Label(club_frame, text=f"Category: {club.category} | Members: {len(club.members)}",
                    bg="lightblue", font=("Arial", 10)).pack(anchor="w", padx=10, pady=2)
            
            button_frame = tk.Frame(club_frame, bg="lightblue")
            button_frame.pack(anchor="e", padx=10, pady=5)
            
            tk.Button(button_frame, text="View Events", bg="blue", fg="white",
                     command=lambda c=club: self.view_club_events(c)).pack(side="left", padx=5)
            
            tk.Button(button_frame, text="Leave Club", bg="red", fg="white",
                     command=lambda c=club: self.leave_club(c)).pack(side="left", padx=5)
    
    def create_my_created_clubs_tab(self):
        """Create the 'My Created Clubs' tab"""
        self.my_created_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.my_created_frame, text="My Created Clubs")
        self.update_my_created_clubs()
    
    def update_my_created_clubs(self):
        """Update the My Created Clubs display"""
        for widget in self.my_created_frame.winfo_children():
            widget.destroy()
        
        user_created_clubs = [club for club in self.clubs if club.creator_username == self.user.username]
        
        if not user_created_clubs:
            tk.Label(self.my_created_frame, text="You haven't created any clubs yet.\n\nClick 'Create Club' from the File menu to start your own club!",
                    font=("Arial", 12), fg="gray").pack(pady=50)
            return
        
        tk.Label(self.my_created_frame, text=f"Clubs You've Created ({len(user_created_clubs)})",
                font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=10)
        
        for club in user_created_clubs:
            club_frame = tk.Frame(self.my_created_frame, bg="lightgreen", relief=tk.RIDGE, bd=2)
            club_frame.pack(fill="x", padx=20, pady=10)
            
            tk.Label(club_frame, text=club.name, font=("Arial", 14, "bold"),
                    bg="lightgreen").pack(anchor="w", padx=10, pady=5)
            
            tk.Label(club_frame, text=club.description, bg="lightgreen",
                    font=("Arial", 11), wraplength=700).pack(anchor="w", padx=10, pady=5)
            
            tk.Label(club_frame, text=f"Category: {club.category} | Members: {len(club.members)}",
                    bg="lightgreen", font=("Arial", 10)).pack(anchor="w", padx=10, pady=2)
            
            button_frame = tk.Frame(club_frame, bg="lightgreen")
            button_frame.pack(anchor="e", padx=10, pady=5)
            
            tk.Button(button_frame, text="View Events", bg="blue", fg="white",
                     command=lambda c=club: self.view_club_events(c)).pack(side="left", padx=5)
    
    def create_events_tab(self):
        """Create the events tab"""
        events_frame = ttk.Frame(self.notebook)
        self.notebook.add(events_frame, text="Upcoming Events")
        
        # Refresh button
        refresh_btn = tk.Button(events_frame, text="↻ Refresh Events", bg="blue", fg="white",
                               command=lambda: self.refresh_events_display(events_frame))
        refresh_btn.pack(anchor="e", padx=10, pady=5)
        
        self.display_events(events_frame)
    
    def display_events(self, events_frame):
        """Display events in the events tab"""
        for widget in events_frame.winfo_children():
            if widget != events_frame.winfo_children()[0] if events_frame.winfo_children() else None:
                widget.destroy()
        
        all_events = []
        for club in self.clubs:
            for event in club.events:
                all_events.append((club, event))
        
        if not all_events:
            tk.Label(events_frame, text="No upcoming events.",
                    font=("Arial", 14)).pack(pady=50)
            return
        
        for club, event in all_events:
            event_frame = tk.Frame(events_frame, bg="lightyellow", relief=tk.RIDGE, bd=2)
            event_frame.pack(fill="x", padx=20, pady=10)
            
            tk.Label(event_frame, text=event.name, font=("Arial", 14, "bold"),
                    bg="lightyellow").pack(anchor="w", padx=10, pady=5)
            
            tk.Label(event_frame, text=f"Club: {club.name}",
                    bg="lightyellow", font=("Arial", 11)).pack(anchor="w", padx=10)
            
            tk.Label(event_frame, text=f"Date: {event.date} at {event.time}",
                    bg="lightyellow", font=("Arial", 11)).pack(anchor="w", padx=10)
            
            tk.Label(event_frame, text=f"Location: {event.location}",
                    bg="lightyellow", font=("Arial", 11)).pack(anchor="w", padx=10)
            
            tk.Label(event_frame, text=event.description, bg="lightyellow",
                    font=("Arial", 10), wraplength=700).pack(anchor="w", padx=10, pady=5)
            
            # Attend button
            if self.user.username in event.attendees:
                tk.Label(event_frame, text="✓ You are attending", fg="green",
                        bg="lightyellow", font=("Arial", 10, "bold")).pack(anchor="e", padx=10, pady=2)
            else:
                tk.Button(event_frame, text="I Will Attend", bg="green", fg="white",
                         command=lambda e=event, c=club: self.attend_event(e, c, events_frame)).pack(anchor="e", padx=10, pady=2)
    
    def refresh_events_display(self, events_frame):
        """Refresh the events display"""
        self.refresh_data()
        self.display_events(events_frame)
    
    def attend_event(self, event, club, events_frame):
        """Mark attendance for an event"""
        if event.add_attendee(self.user.username):
            DataManager.save_clubs(self.clubs)
            messagebox.showinfo("Success", f"You are now attending {event.name}!")
            self.refresh_data()
            self.display_events(events_frame)
    
    def create_admin_tab(self):
        """Create admin tab (only for admin users)"""
        admin_frame = ttk.Frame(self.notebook)
        self.notebook.add(admin_frame, text="Admin Panel")
        
        # Create Event section
        event_frame = tk.LabelFrame(admin_frame, text="Create New Event (Admin Only)", font=("Arial", 12, "bold"))
        event_frame.pack(fill="x", padx=20, pady=20)
        
        tk.Label(event_frame, text="Select Club:").grid(row=0, column=0, pady=5, padx=10, sticky="w")
        self.event_club = ttk.Combobox(event_frame, values=[c.name for c in self.clubs], width=30)
        self.event_club.grid(row=0, column=1, pady=5, padx=10)
        
        tk.Label(event_frame, text="Event Name:").grid(row=1, column=0, pady=5, padx=10, sticky="w")
        self.event_name_entry = tk.Entry(event_frame, width=35)
        self.event_name_entry.grid(row=1, column=1, pady=5, padx=10)
        
        tk.Label(event_frame, text="Date (YYYY-MM-DD):").grid(row=2, column=0, pady=5, padx=10, sticky="w")
        self.event_date_entry = tk.Entry(event_frame, width=35)
        self.event_date_entry.grid(row=2, column=1, pady=5, padx=10)
        self.event_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        tk.Label(event_frame, text="Time:").grid(row=3, column=0, pady=5, padx=10, sticky="w")
        self.event_time_entry = tk.Entry(event_frame, width=35)
        self.event_time_entry.grid(row=3, column=1, pady=5, padx=10)
        self.event_time_entry.insert(0, "14:00")
        
        tk.Label(event_frame, text="Location:").grid(row=4, column=0, pady=5, padx=10, sticky="w")
        self.event_location_entry = tk.Entry(event_frame, width=35)
        self.event_location_entry.grid(row=4, column=1, pady=5, padx=10)
        
        tk.Label(event_frame, text="Description:").grid(row=5, column=0, pady=5, padx=10, sticky="nw")
        self.event_desc_text = tk.Text(event_frame, height=3, width=35)
        self.event_desc_text.grid(row=5, column=1, pady=5, padx=10)
        
        tk.Button(event_frame, text="Create Event", bg="green", fg="white",
                 font=("Arial", 11, "bold"), command=self.create_event_with_confirmation).grid(row=6, column=0, columnspan=2, pady=10)
        
        # Info label
        info_label = tk.Label(admin_frame, text="ℹ️ Students can now create clubs from the 'File' menu or 'Create Club' button.\nAdmins have additional event creation privileges.",
                              font=("Arial", 10), fg="blue", bg="white", justify="left")
        info_label.pack(pady=20, padx=20)
    
    def create_event_with_confirmation(self):
        """Create event with confirmation dialog"""
        club_name = self.event_club.get()
        event_name = self.event_name_entry.get().strip()
        event_date = self.event_date_entry.get().strip()
        event_time = self.event_time_entry.get().strip()
        event_location = self.event_location_entry.get().strip()
        event_desc = self.event_desc_text.get("1.0", tk.END).strip()
        
        if not all([club_name, event_name, event_date, event_time, event_location, event_desc]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        # Find club
        club = None
        for c in self.clubs:
            if c.name == club_name:
                club = c
                break
        
        if not club:
            messagebox.showerror("Error", "Club not found")
            return
        
        # Show confirmation
        confirm_msg = f"Please confirm event details:\n\n"
        confirm_msg += f"Club: {club_name}\n"
        confirm_msg += f"Event: {event_name}\n"
        confirm_msg += f"Date: {event_date}\n"
        confirm_msg += f"Time: {event_time}\n"
        confirm_msg += f"Location: {event_location}\n\n"
        confirm_msg += "Do you want to create this event?"
        
        if messagebox.askyesno("Confirm Event Creation", confirm_msg):
            # Generate event ID
            event_id = f"EVT{len(club.events) + 1:03d}"
            
            # Create event
            new_event = Event(event_id, event_name, event_desc, event_date, 
                             event_time, event_location, club.club_id)
            club.add_event(new_event)
            
            # Save
            DataManager.save_clubs(self.clubs)
            
            messagebox.showinfo("Success", f"Event '{event_name}' created successfully!")
            
            # Clear fields
            self.event_name_entry.delete(0, tk.END)
            self.event_date_entry.delete(0, tk.END)
            self.event_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
            self.event_time_entry.delete(0, tk.END)
            self.event_time_entry.insert(0, "14:00")
            self.event_location_entry.delete(0, tk.END)
            self.event_desc_text.delete("1.0", tk.END)
            
            # Refresh display
            self.refresh_data()
            self.display_clubs()
            self.update_my_clubs()
            self.update_my_created_clubs()
    
    def open_create_club_dialog(self):
        """Open the create club dialog"""
        CreateClubDialog(self, self.user, self.on_club_created)
    
    def on_club_created(self):
        """Callback when a club is created"""
        self.refresh_data()
        self.display_clubs()
        self.update_my_clubs()
        self.update_my_created_clubs()
        messagebox.showinfo("Success", "Club created successfully! You have been added as a member.")
    
    def view_club_events(self, club):
        """View events for a specific club"""
        if not club.events:
            messagebox.showinfo("No Events", f"{club.name} has no upcoming events.")
            return
        
        event_list = "📅 UPCOMING EVENTS\n" + "=" * 30 + "\n\n"
        for i, e in enumerate(club.events, 1):
            event_list += f"{i}. {e.name}\n"
            event_list += f"   Date: {e.date} at {e.time}\n"
            event_list += f"   Location: {e.location}\n"
            event_list += f"   {e.description}\n\n"
        
        messagebox.showinfo(f"{club.name} - Events", event_list)
    
    def logout(self):
        """Logout current user"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.window.destroy()
            LoginWindow()
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Student Club Management System
Version 2.0

Features:
• Students can create and join clubs
• Admins can create clubs and events
• Track club memberships
• View and attend events

Developed as a term project for Python Programming Course
© 2024 All Rights Reserved"""
        
        messagebox.showinfo("About", about_text)


# ==================== MAIN ENTRY POINT ====================

if __name__ == "__main__":
    DataManager.initialize()
    LoginWindow()