# Campus Placement Portal (Flask + SQLite)

A beginner-friendly full-stack starter structure for a **Campus Placement Portal** using:

- Backend: Python Flask
- Frontend: HTML + CSS + JavaScript
- Database: SQLite
- Features: Sign Up/Login + Student Home Job Board (search and filters)
- Recruiter home with job posting form

## Project Structure

```text
Campus_Placement_Portal/
  client/   # Static frontend (HTML/CSS/JS)
  server/   # Flask backend + SQLite database
```

## Prerequisites

- Python 3.10+
- pip

## Setup

### 1) Create and activate virtual environment (recommended)

```bash
cd server
python -m venv .venv
.venv\Scripts\activate
```

### 2) Install backend dependencies

```bash
pip install -r requirements.txt
```

## Run the project

### Start app (backend + frontend from Flask)

```bash
cd server
python app.py
```

Open in browser: `http://127.0.0.1:5000`

Both API and frontend are served by Flask from one app.

Available endpoints:

- `GET /api/health`
- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/jobs`
- `POST /api/jobs`
- `PUT /api/jobs/<id>`
- `DELETE /api/jobs/<id>?recruiter_id=<id>`
- `GET /api/jobs/filters`
- `GET /api/recruiter/jobs?recruiter_id=<id>`
- `GET /api/users`
- `POST /api/users`
- `DELETE /api/users/<id>`

## Environment Variables

Create a `.env` file in `server/` based on `server/.env.example`.

Required variable:

- `PORT`
