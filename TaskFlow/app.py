from flask import Flask, render_template, request, jsonify, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

DB = "taskflow.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# -------- HOME --------
@app.route("/")
def home():
    return render_template("home.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            return redirect("/dashboard")
        else:
            return "Invalid Credentials"

    return render_template("login.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# -------- DASHBOARD --------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        session["user_id"] = 1  # temporary login for testing
        session["user_name"] = "Test User"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE user_id=?", (session["user_id"],))
    projects = cursor.fetchall()
    conn.close()
    return render_template(
        "dashboard.html",
        name=session["user_name"],
        projects=projects
    )


# -------- CREATE PROJECT --------
@app.route("/create-project", methods=["GET", "POST"])
def create_project():
    if "user_id" not in session:
        return redirect("/")

    if request.method == "POST":
        title = request.form["title"]
        deadline = request.form["deadline"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO projects (user_id, title, deadline) VALUES (?, ?, ?)",
            (session["user_id"], title, deadline)
        )
        conn.commit()
        conn.close()

        return redirect("/dashboard")

    

# -------- BOARD --------
@app.route("/board/<int:project_id>")
def board(project_id):
    return render_template("board.html", project_id=project_id)



# -------- GET TASKS --------
@app.route("/get-tasks/<int:project_id>")
def get_tasks(project_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE project_id=?", (project_id,))
    tasks = c.fetchall()
    conn.close()
    return jsonify([
    {
        "id": t["id"],
        "title": t["title"],
        "status": t["status"],
        "completed": t["completed"]
    }
    for t in tasks
])

# -------- ADD TASK --------
@app.route("/add-task", methods=["POST"])
def add_task():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO tasks (title,status,project_id) VALUES (?,?,?)",
              (data["title"], data["status"], data["project_id"]))
    conn.commit()
    conn.close()
    return jsonify(success=True)

# -------- UPDATE TASK --------
@app.route("/update-task", methods=["POST"])
def update_task():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE tasks SET title=? WHERE id=?", (data["title"], data["id"]))
    conn.commit()
    conn.close()
    return jsonify(success=True)

# -------- UPDATE STATUS (Drag & Drop) --------
@app.route("/update-status", methods=["POST"])
def update_status():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE tasks SET status=? WHERE id=?", (data["status"], data["id"]))
    conn.commit()
    conn.close()
    return jsonify(success=True)

# -------- DELETE TASK --------
@app.route("/delete-task", methods=["POST"])
def delete_task():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=?", (data["id"],))
    conn.commit()
    conn.close()
    return jsonify(success=True)

@app.route("/toggle-complete", methods=["POST"])
def toggle_complete():
    data = request.json
    conn = get_db()
    c = conn.cursor()

    c.execute(
        "UPDATE tasks SET completed=? WHERE id=?",
        (data["completed"], data["id"])
    )

    conn.commit()
    conn.close()
    return jsonify(success=True)

@app.route("/add-member", methods=["POST"])
def add_member():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO project_members (project_id, user_email, role)
        VALUES (?, ?, ?)
    """, (data["project_id"], data["email"], data["role"]))
    conn.commit()
    conn.close()
    return jsonify(success=True)

@app.route("/get-members/<int:project_id>")
def get_members(project_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM project_members WHERE project_id=?", (project_id,))
    members = c.fetchall()
    conn.close()
    return jsonify([
        {"id": m["id"], "email": m["user_email"], "role": m["role"]}
        for m in members
    ])

@app.route("/remove-member", methods=["POST"])
def remove_member():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM project_members WHERE id=?", (data["id"],))
    conn.commit()
    conn.close()
    return jsonify(success=True)


@app.route("/project-progress/<int:project_id>")
def project_progress(project_id):
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM tasks WHERE project_id=?", (project_id,))
    total = c.fetchone()[0]

    c.execute("""
        SELECT COUNT(*) FROM tasks
        WHERE project_id=? AND completed=1
    """, (project_id,))
    done = c.fetchone()[0]

    conn.close()

    percent = int((done / total) * 100) if total > 0 else 0
    return jsonify(percent=percent)




if __name__ == "__main__":
    app.run(debug=True)
