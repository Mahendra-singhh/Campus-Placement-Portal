import os
import sqlite3
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "placement_portal.db")
CLIENT_DIR = os.path.join(os.path.dirname(BASE_DIR), "client")


def get_connection():
    connection = sqlite3.connect(DB_PATH, timeout=15)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute("PRAGMA journal_mode=WAL")
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL CHECK(role IN ('student', 'recruiter', 'admin')),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS auth_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL CHECK(role IN ('student', 'recruiter')),
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS job_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recruiter_id INTEGER,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT NOT NULL,
                job_type TEXT NOT NULL CHECK(job_type IN ('internship', 'full-time')),
                work_mode TEXT NOT NULL CHECK(work_mode IN ('on-site', 'hybrid', 'remote')),
                salary TEXT NOT NULL,
                description TEXT NOT NULL,
                posted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recruiter_id) REFERENCES auth_users(id)
            )
            """
        )
        job_post_columns = cursor.execute("PRAGMA table_info(job_posts)").fetchall()
        if "recruiter_id" not in [column["name"] for column in job_post_columns]:
            cursor.execute("ALTER TABLE job_posts ADD COLUMN recruiter_id INTEGER")
        existing_jobs = cursor.execute("SELECT COUNT(*) AS count FROM job_posts").fetchone()
        if existing_jobs["count"] == 0:
            cursor.executemany(
                """
                INSERT INTO job_posts (title, company, location, job_type, work_mode, salary, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        "Software Engineer Intern",
                        "TechNova",
                        "Bengaluru",
                        "internship",
                        "hybrid",
                        "INR 35,000/month",
                        "Work on backend APIs and test automation for campus projects.",
                    ),
                    (
                        "Graduate Software Engineer",
                        "CloudSprint",
                        "Hyderabad",
                        "full-time",
                        "on-site",
                        "INR 8 LPA",
                        "Build scalable web services and frontend modules in agile squads.",
                    ),
                    (
                        "Data Analyst Trainee",
                        "InsightLoop",
                        "Pune",
                        "internship",
                        "remote",
                        "INR 30,000/month",
                        "Create dashboards and SQL reports for placement performance metrics.",
                    ),
                    (
                        "Frontend Developer",
                        "PixelBridge",
                        "Chennai",
                        "full-time",
                        "hybrid",
                        "INR 7.5 LPA",
                        "Develop responsive interfaces and improve user journeys.",
                    ),
                    (
                        "Backend Developer",
                        "ScaleGrid",
                        "Bengaluru",
                        "full-time",
                        "remote",
                        "INR 9 LPA",
                        "Design APIs, optimize queries, and ensure secure deployments.",
                    ),
                    (
                        "QA Engineer Intern",
                        "QualiCore",
                        "Mumbai",
                        "internship",
                        "on-site",
                        "INR 28,000/month",
                        "Write integration tests and support release quality checks.",
                    ),
                ],
            )


app = Flask(__name__, static_folder=CLIENT_DIR, static_url_path="")
CORS(app)
init_db()


@app.get("/")
def home():
    return app.send_static_file("index.html")

@app.get("/signup")
def signup_page():
    return app.send_static_file("signup.html")


@app.get("/login")
def login_page():
    return app.send_static_file("login.html")


@app.get("/student/home")
def student_home_page():
    return app.send_static_file("student_home.html")


