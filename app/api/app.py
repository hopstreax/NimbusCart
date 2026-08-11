"""
NimbusCart — Phase 3 Flask API with MySQL
==========================================
Replaces the Phase 2 in-memory list with a real MySQL database.

Architecture:
    Browser  →  Flask (python app.py)  →  MySQL (Docker container)

The API endpoints and JSON shapes are IDENTICAL to Phase 2.
Only the storage layer has changed.

Startup sequence:
    1. Read DB config from environment variables
    2. Connect to MySQL
    3. CREATE TABLE IF NOT EXISTS products  ← auto-init, never manual
    4. Serve requests

Run:
    # Set environment variables first (see .env or README.md), then:
    python app.py

Endpoints (unchanged from Phase 2):
    GET  /health      → { "status": "ok" }  (works even if DB is down)
    GET  /api/items   → [ { id, name, price, stock }, ... ]
    POST /api/items   → { id, name, price, stock }   HTTP 201
    GET  /            → serves app/frontend/index.html
"""

import os
import pymysql
import pymysql.cursors
from flask import Flask, request, jsonify, send_from_directory

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

app = Flask(__name__, static_folder=None)


# ---------------------------------------------------------------------------
# Database configuration  (read from environment variables)
# ---------------------------------------------------------------------------
# Set these before starting Flask. Example (PowerShell):
#   $env:MYSQL_HOST     = "127.0.0.1"
#   $env:MYSQL_PORT     = "3306"
#   $env:MYSQL_DATABASE = "nimbuscart"
#   $env:MYSQL_USER     = "nimbususer"
#   $env:MYSQL_PASSWORD = "nimbuspass"
#
# Defaults point to the local Docker Compose setup defined in docker-compose.yml.

DB_CONFIG = {
    "host":     os.environ.get("MYSQL_HOST",     "127.0.0.1"),
    "port":     int(os.environ.get("MYSQL_PORT", "3306")),
    "database": os.environ.get("MYSQL_DATABASE", "nimbuscart"),
    "user":     os.environ.get("MYSQL_USER",     "nimbususer"),
    "password": os.environ.get("MYSQL_PASSWORD", "nimbuspass"),
    "charset": "utf8mb4",
    # Return rows as dicts ({"id": 1, "name": "Laptop", ...}) instead of tuples
    "cursorclass": pymysql.cursors.DictCursor,
    # Automatically convert MySQL DECIMAL columns to Python float
    "conv": {**pymysql.converters.conversions,
             pymysql.converters.FIELD_TYPE.DECIMAL: float,
             pymysql.converters.FIELD_TYPE.NEWDECIMAL: float},
}


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db_connection():
    """
    Open and return a fresh PyMySQL connection using DB_CONFIG.

    A new connection is opened for every request and closed when done.
    This avoids stale connections from a single long-lived global connection.

    Raises pymysql.Error if MySQL is unavailable.
    """
    return pymysql.connect(**DB_CONFIG)


