<!-- @format -->

# NimbusCart

NimbusCart is a small product-catalog application built with:

- HTML, CSS, and Vanilla JavaScript
- Flask
- MySQL 8
- Docker
- Docker Compose

The application allows users to:

- View products
- Add new products
- View product price and stock
- Validate product information
- Persist products in MySQL

The entire application runs locally using Docker.

---

## Architecture

```text
                    Browser
                       |
                       | http://localhost:5000
                       v
              +------------------+
              |   Flask API      |
              |   API Container  |
              +--------+---------+
                       |
                       | mysql:3306
                       v
              +------------------+
              |     MySQL 8      |
              | MySQL Container  |
              +--------+---------+
                       |
                       v
                 products table
```

### Containers

NimbusCart uses two Docker containers:

```text
api
└── Flask + Python application

mysql
└── MySQL 8 database
```

The Flask container communicates with MySQL using:

```text
mysql:3306
```

Do not use `localhost:3307` from inside the Flask container.

---

# Requirements

You only need the following installed on your laptop:

### 1. Git

Download/install Git if you don't already have it.

After installation, verify:

```powershell
git --version
```

### 2. Docker Desktop

Install Docker Desktop.

After installation, open Docker Desktop and make sure the Docker Engine is running.

Verify:

```powershell
docker --version
```

Then:

```powershell
docker compose version
```

Both commands should return version information.

You do **not** need to install:

- Python
- Flask
- MySQL
- PyMySQL
- Node.js
- npm

These are handled by Docker.

---

# 1. Clone the Repository

Open PowerShell and choose where you want to keep the project.

For example:

```powershell
cd C:\Users\YourName\Desktop
```

Clone the repository:

```powershell
git clone https://github.com/hopstreax/NimbusCart.git
```

Enter the project directory:

```powershell
cd NimbusCart
```

---

# 2. Configure Environment Variables

The `.env` file is intentionally not stored in GitHub because it contains database credentials.

Create a file named:

```text
.env
```

in the root of the project.

The structure should be:

```text
NimbusCart/
├── .env
├── docker-compose.yml
├── README.md
└── app/
```

Add the following:

```env
MYSQL_DATABASE=nimbuscart
MYSQL_USER=nimbususer
MYSQL_PASSWORD=your_database_password
MYSQL_ROOT_PASSWORD=your_root_password
```

You can choose your own passwords.

### Important

Do not commit `.env` to Git.

It is already included in `.gitignore`.

---

# 3. Build and Start the Application

From the NimbusCart project directory, run:

```powershell
docker compose up -d --build
```

This command will:

1. Build the Flask API Docker image.
2. Download the MySQL image if necessary.
3. Create the Docker network.
4. Create the MySQL container.
5. Create the Flask API container.
6. Start both containers.
7. Connect Flask to MySQL.

The first startup may take longer because Docker may need to download images and install Python dependencies.

---

# 4. Check the Containers

Run:

```powershell
docker compose ps
```

You should see two services:

```text
api
mysql
```

The MySQL service should eventually show:

```text
healthy
```

The API should show:

```text
Up
```

If you want to see the logs:

```powershell
docker compose logs
```

To see only the Flask API logs:

```powershell
docker compose logs api
```

To see only MySQL logs:

```powershell
docker compose logs mysql
```

---

# 5. Open NimbusCart

Once both containers are running, open:

```text
http://127.0.0.1:5000/
```

or:

```text
http://localhost:5000/
```

You should see the NimbusCart application.

---

# 6. Using the Application

The application contains:

### Product Table

The table displays:

- Product name
- Price
- Stock

### Add Product

You can add a product using:

- Name
- Price
- Stock

Example:

```text
Name: Mechanical Keyboard
Price: 79.99
Stock: 50
```

After submitting, the product is stored in MySQL.

Refreshing the browser should not remove the product.

---

# 7. API Endpoints

NimbusCart exposes the following endpoints.

## Health Check

```text
GET /health
```

Example:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

---

## Get Products

```text
GET /api/items
```

Example:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/items
```

Example response:

```json
[
  {
    "id": 1,
    "name": "Laptop",
    "price": 60000,
    "stock": 10
  }
]
```

---

## Add Product

```text
POST /api/items
```

PowerShell example:

```powershell
$body = @{
    name  = "Mechanical Keyboard"
    price = 79.99
    stock = 50
} | ConvertTo-Json

Invoke-RestMethod `
    -Method POST `
    -Uri http://127.0.0.1:5000/api/items `
    -ContentType "application/json" `
    -Body $body
```

