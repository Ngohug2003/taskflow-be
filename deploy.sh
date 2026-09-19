#!/usr/bin/env bash
set -e

echo "===== Task Flow Manager BE Deploy ====="

# Copy .env if not exist
[ ! -f .env ] && cp .env.example .env && echo "[+] Created .env from .env.example"

case "$1" in
  up)
    echo "[>] Starting BE + DB..."
    docker compose up -d --build
    echo "[✓] BE running at http://localhost:8000"
    echo "[✓] Swagger  at http://localhost:8000/docs"
    ;;
  down)
    echo "[>] Stopping services..."
    docker compose down
    ;;
  migrate)
    echo "[>] Running migrations..."
    docker compose -f docker-compose-migrate.yml up --build migrate
    docker compose -f docker-compose-migrate.yml down
    echo "[✓] Migration done"
    ;;
  migrate-make)
    if [ -z "$2" ]; then
      echo "Usage: ./deploy.sh migrate-make <migration_name>"
      exit 1
    fi
    echo "[>] Creating migration: $2"
    docker compose exec be alembic revision --autogenerate -m "$2"
    ;;
  logs)
    docker compose logs -f "${2:-be}"
    ;;
  shell)
    echo "[>] Opening shell in BE container..."
    docker compose exec be bash
    ;;
  reset-db)
    echo "[!] Resetting database (all data will be lost)..."
    docker compose down -v
    docker compose up -d db
    echo "[>] Waiting for DB..."
    sleep 8
    bash "$0" migrate
    echo "[✓] DB reset complete"
    ;;
  restart)
    docker compose restart "${2:-be}"
    ;;
  *)
    echo ""
    echo "Commands:"
    echo "  ./deploy.sh up                        — Start BE + DB"
    echo "  ./deploy.sh down                      — Stop all"
    echo "  ./deploy.sh migrate                   — Run Alembic migrations"
    echo "  ./deploy.sh migrate-make <name>       — Create new migration"
    echo "  ./deploy.sh logs [be|db]              — Tail logs"
    echo "  ./deploy.sh shell                     — Open bash in BE container"
    echo "  ./deploy.sh reset-db                  — Wipe DB and re-migrate"
    echo "  ./deploy.sh restart [service]         — Restart a service"
    echo ""
    exit 1
    ;;
esac