# NimbusCart

A simple product-catalog web application built phase-by-phase.

## Architecture

```
Browser
  ↓
Flask API  (python app/api/app.py)  [Host Machine]
  ↓
MySQL 8.0  (Docker Container: nimbuscart_mysql)
  ↓
products table  (Auto-created by Flask at startup)
```

---

## Phase 1 — Static Frontend

Single-file HTML/CSS/JS at `app/frontend/index.html`.

---

## Phase 2 — Flask API (in-memory)

Simple Flask REST API, no database.

---

## Phase 3 — Flask API + Docker MySQL

### 1. MySQL Docker Setup

Start the local MySQL database using Docker Compose:

```powershell
docker compose up -d
```

- MySQL 8.0 runs inside a Docker container (`nimbuscart_mysql`)
- Listens on host port `3307` mapped to container port `3306` (preserving host services)
- Data persists in the `mysql_data` Docker volume

---

### 2. Environment Variables

Environment variables are defined in `.env`:

```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3307
MYSQL_DATABASE=nimbuscart
MYSQL_USER=nimbususer
MYSQL_PASSWORD=nimbuspass
MYSQL_ROOT_PASSWORD=nimbusrootpass
```

You can also export them in PowerShell if needed:

```powershell
$env:MYSQL_HOST     = "127.0.0.1"
$env:MYSQL_PORT     = "3307"
$env:MYSQL_DATABASE = "nimbuscart"
$env:MYSQL_USER     = "nimbususer"
$env:MYSQL_PASSWORD = "nimbuspass"
```

---

### 3. Install Dependencies & Start Flask

```powershell
pip install -r app\api\requirements.txt
python app\api\app.py
```

**What happens on startup:**
1. Connects to MySQL container at `127.0.0.1:3307`
2. Runs `CREATE TABLE IF NOT EXISTS products (...)` automatically
3. Serves the application on `http://127.0.0.1:5000`

---

### 4. API Endpoints

| Method | URL | Description |
|---|---|---|
| GET | `/health` | Health check — returns `{"status":"ok"}`, even if DB is offline |
| GET | `/api/items` | List all products from MySQL |
| POST | `/api/items` | Insert product into MySQL |
| GET | `/` | Serves the frontend (`app/frontend/index.html`) |

---

### 5. Verification & Tests

```powershell
# Phase 3 API test suite
python app\api\test_phase3.py

# Frontend + API integration test
python app\api\test_integration.py
```

---

## Project Structure

```
.
├── .env                    ← Local dev environment variables
├── docker-compose.yml      ← MySQL 8.0 Docker configuration
├── README.md               ← Documentation
└── app/
    ├── frontend/
    │   └── index.html      ← Phase 1/3 frontend
    └── api/
        ├── app.py          ← Flask REST API (Phase 3)
        ├── requirements.txt← Python dependencies (flask, pymysql)
        ├── test_phase3.py  ← Phase 3 test suite
        └── test_integration.py ← Integration test suite
```
