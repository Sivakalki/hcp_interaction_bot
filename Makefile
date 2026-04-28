# HCPFiller Project Makefile

.PHONY: install-backend install-frontend install dev-backend dev-frontend dev db-init

# ── Installation ──────────────────────────────────────────────────────────

install-backend:
	cd Backend && python -m venv venv && .\venv\Scripts\activate && pip install -r requirements.txt

install-frontend:
	cd Frontend && npm install

install: install-backend install-frontend

# ── Development ─────────────────────────────────────────────────────────────

# Run backend development server
dev-backend:
	cd Backend && .\venv\Scripts\python.exe -m app.main

# Run frontend development server
dev-frontend:
	cd Frontend && npm run dev

# Run both backend and frontend concurrently (Windows specific)
dev:
	cmd /c start cmd /k "make dev-backend"
	cmd /c start cmd /k "make dev-frontend"

# ── Database ────────────────────────────────────────────────────────────────

# Initialize database tables
db-init:
	cd Backend && .\venv\Scripts\python.exe scripts/init_db.py

# ── Help ────────────────────────────────────────────────────────────────────

help:
	@echo "Available commands:"
	@echo "  make install      - Install all dependencies (Backend & Frontend)"
	@echo "  make dev          - Run both Backend and Frontend concurrently"
	@echo "  make dev-backend  - Run only the FastAPI backend"
	@echo "  make dev-frontend - Run only the React frontend"
	@echo "  make db-init      - Initialize the database tables"