A successful request returns HTTP `201`.

---

# 8. Database

NimbusCart uses:

```text
MySQL 8
```

The database runs inside Docker.

The Flask application automatically creates the required table when it starts.

The table is:

```text
products
```

with:

```text
id
name
price
stock
```

You do not need to manually create the table.

---

# 9. Data Persistence

MySQL uses a Docker volume to persist database data.

Therefore, this:

```powershell
docker compose down
```

does **not** delete your products.

Starting the application again:

```powershell
docker compose up -d
```

will restore the existing database.

### WARNING

This command deletes the database volume:

```powershell
docker compose down -v
```

That means all locally stored NimbusCart products will be deleted.

Use it only when you intentionally want a completely fresh database.

---

# 10. Stopping the Application

To stop the containers:

```powershell
docker compose down
```

The containers will be removed, but the MySQL data volume will remain.

To start the application again:

```powershell
docker compose up -d
```

---

# 11. Resetting the Database

If you intentionally want to start with an empty database:

```powershell
docker compose down -v
```

Then:

```powershell
docker compose up -d --build
```

The Flask application will automatically create the `products` table again.

---

# 12. Running Tests

The repository contains API and integration tests.

With the Docker application running:

```powershell
python app\api\test_phase3.py
```

and:

```powershell
python app\api\test_integration.py
```

These tests verify things such as:

- API health
- Product creation
- Product retrieval
- Validation
- Database persistence
- Frontend/API integration

---

# 13. Troubleshooting

## Docker command not found

If you see:

```text
docker : The term 'docker' is not recognized
```

make sure Docker Desktop is installed.

Then restart PowerShell.

Verify:

```powershell
docker --version
```

---

## Docker daemon is not running

If you see an error mentioning:

```text
failed to connect to the docker API
```

open Docker Desktop and wait until Docker Engine is running.

Then try:

```powershell
docker info
```

---

## API container is not running

Check:

```powershell
docker compose ps
```

Then inspect the logs:

```powershell
docker compose logs api
```

---

## MySQL is not healthy

Check:

```powershell
docker compose ps
```

Then:

```powershell
docker compose logs mysql
```

MySQL can take some time to initialize during the first startup.

Wait a little and check again:

```powershell
docker compose ps
```

---

## Port 5000 is already in use

If another application is already using port 5000, check which process is using it.

On Windows PowerShell:

```powershell
netstat -ano | findstr :5000
```

Stop the conflicting application or change the host port in `docker-compose.yml`.

---

# 14. Project Structure

The important project files are:

```text
NimbusCart/
│
├── app/
│   ├── api/
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── test_phase3.py
│   │   └── test_integration.py
│   │
│   └── frontend/
│       └── index.html
│
├── docker-compose.yml
├── .gitignore
├── .env
└── README.md
```

---

# 15. Development Workflow

After cloning the project:

```powershell
cd NimbusCart
```

Start everything:

```powershell
docker compose up -d --build
```

Check containers:

```powershell
docker compose ps
```

Open:

```text
http://127.0.0.1:5000/
```

When finished:

```powershell
docker compose down
```

For future code changes, rebuild the API container:

```powershell
docker compose up -d --build
```

---

# 16. Important Security Note

Never commit the `.env` file.

Do not put real passwords directly into:

- Python code
- Dockerfile
- docker-compose.yml
- README.md
- test files

Use environment variables instead.

---

# Quick Start

If Git and Docker Desktop are already installed, the basic setup is:

```powershell
git clone https://github.com/hopstreax/NimbusCart.git
cd NimbusCart
```

Create `.env` in the project root:

```env
MYSQL_DATABASE=nimbuscart
MYSQL_USER=nimbususer
MYSQL_PASSWORD=your_database_password
MYSQL_ROOT_PASSWORD=your_root_password
```

Then:

```powershell
docker compose up -d --build
```

Open:

```text
http://127.0.0.1:5000/
```

That's it.

---

# Stopping NimbusCart

```powershell
docker compose down
```

Start again later with:

```powershell
docker compose up -d
```

Your database data will remain.

---

## Technology Stack

| Technology          | Purpose                   |
| ------------------- | ------------------------- |
| HTML/CSS/JavaScript | Frontend                  |
| Flask               | REST API                  |
| Python              | Backend language          |
| MySQL 8             | Database                  |
| PyMySQL             | Python → MySQL connection |
| Docker              | Containerization          |
| Docker Compose      | Runs API + MySQL together |
