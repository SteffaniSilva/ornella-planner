import sqlite3
import os

if os.environ.get("VERCEL"):
    DATABASE = "/tmp/tasks.db"
else:
    DATABASE = os.path.join(os.path.dirname(__file__), "tasks.db")


class TodoDatabase:
    def __init__(self):
        self.connection = sqlite3.connect(DATABASE, timeout=10, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                due_date TEXT,
                due_time TEXT,
                priority TEXT NOT NULL DEFAULT 'Low',
                status TEXT NOT NULL DEFAULT 'Pending'
            )
            """
        )
        self.connection.commit()

    def get_all_tasks(self):
        self.cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
        return self.cursor.fetchall()

    def add_task(self, title, priority, due_date, due_time):
        self.cursor.execute(
            """
            INSERT INTO tasks (title, due_date, due_time, priority, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title, due_date, due_time, priority, "Pending"),
        )
        self.connection.commit()

    def mark_completed(self, task_id):
        self.cursor.execute("UPDATE tasks SET status='Completed' WHERE id=?", (task_id,))
        self.connection.commit()

    def delete_task(self, task_id):
        self.cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        self.connection.commit()

    def get_task_by_id(self, task_id):
        self.cursor.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
        return self.cursor.fetchone()

    def update_task(self, task_id, title, priority, due_date, due_time):
        self.cursor.execute(
            """
            UPDATE tasks
            SET title=?, due_date=?, due_time=?, priority=?
            WHERE id=?
            """,
            (title, due_date, due_time, priority, task_id),
        )
        self.connection.commit()

    def get_statistics(self):
        stats = {}
        self.cursor.execute("SELECT COUNT(*) FROM tasks")
        stats["total"] = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE status='Completed'")
        stats["completed"] = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE status='Pending'")
        stats["pending"] = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE priority='High'")
        stats["high_priority"] = self.cursor.fetchone()[0]
        return stats
