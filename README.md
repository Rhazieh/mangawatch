> **🔧 Fork Contribution by Maxi Cano ([@Rhazieh](https://github.com/Rhazieh)):**
> Branch [`fix-docker-restart`](https://github.com/Rhazieh/mangawatch/tree/fix-docker-restart) adds `restart` policies to the `docker-compose.yml` services (`fix: add restart policy to docker-compose services`) to improve container resilience and automatic recovery after host reboots or unexpected failures.

---

# MangaWatch

Manga/manhwa chapter release tracker built as a DevOps-oriented full-stack project with **FastAPI**, **PostgreSQL**, **SQLAlchemy 2.0**, **Alembic**, **Docker**, **GitHub Actions**, and **Fly.io** deployment.

For domain glossary and entity definitions (`Series`, `Chapter`, `Source`, `Subscription`, `User`, `Notification`), see [`CONTEXT.md`](./CONTEXT.md).

---

## Tech Stack

- **Backend:** Python 3.12, FastAPI, Uvicorn, SQLAlchemy 2.0, Alembic, Pydantic Settings
- **Scraping & Scheduling:** BeautifulSoup4, APScheduler, `POST /internal/poll` endpoint triggered by GitHub Actions cron (`.github/workflows/poll.yml`)
- **Monitoring & Alerts:** Prometheus metrics (`prometheus-client`), Discord webhooks
- **Frontend:** Static HTML/JS served via FastAPI `StaticFiles` (`/ui`)
- **Database:** PostgreSQL 16 (`psycopg2-binary`)
- **Containers & CI/CD:** Multi-stage `Dockerfile` (`python:3.12-slim`), `docker-compose.yml`, Ruff, Pytest, GitHub Actions (`.github/workflows/ci.yml`, `cd.yml`, `poll.yml`), Fly.io (`fly.toml`)

---

## Quick Start (Docker Compose)

1. Copy `.env.example` to `.env` and configure `JWT_SECRET` and optional integrations (`DISCORD_WEBHOOK_URL`, `SENDGRID_API_KEY`).
2. Start the application and PostgreSQL:

```bash
cp .env.example .env
docker compose up --build -d
```

The container entrypoint runs Alembic migrations on startup and serves the app on `http://localhost:8000`.
