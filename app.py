from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "charan_secret_key"


def init_db():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        task TEXT,
        priority TEXT,
        due_date TEXT,
        completed INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


init_db()


@app.route("/")
def home():
    return redirect("/login")


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        try:

            cur.execute(
                """
                INSERT INTO users(username,password)
                VALUES(?,?)
                """,
                (username, hashed_password)
            )

            conn.commit()

        except:
            return "Username already exists"

        conn.close()

        return redirect("/login")

    return render_template("register.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
            """
            SELECT * FROM users
            WHERE username=?
            """,
            (username,)
        )

        user = cur.fetchone()

        conn.close()

        if user and check_password_hash(user[2], password):

            session["user_id"] = user[0]
            session["username"] = user[1]

            return redirect("/dashboard")

        return "Invalid Username or Password"

    return render_template("login.html")


# DASHBOARD
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        """
        SELECT *
        FROM tasks
        WHERE user_id=?
        """,
        (session["user_id"],)
    )

    tasks = cur.fetchall()

    cur.execute(
        """
        SELECT COUNT(*)
        FROM tasks
        WHERE user_id=?
        """,
        (session["user_id"],)
    )

    total_tasks = cur.fetchone()[0]

    cur.execute(
        """
        SELECT COUNT(*)
        FROM tasks
        WHERE user_id=?
        AND completed=1
        """,
        (session["user_id"],)
    )

    completed_tasks = cur.fetchone()[0]

    cur.execute(
        """
        SELECT COUNT(*)
        FROM tasks
        WHERE user_id=?
        AND completed=0
        """,
        (session["user_id"],)
    )

    pending_tasks = cur.fetchone()[0]

    if total_tasks > 0:
        progress = int(
            (completed_tasks / total_tasks) * 100
        )
    else:
        progress = 0

    conn.close()

    return render_template(
        "dashboard.html",
        username=session["username"],
        tasks=tasks,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        progress=progress
    )


# ADD TASK
@app.route("/add", methods=["POST"])
def add_task():

    task = request.form["task"]
    priority = request.form["priority"]
    due_date = request.form["due_date"]

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO tasks(
        user_id,
        task,
        priority,
        due_date
        )
        VALUES(?,?,?,?)
        """,
        (
            session["user_id"],
            task,
            priority,
            due_date
        )
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# COMPLETE
@app.route("/complete/<int:id>")
def complete_task(id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE tasks
        SET completed=1
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# DELETE
@app.route("/delete/<int:id>")
def delete_task(id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM tasks
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# LOGOUT
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)