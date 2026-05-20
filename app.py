from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

# DATABASE CONNECTION

DATABASE = 'tasks.db'


def get_db_connection():

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    return conn


# CREATE TABLE

def create_table():

    conn = get_db_connection()

    conn.execute('''
    CREATE TABLE IF NOT EXISTS tasks (

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        due_date TEXT,
        priority TEXT,
        due_time TEXT,
        status TEXT DEFAULT 'Pending'

    )
    ''')

    conn.commit()
    conn.close()


create_table()

# HOME PAGE

@app.route('/')
def index():

    conn = get_db_connection()

    tasks = conn.execute(
        'SELECT * FROM tasks ORDER BY id DESC'
    ).fetchall()

    conn.close()

    return render_template(
        'index.html',
        tasks=tasks
    )

# ADD TASK

@app.route('/add', methods=['GET', 'POST'])
def add_task():

    if request.method == 'POST':

        title = request.form['title']
        due_date = request.form['due_date']
        due_time = request.form['due_time']
        priority = request.form['priority']

        conn = get_db_connection()

        conn.execute(
            '''
            INSERT INTO tasks
            (title, due_date, priority, due_time, status)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (
                title,
                due_date,
                priority,
                due_time,
                'Pending'
            )
        )

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('add_task.html')

# COMPLETE TASK

@app.route('/complete/<int:id>')
def complete_task(id):

    conn = get_db_connection()

    conn.execute(
        '''
        UPDATE tasks
        SET status = ?
        WHERE id = ?
        ''',
        (
            'Completed',
            id
        )
    )

    conn.commit()
    conn.close()

    return redirect('/')

# DELETE TASK

@app.route('/delete/<int:id>')
def delete_task(id):

    conn = get_db_connection()

    conn.execute(
        'DELETE FROM tasks WHERE id = ?',
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/')

# EDIT TASK

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):

    conn = get_db_connection()

    task = conn.execute(
        'SELECT * FROM tasks WHERE id = ?',
        (id,)
    ).fetchone()

    if request.method == 'POST':

        title = request.form['title']
        due_date = request.form['due_date']
        due_time = request.form['due_time']
        priority = request.form['priority']

        conn.execute(
            '''
            UPDATE tasks
            SET title = ?,
                due_date = ?,
                priority = ?,
                due_time = ?
            WHERE id = ?
            ''',
            (
                title,
                due_date,
                priority,
                due_time,
                id
            )
        )

        conn.commit()
        conn.close()

        return redirect('/')

    conn.close()

    return render_template(
        'edit_task.html',
        task=task
    )

# VERCEL DEPLOYMENT FIX

app = app

# RUN APP

if __name__ == '__main__':

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )
