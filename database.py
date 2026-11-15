import sqlite3
import hashlib
from datetime import datetime

class Database:
    def __init__(self, db_name="tasks.db"):
        self.db_name = db_name
        self.init_db()

    def connect(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            # جدول المستخدمين
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    full_name TEXT,
                    theme TEXT DEFAULT 'light',
                    language TEXT DEFAULT 'ar',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # جدول المهام
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'pending',
                    due_date TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    # ===== المستخدمين =====
    def create_user(self, username, password, full_name=""):
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password, full_name) VALUES (?, ?, ?)",
                    (username, self.hash_password(password), full_name)
                )
                conn.commit()
                return cursor.lastrowid, True
        except sqlite3.IntegrityError:
            return None, False

    def verify_user(self, username, password):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, self.hash_password(password))
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_user(self, user_id, full_name=None, theme=None, language=None):
        with self.connect() as conn:
            cursor = conn.cursor()
            if full_name is not None:
                cursor.execute("UPDATE users SET full_name = ? WHERE id = ?", (full_name, user_id))
            if theme is not None:
                cursor.execute("UPDATE users SET theme = ? WHERE id = ?", (theme, user_id))
            if language is not None:
                cursor.execute("UPDATE users SET language = ? WHERE id = ?", (language, user_id))
            conn.commit()

    def change_password(self, user_id, old_password, new_password):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE id = ? AND password = ?",
                (user_id, self.hash_password(old_password))
            )
            if not cursor.fetchone():
                return False
            cursor.execute(
                "UPDATE users SET password = ? WHERE id = ?",
                (self.hash_password(new_password), user_id)
            )
            conn.commit()
            return True

    # ===== المهام =====
    def add_task(self, user_id, title, description="", priority="medium", due_date=""):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO tasks (user_id, title, description, priority, due_date)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, title, description, priority, due_date)
            )
            conn.commit()
            return cursor.lastrowid

    def get_tasks(self, user_id, status_filter=None):
        with self.connect() as conn:
            cursor = conn.cursor()
            if status_filter:
                cursor.execute(
                    "SELECT * FROM tasks WHERE user_id = ? AND status = ? ORDER BY id DESC",
                    (user_id, status_filter)
                )
            else:
                cursor.execute(
                    "SELECT * FROM tasks WHERE user_id = ? ORDER BY id DESC",
                    (user_id,)
                )
            return [dict(r) for r in cursor.fetchall()]

    def update_task(self, task_id, title, description, priority, due_date):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE tasks SET title = ?, description = ?, priority = ?, due_date = ?
                   WHERE id = ?""",
                (title, description, priority, due_date, task_id)
            )
            conn.commit()

    def delete_task(self, task_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()

    def toggle_task_status(self, task_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if row:
                new_status = "completed" if row["status"] == "pending" else "pending"
                cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
                conn.commit()
                return new_status
        return None

    def get_stats(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as c FROM tasks WHERE user_id = ?", (user_id,))
            total = cursor.fetchone()["c"]
            cursor.execute("SELECT COUNT(*) as c FROM tasks WHERE user_id = ? AND status='completed'", (user_id,))
            completed = cursor.fetchone()["c"]
            cursor.execute("SELECT COUNT(*) as c FROM tasks WHERE user_id = ? AND status='pending'", (user_id,))
            pending = cursor.fetchone()["c"]
            cursor.execute("SELECT priority, COUNT(*) as c FROM tasks WHERE user_id = ? GROUP BY priority", (user_id,))
            priority_stats = {r["priority"]: r["c"] for r in cursor.fetchall()}
            return {
                "total": total,
                "completed": completed,
                "pending": pending,
                "priority": priority_stats
            }