@app.get("/recruiter/home")
def recruiter_home_page():
    return app.send_static_file("recruiter_home.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.get("/api/users")
def list_users():
    with get_connection() as connection:
        users = connection.execute(
            "SELECT id, name, email, role, created_at FROM users ORDER BY id DESC"
        ).fetchall()
    return jsonify([dict(user) for user in users]), 200


@app.post("/api/users")
def create_user():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    role = (payload.get("role") or "student").strip().lower()

    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400

    if role not in {"student", "recruiter", "admin"}:
        return jsonify({"error": "role must be student, recruiter, or admin"}), 400

    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, role) VALUES (?, ?, ?)",
                (name, email, role),
            )
            user_id = cursor.lastrowid
            user = connection.execute(
                "SELECT id, name, email, role, created_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        return jsonify(dict(user)), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "email already exists"}), 409


@app.delete("/api/users/<int:user_id>")
def delete_user(user_id):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        deleted_rows = cursor.rowcount

    if deleted_rows == 0:
        return jsonify({"error": "user not found"}), 404

    return jsonify({"message": "user deleted"}), 200


@app.post("/api/auth/signup")
def signup():
    payload = request.get_json(silent=True) or {}
    role = (payload.get("role") or "").strip().lower()
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if role not in {"student", "recruiter"}:
        return jsonify({"error": "role must be student or recruiter"}), 400

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "password must be at least 6 characters"}), 400

    password_hash = generate_password_hash(password)
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO auth_users (role, email, password_hash) VALUES (?, ?, ?)",
                (role, email, password_hash),
            )
            user_id = cursor.lastrowid
            user = connection.execute(
                "SELECT id, role, email, created_at FROM auth_users WHERE id = ?",
                (user_id,),
            ).fetchone()
        return jsonify(dict(user)), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "email already registered"}), 409


@app.post("/api/auth/login")
def login():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    with get_connection() as connection:
        user = connection.execute(
            "SELECT id, role, email, password_hash FROM auth_users WHERE email = ?",
            (email,),
        ).fetchone()

    if user is None or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "invalid email or password"}), 401

    return (
        jsonify(
            {
                "message": "login successful",
                "user": {
                    "id": user["id"],
                    "role": user["role"],
                    "email": user["email"],
                },
            }
        ),
        200,
    )


