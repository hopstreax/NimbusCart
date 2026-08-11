# NimbusCart

A simple product-catalog web application built phase-by-phase.

## Architecture (Phase 5)

```
Browser
  ↓  http://127.0.0.1:5000/
Flask Container  (nimbuscart_api:5000)
  ↓  mysql:3306 (Docker Compose Internal Network)
MySQL Container  (nimbuscart_mysql:3306)
  ↓
products table  (Auto-created by Flask on startup)
```

---

## Container Networking Concept

- **API to MySQL**: Inside the Docker network, the `api` container connects to the `mysql` service using `MYSQL_HOST=mysql` and `MYSQL_PORT=3306`.
- **Browser to API**: The browser accesses the Flask application via host port mapping `http://127.0.0.1:5000/` which forwards to container port `5000`.

---

## Phase 5 — Run Locally with Docker Compose

### 1. Configure Environment Variables

Environment variables are managed in `.env` (never committed to git):

```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3307
MYSQL_DATABASE=nimbuscart
MYSQL_USER=nimbususer
MYSQL_PASSWORD=nimbuspass
MYSQL_ROOT_PASSWORD=nimbusrootpass
```

*(Note: Docker Compose overrides `MYSQL_HOST=mysql` and `MYSQL_PORT=3306` inside the container network automatically).*

---

### 2. Build and Start the Stack

Build the Flask API Docker image and start both container services (`api` + `mysql`):

```powershell
docker compose up -d --build
```

---

### 3. Check Running Services

```powershell
docker compose ps
```

Verify that both `nimbuscart_api` and `nimbuscart_mysql` are running and healthy.

---

### 4. Open in Browser

Open `http://127.0.0.1:5000/` in your browser.

- Serves the frontend catalog interface.
- Loads, adds, and updates products against MySQL through the containerized Flask REST API.

---

### 5. Run Verification Test Suites

```powershell
# API test suite
python app\api\test_phase3.py

# Integration test suite
python app\api\test_integration.py
```

---

### 6. Stop the Application

```powershell
# Stop services and containers (preserves database volume):
docker compose down

# Stop services and remove database volume (resets catalog data):
docker compose down -v
```

---

## Project Structure

```
.
├── .env                    ← Local environment configuration (git-ignored)
├── docker-compose.yml      ← Orchestrates Flask API & MySQL services
├── README.md               ← Documentation
└── app/
    ├── frontend/
    │   └── index.html      ← Frontend application UI
    └── api/
        ├── app.py          ← Flask REST API
        ├── Dockerfile      ← Docker build configuration for Flask API
        ├── requirements.txt← Python dependencies
        ├── test_phase3.py  ← API test suite
        └── test_integration.py ← E2E integration test suite
```
