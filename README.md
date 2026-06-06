# Ornella Planner

A soft, aesthetic daily planner web application built with Flask, SQLite, HTML, CSS, Bootstrap, and JavaScript.

🔗 **Live Website:** https://ornella-planner-98cp.vercel.app/

## Fixed Features

- Add new tasks
- Edit tasks
- Delete tasks
- Mark tasks as completed
- Undo completed tasks
- View due dates and due times on the home page
- Search tasks by title
- Filter tasks by All, Pending, or Completed
- Show task statistics
- Highlight overdue pending tasks
- Browser reminders for tasks that have both due date and due time
- Responsive desktop and mobile layouts
- Cleaner Flask routes using `url_for`
- Safer database handling to reduce SQLite locking issues
- Reduced `requirements.txt` to only the packages the app needs

## How to run locally

```bash
pip install -r requirements.txt
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Project structure

```text
ornella-planner-main/
├── app.py
├── database.py
├── requirements.txt
├── vercel.json
├── static/
│   ├── style.css
│   ├── reminders.js
│   └── images/
│       └── planner.jpg
└── templates/
    ├── index.html
    ├── add_task.html
    ├── edit_task.html
    └── 404.html
```

## Note about reminders

Browser reminders work only while the website is open in the browser. The user must allow notification permission.
