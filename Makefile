.PHONY: dev dev-infra stop migrate seed ingest test-backend test-frontend lint

# Start all services
dev:
	docker-compose up -d

# Start only infrastructure (postgres, redis, elasticsearch)
dev-infra:
	docker-compose up -d postgres redis elasticsearch

# Stop all services
stop:
	docker-compose down

# Run database migrations
migrate:
	cd backend && alembic upgrade head

# Seed all data (archetypes + demo dossiers)
seed:
	cd backend && python -m scripts.seed_archetypes
	cd backend && python -m scripts.seed_demo_dossiers

# Seed archetypes only
seed-archetypes:
	cd backend && python -m scripts.seed_archetypes

# Seed demo dossiers only
seed-dossiers:
	cd backend && python -m scripts.seed_demo_dossiers

# Ingest demo corpus
ingest:
	cd backend && python -m scripts.ingest_corpus

# Precompute demo dossiers
precompute:
	cd backend && python -m scripts.precompute_dossiers

# Run backend tests
test-backend:
	cd backend && python -m pytest tests/ -v

# Run frontend tests
test-frontend:
	cd frontend && npm test

# Lint
lint:
	cd backend && ruff check .
	cd frontend && npm run lint

# Backend dev server (local, no docker)
backend-dev:
	cd backend && uvicorn app.main:app --reload --port 8000

# Frontend dev server (local, no docker)
frontend-dev:
	cd frontend && npm run dev
