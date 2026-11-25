# Multi-Tier Containerized Web App & CI/CD Pipeline

A production-style 3-tier containerized application orchestrated with **Docker Compose** and automated with **GitHub Actions CI/CD**.

## Architecture Overview

Client (Port 8080) -> Nginx Reverse Proxy (frontend-net) -> Python Flask + Gunicorn API (backend-net) -> PostgreSQL 16 DB (pgdata volume)

## Key Engineering Features
- **Network Isolation:** Two separate Docker bridge networks (`frontend-net` and `backend-net`) isolate PostgreSQL from the public-facing Nginx reverse proxy.
- **Service Health Checks:** `depends_on` with `condition: service_healthy` ensures the Python API starts only after `pg_isready` confirms PostgreSQL is ready.
- **Persistent Storage:** Named Docker volume (`pgdata`) preserves database records across container restarts.
- **Automated CI/CD:** GitHub Actions builds the stack on every push to `main`, executes end-to-end integration tests (`/health`, `POST /deployments`, `GET /deployments`), and tags verified container images.

## Quick Start (Local)
1. Copy the environment template: `cp .env.example .env`
2. Build and start all services: `docker compose up --build -d`
3. Test endpoints:
   - Health check: `curl http://localhost:8080/health`
   - Add record: `curl -X POST http://localhost:8080/deployments -H "Content-Type: application/json" -d '{"service_name":"payment-api","status":"deployed"}'`
   - List records: `curl http://localhost:8080/deployments`