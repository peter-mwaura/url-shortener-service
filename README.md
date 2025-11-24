# URL Shortener Service 🚀

A lightweight, containerized **FastAPI URL Shortener** with:

-   PostgreSQL for persistent storage
-   Redis-based **rate limiting**
-   Full test suite (pytest + Docker)
-   Short URL generation with custom aliases
-   Clean project structure using modern Python tooling (`uv`)

---

## ✨ Features

-   🔗 **Shorten URLs** with automatically generated 6-character codes
-   🎯 Support for **custom aliases**
-   🔐 **Rate limiting** per IP using Redis  
    (Default: `5 requests / 60 seconds`)
-   🧪 Fully automated **test environment**
-   🐳 Production-ready **Docker setup** with isolated dev/test services

---

## 📁 Project Structure

```
.
├── README.md
├── app
│   ├── api
│   │   ├── analytics.py
│   │   ├── redirect.py
│   │   └── shorten.py
│   ├── db.py
│   ├── main.py
│   ├── models
│   │   └── urls.py
│   ├── schemas
│   │   └── urls.py
│   └── tests
│       └── test_shorten.py
├── docker
│   ├── Dockerfile.dev
│   └── docker-compose.dev.yml
├── main.py
├── pyproject.toml
└── uv.lock
```

---

## 📥 Clone the Repository

```bash
git clone https://github.com/peter-mwaura/url-shortener-service.git
cd url-shortener-service
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env.dev`:

```bash
cp .env.example .env.dev
```

`.env.example` includes:

```
# APP environment
APP_ENV=dev

# API settings
API_HOST=0.0.0.0
API_PORT=8000

# PostgreSQL
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_database_name
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
RATE_LIMIT=5
RATE_PERIOD=60

# Short URL domain
SHORT_URL_DOMAIN=http://localhost:8000
```

---

## 🐳 Running the Application (Docker)

Start all services (API + Postgres + Redis):

```bash
docker compose -f docker/docker-compose.dev.yml up -d --build
```

This launches:

-   FastAPI → http://localhost:8000
-   PostgreSQL → localhost:5433
-   Redis → localhost:6379

---

## 🧪 Running Tests

Using the built-in test service:

```bash
docker compose -f docker/docker-compose.dev.yml run --rm tests
```

Or include full setup and teardown:

```bash
docker compose -f docker/docker-compose.dev.yml up -d postgres redis   && docker compose -f docker/docker-compose.dev.yml run --rm tests   && docker compose -f docker/docker-compose.dev.yml down
```

---

## 🛣️ API Endpoints

### **POST /shorten**

Shorten a URL with optional custom alias.

#### Request

```json
{
    "original_url": "https://example.com",
    "custom_alias": "my-alias",
    "ttl_seconds": 3600
}
```

#### Response

```json
{
    "short_url": "http://localhost:8000/my-alias"
}
```

---

## 🏗️ Technology Stack

-   FastAPI
-   SQLAlchemy ORM
-   PostgreSQL 15
-   Redis (rate limiting)
-   Docker / Docker Compose
-   uv (Python package manager)
-   pytest

---

## 📌 Development Notes

-   Only the `/shorten` route is implemented for now.
-   Redirect and analytics routes are scaffolded for future work.
-   Rate limiting uses a fixed‑window algorithm with Redis.

---

## 📄 License

MIT License — feel free to use and modify.

---

## 👤 Author

**Peter Mwaura**  
URL Shortener Project — 2025
