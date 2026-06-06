from datetime import datetime, time

from flask import Flask, abort, redirect, render_template, request, url_for

import database

app = Flask(__name__)

database.init_db()


def is_task_overdue(task):
    if task["status"] == "Completed" or not task["due_date"]:
        return False

    try:
        if task["due_time"]:
            due_at = datetime.strptime(
                f"{task['due_date']} {task['due_time']}", "%Y-%m-%d %H:%M"
            )
        else:
            due_day = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
            due_at = datetime.combine(due_day, time.max)
    except ValueError:
        return False

    return due_at < datetime.now()


def prepare_task(task):
    task_dict = dict(task)
    task_dict["is_overdue"] = is_task_overdue(task)
    return task_dict


@app.route("/")
def index():
    search = request.args.get("q", "").strip()
    status = request.args.get("status", "All").strip()

    tasks = [prepare_task(task) for task in database.get_all_tasks(search, status)]
    stats = database.get_statistics()

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

    return render_template(
        "index.html",
        tasks=tasks,
        stats=stats,
        reminder_tasks=reminder_tasks,
        search=search,
        selected_status=status if status in {"All", "Pending", "Completed"} else "All",
    )


@app.route("/add", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        title = request.form.get("title", "")
        due_date = request.form.get("due_date", "")
        due_time = request.form.get("due_time", "")
        priority = request.form.get("priority", "Low")

        try:
            database.add_task(title, due_date, due_time, priority)
        except ValueError as error:
            return render_template(
                "add_task.html",
                error=str(error),
                form=request.form,
            )

        return redirect(url_for("index"))

    return render_template("add_task.html", form={})


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    task = database.get_task(task_id)

    if task is None:
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "")
        due_date = request.form.get("due_date", "")
        due_time = request.form.get("due_time", "")
        priority = request.form.get("priority", "Low")

        try:
            database.update_task(task_id, title, due_date, due_time, priority)
        except ValueError as error:
            task_data = dict(task)
            task_data.update(request.form)
            return render_template("edit_task.html", task=task_data, error=str(error))

        return redirect(url_for("index"))

    return render_template("edit_task.html", task=task)


@app.route("/complete/<int:task_id>", methods=["POST", "GET"])
def complete_task(task_id):
    database.mark_completed(task_id)
    return redirect(url_for("index"))


@app.route("/pending/<int:task_id>", methods=["POST", "GET"])
def pending_task(task_id):
    database.mark_pending(task_id)
    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>", methods=["POST", "GET"])
def delete_task(task_id):
    database.delete_task(task_id)
    return redirect(url_for("index"))


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
