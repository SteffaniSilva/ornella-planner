from flask import Flask, render_template, request, redirect, url_for, abort
import sqlite3
import os

app = Flask(__name__)

# Vercel/serverless can write only to /tmp. This also removes old uploaded task history.
if os.environ.get("VERCEL"):
    DATABASE = "/tmp/tasks.db"
else:
    DATABASE = os.path.join(os.path.dirname(__file__), "tasks.db")


def get_db_connection():
    conn = sqlite3.connect(DATABASE, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_db_connection()
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
    conn.commit()
    conn.close()


create_table()


@app.route("/")
def index():
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
    conn.close()

    # Browser reminders use this safe JSON list.
    # They work while the website is open in the browser.
    reminder_tasks = [
        {
            "id": task["id"],
            "title": task["title"],
            "due_date": task["due_date"] or "",
            "due_time": task["due_time"] or "",
            "status": task["status"],
        }
        for task in tasks
        if task["due_date"] and task["due_time"] and task["status"] != "Completed"
    ]

    return render_template("index.html", tasks=tasks, reminder_tasks=reminder_tasks)


@app.route("/add", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        due_date = request.form.get("due_date", "").strip()
        due_time = request.form.get("due_time", "").strip()
        priority = request.form.get("priority", "Low").strip()

        if not title:
            return redirect(url_for("add_task"))

        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO tasks (title, due_date, due_time, priority, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title, due_date, due_time, priority, "Pending"),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("add_task.html")


@app.route("/complete/<int:id>")
def complete_task(id):
    conn = get_db_connection()
    conn.execute("UPDATE tasks SET status = ? WHERE id = ?", ("Completed", id))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/delete/<int:id>")
def delete_task(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_task(id):
    conn = get_db_connection()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()

    if task is None:
        conn.close()
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        due_date = request.form.get("due_date", "").strip()
        due_time = request.form.get("due_time", "").strip()
        priority = request.form.get("priority", "Low").strip()

        if not title:
            conn.close()
            return redirect(url_for("edit_task", id=id))

        conn.execute(
            """
            UPDATE tasks
            SET title = ?, due_date = ?, due_time = ?, priority = ?
            WHERE id = ?
            """,
            (title, due_date, due_time, priority, id),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    conn.close()
    return render_template("edit_task.html", task=task)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
