# NimbusCart

A simple product-catalog web application built phase-by-phase.

## Architecture

```
Browser
  ↓
Flask API  (python app/api/app.py)
  ↓
MySQL 8.0  (Windows service / Docker)
  ↓
products table
```

---

## Phase 1 — Static Frontend

Single-file HTML/CSS/JS at `app/frontend/index.html`.

To run standalone (with mock data):
```powershell
python -m http.server 8000 --directory .
# Open http://127.0.0.1:8000/app/frontend/index.html
```

---

## Phase 2 — Flask API (in-memory)

Simple Flask REST API, no database.

---

## Phase 3 — Flask API + MySQL

### Prerequisites

- Python 3.x
- MySQL 8.0 running and accessible
- A `nimbuscart` database and `nimbususer` user (see setup below)

---

### 1. MySQL Setup

#### Option A — MySQL already installed on Windows

Run the setup script once (requires root credentials):
```powershell
mysql -u root -p < app\api\setup_mysql.sql
```

Or run manually:
```sql
CREATE DATABASE IF NOT EXISTS nimbuscart CHARACTER SET utf8mb4;
CREATE USER IF NOT EXISTS 'nimbususer'@'localhost' IDENTIFIED BY 'nimbuspass';
GRANT ALL PRIVILEGES ON nimbuscart.* TO 'nimbususer'@'localhost';
FLUSH PRIVILEGES;
```

#### Option B — MySQL via Docker (if Docker is available)

```powershell
docker compose -f app\api\docker-compose.yml up -d
```

---

### 2. Environment Variables

Set these in PowerShell before starting Flask:

```powershell
$env:MYSQL_HOST     = "127.0.0.1"
$env:MYSQL_PORT     = "3306"
$env:MYSQL_DATABASE = "nimbuscart"
$env:MYSQL_USER     = "nimbususer"
$env:MYSQL_PASSWORD = "nimbuspass"
```

Or copy `app/api/.env` and `source` it (requires python-dotenv, not used here).

**Default values** (if env vars are not set) match the docker-compose.yml defaults above, so local dev works without setting anything if using Docker or the same credentials.

---

### 3. Install Python Dependencies

```powershell
pip install -r app\api\requirements.txt
```

Installs: `flask`, `pymysql`

---

### 4. Start Flask

```powershell
python app\api\app.py
```

**What happens on startup:**
1. Reads MySQL config from environment variables (or uses defaults)
2. Connects to MySQL
3. Runs `CREATE TABLE IF NOT EXISTS products (...)` — **automatic, no manual SQL needed**
4. Starts serving on `http://127.0.0.1:5000`

> If MySQL is not running, Flask exits with a clear error message.

---

### 5. API Endpoints

| Method | URL | Description |
|---|---|---|
| GET | `/health` | Health check — always returns `{"status":"ok"}`, even if DB is down |
| GET | `/api/items` | List all products |
| POST | `/api/items` | Create a product |
| GET | `/` | Serves the Phase 1 frontend |

**POST body:**
```json
{ "name": "Laptop", "price": 60000, "stock": 10 }
```

---

### 6. Run Tests

```powershell
# API test suite (Flask must be running)
python app\api\test_phase3.py

# Integration test
python app\api\test_integration.py
```

---

### 7. Database Initialization

The Flask application automatically runs:
```sql
CREATE TABLE IF NOT EXISTS products (
    id    INT           AUTO_INCREMENT PRIMARY KEY,
    name  VARCHAR(255)  NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    stock INT           NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

on every startup. `IF NOT EXISTS` means:
- First run: table is created
- Subsequent runs: existing table (and data) is left untouched

**No manual `CREATE TABLE` is ever needed.**

---

### 8. Data Persistence

Products survive:
- Flask restarts (data is in MySQL, not in Python memory)
- MySQL service restarts (data is on disk)

Products are lost only if:
- The database is dropped: `DROP DATABASE nimbuscart;`
- The Docker volume is deleted: `docker compose down -v`

---

## Project Structure

```
app/
├── frontend/
│   └── index.html              ← Phase 1 static frontend
└── api/
    ├── app.py                  ← Flask application (Phase 3)
    ├── requirements.txt        ← flask + pymysql
    ├── docker-compose.yml      ← MySQL 8.0 via Docker (optional)
    ├── .env                    ← local dev defaults (not committed)
    ├── setup_mysql.sql         ← one-time DB setup script
    ├── test_phase3.py          ← Phase 3 test suite
    └── test_integration.py     ← integration test
```