@app.get("/api/jobs")
def list_jobs():
    search = (request.args.get("search") or "").strip().lower()
    location = (request.args.get("location") or "").strip()
    job_type = (request.args.get("job_type") or "").strip()
    work_mode = (request.args.get("work_mode") or "").strip()

    query = """
        SELECT id, title, company, location, job_type, work_mode, salary, description, posted_at
        FROM job_posts
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (LOWER(title) LIKE ? OR LOWER(company) LIKE ? OR LOWER(description) LIKE ?)"
        search_like = f"%{search}%"
        params.extend([search_like, search_like, search_like])

    if location:
        query += " AND location = ?"
        params.append(location)

    if job_type:
        query += " AND job_type = ?"
        params.append(job_type)

    if work_mode:
        query += " AND work_mode = ?"
        params.append(work_mode)

    query += " ORDER BY posted_at DESC, id DESC"

    with get_connection() as connection:
        jobs = connection.execute(query, params).fetchall()
    return jsonify([dict(job) for job in jobs]), 200


@app.post("/api/jobs")
def create_job():
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    company = (payload.get("company") or "Confidential").strip()
    location = (payload.get("location") or "Not specified").strip()
    job_type = (payload.get("job_type") or "full-time").strip().lower()
    work_mode = (payload.get("work_mode") or "on-site").strip().lower()
    salary = (payload.get("salary") or "Not disclosed").strip()
    description = (
        payload.get("description") or "Details will be shared during the hiring process."
    ).strip()
    recruiter_id = payload.get("recruiter_id")

    if not title:
        return jsonify({"error": "job title is required"}), 400
    if not recruiter_id:
        return jsonify({"error": "recruiter_id is required"}), 400

    if job_type not in {"internship", "full-time"}:
        return jsonify({"error": "job_type must be internship or full-time"}), 400

    if work_mode not in {"on-site", "hybrid", "remote"}:
        return jsonify({"error": "work_mode must be on-site, hybrid, or remote"}), 400

    with get_connection() as connection:
        recruiter = connection.execute(
            "SELECT id FROM auth_users WHERE id = ? AND role = 'recruiter'",
            (recruiter_id,),
        ).fetchone()
        if recruiter is None:
            return jsonify({"error": "invalid recruiter"}), 400

        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO job_posts (recruiter_id, title, company, location, job_type, work_mode, salary, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                recruiter_id,
                title,
                company,
                location,
                job_type,
                work_mode,
                salary,
                description,
            ),
        )
        job_id = cursor.lastrowid
        job = connection.execute(
            """
            SELECT id, recruiter_id, title, company, location, job_type, work_mode, salary, description, posted_at
            FROM job_posts
            WHERE id = ?
            """,
            (job_id,),
        ).fetchone()

    return jsonify(dict(job)), 201


@app.put("/api/jobs/<int:job_id>")
def update_job(job_id):
    payload = request.get_json(silent=True) or {}
    recruiter_id = payload.get("recruiter_id")
    title = (payload.get("title") or "").strip()
    company = (payload.get("company") or "Confidential").strip()
    location = (payload.get("location") or "Not specified").strip()
    job_type = (payload.get("job_type") or "full-time").strip().lower()
    work_mode = (payload.get("work_mode") or "on-site").strip().lower()
    salary = (payload.get("salary") or "Not disclosed").strip()
    description = (
        payload.get("description") or "Details will be shared during the hiring process."
    ).strip()

    if not recruiter_id:
        return jsonify({"error": "recruiter_id is required"}), 400
    if not title:
        return jsonify({"error": "job title is required"}), 400
    if job_type not in {"internship", "full-time"}:
        return jsonify({"error": "job_type must be internship or full-time"}), 400
    if work_mode not in {"on-site", "hybrid", "remote"}:
        return jsonify({"error": "work_mode must be on-site, hybrid, or remote"}), 400

    with get_connection() as connection:
        existing_job = connection.execute(
            "SELECT id FROM job_posts WHERE id = ? AND recruiter_id = ?",
            (job_id, recruiter_id),
        ).fetchone()
        if existing_job is None:
            return jsonify({"error": "job not found for this recruiter"}), 404

        connection.execute(
            """
            UPDATE job_posts
            SET title = ?, company = ?, location = ?, job_type = ?, work_mode = ?, salary = ?, description = ?
            WHERE id = ? AND recruiter_id = ?
            """,
            (
                title,
                company,
                location,
                job_type,
                work_mode,
                salary,
                description,
                job_id,
                recruiter_id,
            ),
        )
        updated_job = connection.execute(
            """
            SELECT id, recruiter_id, title, company, location, job_type, work_mode, salary, description, posted_at
            FROM job_posts
            WHERE id = ?
            """,
            (job_id,),
        ).fetchone()

    return jsonify(dict(updated_job)), 200


@app.delete("/api/jobs/<int:job_id>")
def delete_job(job_id):
    recruiter_id = request.args.get("recruiter_id")
    if not recruiter_id:
        return jsonify({"error": "recruiter_id is required"}), 400

    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM job_posts WHERE id = ? AND recruiter_id = ?",
            (job_id, recruiter_id),
        )
        deleted_rows = cursor.rowcount

    if deleted_rows == 0:
        return jsonify({"error": "job not found for this recruiter"}), 404

    return jsonify({"message": "job deleted"}), 200


@app.get("/api/recruiter/jobs")
def list_recruiter_jobs():
    recruiter_id = request.args.get("recruiter_id")
    if not recruiter_id:
        return jsonify({"error": "recruiter_id is required"}), 400

    with get_connection() as connection:
        jobs = connection.execute(
            """
            SELECT id, recruiter_id, title, company, location, job_type, work_mode, salary, description, posted_at
            FROM job_posts
            WHERE recruiter_id = ?
            ORDER BY posted_at DESC, id DESC
            """,
            (recruiter_id,),
        ).fetchall()
    return jsonify([dict(job) for job in jobs]), 200


@app.get("/api/jobs/filters")
def job_filters():
    with get_connection() as connection:
        locations = connection.execute(
            "SELECT DISTINCT location FROM job_posts ORDER BY location ASC"
        ).fetchall()
    return (
        jsonify(
            {
                "locations": [item["location"] for item in locations],
                "job_types": ["internship", "full-time"],
                "work_modes": ["on-site", "hybrid", "remote"],
            }
        ),
        200,
    )


@app.get("/<path:asset_path>")
def serve_static_assets(asset_path):
    return send_from_directory(CLIENT_DIR, asset_path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
