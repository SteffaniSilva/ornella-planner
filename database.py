import os
import sqlite3
from contextlib import contextmanager

# Vercel/serverless can write only inside /tmp.
# For local development, the database is created inside the project folder.
if os.environ.get("VERCEL"):
    DATABASE = "/tmp/tasks.db"
else:
    DATABASE = os.path.join(os.path.dirname(__file__), "tasks.db")

VALID_PRIORITIES = {"Low", "Medium", "High"}
VALID_STATUSES = {"Pending", "Completed"}


def normalise_priority(priority):
    priority = (priority or "Low").strip().title()
    return priority if priority in VALID_PRIORITIES else "Low"


def normalise_status(status):
    status = (status or "Pending").strip().title()
    return status if status in VALID_STATUSES else "Pending"


@contextmanager
def get_connection():
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.execute(
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

        # Small migration support for older versions of the project.
        existing_columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(tasks)").fetchall()
        }

        migrations = {
            "due_date": "ALTER TABLE tasks ADD COLUMN due_date TEXT",
            "due_time": "ALTER TABLE tasks ADD COLUMN due_time TEXT",
            "priority": "ALTER TABLE tasks ADD COLUMN priority TEXT NOT NULL DEFAULT 'Low'",
            "status": "ALTER TABLE tasks ADD COLUMN status TEXT NOT NULL DEFAULT 'Pending'",
        }

        for column, statement in migrations.items():
            if column not in existing_columns:
                conn.execute(statement)


def get_all_tasks(search="", status="All"):
    search = (search or "").strip()
    status = (status or "All").strip().title()

    query = "SELECT * FROM tasks"
    conditions = []
    params = []

    if search:
        conditions.append("title LIKE ?")
        params.append(f"%{search}%")

    if status in VALID_STATUSES:
        conditions.append("status = ?")
        params.append(status)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += """
        ORDER BY
            CASE WHEN status = 'Pending' THEN 0 ELSE 1 END,
            CASE WHEN due_date IS NULL OR due_date = '' THEN 1 ELSE 0 END,
            due_date ASC,
            CASE WHEN due_time IS NULL OR due_time = '' THEN 1 ELSE 0 END,
            due_time ASC,
            id DESC
    """

    with get_connection() as conn:
        return conn.execute(query, params).fetchall()


def get_task(task_id):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()


def add_task(title, due_date="", due_time="", priority="Low"):
    title = (title or "").strip()
    due_date = (due_date or "").strip()
    due_time = (due_time or "").strip()
    priority = normalise_priority(priority)

    if not title:
        raise ValueError("Task title is required.")

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO tasks (title, due_date, due_time, priority, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title, due_date, due_time, priority, "Pending"),
        )


def update_task(task_id, title, due_date="", due_time="", priority="Low"):
    title = (title or "").strip()
    due_date = (due_date or "").strip()
    due_time = (due_time or "").strip()
    priority = normalise_priority(priority)

    if not title:
        raise ValueError("Task title is required.")

    with get_connection() as conn:
        conn.execute(
            """
            UPDATE tasks
            SET title = ?, due_date = ?, due_time = ?, priority = ?
            WHERE id = ?
            """,
            (title, due_date, due_time, priority, task_id),
        )


def mark_completed(task_id):
    with get_connection() as conn:
        conn.execute("UPDATE tasks SET status = 'Completed' WHERE id = ?", (task_id,))


def mark_pending(task_id):
    with get_connection() as conn:
        conn.execute("UPDATE tasks SET status = 'Pending' WHERE id = ?", (task_id,))


def delete_task(task_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))


def get_statistics():
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) AS completed,
                SUM(CASE WHEN priority = 'High' AND status = 'Pending' THEN 1 ELSE 0 END) AS high_priority
            FROM tasks
            """
        ).fetchone()

    return {
        "total": row["total"] or 0,
        "pending": row["pending"] or 0,
        "completed": row["completed"] or 0,
        "high_priority": row["high_priority"] or 0,
    }