def initialize_database():
    """
    Create the products table if it does not already exist.

    Called ONCE at startup before Flask begins serving requests.
    Safe to call repeatedly — IF NOT EXISTS prevents data loss on restart.

    Table schema:
        id    INT AUTO_INCREMENT PRIMARY KEY
        name  VARCHAR(255) NOT NULL
        price DECIMAL(12,2) NOT NULL      ← stores monetary values precisely
        stock INT NOT NULL
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id    INT          AUTO_INCREMENT PRIMARY KEY,
                    name  VARCHAR(255) NOT NULL,
                    price DECIMAL(12,2) NOT NULL,
                    stock INT          NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
        conn.commit()
        print("[DB] products table ready (created or already existed).")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Serve Phase 1 frontend  (same-origin trick — no CORS needed)
# ---------------------------------------------------------------------------

@app.route("/")
def serve_frontend():
    """Serve index.html so fetch('/api/items') stays on the same origin."""
    return send_from_directory(FRONTEND_DIR, "index.html")


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    """
    Liveness check. Returns 200 as long as Flask is running.
    Intentionally does NOT touch MySQL — works even when the DB is down.
    """
    return jsonify({"status": "ok"}), 200


# ---------------------------------------------------------------------------
# GET /api/items
# ---------------------------------------------------------------------------

@app.route("/api/items", methods=["GET"])
def get_items():
    """
    Fetch all products from MySQL and return them as a JSON array.
    Returns [] with HTTP 200 if the table is empty.
    Returns HTTP 503 if MySQL is unreachable.
    """
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, name, price, stock FROM products ORDER BY id"
                )
                rows = cursor.fetchall()
        finally:
            conn.close()
    except pymysql.Error as e:
        # Log the technical detail on the server; never expose it to the client
        print(f"[DB ERROR] GET /api/items: {e}")
        return jsonify({"error": "Database unavailable. Please try again later."}), 503

    # price comes back as float (via the DECIMAL converter in DB_CONFIG)
    # stock comes back as int — MySQL INT maps directly to Python int
    return jsonify(rows), 200


# ---------------------------------------------------------------------------
# POST /api/items
# ---------------------------------------------------------------------------

@app.route("/api/items", methods=["POST"])
def create_item():
    """
    Insert a new product into MySQL.

    Expected JSON body:
        { "name": "Laptop", "price": 60000, "stock": 10 }

    Validation (identical to Phase 2):
        - name  : required, non-empty string
        - price : number strictly > 0
        - stock : non-negative integer (decimals like 5.5 are rejected)

    Returns the created product (with the MySQL-generated id) and HTTP 201.
    Returns HTTP 400 with { "error": "..." } on invalid input.
    Returns HTTP 503 if MySQL is unreachable.
    """

    # --- Parse body ---
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON with Content-Type: application/json"}), 400

    # --- Validate name ---
    name = data.get("name", "")
    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "name is required and must be a non-empty string"}), 400
    name = name.strip()

    # --- Validate price ---
    price = data.get("price")
    if price is None:
        return jsonify({"error": "price is required"}), 400
    try:
        price = float(price)
    except (TypeError, ValueError):
        return jsonify({"error": "price must be a number"}), 400
    if price <= 0:
        return jsonify({"error": "price must be greater than 0"}), 400

    # --- Validate stock ---
    stock = data.get("stock")
    if stock is None:
        return jsonify({"error": "stock is required"}), 400
    # JSON 5.5 → Python float; JSON 5 → Python int.  isinstance catches the difference.
    if not isinstance(stock, int) or isinstance(stock, bool):
        return jsonify({"error": "stock must be a non-negative integer"}), 400
    if stock < 0:
        return jsonify({"error": "stock must be 0 or greater"}), 400

    # --- Insert into MySQL ---
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s)",
                    (name, price, stock),
                )
                new_id = cursor.lastrowid   # MySQL-generated AUTO_INCREMENT id
            conn.commit()
        finally:
            conn.close()
    except pymysql.Error as e:
        print(f"[DB ERROR] POST /api/items: {e}")
        return jsonify({"error": "Database unavailable. Please try again later."}), 503

    product = {
        "id":    new_id,
        "name":  name,
        "price": price,
        "stock": stock,
    }
    return jsonify(product), 201


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("NimbusCart Phase 3 — Flask + MySQL")
    print(f"  DB host : {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"  DB name : {DB_CONFIG['database']}")
    print(f"  DB user : {DB_CONFIG['user']}")

    # Auto-create the products table on startup (requirement of the assignment)
    try:
        initialize_database()
    except pymysql.Error as e:
        print(f"[FATAL] Cannot connect to MySQL at startup: {e}")
        print("  Make sure MySQL is running and environment variables are set.")
        raise SystemExit(1)

    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", 5000))
    print(f"Starting Flask on http://{host}:{port}")
    print(f"Frontend: http://{host}:{port}/")
    app.run(host=host, port=port, debug=True)
