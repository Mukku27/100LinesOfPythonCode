import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import sqlite3
import speech_recognition as sr
import pyttsx3

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced To-Do List")
        self.root.geometry("900x600")

        # Initialize attributes
        self.is_dark_theme = True  # Start with dark theme
        self.engine = pyttsx3.init()  # Initialize text-to-speech engine

        # Create main frame and sidebar frame
        self.main_frame = tk.Frame(self.root, bg="#2E2E2E")
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.sidebar_frame = tk.Frame(self.root, width=200, bg="#3A3A3A")
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.create_widgets()
        self.create_database()
        self.apply_theme()  # Apply theme after frames are created
        self.create_sidebar()
        self.load_tasks()

    def create_sidebar(self):
        """Create the sidebar with navigation options."""
        tk.Label(self.sidebar_frame, text="Menu", font=("Helvetica", 16), bg="#3A3A3A", fg="#FFFFFF").pack(pady=10)

        # Create the "View All Tasks" button
        self.view_all_button = tk.Button(
            self.sidebar_frame, 
            text="View All Tasks", 
            command=self.load_tasks, 
            bg="#5A5A5A", 
            fg="#FFFFFF", 
            relief="flat"
        )
        self.view_all_button.pack(pady=5, padx=10, fill=tk.X)

        # Create other buttons like "View Completed Tasks", "View Pending Tasks", etc.
        self.view_completed_button = tk.Button(
            self.sidebar_frame, 
            text="View Completed Tasks", 
            command=self.load_completed_tasks, 
            bg="#5A5A5A", 
            fg="#FFFFFF", 
            relief="flat"
        )
        self.view_completed_button.pack(pady=5, padx=10, fill=tk.X)

        self.view_pending_button = tk.Button(
            self.sidebar_frame, 
            text="View Pending Tasks", 
            command=self.load_pending_tasks, 
            bg="#5A5A5A", 
            fg="#FFFFFF", 
            relief="flat"
        )
        self.view_pending_button.pack(pady=5, padx=10, fill=tk.X)

        # Search entry and label
        tk.Label(self.sidebar_frame, text="Search:", bg="#3A3A3A", fg="#FFFFFF").pack(pady=5)
        self.search_entry = tk.Entry(self.sidebar_frame, bg="#4B4B4B", fg="#FFFFFF", relief="flat")
        self.search_entry.pack(pady=5, padx=10, fill=tk.X)
        self.search_entry.bind('<KeyRelease>', self.search_tasks)

        # Toggle theme button
        self.theme_button = tk.Button(
            self.sidebar_frame, 
            text="Toggle Theme", 
            command=self.toggle_theme, 
            bg="#5A5A5A", 
            fg="#FFFFFF", 
            relief="flat"
        )
        self.theme_button.pack(pady=5, padx=10, fill=tk.X)

        # Voice command button
        self.voice_command_button = tk.Button(
            self.sidebar_frame, 
            text="Voice Command", 
            command=self.voice_command, 
            bg="#5A5A5A", 
            fg="#FFFFFF", 
            relief="flat"
        )
        self.voice_command_button.pack(pady=5, padx=10, fill=tk.X)

    def apply_theme(self):
        """Apply the current theme to the application."""
        if self.is_dark_theme:
            bg_color = "#2E2E2E"
            fg_color = "#FFFFFF"
            button_bg = "#5A5A5A"
            entry_bg = "#4B4B4B"
        else:
            bg_color = "#F0F0F0"
            fg_color = "#000000"
            button_bg = "#D0D0D0"
            entry_bg = "#FFFFFF"
        
        self.root.configure(bg=bg_color)
        self.main_frame.configure(bg=bg_color)
        self.sidebar_frame.configure(bg="#3A3A3A" if self.is_dark_theme else "#F0F0F0")

        # Update the colors of sidebar elements
        for widget in self.sidebar_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(bg=button_bg, fg=fg_color)
            elif isinstance(widget, tk.Entry):
                widget.configure(bg=entry_bg, fg=fg_color)

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.is_dark_theme = not self.is_dark_theme
        self.apply_theme()

    def create_database(self):
        """Create the tasks table if it doesn't exist."""
        self.conn = sqlite3.connect("tasks.db")
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    task TEXT NOT NULL,
                    category TEXT,
                    due_date TEXT,
                    priority TEXT,
                    completed INTEGER DEFAULT 0
                )
            """)

    def create_widgets(self):
        """Create the main content area widgets."""
        frame = tk.Frame(self.main_frame, bg="#2E2E2E" if self.is_dark_theme else "#FFFFFF", padx=10, pady=10)
        frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        # Task entry
        tk.Label(frame, text="Task:", font=("Helvetica", 12), bg=frame["bg"], fg="#FFFFFF" if self.is_dark_theme else "#000000").grid(row=0, column=0, sticky="w", pady=5)
        self.task_entry = tk.Entry(frame, width=50, bg="#4B4B4B", fg="#FFFFFF", relief="flat")
        self.task_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Category entry
        tk.Label(frame, text="Category:", font=("Helvetica", 12), bg=frame["bg"], fg="#FFFFFF" if self.is_dark_theme else "#000000").grid(row=1, column=0, sticky="w", pady=5)
        self.category_entry = tk.Entry(frame, width=50, bg="#4B4B4B", fg="#FFFFFF", relief="flat")
        self.category_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Due date entry
        tk.Label(frame, text="Due Date:", font=("Helvetica", 12), bg=frame["bg"], fg="#FFFFFF" if self.is_dark_theme else "#000000").grid(row=2, column=0, sticky="w", pady=5)
        self.due_date_entry = DateEntry(frame, width=20, date_pattern='yyyy-mm-dd', background='#4B4B4B', foreground='white', relief="flat")
        self.due_date_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Priority menu
        tk.Label(frame, text="Priority:", font=("Helvetica", 12), bg=frame["bg"], fg="#FFFFFF" if self.is_dark_theme else "#000000").grid(row=3, column=0, sticky="w", pady=5)
        self.priority_var = tk.StringVar(value="Medium")
        self.priority_menu = ttk.Combobox(frame, textvariable=self.priority_var, values=["High", "Medium", "Low"], state="readonly")
        self.priority_menu.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # Add task button
        self.add_task_button = tk.Button(frame, text="Add Task", command=self.add_task, bg="#5A5A5A", fg="#FFFFFF", relief="flat")
        self.add_task_button.grid(row=4, column=1, sticky="e", pady=10)

        # Listbox for tasks
        self.task_listbox = tk.Listbox(self.main_frame, font=("Helvetica", 10), bg="#2E2E2E", fg="#FFFFFF", height=15, relief="flat")
        self.task_listbox.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

    def load_tasks(self):
        """Load all tasks from the database."""
        self.task_listbox.delete(0, tk.END)
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE completed=0")
        for row in cursor.fetchall():
            self.task_listbox.insert(tk.END, f"{row[1]} | {row[2]} | Due: {row[3]} | Priority: {row[4]}")

    def load_completed_tasks(self):
        """Load completed tasks."""
        self.task_listbox.delete(0, tk.END)
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE completed=1")
        for row in cursor.fetchall():
            self.task_listbox.insert(tk.END, f"{row[1]} | {row[2]} | Due: {row[3]} | Priority: {row[4]}")

    def load_pending_tasks(self):
        """Load pending tasks."""
        self.load_tasks()

    def add_task(self):
        """Add a new task."""
        task = self.task_entry.get()
        category = self.category_entry.get()
        due_date = self.due_date_entry.get()
        priority = self.priority_var.get()

        if task and category and due_date:
            with self.conn:
                self.conn.execute("INSERT INTO tasks (task, category, due_date, priority) VALUES (?, ?, ?, ?)", 
                                  (task, category, due_date, priority))
            self.load_tasks()
            self.task_entry.delete(0, tk.END)
            self.category_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Please fill all fields.")

    def voice_command(self):
        """Add a task using voice command."""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.engine.say("Please say the task details.")
            self.engine.runAndWait()
            print("Listening...")
            audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio)
            print("You said:", command)  # Debug print

        # Example command: "Add grocery shopping to errands due tomorrow with high priority"
            parts = command.split(" ")
        
        # Improved parsing logic
            if "add" in parts:
                task_start = parts.index("add") + 1
                task_end = parts.index("to")
                task = " ".join(parts[task_start:task_end])
            
                category_start = task_end + 1
                category_end = parts.index("due")
                category = " ".join(parts[category_start:category_end])
            
                due_date = parts[parts.index("due") + 1]  # Assuming just a simple due date
                priority = parts[parts.index("with") + 1]  # Assuming just a simple priority
            
            # Print parsed components for debugging
                print(f"Task: {task}, Category: {category}, Due Date: {due_date}, Priority: {priority}")

                self.task_entry.delete(0, tk.END)
                self.category_entry.delete(0, tk.END)
                self.task_entry.insert(0, task)
                self.category_entry.insert(0, category)
                self.due_date_entry.set_date(due_date)
                self.priority_var.set(priority)
    
                self.add_task()  # Add the task to the database

                self.engine.say("Task added successfully.")
                self.engine.runAndWait()
    
            else:
                messagebox.showerror("Voice Error", "Please say the command to add a task.")
    
        except sr.UnknownValueError:
            messagebox.showerror("Voice Error", "Could not understand audio. Please try again.")
        except sr.RequestError as e:
            messagebox.showerror("Voice Error", f"Could not request results from Google Speech Recognition service; {e}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def search_tasks(self, event):
        """Search tasks based on input."""
        query = self.search_entry.get().lower()
        self.task_listbox.delete(0, tk.END)
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE completed=0")
        for row in cursor.fetchall():
            task_str = f"{row[1]} | {row[2]} | Due: {row[3]} | Priority: {row[4]}"
            if query in task_str.lower():
                self.task_listbox.insert(tk.END, task_str)

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()