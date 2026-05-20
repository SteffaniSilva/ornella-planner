import sqlite3


class TodoDatabase:

    def __init__(self):

        self.connection = sqlite3.connect(
            'tasks.db',
            check_same_thread=False
        )

        self.cursor = self.connection.cursor()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT,
            description TEXT,
            priority TEXT,
            due_date TEXT,
            due_time TEXT,

            status TEXT DEFAULT 'Pending'
        )
        """)

        self.connection.commit()

    # GET ALL TASKS
    def get_all_tasks(self):

        self.cursor.execute("""
        SELECT * FROM tasks
        ORDER BY id DESC
        """)

        return self.cursor.fetchall()

    # ADD TASK
    def add_task(
        self,
        title,
        description,
        priority,
        due_date,
        due_time
    ):

        self.cursor.execute("""
        INSERT INTO tasks (

            title,
            description,
            priority,
            due_date,
            due_time

        )

        VALUES (?, ?, ?, ?, ?)
        """, (

            title,
            description,
            priority,
            due_date,
            due_time

        ))

        self.connection.commit()

    # COMPLETE TASK
    def mark_completed(self, task_id):

        self.cursor.execute("""
        UPDATE tasks
        SET status='Completed'
        WHERE id=?
        """, (task_id,))

        self.connection.commit()

    # DELETE TASK
    def delete_task(self, task_id):

        self.cursor.execute("""
        DELETE FROM tasks
        WHERE id=?
        """, (task_id,))

        self.connection.commit()

    # SEARCH TASKS
    def search_tasks(self, keyword):

        self.cursor.execute("""
        SELECT * FROM tasks

        WHERE title LIKE ?
        OR description LIKE ?
        """, (

            f'%{keyword}%',
            f'%{keyword}%'

        ))

        return self.cursor.fetchall()

    # GET STATISTICS
    def get_statistics(self):

        stats = {}

        # TOTAL TASKS
        self.cursor.execute("""
        SELECT COUNT(*) FROM tasks
        """)

        stats['total'] = self.cursor.fetchone()[0]

        # COMPLETED TASKS
        self.cursor.execute("""
        SELECT COUNT(*) FROM tasks
        WHERE status='Completed'
        """)

        stats['completed'] = self.cursor.fetchone()[0]

        # PENDING TASKS
        self.cursor.execute("""
        SELECT COUNT(*) FROM tasks
        WHERE status='Pending'
        """)

        stats['pending'] = self.cursor.fetchone()[0]

        # HIGH PRIORITY TASKS
        self.cursor.execute("""
        SELECT COUNT(*) FROM tasks
        WHERE priority='High'
        """)

        stats['high_priority'] = self.cursor.fetchone()[0]

        return stats

    # GET TASK BY ID
    def get_task_by_id(self, task_id):

        self.cursor.execute("""
        SELECT * FROM tasks
        WHERE id=?
        """, (task_id,))

        return self.cursor.fetchone()

    # UPDATE TASK
    def update_task(
        self,
        task_id,
        title,
        description,
        priority,
        due_date,
        due_time
    ):

        self.cursor.execute("""
        UPDATE tasks

        SET
            title=?,
            description=?,
            priority=?,
            due_date=?,
            due_time=?

        WHERE id=?
        """, (

            title,
            description,
            priority,
            due_date,
            due_time,
            task_id

        ))

        self.connection.commit()